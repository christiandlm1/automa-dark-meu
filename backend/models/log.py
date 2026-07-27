"""
AUTOMA Models - Log.

SQLAlchemy 2.0 ORM model for the ``logs`` table.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Log(Base):
    """Audit log entry recording a user or system action."""

    __tablename__ = "logs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    project_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True
    )
    level: Mapped[str] = mapped_column(String(20), nullable=False, default="info")
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    project: Mapped["Project | None"] = relationship(  # noqa: F821
        "Project", back_populates="logs"
    )

    def __repr__(self) -> str:
        return f"<Log id={self.id!r} action={self.action!r}>"
