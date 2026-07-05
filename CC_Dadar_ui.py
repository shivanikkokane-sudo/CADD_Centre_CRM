# -*- coding: utf-8 -*-
"""
Created on Wed May 13 20:49:19 2026

@author: Karan
"""
import os
print(os.getcwd())

import tkinter as tk

from tkinter import ttk #themed tkinter
#It is a newer set of widgets in Tkinter that provides modern-looking UI components compared to the classic tkinter widgets.
from tkinter import messagebox

import cloud_database

import os
print(os.getcwd())
from dotenv import load_dotenv
load_dotenv()
import requests

# -------------------------
# TELEGRAM CONFIG
# -------------------------

BOT_TOKEN = os.getenv("BOT_TOKEN")

CHAT_ID = os.getenv("CHAT_ID")

Sneha_CHAT_ID = os.getenv("Sneha_CHAT_ID")


"""
def send_wel_telegram_message(message):

    url = (
        f"https://api.telegram.org/bot"
        f"{BOT_TOKEN}/sendMessage"
    )

    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }

    requests.post(
        url,
        data=payload
    )

"""
def send_wel_telegram_message(message, data):

    url = (
        f"https://api.telegram.org/bot"
        f"{BOT_TOKEN}/sendMessage"
    )

    # Your chat id (always receives)
    chat_ids = [CHAT_ID]
    
    centre = data["Nearest_CADD_Centre"]
    
    # Employee based on centre
    if centre == "Dadar":
        chat_ids.append(Sneha_CHAT_ID)
        
    """
    elif centre == "Deccan":
        chat_ids.append(Deccan_chat_ID)
        """
    # Send to all selected people
    for chat_id in chat_ids:

        payload = {
            "chat_id": chat_id,
            "text": message
        }

        requests.post(
            url,
            data=payload
        )

def send_admission_telegram(
    student_name,
    phone,
    centre,
    final_course,
    course_fee,
    first_payment,
    admission_date,
    counsellor
):

    balance_fee = float(course_fee) - float(first_payment)

    message = f"""
🎉 NEW ADMISSION

👨‍🎓 Student: {student_name}
📞 Phone: {phone}

📚 Course: {final_course}

💰 Course Fee: ₹{course_fee}
💵 First Payment: ₹{first_payment}
💳 Balance Fee: ₹{balance_fee}

📅 Admission Date: {admission_date}

🏢 Centre: {centre}
👤 Counsellor: {counsellor}
"""

    data = {
        "Nearest_CADD_Centre": centre
    }

    send_wel_telegram_message(
        message,
        data
    )


def send_payment_telegram(
    student,
    payment_date,
    amount,
    payment_mode,
    remarks,
    finance
):

    centre = student.get(
        "centre",
        ""
    )

    balance = (
        finance.get(
            "balance_receivable",
            "-"
        )
        if finance
        else "-"
    )

    message = f"""
STUDENT PAYMENT RECEIVED

Student: {student.get("student_name", "")}
Phone: {student.get("mobile", "")}
Course: {student.get("course_name", "")}

Amount: Rs. {amount}
Payment Date: {payment_date}
Payment Mode: {payment_mode}
Reference/Remarks: {remarks}

Balance Receivable: Rs. {balance}
Centre: {centre}
"""

    data = {
        "Nearest_CADD_Centre": centre
    }

    send_wel_telegram_message(
        message,
        data
    )


def open_payment_popup():

    selected = (
        student_management_dropdown.get()
    )

    if not selected:

        messagebox.showerror(
            "Validation Error",
            "Select a student first."
        )
        return

    student = (
        student_management_map[selected]
    )

    popup = tk.Toplevel(root)

    popup.title("Add Student Payment")

    popup.geometry("450x330")

    popup.grab_set()

    tk.Label(
        popup,
        text="Add Student Payment",
        font=("Arial", 14, "bold")
    ).pack(pady=10)

    form = tk.Frame(popup)
    form.pack(pady=10)

    tk.Label(
        form,
        text="Student"
    ).grid(row=0, column=0, padx=10, pady=5, sticky="w")

    tk.Label(
        form,
        text=student.get("student_name", ""),
        font=("Arial", 10, "bold")
    ).grid(row=0, column=1, padx=10, pady=5, sticky="w")

    tk.Label(
        form,
        text="Payment Date"
    ).grid(row=1, column=0, padx=10, pady=5, sticky="w")

    payment_date_entry = tk.Entry(
        form,
        width=30
    )

    payment_date_entry.grid(row=1, column=1, padx=10, pady=5)

    payment_date_entry.insert(
        0,
        datetime.now().strftime("%Y-%m-%d")
    )

    tk.Label(
        form,
        text="Amount"
    ).grid(row=2, column=0, padx=10, pady=5, sticky="w")

    amount_entry = tk.Entry(
        form,
        width=30
    )

    amount_entry.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(
        form,
        text="Payment Mode"
    ).grid(row=3, column=0, padx=10, pady=5, sticky="w")

    payment_mode_dropdown = ttk.Combobox(
        form,
        width=27,
        values=(
            "Cash",
            "UPI",
            "Bank Transfer",
            "Cheque",
            "Card"
        )
    )

    payment_mode_dropdown.grid(row=3, column=1, padx=10, pady=5)

    tk.Label(
        form,
        text="Reference/Remarks"
    ).grid(row=4, column=0, padx=10, pady=5, sticky="w")

    remarks_entry = tk.Entry(
        form,
        width=30
    )

    remarks_entry.grid(row=4, column=1, padx=10, pady=5)

    def save_payment():

        payment_date = payment_date_entry.get().strip()

        amount = amount_entry.get().strip()

        payment_mode = payment_mode_dropdown.get().strip()

        remarks = remarks_entry.get().strip()

        if not payment_date:

            messagebox.showerror(
                "Validation Error",
                "Enter payment date."
            )
            return

        if not amount:

            messagebox.showerror(
                "Validation Error",
                "Enter amount."
            )
            return

        try:

            amount_value = float(amount)

        except ValueError:

            messagebox.showerror(
                "Validation Error",
                "Amount must be numeric."
            )
            return

        if amount_value <= 0:

            messagebox.showerror(
                "Validation Error",
                "Amount must be greater than zero."
            )
            return

        if not payment_mode:

            messagebox.showerror(
                "Validation Error",
                "Select payment mode."
            )
            return

        try:

            cloud_database.add_student_payment(
                student_id=student["id"],
                payment_date=payment_date,
                amount=amount_value,
                payment_mode=payment_mode,
                remarks=remarks
            )

            finance = cloud_database.get_student_finance(
                student["id"]
            )

            send_payment_telegram(
                student=student,
                payment_date=payment_date,
                amount=amount_value,
                payment_mode=payment_mode,
                remarks=remarks,
                finance=finance
            )

            show_student_details()
            load_admissions()
            refresh_student_management_dropdown()

            messagebox.showinfo(
                "Success",
                "Payment saved successfully."
            )

            popup.destroy()

        except Exception as e:

            messagebox.showerror(
                "Error",
                str(e)
            )

    tk.Button(
        popup,
        text="Save Payment",
        bg="green",
        fg="white",
        command=save_payment
    ).pack(pady=15)


def open_payment_history_popup():

    selected = (
        student_management_dropdown.get()
    )

    if not selected:

        messagebox.showerror(
            "Validation Error",
            "Select a student first."
        )
        return

    student = (
        student_management_map[selected]
    )

    popup = tk.Toplevel(root)

    popup.title("Payment History")

    popup.geometry("700x400")

    tk.Label(
        popup,
        text=f"Payment History - {student.get('student_name', '')}",
        font=("Arial", 14, "bold")
    ).pack(pady=10)

    columns = (
        "Date",
        "Amount",
        "Mode",
        "Type",
        "Remarks"
    )

    history_table = ttk.Treeview(
        popup,
        columns=columns,
        show="headings"
    )

    for col in columns:

        history_table.heading(
            col,
            text=col
        )

        history_table.column(
            col,
            width=130
        )

    history_table.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=10
    )

    transactions = (
        cloud_database.get_student_transactions(
            student["id"]
        )
    )

    for index, transaction in enumerate(transactions):

        values = (
            transaction.get(
                "payment_date",
                ""
            ),
            transaction.get(
                "amount",
                0
            ),
            transaction.get(
                "payment_mode",
                ""
            ),
            transaction.get(
                "payment_type",
                ""
            ),
            transaction.get(
                "remarks",
                ""
            )
        )

        history_table.insert(
            "",
            tk.END,
            values=values
        )

# ---------------- MAIN WINDOW ---------------- #

root = tk.Tk()

root.title("SKILLVERSE ACADEMY CRM")

root.geometry("1280x760")
root.minsize(1180, 700)

APP_BG = "#f4f7fb"
PANEL_BG = "#ffffff"
TEXT_COLOR = "#1f2937"
MUTED_TEXT = "#64748b"
ACCENT = "#2563eb"
ACCENT_DARK = "#1d4ed8"
SUCCESS = "#15803d"
WARNING = "#f59e0b"
BORDER = "#d8e0eb"
TABLE_HEADER = "#e8eef7"
TABLE_SELECTED = "#dbeafe"


def apply_visual_theme(parent):

    parent.configure(
        bg=APP_BG
    )

    parent.option_add(
        "*Font",
        "Segoe UI 10"
    )

    def style_children(widget):

        for child in widget.winfo_children():

            if isinstance(child, tk.Frame):

                bg = (
                    PANEL_BG
                    if str(child.cget("relief")) in ["groove", "ridge", "solid"]
                    else APP_BG
                )

                child.configure(
                    bg=bg,
                    highlightbackground=BORDER,
                    highlightcolor=BORDER
                )

            elif isinstance(child, tk.Label):

                child.configure(
                    bg=child.master.cget("bg")
                    if hasattr(child.master, "cget")
                    else APP_BG,
                    fg=TEXT_COLOR
                )

            elif isinstance(child, ttk.Combobox):

                continue

            elif isinstance(child, ttk.Widget):

                style_children(child)

                continue

            elif isinstance(child, tk.Button):

                text = child.cget("text").lower()

                button_bg = ACCENT
                button_fg = "#ffffff"

                if "save" in text or "payment" in text:

                    button_bg = SUCCESS

                if "update" in text:

                    button_bg = WARNING
                    button_fg = "#111827"

                child.configure(
                    bg=button_bg,
                    fg=button_fg,
                    activebackground=ACCENT_DARK,
                    activeforeground="#ffffff",
                    relief="flat",
                    bd=0,
                    padx=12,
                    pady=7,
                    cursor="hand2",
                    font=("Segoe UI", 9, "bold")
                )

            elif isinstance(child, tk.Entry):

                child.configure(
                    bg=PANEL_BG,
                    fg=TEXT_COLOR,
                    insertbackground=TEXT_COLOR,
                    relief="solid",
                    bd=1,
                    highlightthickness=1,
                    highlightbackground=BORDER,
                    highlightcolor=ACCENT
                )

            elif isinstance(child, tk.Text):

                child.configure(
                    bg=PANEL_BG,
                    fg=TEXT_COLOR,
                    insertbackground=TEXT_COLOR,
                    relief="solid",
                    bd=1,
                    highlightthickness=1,
                    highlightbackground=BORDER,
                    highlightcolor=ACCENT,
                    wrap="word"
                )

            style_children(child)

    style_children(parent)
# ---------------- ACTIVE CENTRE ---------------- #

ACTIVE_CENTRE = tk.StringVar()

ACTIVE_CENTRE.set("Dadar")   # default centre


centre_frame = tk.Frame(root)

centre_frame.pack(pady=5)

tk.Label(
    centre_frame,
    text="Select Centre:",
    font=("Arial", 11, "bold")
).pack(side="left", padx=5)


centre_dropdown = ttk.Combobox(

    centre_frame,

    textvariable=ACTIVE_CENTRE,

    width=20,

    state="readonly",

    values=(

        "Dadar",
        "NAN"
    )
)

centre_dropdown.pack(side="left")

def on_centre_change(event=None):

    load_enquiries()

    load_followups()
    load_admissions()
    refresh_student_dropdown()
    refresh_student_management_dropdown()


centre_dropdown.bind(
    "<<ComboboxSelected>>",
    on_centre_change
)

def show_student_details(event=None):

    selected = (
        student_management_dropdown.get()
    )

    if not selected:

        return

    student = (
        student_management_map[selected]
    )

    finance = (
        cloud_database.get_student_finance(
            student["id"]
        )
    )

    student_course_label.config(
        text=f"Course: {student['course_name']}"
    )

    if finance:

        student_fee_label.config(
            text=f"Fee: ₹{finance['course_fee']}"
        )

        student_collected_label.config(
            text=f"Collected: ₹{finance['amount_collected_by_kti']}"
        )

        student_balance_label.config(
            text=f"Balance: ₹{finance['balance_receivable']}"
        )

# ---------------- NOTEBOOK ---------------- #

notebook = ttk.Notebook(root)

notebook.pack(fill="both",expand=True)


# Tabs
enquiry_tab = tk.Frame(notebook)

followup_tab = tk.Frame(notebook)

admission_tab = tk.Frame(notebook)

# Add tabs
notebook.add(enquiry_tab,text="Enquiries")

notebook.add(followup_tab,text="Followups")


notebook.add(admission_tab,text="Admissions & Finance")

admission_title = tk.Label(

    admission_tab,

    text="Admissions & Finance Dashboard",

    font=("Arial", 16, "bold")

)

tk.Label(
    admission_tab,
    text="Search Student"
).pack()

student_management_dropdown = ttk.Combobox(
    admission_tab,
    width=50
)

student_management_dropdown.pack(
    pady=5
)
student_management_dropdown.bind(
    "<<ComboboxSelected>>",
    show_student_details
)

admission_title.pack(
    pady=10
)
student_course_label = tk.Label(
    admission_tab,
    text="Course: -"
)

student_course_label.pack()

student_fee_label = tk.Label(
    admission_tab,
    text="Fee: -"
)

student_fee_label.pack()

student_collected_label = tk.Label(
    admission_tab,
    text="Collected: -"
)

student_collected_label.pack()

student_balance_label = tk.Label(
    admission_tab,
    text="Balance: -"
)

student_balance_label.pack()

tk.Button(
    admission_tab,
    text="Add Payment",
    bg="blue",
    fg="white",
    command=open_payment_popup
).pack(pady=5)

tk.Button(
    admission_tab,
    text="View Payment History",
    command=open_payment_history_popup
).pack(pady=5)

admission_columns = (

    "Student Name",

    "Phone",

    "Course",

    "Course Fee",

    "Collected",

    "Balance",

    "Admission Date"

)

admission_table = ttk.Treeview(

    admission_tab,

    columns=admission_columns,

    show="headings"

)

for col in admission_columns:

    admission_table.heading(
        col,
        text=col
    )

    admission_table.column(
        col,
        width=140
    )
    
admission_table.pack(

    fill="both",

    expand=True,

    padx=10,

    pady=10

)

# ---------------- TITLE ---------------- #

title_label = tk.Label(

    enquiry_tab,

    text="Enquiry Follow-Up CRM",

    font=("Arial", 20, "bold")
)

title_label.pack(pady=10)


top_frame = tk.Frame(enquiry_tab)

top_frame.pack(

    fill="x",

    padx=10,

    pady=10
)

# ---------------- FORM FRAME ---------------- #

form_frame = tk.Frame(

    top_frame,

    bd=2,

    relief="groove"
)

form_frame.grid(

    row=0,

    column=0,

    padx=10,

    pady=10,

    sticky="n"
)


# Student Name
tk.Label(
    form_frame,
    text="Student Name"
).grid(row=0, column=0, padx=10, pady=5)

student_name_entry = tk.Entry(
    form_frame,
    width=30
)

student_name_entry.grid(
    row=0,
    column=1,
    padx=10,
    pady=5
)


# Phone
tk.Label(
    form_frame,
    text="Phone"
).grid(row=1, column=0, padx=10, pady=5)

phone_entry = tk.Entry(
    form_frame,
    width=30
)

phone_entry.grid(
    row=1,
    column=1,
    padx=10,
    pady=5
)
phone_entry.insert(
    0,
    "+91"
)

# alternate Phone
tk.Label(
    form_frame,
    text="Alternate Phone"
).grid(row=1, column=2, padx=10, pady=5)

alt_phone_entry = tk.Entry(
    form_frame,
    width=30
)

alt_phone_entry.grid(
    row=1,
    column=3,
    padx=10,
    pady=5
)
alt_phone_entry.insert(
    0,
    "+91"
)


# Email
tk.Label(
    form_frame,
    text="Email"
).grid(row=2, column=0, padx=10, pady=5)

email_entry = tk.Entry(
    form_frame,
    width=30
)

email_entry.grid(
    row=2,
    column=1,
    padx=10,
    pady=5
)

# Education
tk.Label(
    form_frame,
    text="Education"
).grid(
    row=3,
    column=0,
    padx=10,
    pady=5
)

education_dropdown = ttk.Combobox(

    form_frame,

    width=27,

    values=(

        "10th",

        "12th",

        "ITI",

        "Diploma",

        "B.Com",

        "B.Sc",

        "B.A",

        "BCA",

        "B.E./B.Tech",

        "MCA",

        "M.Sc",

        "MBA",

        "Working Professional",

        "Other",
        
        "No Information"
    )
)

education_dropdown.grid(
    row=3,
    column=1,
    padx=10,
    pady=5
)

education_dropdown.set(
    "12th"
)

# Education Stage
tk.Label(
    form_frame,
    text="Year / Status"
).grid(
    row=3,
    column=2,
    padx=10,
    pady=5
)

education_stage_dropdown = ttk.Combobox(

    form_frame,

    width=27,

    values=(

        "School Student",

        "12th Appearing",
        
        "12th Passed",

        "1st Year",

        "2nd Year",

        "3rd Year",

        "Final Year",

        "Graduate",

        "Working Professional",

        "Career Switch",
        
        "No Information"
    )
)

education_stage_dropdown.grid(
    row=3,
    column=3,
    padx=10,
    pady=5
)

education_stage_dropdown.set(
    "1st Year"
)
# locality
tk.Label(
    form_frame,
    text="Locality"
).grid(row=4, column=0, padx=10, pady=5)

locality_entry = tk.Entry(
    form_frame,
    width=30
)

locality_entry.grid(
    row=4,
    column=1,
    padx=10,
    pady=5
)

#neasrest CADD Centre
tk.Label(
    form_frame,
    text = "Nearest CADD Centre"
).grid(row = 4, column = 2, padx = 10, pady = 5)



nr_centre_dropdown = ttk.Combobox(

    form_frame,

    width=27,

    values=(

        "Dadar",
        "NAN"
    )
)

nr_centre_dropdown.grid(
    row = 4,
    column = 3, padx = 30, pady = 5)


# Preferred Language
tk.Label(
    form_frame,
    text="Language"
).grid(row=5, column=0, padx=10, pady=5)

language_dropdown = ttk.Combobox(

    form_frame,

    width=27,

    values=(

        "English",

        "Marathi",

        "Hindi"
    )
)

language_dropdown.grid(
    row=5,
    column=1,
    padx=10,
    pady=5
)

language_dropdown.set("English")


# Lead Temperature
tk.Label(
    form_frame,
    text="Lead Temperature"
).grid(row=6, column=0, padx=10, pady=5)

lead_dropdown = ttk.Combobox(

    form_frame,

    width=27,

    values=(

        "Hot",

        "Warm",

        "Cold"
    )
)

lead_dropdown.grid(
    row=6,
    column=1,
    padx=10,
    pady=5
)

lead_dropdown.set("Warm")

# Remarks
tk.Label(
    form_frame,
    text="Remarks"
).grid(row=7, column=0, padx=10, pady=5)

remarks_text = tk.Text(

    form_frame,

    width=30,

    height=4
)

remarks_text.grid(
    row=7,
    column=1,
    padx=10,
    pady=5
)


# Next Action
tk.Label(
    form_frame,
    text="Next Action"
).grid(
    row=8,
    column=0,
    padx=10,
    pady=5
)

next_action_dropdown = ttk.Combobox(

    form_frame,

    width=27,

    values=(

        "Call Student",

        "Call Parent",

        "Send Brochure",

        "Schedule Demo",

        "Demo Reminder",

        "Fee Discussion",

        "Placement Discussion",

        "WhatsApp Followup",

        "Admission Closure",

        "No Action"
    )
)

next_action_dropdown.grid(

    row=8,

    column=1,

    padx=10,

    pady=5
)

next_action_dropdown.set(
    "Call Student"
)

from datetime import datetime


def parse_followup_datetime(value):

    if not value:
        return "", ""

    value = str(value).strip()

    try:
        parsed = datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )

        return (
            parsed.strftime("%Y-%m-%d"),
            parsed.strftime("%H:%M")
        )

    except ValueError:
        if "T" in value:
            date_part, time_part = value.split("T", 1)
        elif " " in value:
            date_part, time_part = value.split(" ", 1)
        else:
            return value, ""

        return (
            date_part[:10],
            time_part[:5]
        )

# Enquiry Date
tk.Label(
    form_frame,
    text="Enquiry Date (YYYY-MM-DD)"
).grid(row=9, column=0, padx=10, pady=5)

enquiry_date_entry = tk.Entry(
    form_frame,
    width=30
)

enquiry_date_entry.grid(
    row=9,
    column=1,
    padx=10,
    pady=5
)

# Default today's date
today_date = datetime.now().strftime(
    "%Y-%m-%d"
)

enquiry_date_entry.insert(
    0,
    today_date
)


# Next Follow-Up Date
tk.Label(
    form_frame,
    text="Next Follow-Up Date"
).grid(row=10, column=0, padx=10, pady=5)

next_followup_date_entry = tk.Entry(
    form_frame,
    width=30
)

next_followup_date_entry.grid(
    row=10,
    column=1,
    padx=10,
    pady=5
)

# Next Follow-Up Time

tk.Label(
    form_frame,
    text="Time"
).grid(
    row=10,
    column=2,
    padx=5,
    pady=5
)

next_followup_time_entry = tk.Entry(
    form_frame,
    width=10
)

next_followup_time_entry.grid(
    row=10,
    column=3,
    padx=5,
    pady=5
)

next_followup_time_entry.insert(
    0,
    "11:00"
)


# Status
tk.Label(
    form_frame,
    text="Status"
).grid(row=11, column=0, padx=10, pady=5)

status_entry = ttk.Combobox(

    form_frame,

    width=22,

    values=(

        "New",

        "Interested",

        "Demo Scheduled",

        "Demo Attended",

        "Joined",

        "Closed"
    )
)

status_entry.grid(
    row=11,
    column=1,
    padx=10,
    pady=5
)


# Counsellor
tk.Label(
    form_frame,
    text="Counsellor"
).grid(row=12, column=0, padx=10, pady=5)


counsellor_entry = ttk.Combobox(

    form_frame,

    width=22,

    values=(

        "Sneha",
        "Shivani"
    )
)


counsellor_entry.grid(
    row=12,
    column=1,
    padx=10,
    pady=5
)


# Source
tk.Label(
    form_frame,
    text="Source"
).grid(row=13, column=0, padx=10, pady=5)

source_entry = tk.Entry(
    form_frame,
    width=30
)


source_entry = ttk.Combobox(

    form_frame,

    width=22,

    values=(
        "Google",
        "Tele",
        "Meta Ads",
        "Walkin",
        "Friend Reference"

        
    )
)


source_entry.grid(
    row=13,
    column=1,
    padx=10,
    pady=5
)

# Course Interest
tk.Label(
    form_frame,
    text="Course Interest"
).grid(row=14, column=0, padx=10, pady=5)

course_entry = tk.Entry(
    form_frame,
    width=30
)

course_entry = ttk.Combobox(

    form_frame,

    width=22,

    values=(

        "AutoCAD",
        "Solidworks",
        "Revit Architecture",
        "3DS Max",
        "Google Sketchup",
        "Not Decided"
    )
)

course_entry.grid(
    row=14,
    column=1,
    padx=10,
    pady=5
)



# ---------------- SAVE FUNCTION ---------------- #


def refresh_student_dropdown():

    selected_centre = (
        ACTIVE_CENTRE.get()
    ).strip()

    students = (
        cloud_database
        .get_student_names()
    )

    student_options = []

    student_map.clear()

    all_student_options.clear()

    for student in students:

        student_centre = (

            student.get(
                "Nearest_CADD_Centre",
                ""
            )
            .strip()
        )

        # filter by selected centre
        if student_centre != selected_centre:
            continue

        display_text = (

            f'{student["student_name"]} '

            f'({student["phone"]})'
        )

        student_options.append(
            display_text
        )

        all_student_options.append(
            display_text
        )

        student_map[
            display_text
        ] = student["id"]

    student_dropdown["values"] = student_options
    

    
    student_dropdown.set("")
    
    student_dropdown.set("")
    

    
def load_student_details(event=None):

    selected_student = (
        student_dropdown.get()
    )

    if not selected_student:
        return

    enquiry_id = (
        student_map[
            selected_student
        ]
    )

    enquiry = (
        cloud_database.get_enquiry_details(
            enquiry_id
        )
    )
    
    

    if enquiry:
        load_history(enquiry_id)

        # Status
        status_dropdown.set(
            enquiry.get(
                "status",
                ""
            )
        )

        # Remarks
        remarks_update_text.delete(
            "1.0",
            tk.END
        )

        remarks_update_text.insert(

            "1.0",

            enquiry.get(
                "remarks",
                ""
            )
        )

        # Next Followup Date
        followup_date, followup_time = parse_followup_datetime(
            enquiry.get(
                "next_followup_datetime",
                ""
            )
        )

        next_followup_entry.delete(
            0,
            tk.END
        )

        next_followup_entry.insert(

            0,

            followup_date
        )

        followup_time_entry.delete(
            0,
            tk.END
        )

        followup_time_entry.insert(
            0,
            followup_time or "11:00"
        )

        # Counsellor
        followup_counsellor_entry.delete(
            0,
            tk.END
        )

        followup_counsellor_entry.insert(

            0,

            enquiry.get(
                "counsellor",
                "Sneha"
            )
        )

    

def filter_students(event):

    typed_text = (
        student_dropdown.get()
        .lower()
    )

    filtered = []

    for student in all_student_options:

        if typed_text in student.lower():

            filtered.append(
                student
            )

    student_dropdown["values"] = (
        filtered
    )
    
    
def clear_enquiry_form():

    # Text Entries
    student_name_entry.delete(0, tk.END)

    phone_entry.delete(0, tk.END)
    phone_entry.insert(0, "+91")

    alt_phone_entry.delete(0, tk.END)
    alt_phone_entry.insert(0, "+91")

    email_entry.delete(0, tk.END)

    locality_entry.delete(0, tk.END)

    course_entry.set("")

    source_entry.set("")

    counsellor_entry.set("")

    status_entry.set("")

    nr_centre_dropdown.set("")

    # Dates

    enquiry_date_entry.delete(0, tk.END)

    enquiry_date_entry.insert(
        0,
        datetime.now().strftime("%Y-%m-%d")
    )

    next_followup_date_entry.delete(0, tk.END)

    next_followup_time_entry.delete(0, tk.END)

    next_followup_time_entry.insert(
        0,
        "11:00"
    )

    # Dropdowns

    education_dropdown.set("12th")

    education_stage_dropdown.set(
        "1st Year"
    )

    language_dropdown.set(
        "English"
    )

    lead_dropdown.set(
        "Warm"
    )

    next_action_dropdown.set(
        "Call Student"
    )

    # Remarks

    remarks_text.delete(
        "1.0",
        tk.END
    )

    # Cursor back to first field

    student_name_entry.focus()
def save_enquiry():


    try:

        student_name = student_name_entry.get()

        phone = phone_entry.get()
        
        alternate_phone = alt_phone_entry.get()

        course_interest = course_entry.get()

        enquiry_date = enquiry_date_entry.get()

        next_followup_date = next_followup_date_entry.get().strip()
        next_followup_time = next_followup_time_entry.get().strip()        
        status = status_entry.get()
        
        Nearest_CADD_Centre = nr_centre_dropdown.get()
        # ---------- VALIDATION ---------- #

        if not student_name.strip():
        
            messagebox.showerror(
        
                "Validation Error",
        
                "Student NAME is required."
            )
        
            return
        
        
        if phone.strip() in ["", "+91"]:
        
            messagebox.showerror(
        
                "Validation Error",
        
                "Phone Number is required."
            )
        
            return
        
        
        if not course_interest.strip():
        
            messagebox.showerror(
        
                "Validation Error",
        
                "Course Interest is required."
            )
        
            return
        
        if not Nearest_CADD_Centre.strip():
        
            messagebox.showerror(
        
                "Validation Error",
        
                "Nearest Centre is required."
            )
        
            return
        
        
        if not enquiry_date.strip():
        
            messagebox.showerror(
        
                "Validation Error",
        
                "Enquiry Date is required."
            )
        
            return
        
        
        if not status.strip():
        
            messagebox.showerror(
        
                "Validation Error",
        
                "Status is required."
            )
        
            return


        if len(phone.replace("+91", "")) < 10:

            messagebox.showerror("Validation Error","Enter valid mobile number."
            )

            return

        if (
            not next_followup_date
            or not next_followup_time
        ):

            messagebox.showerror(
                "Validation Error",
                "Next Followup Date & Time is required."
            )
        
            return
        counsellor = counsellor_entry.get()

        source = source_entry.get()
        
        email = email_entry.get()

        locality = locality_entry.get()
        
        
        
        preferred_language = language_dropdown.get()

        lead_temperature = lead_dropdown.get()

        remarks = remarks_text.get("1.0", tk.END)

        next_action = next_action_dropdown.get()
        
        last_followup_date = None
        
        education = education_dropdown.get()

        education_stage = education_stage_dropdown.get()
        

        try:
            next_followup_datetime = datetime.strptime(
                f"{next_followup_date} {next_followup_time}",
                "%Y-%m-%d %H:%M"
            ).isoformat()

        except ValueError:
            messagebox.showerror(
                "Validation Error",
                "Next Followup must be in YYYY-MM-DD and HH:MM format."
            )

            return

        data = {

            "student_name": student_name,
        
            "phone": phone,
            
            "alternate_phone":alternate_phone,
        
            "email": email,
        
            "locality": locality,
            
            "Nearest_CADD_Centre": Nearest_CADD_Centre,
        
            "preferred_language": preferred_language,
        
            "course_interest": course_interest,
        
            "enquiry_date": enquiry_date,
        
            "last_followup_date": last_followup_date,
        
            
            "next_followup_datetime":next_followup_datetime,
        
            "status": status,
        
            "lead_temperature": lead_temperature,
        
            "next_action": next_action,
        
            "remarks": remarks,
        
            "counsellor": counsellor,
        
            "source": source,
            
            "education": education,

            "education_stage": education_stage,
        }   

        result = cloud_database.add_enquiry(data)
        
        if result == "duplicate":
        
            messagebox.showwarning(
                "Duplicate Enquiry",
                "Student enquiry already exists."
            )
        
            return
        
        clear_enquiry_form()
        
        messagebox.showinfo(
            "Success",
            "Enquiry added successfully."
        )
        
        refresh_student_dropdown()
        #send telegram message
        wel_telegram_message = f"""
📌 New Enquiry Added

👨 Student: {student_name}

📞 Phone: {phone}

📝 Status: {status}

Centre: {Nearest_CADD_Centre}

Course: {course_interest}

💬 Remark:
{remarks}

"""

        send_wel_telegram_message(
            wel_telegram_message,data
        )

        
        # Clear fields
        clear_enquiry_form()

        # Reload dashboard
        load_enquiries()
        load_followups()

    except Exception as e:

        messagebox.showerror(
            "Error",
            str(e)
        )


def open_admission_popup(enquiry_id, student_name):

    popup = tk.Toplevel(root)

    popup.title("Admission Details")

    popup.geometry("500x450")

    popup.grab_set()   # makes popup modal

    # ---------------- TITLE ---------------- #

    tk.Label(
        popup,
        text="Admission Details",
        font=("Arial", 14, "bold")
    ).pack(pady=10)

    form = tk.Frame(popup)
    form.pack(pady=10)

    # Student Name

    tk.Label(
        form,
        text="Student Name"
    ).grid(row=0, column=0, padx=10, pady=5, sticky="w")

    student_label = tk.Label(
        form,
        text=student_name,
        font=("Arial", 10, "bold")
    )

    student_label.grid(
        row=0,
        column=1,
        padx=10,
        pady=5,
        sticky="w"
    )

    # Final Course

    tk.Label(
        form,
        text="Final Course"
    ).grid(row=1, column=0, padx=10, pady=5)

    final_course_entry = ttk.Combobox(

        form,

        width=25,

        values=(

            "Python",

            "Data Analytics",

            "Data Science",

            "Artificial Intelligence",

            "SQL",

            "Machine Learning"
        )
    )

    final_course_entry.grid(
        row=1,
        column=1,
        padx=10,
        pady=5
    )

    # Course Fee

    tk.Label(
        form,
        text="Course Fee"
    ).grid(row=2, column=0, padx=10, pady=5)

    course_fee_entry = tk.Entry(
        form,
        width=30
    )

    course_fee_entry.grid(
        row=2,
        column=1,
        padx=10,
        pady=5
    )

    # First Payment

    tk.Label(
        form,
        text="First Payment"
    ).grid(row=3, column=0, padx=10, pady=5)

    first_payment_entry = tk.Entry(
        form,
        width=30
    )

    first_payment_entry.grid(
        row=3,
        column=1,
        padx=10,
        pady=5
    )

    # Payment Date

    tk.Label(
        form,
        text="Payment Date"
    ).grid(row=4, column=0, padx=10, pady=5)

    payment_date_entry = tk.Entry(
        form,
        width=30
    )

    payment_date_entry.grid(
        row=4,
        column=1,
        padx=10,
        pady=5
    )

    payment_date_entry.insert(
        0,
        datetime.now().strftime("%Y-%m-%d")
    )

    # Payment Mode

    tk.Label(
        form,
        text="Payment Mode"
    ).grid(row=5, column=0, padx=10, pady=5)

    payment_mode_dropdown = ttk.Combobox(

        form,

        width=27,

        values=(

            "Cash",

            "UPI",

            "Bank Transfer",

            "Cheque",

            "Card"
        )
    )

    payment_mode_dropdown.grid(
        row=5,
        column=1,
        padx=10,
        pady=5
    )

    # Payment Reference

    tk.Label(
        form,
        text="Payment Ref."
    ).grid(row=6, column=0, padx=10, pady=5)

    payment_ref_entry = tk.Entry(
        form,
        width=30
    )

    payment_ref_entry.grid(
        row=6,
        column=1,
        padx=10,
        pady=5
    )

    # Admission Date

    tk.Label(
        form,
        text="Admission Date"
    ).grid(row=7, column=0, padx=10, pady=5)

    admission_date_entry = tk.Entry(
        form,
        width=30
    )

    admission_date_entry.grid(
        row=7,
        column=1,
        padx=10,
        pady=5
    )

    admission_date_entry.insert(
        0,
        datetime.now().strftime("%Y-%m-%d")
    )

    # ---------------- SAVE ---------------- #

    def save_admission():

        final_course = final_course_entry.get()

        course_fee = course_fee_entry.get()

        first_payment = first_payment_entry.get()

        payment_date = payment_date_entry.get()

        payment_mode = payment_mode_dropdown.get()

        payment_reference = payment_ref_entry.get()

        admission_date = admission_date_entry.get()

        if not final_course:

            messagebox.showerror(
                "Validation Error",
                "Select course"
            )
            return

        if not course_fee:

            messagebox.showerror(
                "Validation Error",
                "Enter course fee"
            )
            return

        if not first_payment:

            messagebox.showerror(
                "Validation Error",
                "Enter first payment"
            )
            return

        if not payment_mode:

            messagebox.showerror(
                "Validation Error",
                "Select payment mode"
            )
            return
        if cloud_database.student_exists_for_enquiry(
            enquiry_id
        ):
            messagebox.showerror(
                "Duplicate Admission",
                "This enquiry has already been converted to a student."
            )
            return
        
        cloud_database.save_admission_details(
            enquiry_id,
            final_course,
            course_fee,
            first_payment,
            payment_date,
            payment_mode,
            payment_reference,
            admission_date
        )
        
        # STEP 13
        enquiry_details = cloud_database.get_enquiry_details(
            enquiry_id
        )
        
        # STEP 14
        student_id = cloud_database.create_student_record(
        
            student_name=
                enquiry_details["student_name"],
        
            mobile=
                enquiry_details["phone"],
        
            email=
                enquiry_details.get("email", ""),
        
            course_name=
                final_course,
        
            centre=
                enquiry_details["Nearest_CADD_Centre"],
        
            admission_date=
                admission_date,
        
            counsellor_name=
                followup_counsellor_entry.get(),
        
            lead_source=
                enquiry_details.get("source", ""),
        
            enquiry_id=
                enquiry_id
        )
        
        # STEP 15
        cloud_database.create_student_finance_record(
        
            student_id=student_id,
        
            course_fee=course_fee,
        
            first_payment=first_payment
        )
        
        # STEP 16
        cloud_database.create_student_transaction(
        
            student_id=student_id,
        
            payment_date=payment_date,
        
            amount=first_payment,
        
            payment_mode=payment_mode,
        
            remarks=payment_reference
        )
        
        cloud_database.create_admission_log(
            enquiry_id,
            student_name,
            final_course,
            first_payment,
            followup_counsellor_entry.get()
        )
        enquiry_details = cloud_database.get_enquiry_details(enquiry_id)

        phone = enquiry_details["phone"]

        centre = enquiry_details["Nearest_CADD_Centre"]
        send_admission_telegram(

            student_name,
        
            phone,
        
            centre,
        
            final_course,
        
            course_fee,
        
            first_payment,
        
            admission_date,
        
            followup_counsellor_entry.get()
        )

        load_enquiries()
        
        load_followups()
        load_admissions()
        
        refresh_student_dropdown()
        
        messagebox.showinfo(
        
            "Success",
        
            "Admission saved successfully."
        )
        
        popup.destroy()

    tk.Button(

        popup,

        text="Save Admission",

        bg="green",

        fg="white",

        command=save_admission

    ).pack(pady=15)


def open_edit_enquiry_popup():

    selected_student = (
        student_dropdown.get()
    )

    if not selected_student:

        messagebox.showerror(
            "Validation Error",
            "Select a student first."
        )
        return

    enquiry_id = (
        student_map[
            selected_student
        ]
    )

    enquiry = (
        cloud_database.get_enquiry_details(
            enquiry_id
        )
    )

    if not enquiry:

        messagebox.showerror(
            "Error",
            "Could not load enquiry details."
        )
        return

    popup = tk.Toplevel(root)

    popup.title("Edit Enquiry")

    popup.geometry("620x620")

    popup.grab_set()

    tk.Label(
        popup,
        text="Edit Enquiry",
        font=("Arial", 14, "bold")
    ).pack(pady=10)

    form = tk.Frame(popup)
    form.pack(pady=10)

    fields = {}

    def add_entry(row, label, key, width=35):

        tk.Label(
            form,
            text=label
        ).grid(row=row, column=0, padx=10, pady=5, sticky="w")

        widget = tk.Entry(
            form,
            width=width
        )

        widget.grid(row=row, column=1, padx=10, pady=5)

        widget.insert(
            0,
            enquiry.get(
                key,
                ""
            ) or ""
        )

        fields[key] = widget

    def add_combo(row, label, key, values, width=32):

        tk.Label(
            form,
            text=label
        ).grid(row=row, column=0, padx=10, pady=5, sticky="w")

        widget = ttk.Combobox(
            form,
            width=width,
            values=values
        )

        widget.grid(row=row, column=1, padx=10, pady=5)

        widget.set(
            enquiry.get(
                key,
                ""
            ) or ""
        )

        fields[key] = widget

    add_entry(0, "Student Name", "student_name")
    add_entry(1, "Phone", "phone")
    add_entry(2, "Alternate Phone", "alternate_phone")
    add_entry(3, "Email", "email")
    add_entry(4, "Locality", "locality")

    add_combo(
        5,
        "Nearest CADD Centre",
        "Nearest_CADD_Centre",
        nr_centre_dropdown["values"]
    )

    add_combo(
        6,
        "Course Interest",
        "course_interest",
        course_entry["values"]
    )

    add_combo(
        7,
        "Education",
        "education",
        education_dropdown["values"]
    )

    add_combo(
        8,
        "Year / Status",
        "education_stage",
        education_stage_dropdown["values"]
    )

    add_combo(
        9,
        "Language",
        "preferred_language",
        language_dropdown["values"]
    )

    add_combo(
        10,
        "Lead Temperature",
        "lead_temperature",
        lead_dropdown["values"]
    )

    add_combo(
        11,
        "Status",
        "status",
        status_entry["values"]
    )

    add_combo(
        12,
        "Counsellor",
        "counsellor",
        counsellor_entry["values"]
    )

    add_combo(
        13,
        "Source",
        "source",
        source_entry["values"]
    )

    tk.Label(
        form,
        text="Remarks"
    ).grid(row=14, column=0, padx=10, pady=5, sticky="nw")

    remarks_widget = tk.Text(
        form,
        width=35,
        height=5
    )

    remarks_widget.grid(row=14, column=1, padx=10, pady=5)

    remarks_widget.insert(
        "1.0",
        enquiry.get(
            "remarks",
            ""
        ) or ""
    )

    def save_edit():

        student_name = (
            fields["student_name"]
            .get()
            .strip()
        )

        phone = (
            fields["phone"]
            .get()
            .strip()
        )

        centre = (
            fields["Nearest_CADD_Centre"]
            .get()
            .strip()
        )

        course_interest = (
            fields["course_interest"]
            .get()
            .strip()
        )

        if not student_name:

            messagebox.showerror(
                "Validation Error",
                "Student name is required."
            )
            return

        if phone in ["", "+91"]:

            messagebox.showerror(
                "Validation Error",
                "Phone number is required."
            )
            return

        if len(phone.replace("+91", "")) < 10:

            messagebox.showerror(
                "Validation Error",
                "Enter valid mobile number."
            )
            return

        if not centre:

            messagebox.showerror(
                "Validation Error",
                "Nearest centre is required."
            )
            return

        if not course_interest:

            messagebox.showerror(
                "Validation Error",
                "Course interest is required."
            )
            return

        data = {
            key: widget.get().strip()
            for key, widget in fields.items()
        }

        data["remarks"] = (
            remarks_widget.get(
                "1.0",
                tk.END
            )
            .strip()
        )

        try:

            cloud_database.update_enquiry_details(
                enquiry_id,
                data
            )

            load_enquiries()
            load_followups()
            refresh_student_dropdown()

            messagebox.showinfo(
                "Success",
                "Enquiry updated successfully."
            )

            popup.destroy()

        except Exception as e:

            messagebox.showerror(
                "Error",
                str(e)
            )

    tk.Button(
        popup,
        text="Save Changes",
        bg="green",
        fg="white",
        command=save_edit
    ).pack(pady=15)


def update_status():

    try:

        selected_student = (
            student_dropdown.get()
        )
        student_name = (
            selected_student.split("(")[0].strip()
        )

        enquiry_id = (
            student_map[
                selected_student
            ]
        )

        followup_type = (
            followup_type_dropdown.get()
        )

        response = (
            response_dropdown.get()
        )

        remarks = (
            remarks_update_text.get(
                "1.0",
                tk.END
            ).strip()
        )

        next_followup_date = (
            next_followup_entry.get()
            .strip()
        )

        next_followup_time = (
            followup_time_entry.get()
            .strip()
        )

        if (
            not next_followup_date
            or not next_followup_time
        ):

            messagebox.showerror(
                "Validation Error",
                "Next Followup Date & Time is required."
            )

            return

        try:
            datetime.strptime(
                f"{next_followup_date} {next_followup_time}",
                "%Y-%m-%d %H:%M"
            )

        except ValueError:
            messagebox.showerror(
                "Validation Error",
                "Next Followup must be in YYYY-MM-DD and HH:MM format."
            )

            return
        

        
        status = (
            status_dropdown.get()
        )
        if status == "Joined":

            open_admission_popup(
                enquiry_id,
                student_name
            )
        
            return
        
        counsellor = (
            followup_counsellor_entry.get()
        )


        cloud_database.save_followup(

            enquiry_id,
            
            student_name,

            followup_type,

            response,

            remarks,

            next_followup_date,
            
            next_followup_time,
            
            status,

            counsellor,
            
            
        )


        load_followups()

        load_enquiries()


        messagebox.showinfo(

            "Success",

            "Followup saved successfully."
        )


        # Clear fields after save
        student_dropdown.set("")

        followup_type_dropdown.set(
            "Call"
        )

        response_dropdown.set(
            "Interested"
        )

        remarks_update_text.delete(
            "1.0",
            tk.END
        )

        next_followup_entry.delete(
            0,
            tk.END
        )

        status_dropdown.set("")

        followup_counsellor_entry.delete(
            0,
            tk.END
        )

        followup_counsellor_entry.insert(
            0,
            "Karan"
        )


    except Exception as e:

        messagebox.showerror(

            "Error",

            str(e)
        )

# ---------------- SAVE BUTTON ---------------- #

save_button = tk.Button(

    enquiry_tab,

    text="Save Enquiry",

    font=("Arial", 12, "bold"),

    bg="green",

    fg="white",

    command=save_enquiry
)

save_button.pack(pady=10)



# ---------------- FILTER ---------------- #

filter_frame = tk.Frame(enquiry_tab)

filter_frame.pack(
    pady=5
)

tk.Label(

    filter_frame,

    text="Filter Leads:"
).pack(
    side="left",
    padx=5
)

filter_dropdown = ttk.Combobox(

    filter_frame,

    width=20,

    values=(

        "Last 20 Leads",

        "Last 15 Days",

        "All Leads"
    )
)

filter_dropdown.pack(
    side="left"
)

filter_dropdown.set(
    "Last 20 Leads"
)

filter_dropdown.bind(

    "<<ComboboxSelected>>",

    lambda e:
    load_enquiries()
)
# ---------------- TABLE ---------------- #

columns = (

    "Student Name",

    "Phone",

    "Course",

    "Enquiry Date",

    "Follow-Up Date",

    "Status",

    "Counsellor",

    "Remarks"
)

enquiry_table = ttk.Treeview(

    enquiry_tab,

    columns=columns,

    show="headings"
)


# Headings
for col in columns:

    enquiry_table.heading(
        col,
        text=col
    )


# Column Widths
for col in columns:

    enquiry_table.column(
        col,
        width=120
    )


enquiry_table.pack(

    fill="both",

    expand=True,

    padx=10,

    pady=10
)

# ---------------- FOLLOWUP DASHBOARD ---------------- #

followup_title = tk.Label(

    followup_tab,

    text="Today's Pending Follow-Ups",

    font=("Arial", 16, "bold"),

    fg="red"
)

followup_title.pack(pady=10)


followup_columns = (
    
    "Student Name",

    "Phone",

    "Course",

    "Next Follow-Up Date",
    
    "Follow-Up Date",

    "Status",
    
    "Remarks"
)

# ---------------- FOLLOWUP FILTER ---------------- #

followup_filter_frame = tk.Frame(followup_tab)

followup_filter_frame.pack(
    pady=5
)

tk.Label(

    followup_filter_frame,

    text="Followup Filter:"
).pack(
    side="left",
    padx=5
)

followup_filter_dropdown = ttk.Combobox(

    followup_filter_frame,

    width=22,

    values=(

        "Today's Followups",

        "Tomorrow",

        "Overdue",

        "Next 7 Days",

        "All Pending"
    )
)

followup_filter_dropdown.pack(
    side="left"
)

followup_filter_dropdown.set(
    "Today's Followups"
)

followup_filter_dropdown.bind(

    "<<ComboboxSelected>>",

    lambda e:
    load_followups()
)

followup_table = ttk.Treeview(

    followup_tab,

    columns=followup_columns,

    show="headings",

    height=8
)


# Headings
for col in followup_columns:

    followup_table.heading(
        col,
        text=col
    )


# Column Widths
for col in followup_columns:

    followup_table.column(
        col,
        width=150
    )


followup_table.pack(

    fill="both",

    expand=True,

    padx=10,

    pady=10
)

top_followup_frame = tk.Frame(
    followup_tab
)

top_followup_frame.pack(
    fill="x",
    padx=10,
    pady=10
)

# ---------------- STATUS UPDATE SECTION ---------------- #

status_frame = tk.Frame(
    top_followup_frame,
    bd=2,
    relief="groove"
)

status_frame.pack(
    side="left",
    padx=10,
    anchor="n"
)

history_frame = tk.Frame(

    top_followup_frame,

    bd=2,

    relief="groove"
)

history_frame.pack(

    side="left",

    padx=10,

    fill="both",

    expand=True
)

history_title = tk.Label(

    history_frame,

    text="Counselling History",

    font=("Arial", 14, "bold")
)

history_title.pack(
    pady=10
)

history_columns = (

    "Date",

    "Type",

    "Response",

    "Remarks",
    
    "next_followup_date",

    "Counsellor"
)

history_table = ttk.Treeview(

    history_frame,

    columns=history_columns,

    show="headings",

    height=12
)

for col in history_columns:

    history_table.heading(
        col,
        text=col
    )

    history_table.column(
        col,
        width=120
    )

history_table.pack(

    fill="both",

    expand=True,

    padx=10,

    pady=10
)

def load_history(
    enquiry_id
):

    for row in history_table.get_children():

        history_table.delete(row)


    history = (

        cloud_database
        .get_followup_history(

            enquiry_id
        )
    )


    for item in history:

        values = (

            item.get(
                "followup_date",
                ""
            ),

            item.get(
                "followup_type",
                ""
            ),

            item.get(
                "response",
                ""
            ),

            item.get(
                "remarks",
                ""
            ),

            item.get(
                "next_followup_datetime",
                ""
            ),
            
            item.get(
                "counsellor",
                ""
            )
        )

        history_table.insert(

            "",

            tk.END,

            values=values
        )
# ---------- LOAD STUDENTS ---------- #

students = (
    cloud_database.get_student_names()
)

student_options = []

all_student_options = []

student_map = {}

student_management_map = {}

all_student_management_options = []

for student in students:

    display_text = (

        f'{student["student_name"]} '

        f'({student["phone"]})'
    )

    student_options.append(
        display_text
    )

    all_student_options.append(
        display_text
    )

    student_map[
        display_text
    ] = student["id"]


# ---------- TITLE ---------- #

status_title = tk.Label(

    status_frame,

    text="Update Enquiry Status",

    font=("Arial", 14, "bold")
)

status_title.grid(
    row=0,
    column=0,
    columnspan=2,
    pady=10
)


# ---------- STUDENT SEARCH ---------- #

tk.Label(
    status_frame,
    text="Student"
).grid(
    row=1,
    column=0,
    padx=10,
    pady=5
)

student_dropdown = ttk.Combobox(

    status_frame,

    width=35,

    values=student_options
)

student_dropdown.grid(
    row=1,
    column=1,
    padx=10,
    pady=5
)

tk.Button(
    status_frame,
    text="Edit Enquiry",
    command=open_edit_enquiry_popup
).grid(
    row=1,
    column=2,
    padx=10,
    pady=5
)

student_dropdown.bind(
    "<<ComboboxSelected>>",
    load_student_details
)

student_dropdown.bind(
    "<KeyRelease>",
    filter_students
)


# ---------- FOLLOWUP TYPE ---------- #

tk.Label(
    status_frame,
    text="Followup Type"
).grid(
    row=2,
    column=0,
    padx=10,
    pady=5
)

followup_type_dropdown = ttk.Combobox(

    status_frame,

    width=25,

    values=(

        "Call",

        "WhatsApp",

        "Demo",

        "Parent Discussion",

        "Fee Discussion",

        "Walk-in Visit",

        "Other"
    )
)

followup_type_dropdown.grid(
    row=2,
    column=1,
    padx=10,
    pady=5
)

followup_type_dropdown.set(
    "Call"
)


# ---------- STUDENT RESPONSE ---------- #

tk.Label(
    status_frame,
    text="Student Response"
).grid(
    row=3,
    column=0,
    padx=10,
    pady=5
)

response_dropdown = ttk.Combobox(

    status_frame,

    width=25,

    values=(

        "Interested",

        "Call Later",

        "Busy",

        "No Response",

        "Wants Demo",

        "Fee Issue",

        "Not Interested",

        "Wrong Number",
        
        "Neutral",
        
        "Joined Other Inst."
    )
)

response_dropdown.grid(
    row=3,
    column=1,
    padx=10,
    pady=5
)

response_dropdown.set(
    "Interested"
)


# ---------- REMARKS ---------- #

tk.Label(
    status_frame,
    text="Remarks"
).grid(
    row=4,
    column=0,
    padx=10,
    pady=5
)

remarks_update_text = tk.Text(

    status_frame,

    width=30,

    height=4
)

remarks_update_text.grid(
    row=4,
    column=1,
    padx=10,
    pady=5
)


# ---------- NEXT FOLLOWUP ---------- #

tk.Label(
    status_frame,
    text="Next Followup"
).grid(
    row=5,
    column=0,
    padx=10,
    pady=5
)

next_followup_entry = tk.Entry(
    status_frame,
    width=28
)

next_followup_entry.grid(
    row=5,
    column=1,
    padx=10,
    pady=5
)


# Followup Time

tk.Label(
    status_frame,
    text="Time"
).grid(
    row=5,
    column=2,
    padx=5,
    pady=5
)

followup_time_entry = tk.Entry(
    status_frame,
    width=10
)

followup_time_entry.grid(
    row=5,
    column=3,
    padx=5,
    pady=5
)

followup_time_entry.insert(
    0,
    "11:00"
)

# ---------- STATUS ---------- #

tk.Label(
    status_frame,
    text="New Status"
).grid(
    row=6,
    column=0,
    padx=10,
    pady=5
)

status_dropdown = ttk.Combobox(

    status_frame,

    width=25,

    values=(

        "New",

        "Interested",

        "Demo Scheduled",

        "Demo Attended",

        "Joined",
        
        "On hold",

        "Closed"
    )
)

status_dropdown.grid(
    row=6,
    column=1,
    padx=10,
    pady=5
)


# ---------- COUNSELLOR ---------- #

tk.Label(
    status_frame,
    text="Counsellor"
).grid(
    row=7,
    column=0,
    padx=10,
    pady=5
)
       
followup_counsellor_entry = ttk.Combobox(

    status_frame,

    width=22,

    values=(

        "Karan",
        "Saurabh",
        "Gauri"
    )
)


followup_counsellor_entry.grid(
    row=7,
    column=1,
    padx=10,
    pady=5
)




# ---------- SAVE BUTTON ---------- #

update_button = tk.Button(

    status_frame,

    text="Save Followup",

    font=("Arial", 11, "bold"),

    bg="orange",

    fg="black",

    command=update_status
)

update_button.grid(
    row=8,
    column=0,
    columnspan=2,
    pady=15
)
# ---------------- LOAD ENQUIRIES ---------------- #


def load_enquiries():

    for row in enquiry_table.get_children():

        enquiry_table.delete(row)

    selected_filter = (
        filter_dropdown.get()
    )

    selected_centre = ACTIVE_CENTRE.get()
    
    enquiries = (
        cloud_database
        .get_filtered_enquiries(
            selected_filter
        )
    )
    
    # Filter by centre
    enquiries = [
    
        enquiry
    
        for enquiry in enquiries
    
        if enquiry["Nearest_CADD_Centre"]
        == selected_centre
    ]
    for enquiry in enquiries:

        values = (

    
            enquiry["student_name"],
    
            enquiry["phone"],
    
            enquiry["course_interest"],
    
            enquiry["enquiry_date"],
    
            enquiry.get(
                "next_followup_datetime",
                ""
            ),
    
            enquiry["status"],
    
            enquiry["counsellor"],
    
            enquiry["remarks"]
        )

        enquiry_table.insert(

            "",
    
            tk.END,
    
            values=values
        )


# Initial Load
load_enquiries()

def load_followups():

    for row in followup_table.get_children():

        followup_table.delete(row)

    selected_filter = (

        followup_filter_dropdown
        .get()
    )

    selected_centre = ACTIVE_CENTRE.get()
    
    enquiries = (
        cloud_database
        .get_filtered_followups(
            selected_filter
        )
    )
    
    # Filter by centre
    enquiries = [
    
        enquiry
    
        for enquiry in enquiries
    
        if enquiry["Nearest_CADD_Centre"]
        == selected_centre
    ]
    for enquiry in enquiries:

        values = (

            
            enquiry["student_name"],
        
            enquiry["phone"],
        
            enquiry["course_interest"],
        
            enquiry.get(
                "next_followup_datetime",
                ""
            ),
            
            enquiry["last_followup_date"],
        
            enquiry["status"],
            
            enquiry["remarks"],
        )

        followup_table.insert(

            "",

            tk.END,

            values=values
        )
        

load_followups()

def load_admissions():

    for row in admission_table.get_children():

        admission_table.delete(row)

    admissions = (
        cloud_database.get_students_with_finance()
    )

    selected_centre = (
        ACTIVE_CENTRE.get()
    )

    admissions = [

        student

        for student in admissions

        if student["centre"]
        == selected_centre

    ]

    for student in admissions:

        finance = student.get(
            "finance"
        ) or {}

        values = (
        
            student.get(
                "student_name",
                ""
            ),
        
            student.get(
                "mobile",
                ""
            ),
        
            student.get(
                "course_name",
                ""
            ),
        
            finance.get(
                "course_fee",
                0
            ),
        
            finance.get(
                "amount_collected_by_kti",
                0
            ),
        
            finance.get(
                "balance_receivable",
                0
            ),
        
            student.get(
                "admission_date",
                ""
            )
        
        )

        admission_table.insert(

            "",

            tk.END,

            values=values

        )

def refresh_student_management_dropdown():

    global student_management_map
    global all_student_management_options

    student_management_map = {}

    all_student_management_options = []

    students = cloud_database.get_all_students()

    selected_centre = (
        ACTIVE_CENTRE.get()
    )

    for student in students:

        if student.get("centre") != selected_centre:

            continue

        display_text = (
            f"{student['student_name']} "
            f"({student['mobile']})"
        )

        student_management_map[
            display_text
        ] = student

        all_student_management_options.append(
            display_text
        )

    student_management_dropdown["values"] = (
        all_student_management_options
    )


def repair_all_comboboxes(widget):

    for child in widget.winfo_children():

        if isinstance(child, ttk.Combobox):

            child.configure(
                state="normal",
                takefocus=True
            )

        repair_all_comboboxes(child)


refresh_student_management_dropdown()
load_admissions()
repair_all_comboboxes(root)
# ---------------- RUN APP ---------------- #

root.mainloop()
