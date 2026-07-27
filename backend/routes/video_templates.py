"""
AUTOMA Routes - VideoTemplates.

API route definitions for templates operations.
"""

from fastapi import APIRouter, Depends, Query, status, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
import json
import shutil
from pathlib import Path
from utils.template_packager import export_template_to_file, import_template_from_file
from config import settings

from database import get_db
from controllers.video_template_controller import VideoTemplateController
from schemas.video_template import (
    VideoTemplateCreate,
    VideoTemplateResponse,
    VideoTemplateUpdate,
    VideoTemplateListResponse,
)

router = APIRouter(prefix="/video-templates", tags=["templates"])


@router.post("", response_model=VideoTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    data: VideoTemplateCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new processing template."""
    controller = VideoTemplateController(db)
    return await controller.create(data)


@router.get("", response_model=VideoTemplateListResponse)
async def list_templates(
    query: str | None = Query(None),
    category: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    db: AsyncSession = Depends(get_db),
):
    """Search and list templates."""
    controller = VideoTemplateController(db)
    return await controller.list_all(query=query, category=category, skip=skip, limit=limit)


@router.get("/{template_id}", response_model=VideoTemplateResponse)
async def get_template(
    template_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a template by ID."""
    controller = VideoTemplateController(db)
    return await controller.get(template_id)


@router.put("/{template_id}", response_model=VideoTemplateResponse)
async def update_template(
    template_id: str,
    data: VideoTemplateUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a template by ID."""
    controller = VideoTemplateController(db)
    return await controller.update(template_id, data)


@router.delete("/{template_id}")
async def delete_template(
    template_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a template by ID."""
    controller = VideoTemplateController(db)
    return await controller.delete(template_id)


@router.post("/{template_id}/duplicate", response_model=VideoTemplateResponse)
async def duplicate_template(
    template_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Clone an existing template."""
    controller = VideoTemplateController(db)
    return await controller.duplicate(template_id)


@router.post("/{template_id}/restore/{version}", response_model=VideoTemplateResponse)
async def restore_template_version(
    template_id: str,
    version: int,
    db: AsyncSession = Depends(get_db),
):
    """Revert template to a previous saved version from history."""
    controller = VideoTemplateController(db)
    return await controller.restore_version(template_id, version)


@router.get("/{template_id}/export")
async def export_template(
    template_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Export a template to a .automa_template file."""
    controller = VideoTemplateController(db)
    template = await controller.get(template_id)
    template_data = {
        "name": template.name,
        "description": template.description,
        "category": template.category,
        "pipeline_config": template.pipeline_config
    }
    
    file_path = export_template_to_file(template_data)
    return FileResponse(path=file_path, media_type='application/octet-stream', filename=file_path.name)

@router.post("/import", response_model=VideoTemplateResponse)
async def import_template(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Import a template from a .automa_template file."""
    temp_dir = settings.TEMP_DIR / "uploads"
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_file = temp_dir / file.filename
    
    try:
        with open(temp_file, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        template_data = import_template_from_file(temp_file)
        
        create_data = VideoTemplateCreate(
            name=f"{template_data.get('name', 'Imported')} (Imported)",
            description=template_data.get("description"),
            category=template_data.get("category"),
            pipeline_config=template_data.get("pipeline_config", [])
        )
        
        controller = VideoTemplateController(db)
        return await controller.create(create_data)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        if temp_file.exists():
            temp_file.unlink()
