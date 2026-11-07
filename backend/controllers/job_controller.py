"""
AUTOMA Controllers - Job Controller.

Delegates request/response translation for processing queue and jobs operations.
"""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import hashlib
import json
from pathlib import Path

from config import settings
from processing.jobs.queue_manager import QueueManager
from processing.engine.processing_service import processing_service
from processing.pipeline.pipeline_manager import PipelineManager
from repositories.video_repository import VideoRepository
from repositories.video_template_repository import VideoTemplateRepository
from schemas.job import JobCreate, JobResponse, JobListResponse, JobPreviewRequest


class JobController:
    """Handles HTTP translation for queue jobs and engine execution metrics."""

    def __init__(self, session: AsyncSession) -> None:
        self.queue_manager = QueueManager(session)

    async def enqueue(self, data: JobCreate) -> JobResponse:
        """Enqueue a new video processing task."""
        project_id = data.project_id
        if not project_id:
            from repositories.video_repository import VideoRepository
            video = await VideoRepository(self.queue_manager.session).get_by_id(data.video_id)
            if video:
                project_id = video.project_id
            else:
                raise HTTPException(status_code=404, detail=f"Video não encontrado: {data.video_id}")
        job = await self.queue_manager.enqueue_job(
            project_id=project_id,
            video_id=data.video_id,
            template_id=data.template_id,
            export_profile_id=data.export_profile_id,
        )
        return JobResponse.model_validate(job)

    async def get(self, job_id: str) -> JobResponse:
        """Get job by ID."""
        job = await self.queue_manager.get_job(job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job não encontrado: {job_id}",
            )
        return JobResponse.model_validate(job)

    async def list_by_project(self, project_id: str) -> JobListResponse:
        """List all queue jobs inside a project."""
        jobs = await self.queue_manager.list_jobs(project_id)
        return JobListResponse(
            jobs=[JobResponse.model_validate(j) for j in jobs],
            total=len(jobs),
        )

    async def pause(self, job_id: str) -> JobResponse:
        """Pause a job in the queue using process suspension."""
        # Suspend FFmpeg process if running
        processing_service.worker_manager.pause_worker(job_id)
        
        job = await self.queue_manager.pause_job(job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job não encontrado: {job_id}",
            )
        await processing_service.broadcast_status()
        return JobResponse.model_validate(job)

    async def resume(self, job_id: str) -> JobResponse:
        """Resume a suspended or paused job."""
        # Resume FFmpeg process if suspended
        if job_id in processing_service.worker_manager.paused_jobs:
            processing_service.worker_manager.resume_worker(job_id)
            
        job = await self.queue_manager.resume_job(job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job não encontrado: {job_id}",
            )
        await processing_service.broadcast_status()
        return JobResponse.model_validate(job)

    async def reprocess(self, job_id: str) -> JobResponse:
        """Reset and queue a job for reprocessing."""
        # Stop worker if running
        processing_service.worker_manager.cancel_worker(job_id)
        
        job = await self.queue_manager.reprocess_job(job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job não encontrado: {job_id}",
            )
        await processing_service.broadcast_status()
        return JobResponse.model_validate(job)

    async def cancel(self, job_id: str) -> JobResponse:
        """Cancel a job in the queue."""
        # Cancel execution task
        processing_service.worker_manager.cancel_worker(job_id)
        
        job = await self.queue_manager.cancel_job(job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job não encontrado: {job_id}",
            )
        await processing_service.broadcast_status()
        return JobResponse.model_validate(job)

    async def get_stats(self, project_id: str, session: AsyncSession) -> dict:
        """Get aggregate processing counts and capacity indicators."""
        return await processing_service.get_engine_stats(session, project_id)

    async def render_preview(self, data: JobPreviewRequest, session: AsyncSession) -> dict:
        """Execute a short-duration preview render of the pipeline and return the static file URL."""
        video_repo = VideoRepository(session)
        template_repo = VideoTemplateRepository(session)
        
        video = await video_repo.get_by_id(data.video_id)
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vídeo não encontrado: {data.video_id}"
            )
            
        template = await template_repo.get_by_id(data.template_id)
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template não encontrado: {data.template_id}"
            )
            
        # Target duration for preview
        duration = data.end_time - data.start_time
        if duration <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O tempo final do preview deve ser maior que o inicial."
            )
            
        # Build output directory and file paths
        previews_dir = settings.CACHE_DIR / "previews"
        previews_dir.mkdir(parents=True, exist_ok=True)
        
        # The template signature keeps a cached preview from being reused after the template changes.
        signature = hashlib.md5(
            json.dumps(template.pipeline_config, sort_keys=True, default=str).encode("utf-8")
        ).hexdigest()[:8]
        output_filename = f"preview_{data.video_id}_{data.template_id}_{signature}_{data.start_time:.1f}_{data.end_time:.1f}.mp4"
        output_path = previews_dir / output_filename
        
        # 1. Cache hit check: if the preview file already exists, return URL immediately
        if output_path.exists():
            return {"preview_url": f"http://127.0.0.1:8420/cache/previews/{output_filename}"}
            
        # 2. Run the pipeline with time-sliced settings
        context = {
            "video_duration": float(video.duration or 0.0),
            "start_time": data.start_time,
            "duration_limit": duration,
            "nodes": []
        }
        
        temp_dir = settings.CACHE_DIR / "temp"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        pipeline_manager = PipelineManager()
        try:
            # For preview outputs, the final export node writes directly to output_path
            await pipeline_manager.execute_pipeline(
                input_file=Path(video.project_path),
                temp_dir=temp_dir,
                nodes_config=template.pipeline_config if template else [],
                context=context
            )
            
            # Move or rename compiled file to the target output preview path if not already written there
            temp_output = temp_dir / f"output_preview_{data.video_id}_{data.template_id}_{data.start_time:.1f}_{data.end_time:.1f}.mp4"
            # Our ExportNode writes to the output_path passed during execute (which is context['input_path'] modified or stage_output)
            # Let's check: ExportNode receives 'output_path' argument from execute_pipeline's loop.
            # In execute_pipeline:
            # stage_output = temp_dir / f"output_{input_file.name}"
            # So the output file will be written to that stage_output path.
            # We must move it from stage_output to our preview target path!
            stage_output = temp_dir / f"output_{Path(video.project_path).name}"
            if stage_output.exists():
                import shutil
                shutil.move(stage_output, output_path)
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao gerar preview de render: {e}"
            )
            
        return {"preview_url": f"http://127.0.0.1:8420/cache/previews/{output_filename}"}
