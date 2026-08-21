import logging
import os
from urllib import parse, request


logger = logging.getLogger(__name__)


def _chat_ids():
    values = [
        os.getenv("CHAT_ID"),
        os.getenv("SNEHA_CHAT_ID") or os.getenv("Sneha_CHAT_ID"),
        os.getenv("OFFICE_CHAT_ID"),
    ]
    return list(dict.fromkeys(value for value in values if value))


def send_telegram_message(message):
    """Send without interrupting CRM saves when Telegram is unavailable."""
    bot_token = os.getenv("BOT_TOKEN")
    recipients = _chat_ids()
    if not bot_token or not recipients:
        logger.warning("Telegram notification skipped: configuration is incomplete")
        return False

    endpoint = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    sent = False
    for chat_id in recipients:
        payload = parse.urlencode({"chat_id": chat_id, "text": message}).encode()
        try:
            with request.urlopen(endpoint, data=payload, timeout=15) as response:
                sent = sent or response.status == 200
        except Exception:
            logger.exception("Telegram notification failed for one recipient")
    return sent


def notify_new_enquiry(enquiry):
    message = f"""📌 NEW ENQUIRY

👨 Student: {enquiry['student_name']}
📞 Phone: {enquiry['phone']}
📚 Course: {enquiry['course_interest']}
📝 Status: {enquiry['status']}
🎯 Source: {enquiry['source']}
💰 Budget: {enquiry['budget_range']}
📅 Planning: {enquiry['planning_to_start']}
👤 Counsellor: {enquiry['counsellor']}
🏢 Centre: Dadar

💬 Remark:
{enquiry.get('remarks') or '-'}"""
    return send_telegram_message(message)


def notify_joined(enquiry, course, course_fee, counsellor):
    message = f"""🎉 STUDENT JOINED

👨‍🎓 Student: {enquiry['student_name']}
📞 Phone: {enquiry['phone']}
📚 Confirmed Course: {course}
💰 Course Fee: ₹{course_fee:,.0f}
👤 Counsellor: {counsellor}
🏢 Centre: Dadar

The student is now available for the attendance system."""
    return send_telegram_message(message)
