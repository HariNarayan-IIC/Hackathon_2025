# models.py

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, time
from bson import ObjectId
from enum import Enum

class Priority (str, Enum):
    high= "High"
    medium= "Medium"
    low= "Low"

class Category (str, Enum):
    work= "Work"
    social= "Social"
    finance= "Finance"
    promotions= "Promotions"
    system= "System"
    health= "Health"
    news= "News"
    entertainment= "Entertainment"

class NotificationModel(BaseModel):
    user_id: ObjectId
    source: str
    title: str
    content: str
    summary: Optional[str] = None
    priority: Optional[Priority] = None
    category: Optional[Category] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    scheduled_for_begin: Optional[datetime] = None
    scheduled_for_end: Optional[datetime] = None
    frequency: Optional[int] = None
    delivered_at: list[Optional[datetime]] = []
    class Config:
        arbitrary_types_allowed = True


class UserModel(BaseModel):
    name: str
    timezone: str
    dnd_start: Optional[time] = None
    dnd_end: Optional[time] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)



class Platform (str, Enum):
    windows= "Windows"
    ios= "IOS"
    android= "Android"

class DeviceModel(BaseModel):
    user_id: ObjectId
    endpoint: Optional[str] = None
    platform: Optional[Platform] = None
    key: Optional[str] = None
    created_at: Optional[datetime] = None
    class Config:
        arbitrary_types_allowed = True

class Action(str, Enum):
    clicked= "Clicked"
    dismissed= "Dismissed"


class UserBehaviourModel(BaseModel):
    user_id: ObjectId
    notification_id: ObjectId
    device_id: ObjectId
    action: Action
    created_at: datetime = Field(default_factory=datetime.utcnow)
    class Config:
        arbitrary_types_allowed = True


