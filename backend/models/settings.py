"""
AUTOMA Models - Setting.

SQLAlchemy 2.0 ORM model for the ``settings`` table.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Setting(Base):
    """Key-value application settings with type and category metadata."""

    __tablename__ = "settings"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    value: Mapped[str] = mapped_column(String(500), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False, default="string")
    category: Mapped[str] = mapped_column(String(50), nullable=False, default="general")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<Setting key={self.key!r} value={self.value!r}>"
