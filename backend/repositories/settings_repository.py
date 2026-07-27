"""
AUTOMA Repositories - Settings Repository.

Database access layer for the ``settings`` table.
"""

from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.settings import Setting
from repositories.base_repository import BaseRepository


class SettingsRepository(BaseRepository[Setting]):
    """Repository for Setting CRUD and queries."""

    model = Setting

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_key(self, key: str) -> Setting | None:
        """Find a setting by its unique key."""
        stmt = select(Setting).where(Setting.key == key)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_category(self, category: str) -> Sequence[Setting]:
        """Return all settings in a given category."""
        stmt = (
            select(Setting)
            .where(Setting.category == category)
            .order_by(Setting.key)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def upsert(
        self,
        key: str,
        value: str,
        type_: str = "string",
        category: str = "general",
    ) -> Setting:
        """Insert or update a setting by key."""
        existing = await self.get_by_key(key)
        if existing:
            existing.value = value
            if type_:
                existing.type = type_
            if category:
                existing.category = category
            await self.session.flush()
            await self.session.refresh(existing)
            return existing

        setting = Setting(key=key, value=value, type=type_, category=category)
        self.session.add(setting)
        await self.session.flush()
        await self.session.refresh(setting)
        return setting
