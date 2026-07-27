"""
AUTOMA Services - Settings Service.

Business logic for reading and writing application settings.
"""

from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from models.settings import Setting
from repositories.settings_repository import SettingsRepository
from schemas.settings import SettingCreate, SettingUpdate


class SettingsService:
    """Manages application-level key-value settings."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = SettingsRepository(session)

    async def get_setting(self, setting_id: str) -> Setting | None:
        """Retrieve a setting by ID."""
        return await self.repo.get_by_id(setting_id)

    async def get_by_key(self, key: str) -> Setting | None:
        """Retrieve a setting by its unique key."""
        return await self.repo.get_by_key(key)

    async def list_settings(
        self, category: str | None = None
    ) -> tuple[Sequence[Setting], int]:
        """
        List settings, optionally filtered by category.

        Returns:
            Tuple of (settings sequence, total count).
        """
        if category:
            items = await self.repo.get_by_category(category)
            return items, len(items)

        items = await self.repo.get_all(limit=500)
        total = await self.repo.count()
        return items, total

    async def create_setting(self, data: SettingCreate) -> Setting:
        """Create a new setting or update if the key already exists."""
        return await self.repo.upsert(
            key=data.key,
            value=data.value,
            type_=data.type,
            category=data.category,
        )

    async def update_setting(
        self, setting_id: str, data: SettingUpdate
    ) -> Setting | None:
        """Update a setting by ID."""
        setting = await self.repo.get_by_id(setting_id)
        if not setting:
            return None
        update_data = data.model_dump(exclude_unset=True)
        return await self.repo.update(setting, update_data)

    async def update_by_key(self, key: str, data: SettingUpdate) -> Setting | None:
        """Update a setting by key."""
        setting = await self.repo.get_by_key(key)
        if not setting:
            return None
        update_data = data.model_dump(exclude_unset=True)
        return await self.repo.update(setting, update_data)

    async def delete_setting(self, setting_id: str) -> bool:
        """Delete a setting by ID."""
        return await self.repo.delete_by_id(setting_id)

    async def seed_defaults(self) -> None:
        """
        Ensure default settings exist in the database.

        Called during application startup to populate initial values.
        """
        defaults: list[dict[str, str]] = [
            {
                "key": "theme",
                "value": "dark",
                "type": "string",
                "category": "general",
            },
            {
                "key": "language",
                "value": "pt-BR",
                "type": "string",
                "category": "general",
            },
            {
                "key": "thumbnail_quality",
                "value": "85",
                "type": "number",
                "category": "performance",
            },
            {
                "key": "auto_scan",
                "value": "true",
                "type": "boolean",
                "category": "performance",
            },
            {
                "key": "default_project_path",
                "value": "",
                "type": "string",
                "category": "paths",
            },
            {
                "key": "max_workers",
                "value": "4",
                "type": "number",
                "category": "performance",
            },
            {
                "key": "process_priority",
                "value": "Normal",
                "type": "string",
                "category": "performance",
            },
            {
                "key": "max_cpu_usage",
                "value": "80",
                "type": "number",
                "category": "performance",
            },
            {
                "key": "max_ram_usage",
                "value": "80",
                "type": "number",
                "category": "performance",
            },
            {
                "key": "max_gpu_usage",
                "value": "80",
                "type": "number",
                "category": "performance",
            },
            {
                "key": "first_run_completed",
                "value": "false",
                "type": "boolean",
                "category": "general",
            },
        ]

        for item in defaults:
            existing = await self.repo.get_by_key(item["key"])
            if not existing:
                await self.repo.upsert(
                    key=item["key"],
                    value=item["value"],
                    type_=item["type"],
                    category=item["category"],
                )
