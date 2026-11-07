"""
AUTOMA Processing Engine - History Manager.

Listens to EventBus events (JobFinished, JobFailed) and automatically records
execution results, metrics and logs into the database ``history`` table.
"""

import logging
from datetime import datetime, timezone
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from database import async_session_maker

from models.history import History
from repositories.history_repository import HistoryRepository
from utils.event_bus import event_bus, EVENT_JOB_FINISHED, EVENT_JOB_FAILED

logger = logging.getLogger("automa.processing.engine.history")


def _naive(dt: datetime) -> datetime:
    """Drop tzinfo (converting to UTC first) so naive DB values and aware ones can be subtracted."""
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


class HistoryManager:
    """Listens to queue events and logs job results to the persistent history table."""

    def __init__(self) -> None:
        # Register EventBus subscribers
        event_bus.subscribe(EVENT_JOB_FINISHED, self.on_job_finished)
        event_bus.subscribe(EVENT_JOB_FAILED, self.on_job_failed)
        logger.info("HistoryManager successfully subscribed to JobFinished and JobFailed events.")

    async def get_project_history(
        self,
        session: AsyncSession,
        project_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[Sequence[History], int]:
        """Query and return history records for a project."""
        repo = HistoryRepository(session)
        items = await repo.get_by_project(project_id, skip=skip, limit=limit)
        total = await repo.count_by_project(project_id)
        return items, total

    async def clear_history(self, session: AsyncSession, project_id: str) -> None:
        """Clear all history logs for a project."""
        from sqlalchemy import delete
        stmt = delete(History).where(History.project_id == project_id)
        await session.execute(stmt)
        await session.flush()

    async def on_job_finished(self, job) -> None:
        """Callback executed when a Job finishes successfully."""
        logger.info(f"HistoryManager received JobFinished event for Job {job.id}")
        
        # Calculate execution time in seconds
        exec_time = 0.0
        if job.started_at and job.finished_at:
            exec_time = (_naive(job.finished_at) - _naive(job.started_at)).total_seconds()
            
        async with async_session_maker() as session:
            try:
                repo = HistoryRepository(session)
                
                # Fetch related names if they are lazy loaded
                video_name = job.video.name if job.video else "Vídeo Desconhecido"
                template_name = job.template.name if job.template else "Sem Template"
                
                # Retrieve exported path (usually calculated during export node)
                # In simulation, we store the simulated export path
                exported_path = getattr(job, "exported_path", None)
                
                history_entry = History(
                    project_id=job.project_id,
                    video_id=job.video_id,
                    video_name=video_name,
                    template_id=job.template_id,
                    template_name=template_name,
                    processed_at=datetime.now(timezone.utc),
                    execution_time=round(exec_time, 2),
                    status="completed",
                    log=f"Processamento concluído com sucesso.\nTempo de execução: {exec_time:.2f}s\nVelocidade média: {job.speed:.1f}x",
                    exported_path=exported_path,
                )
                await repo.create(history_entry)
                await session.commit()
                logger.info(f"Recorded completed history entry for job {job.id}")
            except Exception as e:
                logger.error(f"Failed to save finished job history: {e}", exc_info=True)

    async def on_job_failed(self, job, error_message: str) -> None:
        """Callback executed when a Job fails."""
        logger.info(f"HistoryManager received JobFailed event for Job {job.id}: {error_message}")
        
        exec_time = 0.0
        if job.started_at and job.finished_at:
            exec_time = (_naive(job.finished_at) - _naive(job.started_at)).total_seconds()
            
        async with async_session_maker() as session:
            try:
                repo = HistoryRepository(session)
                
                video_name = job.video.name if job.video else "Vídeo Desconhecido"
                template_name = job.template.name if job.template else "Sem Template"
                
                history_entry = History(
                    project_id=job.project_id,
                    video_id=job.video_id,
                    video_name=video_name,
                    template_id=job.template_id,
                    template_name=template_name,
                    processed_at=datetime.now(timezone.utc),
                    execution_time=round(exec_time, 2),
                    status="failed",
                    log=f"Processamento falhou com erro: {error_message}\nTempo decorrido: {exec_time:.2f}s",
                    exported_path=None,
                )
                await repo.create(history_entry)
                await session.commit()
                logger.info(f"Recorded failed history entry for job {job.id}")
            except Exception as e:
                logger.error(f"Failed to save failed job history: {e}", exc_info=True)


# Instantiated during startup to automatically register listeners
history_manager = HistoryManager()
