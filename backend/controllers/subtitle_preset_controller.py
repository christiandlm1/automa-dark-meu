"""
AUTOMA Controllers - Subtitle Preset Controller.
"""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.subtitle_preset import SubtitlePreset
from schemas.subtitle_preset import (
    SubtitlePresetCreate,
    SubtitlePresetUpdate,
    SubtitlePresetResponse,
)


class SubtitlePresetController:
    """Controller for subtitle preset CRUD."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_presets(self) -> list[SubtitlePresetResponse]:
        """List all subtitle presets."""
        stmt = select(SubtitlePreset).order_by(SubtitlePreset.created_at.desc())
        result = await self.session.execute(stmt)
        presets = result.scalars().all()
        return [SubtitlePresetResponse.model_validate(p) for p in presets]

    async def get_preset(self, preset_id: str) -> SubtitlePresetResponse:
        """Get a subtitle preset by ID."""
        preset = await self.session.get(SubtitlePreset, preset_id)
        if not preset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Preset de legenda não encontrado: {preset_id}",
            )
        return SubtitlePresetResponse.model_validate(preset)

    async def create_preset(self, data: SubtitlePresetCreate) -> SubtitlePresetResponse:
        """Create a new subtitle preset."""
        preset = SubtitlePreset(**data.model_dump())
        self.session.add(preset)
        await self.session.flush()
        return SubtitlePresetResponse.model_validate(preset)

    async def update_preset(self, preset_id: str, data: SubtitlePresetUpdate) -> SubtitlePresetResponse:
        """Update an existing subtitle preset."""
        preset = await self.session.get(SubtitlePreset, preset_id)
        if not preset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Preset de legenda não encontrado: {preset_id}",
            )

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(preset, key, value)
            
        await self.session.flush()
        return SubtitlePresetResponse.model_validate(preset)

    async def delete_preset(self, preset_id: str) -> None:
        """Delete a subtitle preset."""
        preset = await self.session.get(SubtitlePreset, preset_id)
        if not preset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Preset de legenda não encontrado: {preset_id}",
            )
        
        await self.session.delete(preset)
        await self.session.flush()
