"""
Service for the logging module.
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, desc
from sqlalchemy.orm import Session

from app.modules.logging.models import LogEntry, LogEntryCreate, LogQueryParams
from app.utils.common import json_serializer


class LoggingService:
    """
    Service for managing structured application logs.
    """

    @staticmethod
    async def create_log_entry(db: Session, log_entry: LogEntryCreate) -> LogEntry:
        """
        Create a new log entry.

        Args:
            db: Database session
            log_entry: Log entry data

        Returns:
            Created log entry
        """
        db_log_entry = LogEntry(
            level=log_entry.level,
            source=log_entry.source,
            message=log_entry.message,
            context=log_entry.context,
            trace_id=log_entry.trace_id,
            span_id=log_entry.span_id,
            user_id=log_entry.user_id,
        )
        db.add(db_log_entry)
        db.commit()
        db.refresh(db_log_entry)
        return db_log_entry

    @staticmethod
    async def get_log_entries(
        db: Session, query_params: LogQueryParams
    ) -> List[LogEntry]:
        """
        Get log entries with filtering.

        Args:
            db: Database session
            query_params: Query parameters for filtering

        Returns:
            List of log entries
        """
        query = db.query(LogEntry)

        if query_params.level:
            query = query.filter(LogEntry.level == query_params.level)
        if query_params.source:
            query = query.filter(LogEntry.source == query_params.source)
        if query_params.start_time:
            query = query.filter(LogEntry.created_at >= query_params.start_time)
        if query_params.end_time:
            query = query.filter(LogEntry.created_at <= query_params.end_time)
        if query_params.trace_id:
            query = query.filter(LogEntry.trace_id == query_params.trace_id)
        if query_params.user_id:
            query = query.filter(LogEntry.user_id == query_params.user_id)

        query = query.order_by(desc(LogEntry.created_at))
        query = query.offset(query_params.offset)
        query = query.limit(query_params.limit)

        return query.all()

    @staticmethod
    async def get_log_entry(db: Session, log_id: int) -> Optional[LogEntry]:
        """
        Get a specific log entry by ID.

        Args:
            db: Database session
            log_id: ID of the log entry

        Returns:
            Log entry if found, None otherwise
        """
        return db.query(LogEntry).filter(LogEntry.id == log_id).first()

    @staticmethod
    async def export_logs_to_json(
        db: Session, query_params: LogQueryParams
    ) -> str:
        """
        Export logs to JSON format.

        Args:
            db: Database session
            query_params: Query parameters for filtering

        Returns:
            JSON string containing log entries
        """
        logs = await LoggingService.get_log_entries(db, query_params)
        return json.dumps([{
            "id": log.id,
            "level": log.level,
            "source": log.source,
            "message": log.message,
            "context": log.context,
            "trace_id": log.trace_id,
            "span_id": log.span_id,
            "user_id": log.user_id,
            "created_at": log.created_at.isoformat(),
        } for log in logs], default=json_serializer)

    @staticmethod
    async def get_log_statistics(
        db: Session, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get statistics about log entries.

        Args:
            db: Database session
            start_time: Optional start time for filtering
            end_time: Optional end time for filtering

        Returns:
            Dictionary containing log statistics
        """
        query = db.query(LogEntry)

        if start_time:
            query = query.filter(LogEntry.created_at >= start_time)
        if end_time:
            query = query.filter(LogEntry.created_at <= end_time)

        total_count = query.count()
        level_counts = {
            level: query.filter(LogEntry.level == level).count()
            for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        }
        source_counts = {
            source[0]: count
            for source, count in (
                db.query(LogEntry.source, db.func.count())
                .group_by(LogEntry.source)
                .all()
            )
        }

        return {
            "total_count": total_count,
            "level_counts": level_counts,
            "source_counts": source_counts,
        }
