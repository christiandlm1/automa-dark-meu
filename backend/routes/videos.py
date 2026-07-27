"""
AUTOMA Routes - Videos
API route definitions for video operations.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from controllers.video_controller import VideoController
from schemas.video import (
    VideoImportRequest,
    VideoListResponse,
    VideoResponse,
    VideoUpdate,
)

from fastapi import APIRouter, Depends, Query, UploadFile, File, Form, HTTPException
import shutil
from pathlib import Path

router = APIRouter(prefix="/videos", tags=["videos"])


@router.post("/import", response_model=list[VideoResponse])
async def import_videos(
    data: VideoImportRequest,
    db: AsyncSession = Depends(get_db),
):
    """Import video files/folders to a project."""
    controller = VideoController(db)
    return await controller.import_videos(data)


from services.project_service import ProjectService


@router.post("/upload", response_model=list[VideoResponse])
async def upload_videos(
    project_id: str = Form(...),
    files: list[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Upload video files directly to a project folder (Web Browser mode)."""
    project_service = ProjectService(db)
    project = await project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    target_dir = Path(project.path) / "videos"
    target_dir.mkdir(parents=True, exist_ok=True)

    saved_paths = []
    for file in files:
        if not file.filename:
            continue
        file_path = target_dir / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        saved_paths.append(str(file_path))

    controller = VideoController(db)
    import_data = VideoImportRequest(project_id=project_id, file_paths=saved_paths, copy_to_project=False)
    return await controller.import_videos(import_data)


@router.get("/project/{project_id}", response_model=VideoListResponse)
async def list_project_videos(
    project_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=5000),
    db: AsyncSession = Depends(get_db),
):
    """List all videos inside a project."""
    controller = VideoController(db)
    return await controller.list_by_project(project_id, skip=skip, limit=limit)


@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(
    video_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a single video by ID."""
    controller = VideoController(db)
    return await controller.get(video_id)


@router.put("/{video_id}", response_model=VideoResponse)
async def update_video(
    video_id: str,
    data: VideoUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update video metadata/notes."""
    controller = VideoController(db)
    return await controller.update(video_id, data)


@router.delete("/{video_id}")
async def delete_video(
    video_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a video from a project."""
    controller = VideoController(db)
    return await controller.delete(video_id)


@router.post("/{video_id}/scan", response_model=VideoResponse)
async def scan_video(
    video_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Scan or rescan a video's metadata and generate thumbnail."""
    controller = VideoController(db)
    return await controller.scan_video(video_id)


@router.post("/scan-pending", response_model=list[VideoResponse])
async def scan_pending(
    project_id: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Scan all pending videos in the queue."""
    controller = VideoController(db)
    return await controller.scan_pending(project_id)
