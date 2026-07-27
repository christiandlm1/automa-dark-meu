"""
AUTOMA Processing Engine - Template Manager.

Handles CRUD operations, search, and duplication/cloning of VideoTemplates.
Decoupled and integrated with the EventBus and LogService.
"""

import logging
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from models.video_template import VideoTemplate
from repositories.video_template_repository import VideoTemplateRepository
from schemas.video_template import VideoTemplateCreate, VideoTemplateUpdate
from services.log_service import LogService
from utils.event_bus import (
    event_bus,
    EVENT_TEMPLATE_CREATED,
    EVENT_TEMPLATE_UPDATED,
)

logger = logging.getLogger("automa.processing.templates")


class TemplateManager:
    """Manages the lifecycle of VideoTemplates."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = VideoTemplateRepository(session)
        self.log_service = LogService(session)

    async def create_template(self, data: VideoTemplateCreate) -> VideoTemplate:
        """Create a new template and trigger the TemplateCreated event."""
        template = VideoTemplate(
            name=data.name,
            description=data.description,
            category=data.category,
            pipeline_config=data.pipeline_config,
        )
        created = await self.repo.create(template)
        await self.session.commit()
        
        # Write audit log
        await self.log_service.log_info(
            action="template_create",
            message=f"Template criado: {created.name} (Categoria: {created.category or 'Nenhuma'})",
            details={"template_id": created.id, "pipeline_config": created.pipeline_config},
        )
        
        # Publish event
        await event_bus.publish(EVENT_TEMPLATE_CREATED, created)
        
        return created

    async def get_template(self, template_id: str) -> VideoTemplate | None:
        """Retrieve a template by ID."""
        return await self.repo.get_by_id(template_id)

    async def list_templates(
        self,
        query: str | None = None,
        category: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[Sequence[VideoTemplate], int]:
        """Search and list templates."""
        templates = await self.repo.search(query=query, category=category, skip=skip, limit=limit)
        total = len(templates) if query or category else await self.repo.count()
        return templates, total

    async def update_template(self, template_id: str, data: VideoTemplateUpdate) -> VideoTemplate | None:
        """Update a template, archiving previous versions to history, and trigger TemplateUpdated."""
        template = await self.repo.get_by_id(template_id)
        if not template:
            return None
            
        update_data = data.model_dump(exclude_unset=True)
        
        # Archive current config to history if config is changing
        if "pipeline_config" in update_data and update_data["pipeline_config"] != template.pipeline_config:
            import datetime
            from sqlalchemy.orm.attributes import flag_modified
            
            new_ver = len(template.versions_history) + 1
            up_at = template.updated_at or template.created_at
            up_at_str = up_at.isoformat() if up_at else datetime.datetime.now(datetime.timezone.utc).isoformat()
            
            snapshot = {
                "version": new_ver,
                "updated_at": up_at_str,
                "pipeline_config": template.pipeline_config
            }
            
            history_list = list(template.versions_history)
            history_list.append(snapshot)
            template.versions_history = history_list
            flag_modified(template, "versions_history")
            
        updated = await self.repo.update(template, update_data)
        await self.session.commit()
        
        # Write audit log
        await self.log_service.log_info(
            action="template_update",
            message=f"Template atualizado: {updated.name}",
            details={"template_id": updated.id, "updates": update_data},
        )
        
        # Publish event
        await event_bus.publish(EVENT_TEMPLATE_UPDATED, updated)
        
        return updated

    async def restore_template_version(self, template_id: str, version_num: int) -> VideoTemplate | None:
        """Revert the pipeline config of a template to a previous saved version."""
        template = await self.repo.get_by_id(template_id)
        if not template:
            return None
            
        target_snapshot = None
        for snapshot in template.versions_history:
            if snapshot.get("version") == version_num:
                target_snapshot = snapshot
                break
                
        if not target_snapshot:
            logger.warning(f"Version {version_num} not found in template {template_id} history.")
            return None
            
        # Save current state before restoring
        import datetime
        from sqlalchemy.orm.attributes import flag_modified
        current_ver = len(template.versions_history) + 1
        up_at = template.updated_at or template.created_at
        up_at_str = up_at.isoformat() if up_at else datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        current_snapshot = {
            "version": current_ver,
            "updated_at": up_at_str,
            "pipeline_config": template.pipeline_config
        }
        
        history_list = list(template.versions_history)
        history_list.append(current_snapshot)
        template.versions_history = history_list
        flag_modified(template, "versions_history")
        
        # Restore pipeline config from version
        template.pipeline_config = target_snapshot["pipeline_config"]
        flag_modified(template, "pipeline_config")
        
        await self.session.commit()
        
        # Write audit log
        await self.log_service.log_info(
            action="template_restore_version",
            message=f"Template {template.name} restaurado para versão {version_num}",
            details={"template_id": template.id, "restored_version": version_num},
        )
        
        return template

    async def delete_template(self, template_id: str) -> bool:
        """Delete a template by ID."""
        template = await self.repo.get_by_id(template_id)
        if not template:
            return False
            
        name = template.name
        deleted = await self.repo.delete_by_id(template_id)
        await self.session.commit()
        
        if deleted:
            # Write audit log
            await self.log_service.log_info(
                action="template_delete",
                message=f"Template removido: {name}",
                details={"template_id": template_id},
            )
        return deleted

    async def duplicate_template(self, template_id: str) -> VideoTemplate | None:
        """Clone an existing template, renaming it with ' (Cópia)' suffix."""
        source = await self.repo.get_by_id(template_id)
        if not source:
            return None
            
        cloned_data = VideoTemplateCreate(
            name=f"{source.name} (Cópia)",
            description=source.description,
            category=source.category,
            pipeline_config=source.pipeline_config,
        )
        
        cloned = await self.create_template(cloned_data)
        logger.info(f"Cloned template {template_id} to new template {cloned.id}")
        return cloned
