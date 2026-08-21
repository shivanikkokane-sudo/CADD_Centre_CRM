import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from supabase import create_client
from werkzeug.security import check_password_hash, generate_password_hash


load_dotenv()

client = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])


class DuplicateEnquiryError(Exception):
    def __init__(self, existing):
        self.existing = existing
        super().__init__("An enquiry already exists for this mobile number")


def authenticate_user(username, password):
    response = (
        client.table("crm_users")
        .select("*")
        .eq("username", username.strip().lower())
        .eq("is_active", True)
        .limit(1)
        .execute()
    )
    if not response.data or not check_password_hash(response.data[0]["password_hash"], password):
        return None
    return response.data[0]


def create_user(full_name, username, password, role="counsellor", centre="Dadar"):
    if len(password) < 8:
        raise ValueError("Password must contain at least 8 characters")
    payload = {
        "full_name": full_name,
        "username": username.strip().lower(),
        "password_hash": generate_password_hash(password),
        "role": role,
        "centre": centre,
        "is_active": True,
    }
    return client.table("crm_users").insert(payload).execute().data[0]


def list_users(centre="Dadar"):
    return client.table("crm_users").select("id,full_name,username,role,centre,is_active").eq("centre", centre).order("full_name").execute().data


def get_user(user_id):
    response = client.table("crm_users").select("id,full_name,role,centre,is_active").eq("id", user_id).limit(1).execute()
    return response.data[0] if response.data else None


def list_counsellors(centre="Dadar"):
    return client.table("crm_users").select("id,full_name").eq("centre", centre).eq("is_active", True).in_("role", ["admin", "counsellor"]).order("full_name").execute().data


def list_enquiries(filter_name="all", search="", centre="Dadar", assigned_user_id=None):
    query = client.table("enquiries").select("*").eq("Nearest_CADD_Centre", centre)
    if assigned_user_id is not None:
        query = query.eq("assigned_user_id", assigned_user_id)

    today = datetime.now().date()
    today_start = f"{today.isoformat()}T00:00:00"
    today_end = f"{today.isoformat()}T23:59:59"
    if filter_name == "today":
        query = query.gte("next_followup_datetime", today_start).lte("next_followup_datetime", today_end)
    elif filter_name == "overdue":
        query = query.lt("next_followup_datetime", datetime.now().isoformat()).not_.in_("status", ["Joined", "Closed"])
    elif filter_name == "upcoming":
        end = f"{(today + timedelta(days=7)).isoformat()}T23:59:59"
        query = query.gt("next_followup_datetime", today_end).lte("next_followup_datetime", end)
    elif filter_name == "joined":
        query = query.eq("status", "Joined")
    elif filter_name == "active":
        query = query.not_.in_("status", ["Joined", "Closed"])

    if search:
        safe = search.replace(",", " ")
        query = query.or_(f"student_name.ilike.%{safe}%,phone.ilike.%{safe}%,course_interest.ilike.%{safe}%")
    return query.order("id", desc=True).execute().data


def get_enquiry(enquiry_id):
    response = client.table("enquiries").select("*").eq("id", enquiry_id).limit(1).execute()
    return response.data[0] if response.data else None


def create_enquiry(data):
    data["telegram_sent"] = False
    duplicate = find_enquiry_by_phone(data["phone"])
    if duplicate:
        raise DuplicateEnquiryError(duplicate)
    response = client.table("enquiries").insert(data).execute()
    enquiry = response.data[0]
    client.table("followup_logs").insert(
        {
            "enquiry_id": enquiry["id"],
            "student_name": data["student_name"],
            "followup_date": datetime.now().isoformat(),
            "followup_type": "Enquiry Created",
            "response": "New Lead",
            "response_status": data["status"],
            "remarks": data.get("remarks", ""),
            "next_followup_datetime": data.get("next_followup_datetime"),
            "counsellor": data["counsellor"],
            "created_by": data["created_by"],
        }
    ).execute()
    return enquiry["id"]


def find_enquiry_by_phone(phone, exclude_id=None):
    digits = "".join(character for character in phone if character.isdigit())[-10:]
    response = client.table("enquiries").select(
        "id,student_name,phone,alternate_phone,course_interest,status,assigned_user_id"
    ).execute()
    for enquiry in response.data:
        if exclude_id is not None and str(enquiry["id"]) == str(exclude_id):
            continue
        stored_numbers = (enquiry.get("phone"), enquiry.get("alternate_phone"))
        for stored in stored_numbers:
            stored_digits = "".join(character for character in (stored or "") if character.isdigit())[-10:]
            if stored_digits == digits:
                return enquiry
    return None


def update_enquiry(enquiry_id, data):
    current = get_enquiry(enquiry_id)
    duplicate = find_enquiry_by_phone(data["phone"], exclude_id=enquiry_id)
    if duplicate:
        raise DuplicateEnquiryError(duplicate)
    if data.get("status") == "Joined" and current.get("status") != "Joined":
        data.update(joined_at=datetime.now().isoformat(), joined_by=data.get("updated_by"))
    elif data.get("status") != "Joined" and current.get("status") == "Joined":
        data.update(joined_at=None, joined_by=None)
    return client.table("enquiries").update(data).eq("id", enquiry_id).execute()


def add_followup(enquiry, followup_type, response, remarks, next_followup_datetime, status, user_id, counsellor, joined_course=None, joined_course_fee=None):
    now = datetime.now().isoformat()
    client.table("followup_logs").insert(
        {
            "enquiry_id": enquiry["id"],
            "student_name": enquiry["student_name"],
            "followup_date": now,
            "followup_type": followup_type,
            "response": response,
            "response_status": status,
            "remarks": remarks,
            "next_followup_datetime": next_followup_datetime,
            "counsellor": counsellor,
            "created_by": user_id,
        }
    ).execute()
    update = {
        "status": status,
        "remarks": remarks,
        "last_followup_date": now,
        "next_followup_datetime": next_followup_datetime,
        "updated_by": user_id,
        "telegram_sent": False,
    }
    if status == "Joined" and enquiry.get("status") != "Joined":
        update.update(
            joined_at=now,
            joined_by=user_id,
            course_interest=joined_course,
            course_fee=joined_course_fee,
        )
    return client.table("enquiries").update(update).eq("id", enquiry["id"]).execute()


def get_followup_history(enquiry_id):
    return client.table("followup_logs").select("*").eq("enquiry_id", enquiry_id).order("followup_date", desc=True).execute().data
