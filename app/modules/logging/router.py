"""
Router for the logging module.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.logging.models import LogEntryCreate, LogEntryResponse, LogQueryParams
from app.modules.logging.service import LoggingService
from app.utils.common import parse_datetime

router = APIRouter()


@router.post("/", response_model=LogEntryResponse, status_code=201)
async def create_log_entry(log_entry: LogEntryCreate, db: Session = Depends(get_db)) -> LogEntryResponse:
    """
    Create a new log entry.
    """
    return await LoggingService(db).create_log_entry(log_entry)


@router.get("/", response_model=List[LogEntryResponse])
async def get_log_entries(
    level: Optional[str] = Query(None, description="Filter by log level"),
    source: Optional[str] = Query(None, description="Filter by source name"),
    start_time: Optional[str] = Query(None, description="Start time (ISO format)"),
    end_time: Optional[str] = Query(None, description="End time (ISO format)"),
    trace_id: Optional[str] = Query(None, description="Filter by trace ID"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of logs to return"),
    offset: int = Query(0, ge=0, description="Number of logs to skip"),
    db: Session = Depends(get_db),
) -> List[LogEntryResponse]:
    """
    Get log entries with optional filtering.
    """
    # Parse datetime strings if provided
    parsed_start_time = parse_datetime(start_time) if start_time else None
    parsed_end_time = parse_datetime(end_time) if end_time else None

    # Create query params object
    query_params = LogQueryParams(
        level=level,
        source=source,
        start_time=parsed_start_time,
        end_time=parsed_end_time,
        trace_id=trace_id,
        user_id=user_id,
        limit=limit,
        offset=offset,
    )

    return await LoggingService(db).get_log_entries(query_params)


@router.get("/{log_id}", response_model=LogEntryResponse)
async def get_log_entry(log_id: int, db: Session = Depends(get_db)) -> LogEntryResponse:
    """
    Get a specific log entry by ID.
    """
    log_entry = await LoggingService(db).get_log_entry(log_id)
    if not log_entry:
        raise HTTPException(status_code=404, detail="Log entry not found")
    return log_entry


@router.get("/export/json")
async def export_logs_to_json(
    level: Optional[str] = Query(None, description="Filter by log level"),
    source: Optional[str] = Query(None, description="Filter by source name"),
    start_time: Optional[str] = Query(None, description="Start time (ISO format)"),
    end_time: Optional[str] = Query(None, description="End time (ISO format)"),
    trace_id: Optional[str] = Query(None, description="Filter by trace ID"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    limit: int = Query(1000, ge=1, le=10000, description="Maximum number of logs to export"),
    offset: int = Query(0, ge=0, description="Number of logs to skip"),
    db: Session = Depends(get_db),
) -> Response:
    """
    Export logs to JSON format.
    """
    # Parse datetime strings if provided
    parsed_start_time = parse_datetime(start_time) if start_time else None
    parsed_end_time = parse_datetime(end_time) if end_time else None

    # Create query params object
    query_params = LogQueryParams(
        level=level,
        source=source,
        start_time=parsed_start_time,
        end_time=parsed_end_time,
        trace_id=trace_id,
        user_id=user_id,
        limit=limit,
        offset=offset,
    )

    # Export logs to JSON
    json_data = await LoggingService(db).export_logs_to_json(query_params)

    # Return JSON response
    return Response(
        content=json_data,
        media_type="application/json",
        headers={"Content-Disposition": 'attachment; filename="logs.json"'},
    )


@router.get("/stats/summary")
async def get_log_statistics(
    start_time: Optional[str] = Query(None, description="Start time (ISO format)"),
    end_time: Optional[str] = Query(None, description="End time (ISO format)"),
    db: Session = Depends(get_db),
) -> dict:
    """
    Get statistics about log entries.
    """
    # Parse datetime strings if provided
    parsed_start_time = parse_datetime(start_time) if start_time else None
    parsed_end_time = parse_datetime(end_time) if end_time else None

    return await LoggingService(db).get_log_statistics(
        start_time=parsed_start_time, end_time=parsed_end_time
    )
