import os
import smtplib
import json
import asyncio
import logging
from dotenv import load_dotenv
from email.mime.text import MIMEText
from twilio.rest import Client
import nats
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# -------------------------
# ENV Values
# -------------------------
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH = os.getenv("TWILIO_AUTH")
TWILIO_WHATSAPP = os.getenv("TWILIO_WHATSAPP")

MONGO_URI = os.getenv("MONGODB_URI")
NATS_SERVERS = os.getenv("NATS_SERVERS", "nats://localhost:4222")

# Initialize MongoDB
try:
    mongo = MongoClient(MONGO_URI)
    db = mongo["ats"]
    applications = db["applications"]
    logger.info("✅ Notification Agent: MongoDB connected")
except Exception as e:
    logger.error(f"❌ Notification Agent: MongoDB connection error: {e}")
    applications = None

# Initialize Twilio
try:
    twilio_client = Client(TWILIO_SID, TWILIO_AUTH)
    logger.info("✅ Notification Agent: Twilio initialized")
except Exception as e:
    logger.error(f"❌ Notification Agent: Twilio init error: {e}")
    twilio_client = None

def extract_name(text):
    """Simple name extraction from the start of resume text"""
    if not text:
        return "Candidate"
    # Take the first line or first few words
    lines = text.strip().split('\n')
    if lines:
        name = lines[0].strip()
        if len(name) < 50:  # Sanity check
            return name
    return "Candidate"

async def send_email(candidate_name, candidate_email):
    if not EMAIL_USER or not EMAIL_PASS:
        logger.warning("SMTP credentials missing, skipping email")
        return

    subject = "🎉 Resume Selected"
    body = f"""
Hi {candidate_name},

Congratulations! 🎉

Your resume has been selected for the next round.

Our HR team will contact you soon.

Best Regards,
HR Team
"""
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = candidate_email

    try:
        # Using loop.run_in_executor for blocking SMTP calls
        loop = asyncio.get_running_loop()
        def _send():
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, candidate_email, msg.as_string())
            server.quit()
        
        await loop.run_in_executor(None, _send)
        logger.info(f"✅ Email Sent Successfully to {candidate_email}")
    except Exception as e:
        logger.error(f"❌ Email Error for {candidate_email}: {e}")

async def send_whatsapp(candidate_name, candidate_phone):
    if not twilio_client or not TWILIO_WHATSAPP:
        logger.warning("Twilio client not initialized, skipping WhatsApp")
        return

    try:
        # Ensure phone number formatting (Twilio expects E.164)
        phone = candidate_phone.strip()
        if not phone.startswith('+'):
            # Assuming Indian numbers if no prefix, or you might need a more robust check
            if len(phone) == 10:
                phone = "+91" + phone
            else:
                phone = "+" + phone

        # Using loop.run_in_executor for blocking Twilio calls
        loop = asyncio.get_running_loop()
        def _send():
            twilio_client.messages.create(
                body=f"Hi {candidate_name}, 🎉 Your resume has been selected. HR team will contact you soon.",
                from_=TWILIO_WHATSAPP,
                to=f"whatsapp:{phone}"
            )
        
        await loop.run_in_executor(None, _send)
        logger.info(f"✅ WhatsApp Sent Successfully to {phone}")
    except Exception as e:
        logger.error(f"❌ WhatsApp Error for {phone}: {e}")

async def process_notification(application_id):
    """Fetch candidate details and send notifications"""
    if applications is None:
        logger.error("MongoDB not available")
        return

    try:
        app = applications.find_one({"_id": ObjectId(application_id)})
        if not app:
            logger.error(f"Application {application_id} not found")
            return

        candidate_email = app.get("emailInfo")
        candidate_phone = app.get("contactInfo")
        resume_text = app.get("resume_text_extracted", "")
        candidate_name = extract_name(resume_text)

        logger.info(f"发送通知给: {candidate_name} ({candidate_email}, {candidate_phone})")

        tasks = []
        if candidate_email:
            tasks.append(send_email(candidate_name, candidate_email))
        if candidate_phone:
            tasks.append(send_whatsapp(candidate_name, candidate_phone))
        
        if tasks:
            await asyncio.gather(*tasks)
        else:
            logger.warning(f"No contact info for application {application_id}")

    except Exception as e:
        logger.error(f"Error processing notification for {application_id}: {e}")

async def run_notification_agent(nc=None):
    """Run as a NATS subscriber"""
    logger.info("="*60)
    logger.info("🔔 NOTIFICATION AGENT STARTING")
    logger.info("="*60)

    should_close_nc = False
    if nc is None:
        try:
            nc = await nats.connect(NATS_SERVERS)
            should_close_nc = True
            logger.info(f"✅ Notification Agent: NATS connected at {NATS_SERVERS}")
        except Exception as e:
            logger.error(f"❌ Notification Agent: NATS connection error: {e}")
            return

    async def message_handler(msg):
        try:
            data = json.loads(msg.data.decode())
            app_id = data.get("application_id")
            if app_id:
                logger.info(f"🔔 Received selection event for app: {app_id}")
                await process_notification(app_id)
            else:
                logger.error("Message missing application_id")
        except Exception as e:
            logger.error(f"Error in notification message handler: {e}")

    await nc.subscribe("resume.selected", cb=message_handler)
    logger.info("✅ Notification Agent: Subscribed to 'resume.selected'")
    
    if should_close_nc:
        # If we created the connection here, we need to keep the function alive
        while True:
            await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        asyncio.run(run_notification_agent())
    except KeyboardInterrupt:
        logger.info("Stop by user")