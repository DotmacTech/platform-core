from datetime import datetime
from typing import Annotated

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class BaseModel(DeclarativeBase):
    """
    Base model for all SQLAlchemy models.
    """

    # Auto-generate tablename from class name
    # @declared_attr - no longer needed with Base
    # def __tablename__(cls) -> str:
    #     return cls.__name__.lower()

    # Primary key using Mapped and mapped_column
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Timestamps using Mapped and mapped_column with explicit DateTime type
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
