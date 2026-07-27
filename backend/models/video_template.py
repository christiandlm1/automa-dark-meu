"""
AUTOMA Models - VideoTemplate.

SQLAlchemy 2.0 ORM model for the ``video_templates`` table.
Stores name, category, and a structured pipeline config JSON.
"""

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import String, Text, DateTime, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class VideoTemplate(Base):
    """Represents a reusable processing template configured as a pipeline of nodes."""

    __tablename__ = "video_templates"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    # Store the pipeline node-based configuration as JSON.
    # Format: [{"type": "crop", "config": {...}}, ...]
    pipeline_config: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    
    # Store version history of this template
    # Format: [{"version": 1, "updated_at": "...", "pipeline_config": [...]}, ...]
    versions_history: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    jobs: Mapped[list["Job"]] = relationship(  # noqa: F821
        "Job", back_populates="template", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<VideoTemplate id={self.id!r} name={self.name!r}>"
