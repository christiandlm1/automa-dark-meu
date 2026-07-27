"""
AUTOMA Models - Job.

SQLAlchemy 2.0 ORM model for the ``jobs`` table.
Tracks the state, progress, speed and execution times of editing queue tasks.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Text, Float, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Job(Base):
    """Represents a video processing task inside the queue."""

    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    video_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False
    )
    template_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("video_templates.id", ondelete="SET NULL"), nullable=True
    )
    export_profile_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("export_profiles.id", ondelete="SET NULL"), nullable=True
    )
    
    # Status options: "pending" (Fila), "running" (Executando), "completed" (Concluído),
    # "failed" (Erro), "cancelled" (Cancelado), "paused" (Pausado)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    
    progress: Mapped[float] = mapped_column(Float, default=0.0)  # Percentage (0.0 to 100.0)
    speed: Mapped[float] = mapped_column(Float, default=0.0)  # Processing speed multiplier (e.g. 2.5x)
    
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    estimated_time: Mapped[float | None] = mapped_column(Float, nullable=True)  # Remaining seconds
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Priority and Retry (Module 08)
    priority: Mapped[int] = mapped_column(Integer, default=0)  # Higher is higher priority
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="jobs")  # noqa: F821
    video: Mapped["Video"] = relationship("Video")  # noqa: F821
    template: Mapped["VideoTemplate | None"] = relationship("VideoTemplate", back_populates="jobs")  # noqa: F821
    export_profile: Mapped["ExportProfile | None"] = relationship("ExportProfile", back_populates="jobs")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Job id={self.id!r} status={self.status!r} progress={self.progress!r}>"
