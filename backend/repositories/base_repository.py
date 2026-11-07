"""
AUTOMA Repositories - Base Repository.

Generic async CRUD repository that all entity-specific repositories extend.
Uses SQLAlchemy 2.0 ``select`` / ``delete`` style.
"""

from typing import Any, Generic, Sequence, Type, TypeVar

from sqlalchemy import func, select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """
    Generic async repository providing CRUD primitives.

    Subclasses set ``model`` to the concrete SQLAlchemy model class.
    """

    model: Type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # --- Create ---

    async def create(self, entity: "ModelT | dict") -> ModelT:
        """Add a new entity and flush to obtain defaults.

        Accepts either a model instance or a dict of column values.
        """
        if isinstance(entity, dict):
            entity = self.model(**entity)
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    # --- Read ---

    async def get_by_id(self, entity_id: str) -> ModelT | None:
        """Return a single entity by primary key, or None."""
        stmt = select(self.model).where(self.model.id == entity_id)  # type: ignore[attr-defined]
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        order_by: Any | None = None,
    ) -> Sequence[ModelT]:
        """Return a paginated list of entities."""
        stmt = select(self.model)
        if order_by is not None:
            stmt = stmt.order_by(order_by)
        stmt = stmt.offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count(self) -> int:
        """Return the total number of entities."""
        stmt = select(func.count()).select_from(self.model)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    # --- Update ---

    async def update(self, entity: ModelT, data: dict[str, Any]) -> ModelT:
        """Apply a dict of updates to an entity and flush."""
        for key, value in data.items():
            if hasattr(entity, key) and value is not None:
                setattr(entity, key, value)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    # --- Delete ---

    async def delete(self, entity: ModelT) -> None:
        """Delete a single entity."""
        await self.session.delete(entity)
        await self.session.flush()

    async def delete_by_id(self, entity_id: str) -> bool:
        """Delete by primary key.  Returns True if a row was deleted."""
        stmt = delete(self.model).where(self.model.id == entity_id)  # type: ignore[attr-defined]
        result = await self.session.execute(stmt)
        await self.session.flush()
        return (result.rowcount or 0) > 0
