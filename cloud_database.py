# -*- coding: utf-8 -*-
"""
Created on Thu May 14 18:20:51 2026

@author: Karan
"""
"""

from crm_reminder_engine.followup_checker import (
    send_whatsapp_message,
    get_whatsapp_message
)
"""

from supabase import create_client

from datetime import datetime

import os
from dotenv import load_dotenv
load_dotenv()

url = os.getenv("SUPABASE_URL")

key = os.getenv("SUPABASE_KEY")


supabase = create_client(
    url,
    key
)

def add_enquiry(data):

    for field in (
        "enquiry_date",
        "last_followup_date",
        "next_followup_datetime"
    ):
        if data.get(field) == "":
            data[field] = None

    # Check duplicate enquiry
    existing = supabase.table(
        "enquiries"
    ).select(
        "*"
    ).eq(
        "phone", data["phone"]
    ).eq(
        "course_interest",
        data["course_interest"]
    ).execute()

    # Duplicate found
    if len(existing.data) > 0:
        return "duplicate"

    # Insert enquiry
    response = supabase.table(
        "enquiries"
    ).insert(
        data
    ).execute()

    enquiry_id = (
        response.data[0]["id"]
    )

    create_initial_followup_log(

        enquiry_id,

        data["student_name"],

        data["remarks"],

        data["status"],

        data["counsellor"],
        data["next_followup_datetime"]
    )
    return "success"

    # ---------- SEND WELCOME WHATSAPP ---------- #
"""
    try:

        whatsapp_message = (
            get_whatsapp_message(
                data
            )
        )

        success = send_whatsapp_message(
        
            data["phone"],
        
            whatsapp_message
        )

        if success:

            supabase.table(
                "enquiries"
            ).update({

                "whatsapp_sent": True

            }).eq(

                "id",

                enquiry_id

            ).execute()

            print(
                f"WhatsApp sent to "
                f'{data["student_name"]}'
            )

        else:

            print(
                f"WhatsApp FAILED for "
                f'{data["student_name"]}'
            )

    except Exception as e:

        print(
            "WhatsApp Error:",
            e
        )

    return "success"
"""
    

def get_all_enquiries():

    response = supabase.table(
        "enquiries"
    ).select("*").execute()

    return response.data


from datetime import datetime

def get_pending_followups():

    now = datetime.now().isoformat()

    response = (
        supabase.table("enquiries")
        .select("*")
        .lte("next_followup_datetime", now)
        .neq("status", "Joined")
        .neq("status", "Closed")
        .execute()
    )

    return response.data


def update_enquiry_status(

    enquiry_id,

    new_status
):

    response = supabase.table(
        "enquiries"
    ).update({

        "status": new_status

    }).eq(

        "id",

        enquiry_id

    ).execute()

    return response



def save_followup(

    enquiry_id,

    student_name,

    followup_type,

    response,

    remarks,

    next_followup_date,
    next_followup_time,

    status,

    counsellor
):

    today = datetime.now().isoformat()



    local_datetime = datetime.strptime(
        f"{next_followup_date} {next_followup_time}",
        "%Y-%m-%d %H:%M"
    )

    next_followup_datetime = local_datetime.isoformat()
    # INSERT INTO FOLLOWUP LOGS
    supabase.table(
        "followup_logs"
    ).insert({

        "enquiry_id": enquiry_id,

        "student_name": student_name,

        "followup_date": today,

        "followup_type": followup_type,

        "response": response,

        "response_status": status,

        "remarks": remarks,

        "next_followup_datetime": next_followup_datetime,

        "counsellor": counsellor

    }).execute()

    # UPDATE ENQUIRY TABLE
    supabase.table(
        "enquiries"
    ).update({
    
        "status": status,
    
        "remarks": remarks,
        


        "last_followup_date": today,

        "next_followup_datetime": next_followup_datetime,
    
        "telegram_sent": False
    
    }).eq(

        "id",

        enquiry_id

    ).execute()
        
        
        
def get_student_names():

    response = supabase.table(
        "enquiries"
    ).select(
        "id,student_name,phone,Nearest_CADD_Centre"
    ).execute()

    return response.data

def get_enquiry_details(enquiry_id):

    response = supabase.table(
        "enquiries"
    ).select("*").eq(
        "id",
        enquiry_id
    ).execute()

    if response.data:
        return response.data[0]

    return None


def update_enquiry_details(enquiry_id, data):

    response = supabase.table(
        "enquiries"
    ).update(
        data
    ).eq(
        "id",
        enquiry_id
    ).execute()

    if "student_name" in data:

        supabase.table(
            "followup_logs"
        ).update({

            "student_name":
                data["student_name"]

        }).eq(

            "enquiry_id",
            enquiry_id

        ).execute()

    return response


def save_admission_details(

    enquiry_id,

    final_course,

    course_fee,

    first_payment,

    payment_date,

    payment_mode,

    payment_reference,

    admission_date
):

    response = supabase.table(
        "enquiries"
    ).update({

        "status": "Joined",

        "final_course_selected":
            final_course,

        "final_course_fee":
            float(course_fee),

        "first_payment_amount":
            float(first_payment),

        "first_payment_date":
            payment_date,

        "payment_mode":
            payment_mode,

        "payment_reference":
            payment_reference,

        "admission_date":
            admission_date

    }).eq(

        "id",

        enquiry_id

    ).execute()

    return response

from datetime import datetime, timedelta


def get_filtered_enquiries(
    filter_type
):

    if filter_type == (
        "Last 20 Leads"
    ):

        response = supabase.table(
            "enquiries"
        ).select("*").order(

            "id",

            desc=True

        ).limit(20).execute()

        return response.data


    elif filter_type == (
        "Last 15 Days"
    ):

        date_15_days_ago = (

            datetime.today()

            - timedelta(days=15)

        ).strftime(
            "%Y-%m-%d"
        )

        response = supabase.table(
            "enquiries"
        ).select("*").gte(

            "enquiry_date",

            date_15_days_ago

        ).order(

            "id",

            desc=True

        ).execute()

        return response.data


    else:

        response = supabase.table(
            "enquiries"
        ).select("*").order(

            "id",

            desc=True

        ).execute()

        return response.data



def get_filtered_followups(filter_type):

    today = datetime.today()

    now = datetime.now().isoformat()

    today_start = today.strftime("%Y-%m-%dT00:00:00")
    today_end = today.strftime("%Y-%m-%dT23:59:59")

    tomorrow = today + timedelta(days=1)

    tomorrow_start = tomorrow.strftime("%Y-%m-%dT00:00:00")
    tomorrow_end = tomorrow.strftime("%Y-%m-%dT23:59:59")

    next_7_days_end = (
        today + timedelta(days=7)
    ).strftime("%Y-%m-%dT23:59:59")

    if filter_type == "Today's Followups":

        response = (
            supabase.table("enquiries")
            .select("*")
            .gte(
                "next_followup_datetime",
                today_start
            )
            .lte(
                "next_followup_datetime",
                today_end
            )
            .execute()
        )

    elif filter_type == "Tomorrow":

        response = (
            supabase.table("enquiries")
            .select("*")
            .gte(
                "next_followup_datetime",
                tomorrow_start
            )
            .lte(
                "next_followup_datetime",
                tomorrow_end
            )
            .execute()
        )

    elif filter_type == "Overdue":

        response = (
            supabase.table("enquiries")
            .select("*")
            .lt(
                "next_followup_datetime",
                now
            )
            .neq(
                "status",
                "Joined"
            )
            .neq(
                "status",
                "Closed"
            )
            .execute()
        )

    elif filter_type == "Next 7 Days":

        response = (
            supabase.table("enquiries")
            .select("*")
            .gte(
                "next_followup_datetime",
                today_start
            )
            .lte(
                "next_followup_datetime",
                next_7_days_end
            )
            .execute()
        )

    else:

        response = (
            supabase.table("enquiries")
            .select("*")
            .neq(
                "status",
                "Joined"
            )
            .execute()
        )

    return response.data

def get_followup_history(
    enquiry_id
):

    response = supabase.table(
        "followup_logs"
    ).select("*").eq(

        "enquiry_id",

        enquiry_id

    ).order(

        "followup_date",

        desc=True

    ).execute()

    return response.data


def create_initial_followup_log(

    enquiry_id,

    student_name,

    remarks,

    status,

    counsellor, 
    next_followup_datetime
):

    from datetime import datetime

    today = datetime.today().strftime(
        "%Y-%m-%d"
    )

    supabase.table(
        "followup_logs"
    ).insert({

        "enquiry_id": enquiry_id,

        "student_name": student_name,

        "followup_date": today,

        "followup_type":
            "Enquiry Created",

        "response":
            "New Lead",

        "remarks":
            remarks,

        "response_status":
            status,

        "counsellor":
            counsellor,
            
        "next_followup_datetime": 
            next_followup_datetime

    }).execute()
            
def create_admission_log(

    enquiry_id,

    student_name,

    final_course,

    first_payment,

    counsellor
):

    today = datetime.now().isoformat()

    supabase.table(
        "followup_logs"
    ).insert({

        "enquiry_id": enquiry_id,

        "student_name": student_name,

        "followup_date": today,

        "followup_type": "Admission",

        "response": "Joined",

        "response_status": "Joined",

        "counsellor": counsellor,

        "remarks":
            f"Course: {final_course} | "
            f"First Payment: ₹{first_payment}"

    }).execute()
            
def get_joined_students():

    response = (

        supabase.table("enquiries")

        .select("*")

        .eq("status", "Joined")

        .execute()

    )

    return response.data


def create_student_record(
    student_name,
    mobile,
    email,
    course_name,
    centre,
    admission_date,
    counsellor_name,
    lead_source,
    enquiry_id
):

    response = (
        supabase.table("student_master")
        .insert({
            "student_name": student_name,
            "mobile": mobile,
            "email": email,
            "course_name": course_name,
            "centre": centre,
            "admission_date": admission_date,
            "counsellor_name": counsellor_name,
            "lead_source": lead_source,
            "crm_enquiry_id": enquiry_id,
            "admission_status": "Active"
        })
        .execute()
    )

    return response.data[0]["id"]


def create_student_finance_record(
    student_id,
    course_fee,
    first_payment
):

    balance = float(course_fee) - float(first_payment)

    finance_status = (
        "Paid"
        if balance <= 0
        else "Partial"
    )

    response = (
        supabase.table("student_finance")
        .insert({
            "student_id": student_id,

            "course_fee": float(course_fee),

            "amount_collected_by_kti":
                float(first_payment),

            "balance_receivable":
                balance,

            "finance_status":
                finance_status
        })
        .execute()
    )

    return response


def create_student_transaction(
    student_id,
    payment_date,
    amount,
    payment_mode,
    remarks="",
    payment_type="Admission"
):

    response = (
        supabase.table(
            "student_finance_transactions"
        )
        .insert({
            "student_id": student_id,

            "payment_date":
                payment_date,

            "amount":
                float(amount),

            "payment_mode":
                payment_mode,

            "payment_type":
                payment_type,

            "remarks":
                remarks
        })
        .execute()
    )

    return response


def add_student_payment(
    student_id,
    payment_date,
    amount,
    payment_mode,
    remarks=""
):

    transaction_response = create_student_transaction(
        student_id=student_id,
        payment_date=payment_date,
        amount=amount,
        payment_mode=payment_mode,
        remarks=remarks,
        payment_type="Installment"
    )

    finance = get_student_finance(student_id)

    if not finance:

        return transaction_response

    collected = (
        float(
            finance.get(
                "amount_collected_by_kti",
                0
            )
        )
        +
        float(amount)
    )

    course_fee = float(
        finance.get(
            "course_fee",
            0
        )
    )

    balance = course_fee - collected

    if balance < 0:

        balance = 0

    finance_status = (
        "Paid"
        if balance <= 0
        else "Partial"
    )

    supabase.table(
        "student_finance"
    ).update({

        "amount_collected_by_kti":
            collected,

        "balance_receivable":
            balance,

        "finance_status":
            finance_status

    }).eq(

        "student_id",
        student_id

    ).execute()

    return transaction_response

def student_exists_for_enquiry(enquiry_id):

    response = (
        supabase.table("student_master")
        .select("id")
        .eq("crm_enquiry_id", enquiry_id)
        .execute()
    )

    return len(response.data) > 0


def get_all_students():

    response = (
        supabase.table("student_master")
        .select("*")
        .order("student_name")
        .execute()
    )

    return response.data


def get_students_with_finance():

    students = get_all_students()

    for student in students:

        student["finance"] = get_student_finance(
            student["id"]
        )

    return students


def get_student_transactions(student_id):

    response = (
        supabase.table(
            "student_finance_transactions"
        )
        .select("*")
        .eq(
            "student_id",
            student_id
        )
        .order(
            "payment_date",
            desc=True
        )
        .execute()
    )

    return response.data

def get_student_finance(student_id):

    response = (
        supabase.table(
            "student_finance"
        )
        .select("*")
        .eq(
            "student_id",
            student_id
        )
        .execute()
    )

    if response.data:

        return response.data[0]

    return None


