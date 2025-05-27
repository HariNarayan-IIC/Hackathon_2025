from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from db import db  # your mongodb client
import pytz

def push_notification(notification):
    # Dummy function to "push" notification
    print(f"Pushing notification to users {notification['recipients']}: {notification['title']} at {datetime.utcnow()}")

async def fetch_and_schedule():
    now = datetime.utcnow()
    # Fetch notifications with scheduled_for <= now and status pending
    notifs = await list(db.notifications.find({"scheduled_for": {"$lte": now}, "status": "pending"}))
    for notif in notifs:
        push_notification(notif)
        await db.notifications.update_one(
            {"_id": notif["_id"]},
            {"$set": {"delivered_at": datetime.utcnow()}}
        )

async def start_scheduler():
    print("Starting scheduler...\n")
    scheduler = BackgroundScheduler(timezone=pytz.utc)
    # run fetch_and_schedule every 5 minutes
    await scheduler.add_job(fetch_and_schedule, 'interval', minutes=5)
    scheduler.start()


