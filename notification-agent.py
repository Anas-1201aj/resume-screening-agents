import os
from pymongo import MongoClient
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from twilio.rest import Client

# Load .env
load_dotenv()

# -------------------------------
# MongoDB Connection
# -------------------------------
mongo_uri = os.getenv("MONGODB_URI")
db_name = os.getenv("ats")
collection_name = os.getenv("applications")

client = MongoClient(mongo_uri)
db = client[db_name]
collection = db[collection_name]

# -------------------------------
# Email Credentials
# -------------------------------
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

# -------------------------------
# Twilio Credentials
# -------------------------------
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH = os.getenv("TWILIO_AUTH")
TWILIO_WHATSAPP = os.getenv("TWILIO_WHATSAPP")

twilio_client = Client(TWILIO_SID, TWILIO_AUTH)

# -------------------------------
# Send Email Function
# -------------------------------
def send_email(to_email, candidate_name):
    subject = "🎉 Resume Selected"
    
    body = f"""
Hi {candidate_name},

Congratulations! 🎉

Your resume has been selected for the next round.

Our team will contact you soon.

Best Regards,
HR Team
"""

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = to_email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, to_email, msg.as_string())
        server.quit()
        print(f"✅ Email sent to {to_email}")
        return True

    except Exception as e:
        print("❌ Email Error:", e)
        return False

# -------------------------------
# Send WhatsApp Function
# -------------------------------
def send_whatsapp(phone, candidate_name):
    try:
        message = twilio_client.messages.create(
            body=f"Hi {candidate_name}, 🎉 Your resume has been selected. HR will contact you soon.",
            from_=TWILIO_WHATSAPP,
            to=f"whatsapp:{phone}"
        )
        print(f"✅ WhatsApp sent to {phone}")
        return True

    except Exception as e:
        print("❌ WhatsApp Error:", e)
        return False

# -------------------------------
# Main Agent Logic
# -------------------------------
def run_agent():
    
    selected_candidates = collection.find({
        "resume_status": "selected",
        "notification_sent": {"$ne": True}
    })

    for candidate in selected_candidates:
        name = candidate.get("name")
        email = candidate.get("email")
        phone = candidate.get("phone")

        print(f"\n📌 Processing {name}")

        email_status = send_email(email, name)
        whatsapp_status = send_whatsapp(phone, name)

        if email_status and whatsapp_status:
            collection.update_one(
                {"_id": candidate["_id"]},
                {
                    "$set": {
                        "notification_sent": True
                    }
                }
            )
            print(f"✅ Updated DB for {name}")

# -------------------------------
# Run Agent
# -------------------------------
if __name__ == "__main__":
    run_agent()