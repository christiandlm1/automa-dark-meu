"""
AUTOMA Routes - Subtitle Presets
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from database import get_db
from controllers.subtitle_preset_controller import SubtitlePresetController
from schemas.subtitle_preset import (
    SubtitlePresetCreate,
    SubtitlePresetUpdate,
    SubtitlePresetResponse,
)

router = APIRouter(prefix="/subtitle-presets", tags=["Subtitle Presets"])


def get_controller(session: AsyncSession = Depends(get_db)) -> SubtitlePresetController:
    return SubtitlePresetController(session)


@router.get("", response_model=List[SubtitlePresetResponse])
async def list_presets(controller: SubtitlePresetController = Depends(get_controller)):
    """List all subtitle presets."""
    return await controller.list_presets()


@router.get("/{preset_id}", response_model=SubtitlePresetResponse)
async def get_preset(
    preset_id: str,
    controller: SubtitlePresetController = Depends(get_controller),
):
    """Get a specific subtitle preset."""
    return await controller.get_preset(preset_id)


@router.post("", response_model=SubtitlePresetResponse, status_code=status.HTTP_201_CREATED)
async def create_preset(
    data: SubtitlePresetCreate,
    controller: SubtitlePresetController = Depends(get_controller),
):
    """Create a new subtitle preset."""
    return await controller.create_preset(data)


@router.put("/{preset_id}", response_model=SubtitlePresetResponse)
async def update_preset(
    preset_id: str,
    data: SubtitlePresetUpdate,
    controller: SubtitlePresetController = Depends(get_controller),
):
    """Update a subtitle preset."""
    return await controller.update_preset(preset_id, data)


@router.delete("/{preset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_preset(
    preset_id: str,
    controller: SubtitlePresetController = Depends(get_controller),
):
    """Delete a subtitle preset."""
    await controller.delete_preset(preset_id)
