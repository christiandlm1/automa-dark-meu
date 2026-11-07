"""
AUTOMA Repositories - Asset Repository.

Database access layer for the ``assets`` table.
"""

from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.asset import Asset
from repositories.base_repository import BaseRepository


class AssetRepository(BaseRepository[Asset]):
    """Repository for Asset CRUD operations."""

    model = Asset

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get(self, asset_id: str) -> Asset | None:
        """Return an asset by its ID, or None (alias of ``get_by_id``)."""
        return await self.get_by_id(asset_id)

    async def get_by_hash(self, file_hash: str) -> Asset | None:
        """Return the asset with the given xxhash digest, or None."""
        result = await self.session.execute(select(Asset).where(Asset.file_hash == file_hash))
        return result.scalar_one_or_none()

    async def list_by_type(self, asset_type: str) -> Sequence[Asset]:
        """Return all assets of a given type."""
        result = await self.session.execute(select(Asset).where(Asset.type == asset_type))
        return result.scalars().all()
