from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from db import db  # your mongodb client
import pytz

def push_notification(notification):
    # Dummy function to "push" notification
    print(f"Pushing notification to users {notification['recipients']}: {notification['title']} at {datetime.utcnow()}")

def fetch_and_schedule():
    now = datetime.utcnow()
    # Fetch notifications with scheduled_for <= now and status pending
    notifs = list(db.notifications.find({"scheduled_for": {"$lte": now}, "status": "pending"}))
    for notif in notifs:
        push_notification(notif)
        db.notifications.update_one(
            {"_id": notif["_id"]},
            {"$set": {"status": "delivered", "delivered_at": datetime.utcnow()}}
        )

def start_scheduler():
    scheduler = BackgroundScheduler(timezone=pytz.utc)
    # run fetch_and_schedule every 5 minutes
    scheduler.add_job(fetch_and_schedule, 'interval', minutes=5)
    scheduler.start()

# -----------------------------------------------------------
# In your main.py you can import and start scheduler on startup

from fastapi import FastAPI
from scheduler import start_scheduler

app = FastAPI()

@app.on_event("startup")
def startup_event():
    start_scheduler()