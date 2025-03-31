from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field
from sqlalchemy import ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_model import BaseModel as DBBaseModel


class ConfigScope(DBBaseModel):
    """
    Configuration scope model (e.g., 'auth', 'billing').
    """
    __tablename__ = "configscope"

    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationship - Mapped[List[...]] is standard for one-to-many
    configs: Mapped[List["ConfigItem"]] = relationship(
        "ConfigItem", back_populates="scope", cascade="all, delete-orphan"
    )


class ConfigItem(DBBaseModel):
    """
    Configuration item model.
    """
    __tablename__ = "configitem"

    key: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_secret: Mapped[bool] = mapped_column(Integer, default=0, nullable=False)
    scope_id: Mapped[int] = mapped_column(ForeignKey("configscope.id"), nullable=False)
    
    # Relationships
    scope: Mapped["ConfigScope"] = relationship("ConfigScope", back_populates="configs")
    history: Mapped[List["ConfigHistory"]] = relationship(
        "ConfigHistory", back_populates="config_item", cascade="all, delete-orphan"
    )

    __table_args__ = (UniqueConstraint("scope_id", "key", name="uix_config_scope_key"),)


class ConfigHistory(DBBaseModel):
    """
    Configuration history model for tracking changes.
    """
    __tablename__ = "confighistory"

    value: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    changed_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    config_id: Mapped[int] = mapped_column(ForeignKey("configitem.id"), nullable=False)
    
    # Relationship
    config_item: Mapped["ConfigItem"] = relationship("ConfigItem", back_populates="history")


# Pydantic models for API
class ConfigScopeCreate(BaseModel):
    """
    Schema for creating a config scope.
    """
    name: str
    description: Optional[str] = None


class ConfigScopeUpdate(BaseModel):
    """
    Schema for updating a config scope.
    """
    name: Optional[str] = None
    description: Optional[str] = None


class ConfigScopeResponse(BaseModel):
    """
    Schema for config scope response.
    """
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ConfigItemCreate(BaseModel):
    """
    Schema for creating a config item.
    """
    key: str = Field(..., max_length=255, description="Name/key of the config item")
    value: str
    description: Optional[str] = None
    is_secret: bool = False


class ConfigItemUpdate(BaseModel):
    """
    Schema for updating a config item.
    """
    value: str
    description: Optional[str] = None
    is_secret: Optional[bool] = None


class ConfigItemResponse(BaseModel):
    """
    Schema for config item response.
    """
    id: int
    key: str
    value: str
    description: Optional[str] = None
    version: int
    is_secret: bool
    scope_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ConfigHistoryResponse(BaseModel):
    """
    Schema for config history response.
    """
    id: int
    value: str
    version: int
    changed_by: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True
