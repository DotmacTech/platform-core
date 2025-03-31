"""
Tests for the logging module.
"""

import json
from datetime import datetime, timedelta

import pytest

from app.core.settings import get_settings
from app.modules.logging.models import LogEntry, LogEntryCreate, LogLevel, LogQueryParams
from app.modules.logging.service import LoggingService


@pytest.mark.asyncio
async def test_create_log_entry(client, db_session):
    """Test creating a log entry."""
    # Create log entry data
    log_data = {
        "level": "INFO",
        "message": "Test log message",
        "source": "test_service",
        "context": {"test_key": "test_value"},
    }

    # Send request
    response = client.post(f"{get_settings().API_V1_STR}/logs/", json=log_data)

    # Check response
    assert response.status_code == 201
    data = response.json()
    assert data["level"] == log_data["level"]
    assert data["message"] == log_data["message"]
    assert data["source"] == log_data["source"]
    assert data["context"] == log_data["context"]

    # Check database
    db_log = db_session.query(LogEntry).filter(LogEntry.id == data["id"]).first()
    assert db_log is not None
    assert db_log.level == log_data["level"]
    assert db_log.message == log_data["message"]


@pytest.mark.asyncio
async def test_get_log_entries(client, db_session):
    """Test getting log entries."""
    # Create test log entries
    for i in range(3):
        log_entry = LogEntry(
            level=LogLevel.INFO.value,
            message=f"Test message {i}",
            source="test_service",
            context={"test_key": f"test_value_{i}"},
        )
        db_session.add(log_entry)
    db_session.commit()

    # Send request
    response = client.get(f"{get_settings().API_V1_STR}/logs/")

    # Check response
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["source"] == "test_service"


@pytest.mark.asyncio
async def test_get_log_entries_with_filters(client, db_session):
    """Test getting log entries with filters."""
    # Create test log entries with different levels
    levels = [LogLevel.INFO.value, LogLevel.WARNING.value, LogLevel.ERROR.value]
    for i, level in enumerate(levels):
        log_entry = LogEntry(
            level=level,
            message=f"Test message {i}",
            source="test_service",
            context={"test_key": f"test_value_{i}"},
        )
        db_session.add(log_entry)
    db_session.commit()

    # Send request with level filter
    response = client.get(f"{get_settings().API_V1_STR}/logs/?level=WARNING")

    # Check response
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["level"] == "WARNING"


@pytest.mark.asyncio
async def test_get_log_entries_with_time_range(client, db_session):
    """Test getting log entries within a time range."""
    # Create test log entry from yesterday
    yesterday = datetime.utcnow() - timedelta(days=1)
    old_log = LogEntry(
        level=LogLevel.INFO.value,
        message="Old log message",
        source="test_service",
        context={"test_key": "old_value"},
        created_at=yesterday,
    )
    db_session.add(old_log)

    # Create test log entry from today
    new_log = LogEntry(
        level=LogLevel.INFO.value,
        message="New log message",
        source="test_service",
        context={"test_key": "new_value"},
    )
    db_session.add(new_log)
    db_session.commit()

    # Send request with time range filter
    start_time = (datetime.utcnow() - timedelta(hours=1)).isoformat()
    response = client.get(f"{get_settings().API_V1_STR}/logs/?start_time={start_time}")

    # Check response
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["message"] == "New log message"


@pytest.mark.asyncio
async def test_export_logs(client, db_session):
    """Test exporting logs to JSON."""
    # Create test log entries
    for i in range(3):
        log_entry = LogEntry(
            level=LogLevel.INFO.value,
            message=f"Test message {i}",
            source="test_service",
            context={"test_key": f"test_value_{i}"},
        )
        db_session.add(log_entry)
    db_session.commit()

    # Send request
    response = client.get(f"{get_settings().API_V1_STR}/logs/export/json")

    # Check response
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert response.headers["Content-Disposition"].startswith("attachment")

    # Parse JSON data
    data = json.loads(response.content)
    assert len(data) == 3
    assert data[0]["source"] == "test_service"


@pytest.mark.asyncio
async def test_log_entry_service_methods(db_session):
    """Test LoggingService methods directly."""
    # Create log entry
    log_data = LogEntryCreate(
        level=LogLevel.INFO,
        message="Test message",
        source="test_service",
        context={"test_key": "test_value"},
    )
    log_entry = await LoggingService.create_log_entry(db_session, log_data)
    assert log_entry is not None
    assert log_entry.level == LogLevel.INFO.value

    # Get log entry by ID
    retrieved_log = await LoggingService.get_log_entry(db_session, log_entry.id)
    assert retrieved_log is not None
    assert retrieved_log.id == log_entry.id

    # Get log entries with filters
    query_params = LogQueryParams(
        level=LogLevel.INFO.value,
        source="test_service",
        limit=10,
        offset=0,
    )
    log_entries = await LoggingService.get_log_entries(db_session, query_params)
    assert len(log_entries) == 1
    assert log_entries[0].id == log_entry.id
