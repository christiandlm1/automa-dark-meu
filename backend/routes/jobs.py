"""
AUTOMA Routes - Jobs.

API route definitions for processing jobs queue management.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from controllers.job_controller import JobController
from schemas.job import JobCreate, JobResponse, JobListResponse, JobPreviewRequest

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
@router.post("/enqueue", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def enqueue_job(
    data: JobCreate,
    db: AsyncSession = Depends(get_db),
):
    """Enqueue a video for rendering under a specific template."""
    controller = JobController(db)
    return await controller.enqueue(data)


@router.post("/preview")
async def render_preview_endpoint(
    data: JobPreviewRequest,
    db: AsyncSession = Depends(get_db),
):
    """Execute a short-duration preview render of the pipeline and return the static file URL."""
    controller = JobController(db)
    return await controller.render_preview(data, db)


@router.get("/project/{project_id}", response_model=JobListResponse)
async def list_jobs_by_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """List queue jobs inside a project."""
    controller = JobController(db)
    return await controller.list_by_project(project_id)


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get job details by ID."""
    controller = JobController(db)
    return await controller.get(job_id)


@router.post("/{job_id}/pause", response_model=JobResponse)
async def pause_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Pause an active or pending job."""
    controller = JobController(db)
    return await controller.pause(job_id)


@router.post("/{job_id}/resume", response_model=JobResponse)
async def resume_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Resume a paused job."""
    controller = JobController(db)
    return await controller.resume(job_id)


@router.delete("/project/{project_id}/queue")
async def delete_queue(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Remove pending/paused/etc jobs from queue."""
    controller = JobController(db)
    return await controller.delete_queue(project_id)


@router.post("/{job_id}/cancel", response_model=JobResponse)
async def cancel_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Cancel a job from queue execution."""
    controller = JobController(db)
    return await controller.cancel(job_id)


@router.post("/{job_id}/reprocess", response_model=JobResponse)
async def reprocess_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Reset and re-run a processing job."""
    controller = JobController(db)
    return await controller.reprocess(job_id)


@router.get("/project/{project_id}/stats")
async def get_job_stats(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get aggregate queue metrics and hardware priority configurations."""
    controller = JobController(db)
    return await controller.get_stats(project_id, db)
