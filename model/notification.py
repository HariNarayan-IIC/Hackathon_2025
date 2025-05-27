from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime

class Notification(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    source_app: str
    title: str
    message: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = "low" # low, medium, high, emergency
    scheduled_time: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    dismissed_at: Optional[datetime] = None
    status: str = "pending" # pending, delivered, read, dismissed, ignored
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)