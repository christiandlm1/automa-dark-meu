"""
AUTOMA Processing Engine - Queue Scheduler.

Decides which Job to execute and coordinates task distribution among active workers.
Integrates with the ResourceManager to throttle executions under high load.
Decouples job queues from execution policies.
"""

import logging
import time
from sqlalchemy.ext.asyncio import AsyncSession

from processing.jobs.queue_manager import QueueManager
from processing.workers.worker_manager import WorkerManager
from utils.resource_manager import resource_manager

logger = logging.getLogger("automa.processing.scheduler")


class Scheduler:
    """Manages queue scheduling, worker distribution and throttle policies."""

    def __init__(self) -> None:
        self._last_throttle_log = 0.0

    async def schedule_jobs(
        self,
        session: AsyncSession,
        queue_manager: QueueManager,
        worker_manager: WorkerManager,
    ) -> None:
        """
        Polls the queue and schedules pending jobs on available workers.
        Applies ResourceManager checks to delay startup under high hardware usage.
        """
        # 1. Check if we have available worker slots
        active_count = len(worker_manager.active_workers)
        max_slots = worker_manager.max_workers
        
        if active_count >= max_slots:
            return  # Worker pool is full

        # 2. Check if the system has sufficient resources to run another task
        # If resources are overloaded, we delay executing new jobs to prevent freeze
        # With no job running, the load comes from other programs, not from AUTOMA: delaying
        # would block the queue forever, so at least one job is always allowed to start.
        if active_count > 0 and not resource_manager.has_sufficient_resources(
            max_cpu=worker_manager.max_cpu,
            max_ram=worker_manager.max_ram,
            max_gpu=worker_manager.max_gpu,
        ):
            now = time.monotonic()
            if now - self._last_throttle_log > 30:  # avoid one warning per second
                logger.warning("Resource limits exceeded. Scheduler is delaying new jobs.")
                self._last_throttle_log = now
            return

        # 3. Pull next pending jobs from queue
        available_slots = max_slots - active_count
        pending_jobs = await queue_manager.repo.get_pending_jobs(limit=available_slots)
        
        if not pending_jobs:
            return

        # 4. Distribute jobs to workers
        # Import the execute runner dynamically to avoid circular references
        from processing.engine.processing_service import processing_service
        
        for job in pending_jobs:
            job_id = job.id
            logger.info(f"Scheduler distributing Job {job_id} to worker pool.")
            
            # Update job status to 'running'
            # (get_next_job did this in Módulo 02, now the scheduler orchestrates it)
            job.status = "running"
            import datetime
            job.started_at = datetime.datetime.now(datetime.timezone.utc)
            await session.commit()
            
            # Spawn worker task
            success = worker_manager.spawn_worker(
                job_id=job_id,
                coro_func=processing_service._run_job_pipeline
            )
            
            if not success:
                # Revert job to pending if worker couldn't start
                job.status = "pending"
                job.started_at = None
                await session.commit()
                logger.error(f"Failed to spawn worker for Job {job_id}. Reverted status.")
