"""
AUTOMA Models - Project.

SQLAlchemy 2.0 ORM model for the ``projects`` table.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Project(Base):
    """Represents a video project managed by AUTOMA."""

    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    path: Mapped[str] = mapped_column(String(500), nullable=False)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    database_path: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    status: Mapped[str] = mapped_column(String(20), default="active")

    # Relationships
    videos: Mapped[list["Video"]] = relationship(  # noqa: F821
        "Video", back_populates="project", cascade="all, delete-orphan"
    )
    logs: Mapped[list["Log"]] = relationship(  # noqa: F821
        "Log", back_populates="project", cascade="all, delete-orphan"
    )
    recent_entries: Mapped[list["RecentProject"]] = relationship(  # noqa: F821
        "RecentProject", back_populates="project", cascade="all, delete-orphan"
    )
    jobs: Mapped[list["Job"]] = relationship(  # noqa: F821
        "Job", back_populates="project", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Project id={self.id!r} name={self.name!r}>"
