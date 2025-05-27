from fastapi import FastAPI, HTTPException, Query
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    start_scheduler()
    yield
    # Shutdown actions (optional)
    # stop_scheduler()
app = FastAPI(lifespan=lifespan)




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

@app.post("/notifications/")
async def create_notification(notification: NotificationModel):
    print("In here")
    result = await db.notifications.insert_one(notification.dict())
    notification = await db.notifications.find_one(result.inserted_id)
    print(notification)
    #Classify and Summarize
    classificationResult = classify_notification(notification["title"], notification["content"], notification["source"])

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
    notifications = await list(db.notifications.find())
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
