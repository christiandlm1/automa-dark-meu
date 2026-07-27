"""
AUTOMA Models - Hardware.

SQLAlchemy 2.0 ORM model for the ``hardware`` table.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Integer, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Hardware(Base):
    """Snapshot of the detected hardware configuration."""

    __tablename__ = "hardware"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    cpu_name: Mapped[str] = mapped_column(String(200), nullable=False)
    cpu_cores: Mapped[int] = mapped_column(Integer, nullable=False)
    cpu_threads: Mapped[int] = mapped_column(Integer, nullable=False)
    ram_total_gb: Mapped[float] = mapped_column(Float, nullable=False)
    gpu_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    gpu_memory_gb: Mapped[float | None] = mapped_column(Float, nullable=True)
    os_name: Mapped[str] = mapped_column(String(100), nullable=False)
    os_version: Mapped[str] = mapped_column(String(100), nullable=False)
    detected_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self) -> str:
        return f"<Hardware id={self.id!r} cpu={self.cpu_name!r}>"
