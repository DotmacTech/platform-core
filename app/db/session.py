"""
Database session module.
"""

import os
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.settings import get_settings
from app.db.base_model import BaseModel as Base

settings = get_settings()

# Create SQLAlchemy engine
# Use test database URL if TESTING environment variable is set
database_url = settings.TEST_DATABASE_URL if os.getenv("TESTING") else settings.DATABASE_URL
engine = create_engine(
    str(database_url),
    json_serializer=lambda obj: json.dumps(obj, ensure_ascii=False),
    json_deserializer=lambda obj: json.loads(obj),
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency to get DB session
def get_db():
    """
    Get a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
