# -*- coding: utf-8 -*-
"""
Created on Sat Jun 13 15:11:45 2026

@author: Karan
"""

from supabase import create_client
from datetime import datetime
from zoneinfo import ZoneInfo
import requests


print("GitHub scheduler running")
import os
from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")

SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

INDIA_TZ = ZoneInfo("Asia/Kolkata")
# -------------------------
# TELEGRAM CONFIG
# -------------------------

BOT_TOKEN = os.getenv("BOT_TOKEN")

CHAT_ID = os.getenv("CHAT_ID")

SNEHA_CHAT_ID = os.getenv("SNEHA_CHAT_ID")






def send_telegram_message(message, centre):
    url = (
        f"https://api.telegram.org/bot"
        f"{BOT_TOKEN}/sendMessage"
    )

    # Your chat id (always receives)
    chat_ids = [CHAT_ID]
    
    
    # Employee based on centre
    if centre == "Dadar":
        print("appending Dadar")
        chat_ids.append(Sneha_CHAT_ID)


    chat_ids = [
        chat_id
        for chat_id in chat_ids
        if chat_id
    ]

    print("Final chat_ids:", chat_ids)

    sent = False
    
    # Send to all selected people
    for chat_id in chat_ids:

        payload = {
            "chat_id": chat_id,
            "text": message
        }
        
        try:
            requests.post(
                url,
                data=payload,
                timeout=20
            ).raise_for_status()

            sent = True

        except requests.RequestException as exc:
            print(
                "Telegram send failed:",
                exc
            )

    return sent
        

def parse_followup_datetime(value):

    if not value:
        return None

    parsed_datetime = datetime.fromisoformat(
        str(value).replace(
            "Z",
            "+00:00"
        )
    )

    if parsed_datetime.tzinfo:
        parsed_datetime = (
            parsed_datetime
            .astimezone(INDIA_TZ)
            .replace(tzinfo=None)
        )

    return parsed_datetime

        
        
def check_due_followups():

    current_time = datetime.now(
        INDIA_TZ
    ).replace(tzinfo=None)

    print("Current India Time:")
    print(current_time)

    response = supabase.table(
        "enquiries"
    ).select("*").neq(
        "status",
        "Joined"
    ).neq(
        "status",
        "Closed"
    ).execute()

    enquiries = response.data

    for enquiry in enquiries:

        student_name = enquiry.get(
            "student_name",
            "Unknown"
        )

        phone = enquiry.get(
            "phone"
        )

        status = enquiry.get(
            "status",
            "No Status"
        )

        remarks = enquiry.get(
            "remarks",
            ""
        )
        centre = enquiry.get(
            "Nearest_CADD_Centre"
        )
        
        followup_datetime = enquiry.get(
            "next_followup_datetime"
        )

        if not followup_datetime:
            continue

        try:
            followup_datetime = parse_followup_datetime(
                followup_datetime
            )

        except ValueError:
            print(
                "Invalid followup datetime for",
                student_name,
                followup_datetime
            )
            continue

        if (
            followup_datetime
            > current_time
        ):
            continue

        print("----------------")
        print(student_name)

        # -------------------------
        # TELEGRAM REMINDER
        # -------------------------

        if not enquiry.get(
            "telegram_sent",
            False
        ):

            telegram_message = f"""
FOLLOW-UP DUE

Student: {student_name}

Phone: {phone}

Status: {status}

Remark:
{remarks}

Call student now.
"""


            sent = send_telegram_message(
                telegram_message, centre
            )

            if not sent:
                print(
                    "Telegram not marked sent for",
                    student_name
                )
                continue

            supabase.table(
                "enquiries"
            ).update({

                "telegram_sent":
                    True

            }).eq(

                "id",
                enquiry["id"]

            ).execute()

            print(
                f"Telegram sent for "
                f"{student_name}"
            )



#########

if __name__ == "__main__":


    print(
        "Checking due followups..."
    )

    check_due_followups()

    print(
        "Check Complete"
    )
