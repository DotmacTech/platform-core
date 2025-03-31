"""
Models for the logging module.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import JSON, DateTime, Integer, String, Text, Index, Column
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base_model import BaseModel as DBBaseModel


class LogLevel(str, Enum):
    """
    Enum for log levels.
    """
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogEntry(DBBaseModel):
    """
    Model for storing structured log entries in the database.
    """

    __tablename__ = "log_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    level: Mapped[str] = mapped_column(String(10), index=True)  # INFO, WARNING, ERROR, DEBUG, etc.
    source: Mapped[str] = mapped_column(String(100), index=True)  # Service or component name
    message: Mapped[str] = mapped_column(Text)
    context: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)  # Additional context data
    trace_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)  # For distributed tracing
    span_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # For distributed tracing
    user_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)  # User ID if applicable
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # Client IP address if applicable

    # Create indexes for common query patterns
    __table_args__ = (
        Index('ix_log_entries_level_created_at', 'level', 'created_at'),
        Index('ix_log_entries_source_created_at', 'source', 'created_at'),
    )


class LogEntryCreate(BaseModel):
    """
    Schema for creating a new log entry.
    """

    level: LogLevel
    message: str
    source: str = Field(..., max_length=100)
    context: Optional[Dict[str, Any]] = None
    trace_id: Optional[str] = Field(
        None, description="Trace ID for distributed tracing"
    )
    span_id: Optional[str] = Field(None, description="Span ID for distributed tracing")
    user_id: Optional[str] = Field(None, description="User ID if applicable")
    ip_address: Optional[str] = Field(
        None, description="Client IP address if applicable"
    )


class LogEntryResponse(BaseModel):
    """
    Schema for log entry response.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    level: LogLevel
    message: str
    source: str
    context: Optional[Dict[str, Any]]
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    user_id: Optional[str] = None
    ip_address: Optional[str] = None


class LogQueryParams(BaseModel):
    """
    Schema for log query parameters.
    """

    level: Optional[str] = None
    source: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    trace_id: Optional[str] = None
    user_id: Optional[str] = None
    limit: int = 100
    offset: int = 0
