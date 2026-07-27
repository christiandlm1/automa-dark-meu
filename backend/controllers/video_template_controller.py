"""
AUTOMA Controllers - VideoTemplate Controller.

Delegates request/response validation and CRUD actions to TemplateManager.
"""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from processing.templates.manager import TemplateManager
from schemas.video_template import (
    VideoTemplateCreate,
    VideoTemplateResponse,
    VideoTemplateUpdate,
    VideoTemplateListResponse,
)


class VideoTemplateController:
    """Handles HTTP translation for VideoTemplates endpoints."""

    def __init__(self, session: AsyncSession) -> None:
        self.manager = TemplateManager(session)

    async def create(self, data: VideoTemplateCreate) -> VideoTemplateResponse:
        """Create a new template."""
        template = await self.manager.create_template(data)
        return VideoTemplateResponse.model_validate(template)

    async def get(self, template_id: str) -> VideoTemplateResponse:
        """Get a template by ID."""
        template = await self.manager.get_template(template_id)
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template não encontrado: {template_id}",
            )
        return VideoTemplateResponse.model_validate(template)

    async def list_all(
        self,
        query: str | None = None,
        category: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> VideoTemplateListResponse:
        """Search and list templates."""
        templates, total = await self.manager.list_templates(
            query=query, category=category, skip=skip, limit=limit
        )
        return VideoTemplateListResponse(
            templates=[VideoTemplateResponse.model_validate(t) for t in templates],
            total=total,
        )

    async def update(self, template_id: str, data: VideoTemplateUpdate) -> VideoTemplateResponse:
        """Update an existing template."""
        template = await self.manager.update_template(template_id, data)
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template não encontrado: {template_id}",
            )
        return VideoTemplateResponse.model_validate(template)

    async def delete(self, template_id: str) -> dict[str, str]:
        """Delete a template by ID."""
        success = await self.manager.delete_template(template_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template não encontrado ou falha ao remover: {template_id}",
            )
        return {"detail": "Template removido com sucesso"}

    async def duplicate(self, template_id: str) -> VideoTemplateResponse:
        """Clone a template."""
        cloned = await self.manager.duplicate_template(template_id)
        if not cloned:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template de origem não encontrado: {template_id}",
            )
        return VideoTemplateResponse.model_validate(cloned)

    async def restore_version(self, template_id: str, version_num: int) -> VideoTemplateResponse:
        """Restore a template to a previous version."""
        template = await self.manager.restore_template_version(template_id, version_num)
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template {template_id} ou versão {version_num} não encontrados.",
            )
        return VideoTemplateResponse.model_validate(template)
