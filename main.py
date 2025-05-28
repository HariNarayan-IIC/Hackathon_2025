from fastapi import FastAPI, HTTPException, Query, Request
from bson import ObjectId
from db import db
from models import UserModel, DeviceModel, NotificationModel
from typing import List
from dummy_data import dummy_notifications
from datetime import datetime
from NotificationClassifier import classify_notification
from NotificationScheduler import generate_prompt, get_schedule
from CronJobScheduler import start_scheduler
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from pywebpush import webpush, WebPushException
import os
import json
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
VAPID_PRIVATE_KEY = os.getenv("PRIVATE_KEY")
VAPID_PUBLIC_KEY= os.getenv("PUBLIC_KEY")
VAPID_CLAIMS = {
    "sub": "mailto:rhari.narayan@iic.ac.in"
}

def send_notification(subscription_info, data):
    try:
        webpush(
            subscription_info=subscription_info,
            data=data,
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims=VAPID_CLAIMS
        )
    except WebPushException as ex:
        print("Web push failed:", repr(ex))


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    start_scheduler()
    yield
    # Shutdown actions (optional)
    # stop_scheduler()
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080, https://naughtyfication.netlify.app/"],  # your frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

subscriptions = []

@app.post("/users/")
async def create_user(user: UserModel):
    result = await db.users.insert_one(user.dict())
    return {"id": str(result.inserted_id)}

@app.get("/users/{user_id}")
async def get_user(user_id: str):
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user["_id"] = str(user["_id"])
    return user

@app.post("/devices/")
async def register_device(device: DeviceModel):
    result = await db.devices.insert_one(device.dict())
    return {"id": str(result.inserted_id)}


@app.post("/api/subscribe")
async def subscribe(request: Request):
    data = await request.json()
    subscriptions.append(data)  # In production, store in DB
    return {"status": "subscribed"}

@app.post("/api/notify")
def notify_all():
    for sub in subscriptions:
        send_notification(sub, '{"title":"Hello!", "body":"This is a test notification"}')
    return {"status": "sent"}

@app.post("/notifications/")
async def create_notification(notification: NotificationModel):
    print("In here")
    result = await db.notifications.insert_one(notification.dict())
    notification = await db.notifications.find_one(result.inserted_id)
    #Classify and Summarize
    classificationResult = classify_notification(notification["title"], notification["content"], notification["source"])

    if classificationResult["category"] == "Hazard" or classificationResult["priority"] == "Urgent":
        # Update notification with classification and summary but no scheduling
        await db.notifications.update_one(
            {"_id": result.inserted_id},
            {
                "$set": {
                    "category": classificationResult["category"],
                    "priority": classificationResult["priority"],
                    "summary": classificationResult["summary"],
                    "scheduled_for_begin": None,
                    "scheduled_for_end": None,
                    "frequency": None,
                    "status": "Sent"  # Optionally mark as sent
                }
            }
        )
        for sub in subscriptions:
            payload = {
                "title": notification["title"],
                "body": classificationResult["summary"]  # summary is better for body
            }
            send_notification(sub, json.dumps(payload))

        return {"id": str(result.inserted_id), "message": "Notification sent immediately due to Hazard/Urgent classification."}

    #Schedule notification
    userBehaviourResult = await db.user_behaviours.find_one({
        "user_id": notification["user_id"], 
        "notification_category": classificationResult["category"], 
        "notification_priority": classificationResult["priority"]})
    if (not userBehaviourResult):
        userBehaviourResult = {
            "average_reaction_time": None, 
            "clickedCount": None, 
            "dismissedCount": None}
    prompt = generate_prompt(category= classificationResult["category"], priority= classificationResult["priority"], avg_reaction_time= userBehaviourResult["average_reaction_time"], click_count= userBehaviourResult["clickedCount"], dismiss_count= userBehaviourResult["dismissedCount"], creation_datetime=notification["created_at"] )
    scheduleResult = get_schedule(prompt)

    # Update notification document in MongoDB
    await db.notifications.update_one(
        {"_id": result.inserted_id},
        {
            "$set": {
                "category": classificationResult["category"],
                "priority": classificationResult["priority"],
                "summary": classificationResult["summary"],
                "scheduled_for_begin": scheduleResult["startdatetime"],
                "scheduled_for_end": scheduleResult["enddatetime"],
                "frequency": scheduleResult["frequency"]
            }
        }
    )


    return {"id": str(result.inserted_id)}


@app.get("/notifications/")
async def get_notifications():
    # Filter out notifications with status "Clicked" or "Dismissed"
    query = {"status": {"$nin": ["Clicked", "Dismissed"]}}
    notifications = await db.notifications.find(query).to_list(length=None)
    
    # Convert ObjectId to string for JSON serialization
    for notif in notifications:
        notif["_id"] = str(notif["_id"])
    
    return notifications


@app.get("/notifications/{notif_id}")
async def get_notification(notif_id: str):
    notif = await db.notifications.find_one({"_id": ObjectId(notif_id)})
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif["_id"] = str(notif["_id"])
    return notif

@app.put("/notifications/{notif_id}/read")
async def mark_as_read(notif_id: str, user_id: str = Query(...)):
    result = await db.notifications.update_one(
        {"_id": ObjectId(notif_id)},
        {"$addToSet": {"read_by": user_id}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification marked as read"}

@app.get("/users/{user_id}/notifications")
async def get_user_notifications(user_id: str):
    notifs = await list(db.notifications.find({"recipients": user_id}))
    for n in notifs:
        n["_id"] = str(n["_id"])
    return notifs

@app.delete("/notifications/{notif_id}")
async def delete_notification(notif_id: str):
    result = await db.notifications.delete_one({"_id": ObjectId(notif_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification deleted"}

@app.post("/notifications/insert_dummy")
async def insert_dummy_notifications():
    inserted_ids = []
    for notif in dummy_notifications:
        result = await db.notifications.insert_one({**notif, "status": "pending"})
        inserted_ids.append(str(result.inserted_id))
    return {"inserted_ids": inserted_ids}
