from fastapi import FastAPI, HTTPException, Query
from bson import ObjectId
from db import db
from models import UserModel, DeviceModel, NotificationModel
from typing import List
from dummy_data import dummy_notifications
from datetime import datetime

app = FastAPI()

@app.post("/users/")
def create_user(user: UserModel):
    result = db.users.insert_one(user.dict())
    return {"id": str(result.inserted_id)}

@app.get("/users/{user_id}")
def get_user(user_id: str):
    user = db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user["_id"] = str(user["_id"])
    return user

@app.post("/devices/")
def register_device(device: DeviceModel):
    result = db.devices.insert_one(device.dict())
    return {"id": str(result.inserted_id)}

@app.post("/notifications/")
def create_notification(notification: NotificationModel):
    result = db.notifications.insert_one(notification.dict())
    return {"id": str(result.inserted_id)}

@app.get("/notifications/")
def get_notifications():
    notifications = list(db.notifications.find())
    for notif in notifications:
        notif["_id"] = str(notif["_id"])
    return notifications

@app.get("/notifications/{notif_id}")
def get_notification(notif_id: str):
    notif = db.notifications.find_one({"_id": ObjectId(notif_id)})
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif["_id"] = str(notif["_id"])
    return notif

@app.put("/notifications/{notif_id}/read")
def mark_as_read(notif_id: str, user_id: str = Query(...)):
    result = db.notifications.update_one(
        {"_id": ObjectId(notif_id)},
        {"$addToSet": {"read_by": user_id}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification marked as read"}

@app.get("/users/{user_id}/notifications")
def get_user_notifications(user_id: str):
    notifs = list(db.notifications.find({"recipients": user_id}))
    for n in notifs:
        n["_id"] = str(n["_id"])
    return notifs

@app.delete("/notifications/{notif_id}")
def delete_notification(notif_id: str):
    result = db.notifications.delete_one({"_id": ObjectId(notif_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification deleted"}

@app.post("/notifications/insert_dummy")
def insert_dummy_notifications():
    inserted_ids = []
    for notif in dummy_notifications:
        result = db.notifications.insert_one({**notif, "status": "pending"})
        inserted_ids.append(str(result.inserted_id))
    return {"inserted_ids": inserted_ids}
