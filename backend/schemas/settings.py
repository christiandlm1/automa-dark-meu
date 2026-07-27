"""
AUTOMA Schemas - Settings.

Pydantic models for settings request/response validation.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class SettingCreate(BaseModel):
    """Schema for creating a setting."""

    key: str = Field(..., min_length=1, max_length=100)
    value: str = Field(..., max_length=500)
    type: str = Field("string", pattern=r"^(string|number|boolean)$")
    category: str = Field("general", pattern=r"^(general|performance|paths)$")


class SettingUpdate(BaseModel):
    """Schema for updating a setting value."""

    value: str = Field(..., max_length=500)
    type: str | None = Field(None, pattern=r"^(string|number|boolean)$")
    category: str | None = Field(None, pattern=r"^(general|performance|paths)$")


class SettingResponse(BaseModel):
    """Schema for setting responses."""

    id: str
    key: str
    value: str
    type: str
    category: str
    updated_at: datetime

    model_config = {"from_attributes": True}


class SettingListResponse(BaseModel):
    """Schema for listing all settings."""

    settings: list[SettingResponse]
    total: int
