"""
AUTOMA Controllers - Export Profile Controller.

Handles HTTP requests and business logic for Export Profiles.
"""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from models.export_profile import ExportProfile
from schemas.export_profile import (
    ExportProfileCreate,
    ExportProfileUpdate,
    ExportProfileResponse,
    ExportProfileListResponse,
)


class ExportProfileController:
    """Controller for export profile CRUD."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_profiles(self) -> ExportProfileListResponse:
        """List all export profiles."""
        stmt = select(ExportProfile).order_by(ExportProfile.created_at.desc())
        result = await self.session.execute(stmt)
        profiles = result.scalars().all()
        
        return ExportProfileListResponse(
            profiles=[ExportProfileResponse.model_validate(p) for p in profiles],
            total=len(profiles),
        )

    async def get_profile(self, profile_id: str) -> ExportProfileResponse:
        """Get an export profile by ID."""
        profile = await self.session.get(ExportProfile, profile_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Perfil de exportação não encontrado: {profile_id}",
            )
        return ExportProfileResponse.model_validate(profile)

    async def create_profile(self, data: ExportProfileCreate) -> ExportProfileResponse:
        """Create a new export profile."""
        profile = ExportProfile(**data.model_dump())
        self.session.add(profile)
        await self.session.flush()
        return ExportProfileResponse.model_validate(profile)

    async def update_profile(self, profile_id: str, data: ExportProfileUpdate) -> ExportProfileResponse:
        """Update an existing export profile."""
        profile = await self.session.get(ExportProfile, profile_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Perfil de exportação não encontrado: {profile_id}",
            )

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(profile, key, value)
            
        await self.session.flush()
        return ExportProfileResponse.model_validate(profile)

    async def delete_profile(self, profile_id: str) -> None:
        """Delete an export profile."""
        profile = await self.session.get(ExportProfile, profile_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Perfil de exportação não encontrado: {profile_id}",
            )
        
        await self.session.delete(profile)
        await self.session.flush()

    async def seed_defaults(self) -> None:
        """Seed default profiles if they don't exist."""
        stmt = select(ExportProfile)
        result = await self.session.execute(stmt)
        existing = result.scalars().all()
        
        if existing:
            return
            
        defaults = [
            ExportProfile(
                name="Instagram Reels",
                resolution="1080x1920",
                fps=30.0,
                codec="h264",
                bitrate="5M",
                is_custom=False
            ),
            ExportProfile(
                name="TikTok",
                resolution="1080x1920",
                fps=60.0,
                codec="h264",
                bitrate="8M",
                is_custom=False
            ),
            ExportProfile(
                name="YouTube Shorts",
                resolution="1080x1920",
                fps=60.0,
                codec="h264",
                bitrate="10M",
                is_custom=False
            )
        ]
        
        for profile in defaults:
            self.session.add(profile)
            
        await self.session.commit()
