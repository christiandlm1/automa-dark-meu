"""
AUTOMA Processing Engine - Queue Manager.

Manages the persistent processing queue.
Provides methods to enqueue, pause, resume, cancel, and update jobs.
Interfaces with the EventBus and logs operations.
"""

import logging
from datetime import datetime, timezone
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from models.job import Job
from repositories.job_repository import JobRepository
from repositories.video_template_repository import VideoTemplateRepository
from services.log_service import LogService
from utils.event_bus import (
    event_bus,
    EVENT_JOB_CREATED,
    EVENT_JOB_STARTED,
    EVENT_JOB_PAUSED,
    EVENT_JOB_FINISHED,
    EVENT_JOB_FAILED,
)

logger = logging.getLogger("automa.processing.jobs")


class QueueManager:
    """Manages enqueueing and states of Jobs."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = JobRepository(session)
        self.template_repo = VideoTemplateRepository(session)
        self.log_service = LogService(session)

    async def enqueue_job(self, project_id: str, video_id: str, template_id: str | None = None, export_profile_id: str | None = None) -> Job:
        """Add a job to the processing queue."""
        # Log which template is being used
        template = await self.template_repo.get_by_id(template_id) if template_id else None
        template_name = template.name if template else "Nenhum"
        
        job = Job(
            project_id=project_id,
            video_id=video_id,
            template_id=template_id,
            export_profile_id=export_profile_id,
            status="pending",
            progress=0.0,
        )
        created = await self.repo.create(job)
        await self.session.commit()
        
        # Load video and template relations for response
        full_job = await self.repo.get_job_with_relations(created.id) or created
        
        # Write audit logs
        await self.log_service.log_info(
            action="job_create",
            project_id=project_id,
            message=f"Job de processamento adicionado à fila: Vídeo '{full_job.video.name}' com template '{template_name}'",
            details={"job_id": created.id, "video_id": video_id, "template_id": template_id, "export_profile_id": export_profile_id},
        )
        
        # Publish event
        await event_bus.publish(EVENT_JOB_CREATED, full_job)
        
        return full_job

    async def get_next_job(self) -> Job | None:
        """Fetch the next pending job from the queue and set its status to running."""
        pending = await self.repo.get_pending_jobs(limit=1)
        if not pending:
            return None
            
        job = pending[0]
        job.status = "running"
        job.started_at = datetime.now(timezone.utc)
        await self.session.commit()
        
        # Write audit log
        await self.log_service.log_info(
            action="job_start",
            project_id=job.project_id,
            message=f"Processamento iniciado para o vídeo '{job.video.name}'",
            details={"job_id": job.id},
        )
        
        # Publish event
        await event_bus.publish(EVENT_JOB_STARTED, job)
        
        return job

    async def update_progress(
        self,
        job_id: str,
        progress: float,
        speed: float,
        estimated_time: float | None = None,
    ) -> Job | None:
        """Update progress metrics of a running job."""
        job = await self.repo.get_by_id(job_id)
        if not job:
            return None
            
        job.progress = progress
        job.speed = speed
        if estimated_time is not None:
            job.estimated_time = estimated_time
            
        await self.session.commit()
        return job

    async def pause_job(self, job_id: str) -> Job | None:
        """Pause a job in the queue."""
        job = await self.repo.get_job_with_relations(job_id)
        if not job or job.status not in ["pending", "running"]:
            return job
            
        job.status = "paused"
        await self.session.commit()
        
        # Write audit log
        await self.log_service.log_info(
            action="job_pause",
            project_id=job.project_id,
            message=f"Processamento pausado para o vídeo '{job.video.name}'",
            details={"job_id": job.id},
        )
        
        # Publish event
        await event_bus.publish(EVENT_JOB_PAUSED, job)
        
        return job

    async def resume_job(self, job_id: str) -> Job | None:
        """Resume a paused job, putting it back in pending status."""
        job = await self.repo.get_job_with_relations(job_id)
        if not job or job.status != "paused":
            return job
            
        job.status = "pending"
        await self.session.commit()
        
        # Write audit log
        await self.log_service.log_info(
            action="job_resume",
            project_id=job.project_id,
            message=f"Processamento retomado para o vídeo '{job.video.name}'",
            details={"job_id": job.id},
        )
        
        return job

    async def reprocess_job(self, job_id: str) -> Job | None:
        """Reset a job status to pending and clear metrics to trigger reprocessing."""
        job = await self.repo.get_job_with_relations(job_id)
        if not job:
            return None
            
        job.status = "pending"
        job.progress = 0.0
        job.speed = 0.0
        job.estimated_time = None
        job.started_at = None
        job.finished_at = None
        job.error_message = None
        await self.session.commit()
        
        # Write audit log
        await self.log_service.log_info(
            action="job_reprocess",
            project_id=job.project_id,
            message=f"Processamento reiniciado para o vídeo '{job.video.name}'",
            details={"job_id": job.id},
        )
        
        return job

    async def cancel_job(self, job_id: str) -> Job | None:
        """Cancel a job in the queue."""
        job = await self.repo.get_job_with_relations(job_id)
        if not job or job.status in ["completed", "failed", "cancelled"]:
            return job
            
        job.status = "cancelled"
        job.finished_at = datetime.now(timezone.utc)
        job.error_message = "Cancelado pelo usuário."
        await self.session.commit()
        
        # Write audit log
        await self.log_service.log_info(
            action="job_cancel",
            project_id=job.project_id,
            message=f"Processamento cancelado para o vídeo '{job.video.name}'",
            details={"job_id": job.id},
        )
        
        # Publish event as failed (cancelled)
        await event_bus.publish(EVENT_JOB_FAILED, job, "Cancelado pelo usuário.")
        
        return job

    async def complete_job(self, job_id: str) -> Job | None:
        """Mark a job as successfully completed."""
        job = await self.repo.get_job_with_relations(job_id)
        if not job:
            return None
            
        job.status = "completed"
        job.progress = 100.0
        job.finished_at = datetime.now(timezone.utc)
        job.estimated_time = 0.0
        await self.session.commit()
        
        # Write audit log
        await self.log_service.log_info(
            action="job_finish",
            project_id=job.project_id,
            message=f"Processamento concluído com sucesso: '{job.video.name}'",
            details={"job_id": job.id},
        )
        
        # Publish event
        await event_bus.publish(EVENT_JOB_FINISHED, job)
        
        return job

    async def fail_job(self, job_id: str, error_message: str) -> Job | None:
        """Mark a job as failed with an error message."""
        job = await self.repo.get_job_with_relations(job_id)
        if not job:
            return None
            
        job.status = "failed"
        job.finished_at = datetime.now(timezone.utc)
        job.error_message = error_message
        await self.session.commit()
        
        # Write audit log
        await self.log_service.log_error(
            action="job_fail",
            project_id=job.project_id,
            message=f"Falha no processamento do vídeo '{job.video.name}': {error_message}",
            details={"job_id": job.id, "error": error_message},
        )
        
        # Publish event
        await event_bus.publish(EVENT_JOB_FAILED, job, error_message)
        
        return job

    async def list_jobs(self, project_id: str) -> Sequence[Job]:
        """List all queue jobs for a project."""
        return await self.repo.get_by_project(project_id)
        
    async def get_job(self, job_id: str) -> Job | None:
        """Get a single job details with relations."""
        return await self.repo.get_job_with_relations(job_id)
