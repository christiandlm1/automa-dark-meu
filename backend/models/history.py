"""
AUTOMA Models - History.

SQLAlchemy 2.0 ORM model for the ``history`` table.
Stores detailed execution records, metadata, processing times and logs of processed jobs.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Text, Float, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class History(Base):
    """Represents a finalized processing job record."""

    __tablename__ = "history"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    
    # Store video metadata directly so the history persists even if the video is deleted.
    video_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    video_name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    template_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    template_name: Mapped[str] = mapped_column(String(255), default="Nenhum")
    
    processed_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    execution_time: Mapped[float] = mapped_column(Float, default=0.0)  # Total elapsed seconds
    
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # "completed", "failed"
    log: Mapped[str | None] = mapped_column(Text, nullable=True)
    exported_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    # Retry details (Module 08)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    attempts_details: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON with {time, reason, duration, attempt}

    
    # Telemetry and benchmarks data for MetricsEngine
    speed: Mapped[float] = mapped_column(Float, default=0.0)
    cpu_usage: Mapped[float] = mapped_column(Float, default=0.0)
    ram_usage: Mapped[float] = mapped_column(Float, default=0.0)
    gpu_usage: Mapped[float] = mapped_column(Float, default=0.0)

    # Relationships
    project: Mapped["Project"] = relationship("Project")  # noqa: F821

    def __repr__(self) -> str:
        return f"<History id={self.id!r} video_name={self.video_name!r} status={self.status!r}>"
