"""
AUTOMA Controllers - History Controller.

Delegates request/response validation for execution logs history.
"""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from processing.engine.history_manager import history_manager
from schemas.history import HistoryResponse, HistoryListResponse


class HistoryController:
    """Handles HTTP request translation for finalized jobs history logs."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_by_project(
        self,
        project_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> HistoryListResponse:
        """Fetch paginated completed/failed executions history for a project."""
        items, total = await history_manager.get_project_history(
            self.session, project_id, skip=skip, limit=limit
        )
        return HistoryListResponse(
            history=[HistoryResponse.model_validate(h) for h in items],
            total=total,
        )

    async def clear(self, project_id: str) -> dict[str, str]:
        """Erase all history logs for a project."""
        await history_manager.clear_history(self.session, project_id)
        return {"detail": "Histórico limpo com sucesso"}
