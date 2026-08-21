import os
import re
import secrets
from datetime import datetime
from functools import wraps

import click
from dotenv import load_dotenv
from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import generate_password_hash

import web_database as db
from telegram_notifications import notify_joined, notify_new_enquiry


load_dotenv()

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.getenv("FLASK_SECRET_KEY", "dev-only-change-me"),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.getenv("COOKIE_SECURE", "false").lower() == "true",
)

CENTRE = "Dadar"
STATUSES = ["New", "Interested", "Demo Scheduled", "Demo Attended", "Joined", "Closed"]
SOURCES = [
    "Google Search",
    "Justdial",
    "Friend Reference",
    "Past Student",
    "Google Ad",
    "Meta Ad",
    "Instagram Post",
    "Other",
    "Not Specified",
]
DECISION_MAKERS = ["Self", "Parents", "Spouse", "Employer", "Other", "Not Specified"]
BUDGET_RANGES = [
    "Below ₹10,000",
    "₹10,000–₹25,000",
    "₹25,000–₹50,000",
    "₹50,000–₹1,00,000",
    "Above ₹1,00,000",
    "Not Discussed",
]
START_PLANS = [
    "Immediately",
    "Within 7 Days",
    "Within 15 Days",
    "Within 1 Month",
    "Within 3 Months",
    "Just Exploring",
    "Not Specified",
]
COURSES = [
    "AutoCAD",
    "Solidworks",
    "Revit Architecture",
    "3DS Max",
    "Google SketchUp",
    "Not Decided",
]


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)

    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login"))
        if session.get("role") != "admin":
            abort(403)
        return view(*args, **kwargs)

    return wrapped


@app.before_request
def csrf_protection():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)
    if request.method == "POST" and not secrets.compare_digest(
        session["csrf_token"], request.form.get("csrf_token", "")
    ):
        abort(400, "Invalid form token. Refresh the page and try again.")


def visible_enquiries(filter_name="all", search=""):
    assigned_user_id = None if session.get("role") == "admin" else session["user_id"]
    return db.list_enquiries(
        filter_name=filter_name,
        search=search,
        centre=CENTRE,
        assigned_user_id=assigned_user_id,
    )


def can_access(enquiry):
    return session.get("role") == "admin" or str(enquiry.get("assigned_user_id")) == str(
        session.get("user_id")
    )


def normalize_indian_mobile(value, required=True):
    raw = (value or "").strip()
    if not raw and not required:
        return None
    digits = re.sub(r"\D", "", raw)
    if len(digits) == 11 and digits.startswith("0"):
        digits = digits[1:]
    if len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]
    if len(digits) != 10 or digits[0] not in "6789":
        raise ValueError("Enter a valid 10-digit Indian mobile number starting with 6, 7, 8 or 9.")
    return f"+91{digits}"


@app.context_processor
def shared_template_data():
    return {
        "centre": CENTRE,
        "today": datetime.now().date().isoformat(),
        "statuses": STATUSES,
        "sources": SOURCES,
        "decision_makers": DECISION_MAKERS,
        "budget_ranges": BUDGET_RANGES,
        "start_plans": START_PLANS,
        "courses": COURSES,
    }


@app.get("/")
def index():
    return redirect(url_for("dashboard") if session.get("user_id") else url_for("login"))


@app.get("/health")
def health():
    return {"status": "ok"}


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = db.authenticate_user(request.form.get("username", ""), request.form.get("password", ""))
        if not user:
            flash("Invalid username or password.", "error")
        else:
            session.clear()
            session.update(
                user_id=user["id"],
                full_name=user["full_name"],
                role=user["role"],
                centre=user.get("centre") or CENTRE,
            )
            return redirect(url_for("dashboard"))
    return render_template("login.html")


@app.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.get("/dashboard")
@login_required
def dashboard():
    enquiries = visible_enquiries()
    today = datetime.now().date().isoformat()
    active = [row for row in enquiries if row.get("status") not in ("Joined", "Closed")]
    due = [
        row
        for row in active
        if row.get("next_followup_datetime")
        and str(row["next_followup_datetime"])[:10] <= today
    ]
    return render_template(
        "dashboard.html",
        total=len(enquiries),
        active=len(active),
        due=len(due),
        joined=sum(row.get("status") == "Joined" for row in enquiries),
        due_enquiries=due[:8],
    )


@app.get("/enquiries")
@login_required
def enquiries():
    filter_name = request.args.get("filter", "all")
    search = request.args.get("search", "").strip()
    return render_template(
        "enquiries.html",
        enquiries=visible_enquiries(filter_name, search),
        selected_filter=filter_name,
        search=search,
    )


@app.route("/enquiries/new", methods=["GET", "POST"])
@login_required
def new_enquiry():
    counsellors = db.list_counsellors(CENTRE)
    if request.method == "POST":
        try:
            data = enquiry_payload(request.form)
        except ValueError as exc:
            flash(str(exc), "error")
            return render_template("enquiry_form.html", enquiry=None, counsellors=counsellors), 400
        if data["status"] == "Joined":
            data["status"] = "New"
        assigned_user_id = data["assigned_user_id"]
        if session.get("role") != "admin":
            assigned_user_id = session["user_id"]
            data["counsellor"] = session["full_name"]
        else:
            assigned_user = db.get_user(assigned_user_id)
            if not assigned_user or assigned_user.get("centre") != CENTRE:
                abort(400)
            data["counsellor"] = assigned_user["full_name"]
        data["assigned_user_id"] = assigned_user_id
        data["created_by"] = session["user_id"]
        try:
            enquiry_id = db.create_enquiry(data)
        except db.DuplicateEnquiryError as exc:
            existing = exc.existing
            flash(
                f"This mobile number already belongs to {existing.get('student_name', 'an existing student')} "
                f"({existing.get('course_interest', 'course not specified')}, status: {existing.get('status', 'unknown')}).",
                "error",
            )
            if can_access(existing):
                return redirect(url_for("enquiry_detail", enquiry_id=existing["id"]))
        else:
            notify_new_enquiry(data)
            flash("Enquiry created successfully.", "success")
            return redirect(url_for("enquiry_detail", enquiry_id=enquiry_id))
    return render_template("enquiry_form.html", enquiry=None, counsellors=counsellors)


@app.get("/enquiries/<int:enquiry_id>")
@login_required
def enquiry_detail(enquiry_id):
    enquiry = db.get_enquiry(enquiry_id)
    if not enquiry:
        abort(404)
    if not can_access(enquiry):
        abort(403)
    return render_template(
        "enquiry_detail.html",
        enquiry=enquiry,
        history=db.get_followup_history(enquiry_id),
    )


@app.route("/enquiries/<int:enquiry_id>/edit", methods=["GET", "POST"])
@login_required
def edit_enquiry(enquiry_id):
    enquiry = db.get_enquiry(enquiry_id)
    if not enquiry:
        abort(404)
    if not can_access(enquiry):
        abort(403)
    counsellors = db.list_counsellors(CENTRE)
    if request.method == "POST":
        try:
            data = enquiry_payload(request.form, editing=True)
        except ValueError as exc:
            flash(str(exc), "error")
            return render_template("enquiry_form.html", enquiry=enquiry, counsellors=counsellors), 400
        if data["status"] == "Joined" and enquiry.get("status") != "Joined":
            data["status"] = enquiry.get("status", "New")
        if session.get("role") != "admin":
            data.pop("assigned_user_id", None)
            data.pop("counsellor", None)
        else:
            assigned_user = db.get_user(data["assigned_user_id"])
            if not assigned_user or assigned_user.get("centre") != CENTRE:
                abort(400)
            data["counsellor"] = assigned_user["full_name"]
        data["updated_by"] = session["user_id"]
        try:
            db.update_enquiry(enquiry_id, data)
        except db.DuplicateEnquiryError as exc:
            flash(f"That mobile number already belongs to {exc.existing.get('student_name', 'another enquiry')}.", "error")
            return render_template("enquiry_form.html", enquiry=enquiry, counsellors=counsellors), 409
        flash("Enquiry updated.", "success")
        return redirect(url_for("enquiry_detail", enquiry_id=enquiry_id))
    return render_template("enquiry_form.html", enquiry=enquiry, counsellors=counsellors)


@app.route("/enquiries/<int:enquiry_id>/follow-up", methods=["GET", "POST"])
@login_required
def add_followup(enquiry_id):
    enquiry = db.get_enquiry(enquiry_id)
    if not enquiry:
        abort(404)
    if not can_access(enquiry):
        abort(403)
    if request.method == "POST":
        next_date = request.form.get("next_followup_date", "")
        next_time = request.form.get("next_followup_time", "")
        next_at = f"{next_date}T{next_time}:00" if next_date and next_time else None
        status = request.form.get("status", enquiry.get("status", "New"))
        joined_course = None
        joined_course_fee = None
        if status == "Joined":
            joined_course = request.form.get("joined_course", "").strip()
            try:
                joined_course_fee = float(request.form.get("joined_course_fee", ""))
            except (TypeError, ValueError):
                joined_course_fee = 0
            if not joined_course or joined_course_fee <= 0:
                flash("Select the confirmed course and enter its fee before marking the student as Joined.", "error")
                return render_template("followup_form.html", enquiry=enquiry), 400
        db.add_followup(
            enquiry=enquiry,
            followup_type=request.form.get("followup_type", "Call"),
            response=request.form.get("response", ""),
            remarks=request.form.get("remarks", ""),
            next_followup_datetime=next_at,
            status=status,
            user_id=session["user_id"],
            counsellor=session["full_name"],
            joined_course=joined_course,
            joined_course_fee=joined_course_fee,
        )
        if status == "Joined" and enquiry.get("status") != "Joined":
            notify_joined(enquiry, joined_course, joined_course_fee, session["full_name"])
        flash("Follow-up saved." + (" Student is now available to the attendance system." if status == "Joined" else ""), "success")
        return redirect(url_for("enquiry_detail", enquiry_id=enquiry_id))
    return render_template("followup_form.html", enquiry=enquiry)


@app.get("/follow-ups")
@login_required
def followups():
    filter_name = request.args.get("filter", "today")
    return render_template(
        "followups.html",
        enquiries=visible_enquiries(filter_name),
        selected_filter=filter_name,
    )


@app.route("/users", methods=["GET", "POST"])
@admin_required
def users():
    if request.method == "POST":
        try:
            db.create_user(
                full_name=request.form["full_name"].strip(),
                username=request.form["username"].strip(),
                password=request.form["password"],
                role=request.form.get("role", "counsellor"),
                centre=CENTRE,
            )
        except Exception as exc:
            flash(f"Could not create user: {exc}", "error")
        else:
            flash("User created.", "success")
            return redirect(url_for("users"))
    return render_template("users.html", users=db.list_users(CENTRE))


def enquiry_payload(form, editing=False):
    next_date = form.get("next_followup_date", "")
    next_time = form.get("next_followup_time", "")
    assigned_user_id = form.get("assigned_user_id") or session["user_id"]
    counsellor = form.get("counsellor") or session["full_name"]
    phone = normalize_indian_mobile(form.get("phone"))
    alternate_phone = normalize_indian_mobile(form.get("alternate_phone"), required=False)
    if alternate_phone == phone:
        raise ValueError("Alternate phone number must be different from the primary mobile number.")
    data = {
        "student_name": form.get("student_name", "").strip(),
        "phone": phone,
        "alternate_phone": alternate_phone,
        "email": form.get("email", "").strip() or None,
        "education": form.get("education", "Not Specified"),
        "education_stage": form.get("education_stage", "Not Specified"),
        "locality": form.get("locality", "").strip() or None,
        "preferred_language": form.get("preferred_language", "English"),
        "lead_temperature": form.get("lead_temperature", "Warm"),
        "remarks": form.get("remarks", "").strip(),
        "next_action": form.get("next_action", "Call Student"),
        "enquiry_date": form.get("enquiry_date") or datetime.now().date().isoformat(),
        "next_followup_datetime": f"{next_date}T{next_time}:00" if next_date and next_time else None,
        "status": form.get("status", "New"),
        "counsellor": counsellor,
        "source": form.get("source", "Not Specified"),
        "course_interest": form.get("course_interest", "Not Decided"),
        "decision_maker": form.get("decision_maker", "Not Specified"),
        "budget_range": form.get("budget_range", "Not Discussed"),
        "planning_to_start": form.get("planning_to_start", "Not Specified"),
        "demo_attended": form.get("demo_attended", "No") == "Yes",
        "Nearest_CADD_Centre": CENTRE,
        "assigned_user_id": assigned_user_id,
    }
    if editing:
        data.pop("enquiry_date", None)
    return data


@app.cli.command("create-user")
@click.option("--name", prompt="Full name")
@click.option("--username", prompt=True)
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
@click.option("--role", type=click.Choice(["admin", "counsellor"]), default="admin")
def create_user_command(name, username, password, role):
    """Create the first admin or another CRM user."""
    db.create_user(name, username, password, role, CENTRE)
    click.echo(f"Created {role} user {username}.")


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
