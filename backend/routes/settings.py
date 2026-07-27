"""
AUTOMA Routes - Settings
API route definitions for settings operations.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path

from database import get_db
from controllers.settings_controller import SettingsController
from schemas.settings import (
    SettingCreate,
    SettingListResponse,
    SettingResponse,
    SettingUpdate,
)
from utils.maintenance import clear_cache, backup_database, generate_diagnostics
from fastapi.responses import FileResponse
from fastapi import HTTPException

router = APIRouter(prefix="/settings", tags=["settings"])


@router.post("", response_model=SettingResponse)
async def create_setting(
    data: SettingCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create or upsert a setting."""
    controller = SettingsController(db)
    return await controller.create(data)


@router.get("", response_model=SettingListResponse)
async def list_settings(
    category: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List all settings."""
    controller = SettingsController(db)
    return await controller.list_all(category=category)


@router.get("/key/{key}", response_model=SettingResponse)
async def get_setting_by_key(
    key: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a setting by its key."""
    controller = SettingsController(db)
    return await controller.get_by_key(key)


@router.get("/{setting_id}", response_model=SettingResponse)
async def get_setting(
    setting_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a setting by ID."""
    controller = SettingsController(db)
    return await controller.get(setting_id)


@router.put("/key/{key}", response_model=SettingResponse)
async def update_setting_by_key(
    key: str,
    data: SettingUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a setting value by key."""
    controller = SettingsController(db)
    return await controller.update_by_key(key, data)


@router.put("/{setting_id}", response_model=SettingResponse)
async def update_setting(
    setting_id: str,
    data: SettingUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a setting by ID."""
    controller = SettingsController(db)
    return await controller.update(setting_id, data)


@router.delete("/{setting_id}")
async def delete_setting(
    setting_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a setting."""
    controller = SettingsController(db)
    return await controller.delete(setting_id)

@router.post("/maintenance/clear_cache")
async def api_clear_cache():
    if clear_cache():
        return {"status": "success", "message": "Cache cleared."}
    raise HTTPException(status_code=500, detail="Failed to clear cache")

@router.post("/maintenance/backup_db")
async def api_backup_db():
    backup_path = backup_database()
    if backup_path:
        return {"status": "success", "backup_path": backup_path}
    raise HTTPException(status_code=500, detail="Failed to backup database")

@router.get("/maintenance/diagnostics")
async def api_diagnostics():
    zip_path = generate_diagnostics()
    if zip_path:
        return FileResponse(zip_path, media_type='application/zip', filename=Path(zip_path).name)
    raise HTTPException(status_code=500, detail="Failed to generate diagnostics")
