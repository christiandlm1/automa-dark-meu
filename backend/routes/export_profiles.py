"""
AUTOMA Routes - Export Profiles.

FastAPI endpoints for export profiles.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from controllers.export_profile_controller import ExportProfileController
from schemas.export_profile import (
    ExportProfileCreate,
    ExportProfileUpdate,
    ExportProfileResponse,
    ExportProfileListResponse,
)

router = APIRouter(prefix="/export-profiles", tags=["Export Profiles"])


@router.get("", response_model=ExportProfileListResponse)
async def list_profiles(session: AsyncSession = Depends(get_db)):
    """List all export profiles."""
    controller = ExportProfileController(session)
    return await controller.list_profiles()


@router.get("/{profile_id}", response_model=ExportProfileResponse)
async def get_profile(
    profile_id: str, session: AsyncSession = Depends(get_db)
):
    """Get export profile by ID."""
    controller = ExportProfileController(session)
    return await controller.get_profile(profile_id)


@router.post("", response_model=ExportProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    data: ExportProfileCreate, session: AsyncSession = Depends(get_db)
):
    """Create a new export profile."""
    controller = ExportProfileController(session)
    return await controller.create_profile(data)


@router.patch("/{profile_id}", response_model=ExportProfileResponse)
async def update_profile(
    profile_id: str, data: ExportProfileUpdate, session: AsyncSession = Depends(get_db)
):
    """Update an export profile."""
    controller = ExportProfileController(session)
    return await controller.update_profile(profile_id, data)


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    profile_id: str, session: AsyncSession = Depends(get_db)
):
    """Delete an export profile."""
    controller = ExportProfileController(session)
    await controller.delete_profile(profile_id)


@router.post("/seed", status_code=status.HTTP_200_OK)
async def seed_defaults(session: AsyncSession = Depends(get_db)):
    """Seed default export profiles."""
    controller = ExportProfileController(session)
    await controller.seed_defaults()
    return {"status": "ok", "message": "Default profiles seeded"}
