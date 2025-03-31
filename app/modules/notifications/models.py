"""
Models for the notifications module.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, List

from pydantic import BaseModel, Field
from sqlalchemy import JSON, Boolean, DateTime, Integer, String, Text, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base_model import BaseModel as DBBaseModel


class NotificationType(str, Enum):
    """
    Enum for notification types.
    """

    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class NotificationPriority(str, Enum):
    """
    Enum for notification priorities.
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class NotificationStatus(str, Enum):
    """
    Enum for notification status.
    """

    PENDING = "pending"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    EXPIRED = "expired"


class Notification(DBBaseModel):
    """
    Model for storing notifications.
    """

    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    notification_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default=NotificationType.INFO.value
    )
    priority: Mapped[str] = mapped_column(
        String(20), nullable=False, default=NotificationPriority.MEDIUM.value
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=NotificationStatus.PENDING.value
    )
    recipient_id: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )  # User ID or group ID
    recipient_type: Mapped[str] = mapped_column(String(20), nullable=False)  # "user" or "group"
    sender_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # User ID or system ID
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), index=True)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)  # Optional expiration time
    data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)  # Additional data for the notification
    action_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # Optional URL for action button

    # Create indexes for common query patterns
    __table_args__ = (
        Index("idx_notifications_recipient_status", "recipient_id", "status"),
        Index("idx_notifications_created_at", "created_at"),
    )


# Pydantic models for API
class NotificationCreate(BaseModel):
    """
    Schema for creating a new notification.
    """

    title: str = Field(..., max_length=200, description="Notification title")
    message: str = Field(..., description="Notification message")
    notification_type: NotificationType = Field(
        NotificationType.INFO, description="Type of notification"
    )
    priority: NotificationPriority = Field(
        NotificationPriority.MEDIUM, description="Priority of notification"
    )
    recipient_id: str = Field(..., max_length=100, description="ID of the recipient (user or group)")
    recipient_type: str = Field(
        ..., max_length=20, description="Type of recipient ('user' or 'group')"
    )
    sender_id: Optional[str] = Field(
        None, max_length=100, description="ID of the sender (user or system)"
    )
    expires_at: Optional[datetime] = Field(None, description="Optional expiration time")
    data: Optional[Dict[str, Any]] = Field(
        None, description="Additional data for the notification"
    )
    action_url: Optional[str] = Field(
        None, max_length=500, description="Optional URL for action button"
    )


class NotificationUpdate(BaseModel):
    """
    Schema for updating a notification.
    """

    status: Optional[NotificationStatus] = Field(
        None, description="Status of the notification"
    )
    delivered_at: Optional[datetime] = Field(
        None, description="Time when the notification was delivered"
    )
    read_at: Optional[datetime] = Field(
        None, description="Time when the notification was read"
    )


class NotificationResponse(BaseModel):
    """
    Schema for notification response.
    """

    id: int
    title: str
    message: str
    notification_type: NotificationType
    priority: NotificationPriority
    status: NotificationStatus
    recipient_id: str
    recipient_type: str
    sender_id: Optional[str]
    created_at: datetime
    delivered_at: Optional[datetime]
    read_at: Optional[datetime]
    expires_at: Optional[datetime]
    data: Optional[Dict[str, Any]]
    action_url: Optional[str]

    class Config:
        orm_mode = True


class NotificationBulkCreate(BaseModel):
    """
    Schema for creating multiple notifications at once.
    """
    title: str = Field(..., max_length=200, description="Notification title")
    message: str = Field(..., description="Notification message")
    notification_type: NotificationType = Field(
        NotificationType.INFO, description="Type of notification"
    )
    priority: NotificationPriority = Field(
        NotificationPriority.MEDIUM, description="Priority of notification"
    )
    recipient_ids: List[str] = Field(..., description="List of recipient IDs")
    recipient_type: str = Field(
        ..., max_length=20, description="Type of recipients ('user' or 'group')"
    )
    sender_id: Optional[str] = Field(
        None, max_length=100, description="ID of the sender (user or system)"
    )
    expires_at: Optional[datetime] = Field(None, description="Optional expiration time")
    data: Optional[Dict[str, Any]] = Field(
        None, description="Additional data for the notification"
    )
    action_url: Optional[str] = Field(
        None, max_length=500, description="Optional URL for action button"
    )
