"""
Test configuration and fixtures.
"""

import asyncio
import json
import os
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.settings import get_settings
from app.db.base_model import BaseModel
from app.db.session import Base, get_db
from app.main import app

# Import all models to ensure they are registered with Base.metadata
from app.modules.audit.models import AuditLog  # noqa: F401
from app.modules.config.models import ConfigScope  # noqa: F401
from app.modules.feature_flags.models import FeatureFlag  # noqa: F401
from app.modules.logging.models import LogEntry  # noqa: F401
from app.modules.notifications.models import Notification  # noqa: F401
from app.modules.webhooks.models import WebhookEvent  # noqa: F401

# Set TESTING environment variable
os.environ["TESTING"] = "1"

settings = get_settings()

# Enable SQLite foreign key support
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# Create test engine with SQLite
engine = create_engine(
    settings.TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    json_serializer=lambda obj: json.dumps(obj, ensure_ascii=False),
    json_deserializer=lambda obj: json.loads(obj),
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session() -> Generator:
    """Create a fresh database session for each test."""
    # Drop all tables
    Base.metadata.drop_all(bind=engine)
    # Create all tables
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after the test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_app() -> FastAPI:
    """Create a test instance of the FastAPI application."""
    return app


@pytest.fixture(scope="function")
def client(test_app: FastAPI, db_session: Session) -> Generator:
    """Create a test client with a fresh database session."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    test_app.dependency_overrides = {}
    test_app.dependency_overrides[get_db] = override_get_db
    with TestClient(test_app) as test_client:
        yield test_client


# Add pytest-asyncio mark to all async tests
def pytest_collection_modifyitems(items):
    """Add pytest.mark.asyncio to all async test functions."""
    for item in items:
        if item.get_closest_marker("asyncio") is None:
            item.add_marker(pytest.mark.asyncio)
