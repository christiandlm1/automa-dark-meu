import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from database import Base

class SubtitlePreset(Base):
    __tablename__ = "subtitle_presets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String, nullable=False)
    
    font_name: Mapped[str] = mapped_column(String, nullable=False, default="Roboto")
    font_size: Mapped[int] = mapped_column(Integer, nullable=False, default=48)
    primary_color: Mapped[str] = mapped_column(String, nullable=False, default="#FFFFFF")
    outline_color: Mapped[str] = mapped_column(String, nullable=False, default="#000000")
    back_color: Mapped[str] = mapped_column(String, nullable=False, default="#00000080")
    margin_v: Mapped[int] = mapped_column(Integer, nullable=False, default=20)
    margin_l: Mapped[int] = mapped_column(Integer, nullable=False, default=20)
    margin_r: Mapped[int] = mapped_column(Integer, nullable=False, default=20)
    
    max_lines: Mapped[int] = mapped_column(Integer, nullable=False, default=2)
    uppercase: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    word_wrap: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    alignment: Mapped[str] = mapped_column(String, nullable=False, default="Center")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
