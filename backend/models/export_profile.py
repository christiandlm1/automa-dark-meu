"""
AUTOMA Models - Export Profile.

SQLAlchemy 2.0 ORM model for the ``export_profiles`` table.
Defines encoding and formatting settings used for exporting processed videos.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Integer, Float, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class ExportProfile(Base):
    """Represents a set of video export parameters."""

    __tablename__ = "export_profiles"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    resolution: Mapped[str | None] = mapped_column(String(50), nullable=True)  # e.g. "1920x1080"
    fps: Mapped[float | None] = mapped_column(Float, nullable=True)
    codec: Mapped[str | None] = mapped_column(String(50), nullable=True)
    bitrate: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_custom: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    jobs: Mapped[list["Job"]] = relationship("Job", back_populates="export_profile")  # noqa: F821

    def __repr__(self) -> str:
        return f"<ExportProfile id={self.id!r} name={self.name!r}>"
