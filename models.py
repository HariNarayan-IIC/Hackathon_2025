# models.py

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, time
from enum import Enum

class Priority (str, Enum):
    high= "High"
    medium= "Medium"
    low= "Low"
    urgent= "Urgent"

class Category (str, Enum):
    work= "Work"
    social= "Social"
    finance= "Finance"
    promotions= "Promotions"
    system= "System"
    health= "Health"
    news= "News"
    entertainment= "Entertainment"
    hazard= "Hazard"

class Status(str, Enum):
    pending= "Pending"
    deliverd= "Delivered"
    clicked= "Clicked"
    dismissed= "Dismissed"

class NotificationModel(BaseModel):
    user_id: str
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
    status: Status= Status.pending
    delivered_at: list[Optional[datetime]] = []

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
    user_id: str
    endpoint: Optional[str] = None
    platform: Optional[Platform] = None
    key: Optional[str] = None
    created_at: Optional[datetime] = None
    

class Action(str, Enum):
    clicked= "Clicked"
    dismissed= "Dismissed"


class UserFeedback(BaseModel):
    user_id: str
    notification_id: str
    device_id: str
    action: Action
    created_at: datetime = Field(default_factory=datetime.utcnow)
    


class UserBehaviour(BaseModel):
    user_id: str
    notification_category: Category
    notification_priority: Priority
    average_reaction_time: time
    clickedCount: int
    dismissedCount: int
    class Config:
        arbitrary_types_allowed = True


