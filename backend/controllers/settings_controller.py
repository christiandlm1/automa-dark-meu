"""
AUTOMA Controllers - Settings Controller.

Thin controller that delegates to SettingsService.
"""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.settings import (
    SettingCreate,
    SettingListResponse,
    SettingResponse,
    SettingUpdate,
)
from services.settings_service import SettingsService


class SettingsController:
    """Handles HTTP request/response translation for settings endpoints."""

    def __init__(self, session: AsyncSession) -> None:
        self.service = SettingsService(session)

    async def create(self, data: SettingCreate) -> SettingResponse:
        """Create or upsert a setting."""
        setting = await self.service.create_setting(data)
        return SettingResponse.model_validate(setting)

    async def get(self, setting_id: str) -> SettingResponse:
        """Get a setting by ID."""
        setting = await self.service.get_setting(setting_id)
        if not setting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Setting not found: {setting_id}",
            )
        return SettingResponse.model_validate(setting)

    async def get_by_key(self, key: str) -> SettingResponse:
        """Get a setting by its key."""
        setting = await self.service.get_by_key(key)
        if not setting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Setting not found for key: {key}",
            )
        return SettingResponse.model_validate(setting)

    async def list_all(
        self, category: str | None = None
    ) -> SettingListResponse:
        """List all settings, optionally by category."""
        settings_list, total = await self.service.list_settings(category=category)
        return SettingListResponse(
            settings=[SettingResponse.model_validate(s) for s in settings_list],
            total=total,
        )

    async def update(
        self, setting_id: str, data: SettingUpdate
    ) -> SettingResponse:
        """Update a setting by ID."""
        setting = await self.service.update_setting(setting_id, data)
        if not setting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Setting not found: {setting_id}",
            )
        return SettingResponse.model_validate(setting)

    async def update_by_key(
        self, key: str, data: SettingUpdate
    ) -> SettingResponse:
        """Update a setting by key."""
        setting = await self.service.update_by_key(key, data)
        if not setting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Setting not found for key: {key}",
            )
        return SettingResponse.model_validate(setting)

    async def delete(self, setting_id: str) -> dict[str, str]:
        """Delete a setting."""
        success = await self.service.delete_setting(setting_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Setting not found: {setting_id}",
            )
        return {"detail": "Setting deleted successfully"}
