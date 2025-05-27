# models.py

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class NotificationModel(BaseModel):
    title: str
    message: str
    priority: int = Field(ge=1, le=5, description="1=Highest, 5=Lowest")
    created_at: Optional[datetime] = None
    scheduled_for: Optional[datetime] = None
    sender: Optional[str] = None
    read: bool = False


class UserModel(BaseModel):
    title: str
    message: str
    priority: int = Field(ge=1, le=5, description="1=Highest, 5=Lowest")
    created_at: Optional[datetime] = None
    scheduled_for: Optional[datetime] = None
    sender: Optional[str] = None
    read: bool = False


class DeviceModel(BaseModel):
    title: str
    message: str
    priority: int = Field(ge=1, le=5, description="1=Highest, 5=Lowest")
    created_at: Optional[datetime] = None
    scheduled_for: Optional[datetime] = None
    sender: Optional[str] = None
    read: bool = False
