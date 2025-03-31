"""
Models for the webhooks module.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field
from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base_model import BaseModel as DBBaseModel


class WebhookEventType(str, Enum):
    """
    Enum for webhook event types.
    """

    CONFIG_CREATED = "config.created"
    CONFIG_UPDATED = "config.updated"
    CONFIG_DELETED = "config.deleted"
    FEATURE_FLAG_CREATED = "feature_flag.created"
    FEATURE_FLAG_UPDATED = "feature_flag.updated"
    FEATURE_FLAG_DELETED = "feature_flag.deleted"
    AUDIT_EVENT = "audit.event"
    SYSTEM_ALERT = "system.alert"


class WebhookStatus(str, Enum):
    """
    Enum for webhook status.
    """

    ACTIVE = "active"
    INACTIVE = "inactive"
    FAILED = "failed"  # Too many failures


class WebhookDeliveryStatus(str, Enum):
    """
    Enum for webhook delivery status.
    """

    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"


class WebhookEndpoint(DBBaseModel):
    """
    Model for storing webhook endpoints.
    """

    __tablename__ = "webhook_endpoints"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    secret: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # For HMAC signature verification
    status: Mapped[str] = mapped_column(String(20), default=WebhookStatus.ACTIVE.value)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    created_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    headers: Mapped[Optional[Dict[str, str]]] = mapped_column(JSON, nullable=True)  # Custom headers to include in requests
    retry_count: Mapped[int] = mapped_column(Integer, default=3)  # Number of retries for failed webhooks
    timeout_seconds: Mapped[int] = mapped_column(Integer, default=5)  # Timeout for webhook requests

    # Create indexes for common query patterns
    __table_args__ = (Index("idx_webhook_endpoints_status", status),)


class WebhookSubscription(DBBaseModel):
    """
    Model for storing webhook subscriptions to event types.
    """

    __tablename__ = "webhook_subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    endpoint_id: Mapped[int] = mapped_column(Integer, ForeignKey("webhook_endpoints.id", ondelete="CASCADE"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    filter_conditions: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)  # Optional conditions for triggering
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    # Create indexes for common query patterns
    __table_args__ = (
        Index("idx_webhook_subscriptions_endpoint_event", endpoint_id, event_type),
    )


class WebhookDelivery(DBBaseModel):
    """
    Model for storing webhook delivery attempts.
    """

    __tablename__ = "webhook_deliveries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    endpoint_id: Mapped[int] = mapped_column(Integer, ForeignKey("webhook_endpoints.id", ondelete="CASCADE"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    payload: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    request_headers: Mapped[Optional[Dict[str, str]]] = mapped_column(JSON, nullable=True)
    response_status: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    response_body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    success: Mapped[bool] = mapped_column(Boolean, default=False)
    attempt_count: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    next_retry_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Create indexes for common query patterns
    __table_args__ = (
        Index("idx_webhook_deliveries_success", success),
        Index("idx_webhook_deliveries_next_retry", next_retry_at),
    )


class WebhookEvent(DBBaseModel):
    """
    Model for storing webhook events.
    """
    __tablename__ = "webhook_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    event_type: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    payload: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    target_url: Mapped[str] = mapped_column(String(500), nullable=False)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_attempt: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    next_retry: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    response_code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    response_body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), index=True)

    # Create indexes for common query patterns
    __table_args__ = (
        Index("idx_webhook_events_status", "status"),
        Index("idx_webhook_events_event_type", "event_type"),
        Index("idx_webhook_events_next_retry", "next_retry"),
    )


# Pydantic models for API
class WebhookEndpointCreate(BaseModel):
    """
    Schema for creating a new webhook endpoint.
    """

    name: str = Field(..., description="Name of the webhook endpoint")
    url: str = Field(..., description="URL of the webhook endpoint")
    description: Optional[str] = Field(None, description="Description of the webhook endpoint")
    secret: Optional[str] = Field(None, description="Secret for HMAC signature verification")
    headers: Optional[Dict[str, str]] = Field(None, description="Custom headers to include in requests")
    retry_count: Optional[int] = Field(3, description="Number of retries for failed webhooks")
    timeout_seconds: Optional[int] = Field(5, description="Timeout for webhook requests in seconds")


class WebhookEndpointUpdate(BaseModel):
    """
    Schema for updating a webhook endpoint.
    """

    name: Optional[str] = Field(None, description="Name of the webhook endpoint")
    url: Optional[str] = Field(None, description="URL of the webhook endpoint")
    description: Optional[str] = Field(None, description="Description of the webhook endpoint")
    secret: Optional[str] = Field(None, description="Secret for HMAC signature verification")
    status: Optional[WebhookStatus] = Field(None, description="Status of the webhook endpoint")
    headers: Optional[Dict[str, str]] = Field(None, description="Custom headers to include in requests")
    retry_count: Optional[int] = Field(None, description="Number of retries for failed webhooks")
    timeout_seconds: Optional[int] = Field(None, description="Timeout for webhook requests in seconds")


class WebhookSubscriptionCreate(BaseModel):
    """
    Schema for creating a new webhook subscription.
    """

    event_type: WebhookEventType = Field(..., description="Event type to subscribe to")
    filter_conditions: Optional[Dict[str, Any]] = Field(None, description="Optional conditions for triggering")


class WebhookEndpointResponse(BaseModel):
    """
    Schema for webhook endpoint response.
    """

    id: int
    name: str
    url: str
    description: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    retry_count: int
    timeout_seconds: int

    class Config:
        orm_mode = True


class WebhookSubscriptionResponse(BaseModel):
    """
    Schema for webhook subscription response.
    """

    id: int
    endpoint_id: int
    event_type: str
    filter_conditions: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        orm_mode = True


class WebhookDeliveryResponse(BaseModel):
    """
    Schema for webhook delivery response.
    """

    id: int
    endpoint_id: int
    event_type: str
    payload: Dict[str, Any]
    response_status: Optional[int] = None
    success: bool
    attempt_count: int
    created_at: datetime
    completed_at: Optional[datetime] = None
    next_retry_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class WebhookTestRequest(BaseModel):
    """
    Schema for testing a webhook endpoint.
    """

    event_type: WebhookEventType = Field(..., description="Event type to test")
    payload: Dict[str, Any] = Field(..., description="Test payload to send")


class WebhookEventCreate(BaseModel):
    """
    Schema for creating a webhook event.
    """
    event_type: str = Field(..., max_length=100, description="Type of the event")
    payload: Dict[str, Any] = Field(..., description="Event payload")
    target_url: str = Field(..., max_length=500, description="URL to send the webhook to")


class WebhookEventUpdate(BaseModel):
    """
    Schema for updating a webhook event.
    """
    status: Optional[str] = None
    retry_count: Optional[int] = None
    last_attempt: Optional[datetime] = None
    next_retry: Optional[datetime] = None
    response_code: Optional[int] = None
    response_body: Optional[str] = None
    error_message: Optional[str] = None


class WebhookEventResponse(BaseModel):
    """
    Schema for webhook event response.
    """
    id: int
    event_type: str
    payload: Dict[str, Any]
    status: str
    target_url: str
    retry_count: int
    last_attempt: Optional[datetime]
    next_retry: Optional[datetime]
    response_code: Optional[int]
    response_body: Optional[str]
    error_message: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True
