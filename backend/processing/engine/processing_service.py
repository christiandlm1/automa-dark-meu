"""
AUTOMA Processing Engine - Processing Service.

Central orchestrator for the video processing engine.
Orchestrates worker threads, triggers queue scheduling via Scheduler,
restores interrupted jobs, caches output streams, and computes benchmarks.
"""

import asyncio
import logging
import time
from pathlib import Path
from typing import Any, Callable, Coroutine, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import psutil

from database import async_session_maker
from models.job import Job
from processing.jobs.queue_manager import QueueManager
from processing.workers.worker_manager import WorkerManager
from processing.pipeline.pipeline_manager import PipelineManager
from processing.engine.export_manager import ExportManager
from processing.scheduler.scheduler import Scheduler
from processing.engine.metrics_engine import metrics_engine
from services.settings_service import SettingsService
from services.project_service import ProjectService
from utils.event_bus import event_bus
from utils.cache_manager import cache_manager
from utils.resource_manager import resource_manager

logger = logging.getLogger("automa.processing.engine.service")


class ProcessingService:
    """Core coordinator of AUTOMA Processing Engine."""

    _instance: Optional["ProcessingService"] = None

    def __new__(cls, *args, **kwargs) -> "ProcessingService":
        if not cls._instance:
            cls._instance = super(ProcessingService, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        
        self.worker_manager = WorkerManager()
        self.pipeline_manager = PipelineManager()
        self.export_manager = ExportManager()
        self.scheduler = Scheduler()
        
        self.loop_task: Optional[asyncio.Task] = None
        self.is_running = False
        
        # Callback for WS status broadcasting
        self.status_callback: Optional[Callable[[Dict[str, Any]], Coroutine[Any, Any, None]]] = None
        self._initialized = True

    async def start(self) -> None:
        """Start the background processing queue loop and execute Recovery."""
        if self.is_running:
            return
        self.is_running = True
        
        # 1. Recover any jobs left in "running" or "paused" from unexpected shutdown
        await self.recover_interrupted_jobs()
        
        # 2. Start queue monitoring loop
        self.loop_task = asyncio.create_task(self._queue_loop())
        logger.info("Processing Engine started.")

    async def stop(self) -> None:
        """Stop the background processing queue loop and cancel running workers."""
        self.is_running = False
        if self.loop_task:
            self.loop_task.cancel()
            try:
                await self.loop_task
            except asyncio.CancelledError:
                pass
        self.worker_manager.cancel_all_workers()
        logger.info("Processing Engine stopped.")

    async def recover_interrupted_jobs(self) -> None:
        """Startup Recovery: updates running/paused jobs to 'paused' state."""
        logger.info("Running job recovery checks...")
        async with async_session_maker() as session:
            qm = QueueManager(session)
            try:
                # Retrieve active running/paused jobs in DB
                from sqlalchemy import select, update
                stmt = select(Job).where(Job.status.in_(["running", "paused"]))
                res = await session.execute(stmt)
                interrupted = res.scalars().all()
                
                if interrupted:
                    logger.info(f"Recovery found {len(interrupted)} interrupted jobs. Marking them as paused.")
                    # Reset status to 'paused' so the user can click Resume
                    upd = update(Job).where(Job.status == "running").values(status="paused", speed=0.0)
                    await session.execute(upd)
                    await session.commit()
            except Exception as e:
                logger.error(f"Failed to recover interrupted jobs: {e}")

    async def _queue_loop(self) -> None:
        """Background loop continuously polling and executing queue jobs via Scheduler."""
        try:
            while self.is_running:
                # Load configuration and update worker limits on every loop iteration
                await self._refresh_engine_settings()
                
                async with async_session_maker() as session:
                    qm = QueueManager(session)
                    # Let the Scheduler decide which job to run and throttle resources
                    await self.scheduler.schedule_jobs(session, qm, self.worker_manager)
                    
                await asyncio.sleep(1.0)  # Check queue every second
        except asyncio.CancelledError:
            logger.info("Queue polling loop canceled.")
        except Exception as e:
            logger.error(f"Fatal error in queue loop: {e}", exc_info=True)
            self.is_running = False

    async def _refresh_engine_settings(self) -> None:
        """Load limits and priorities from settings DB table."""
        async with async_session_maker() as session:
            ss = SettingsService(session)
            try:
                # Retrieve settings keys, using defaults if not found
                max_w = await ss.get_by_key("max_workers")
                priority = await ss.get_by_key("process_priority")
                cpu = await ss.get_by_key("max_cpu_usage")
                ram = await ss.get_by_key("max_ram_usage")
                gpu = await ss.get_by_key("max_gpu_usage")
                
                max_workers_val = int(max_w.value) if max_w else self.worker_manager.get_recommended_workers_count()
                priority_val = priority.value if priority else "Normal"
                cpu_val = int(cpu.value) if cpu else 80
                ram_val = int(ram.value) if ram else 80
                gpu_val = int(gpu.value) if gpu else 80
                
                self.worker_manager.update_settings(
                    max_workers=max_workers_val,
                    priority=priority_val,
                    max_cpu=cpu_val,
                    max_ram=ram_val,
                    max_gpu=gpu_val
                )
            except Exception as e:
                logger.error(f"Error seeding or retrieving engine settings: {e}")

    async def _run_job_pipeline(self, job_id: str) -> None:
        """Run the video node pipeline sequentially using compiler, cache and telemetry logs."""
        logger.info(f"Worker started pipeline for Job {job_id}")
        start_time = time.time()
        
        # Telemetry statistics accumulators
        cpu_samples: List[float] = []
        ram_samples: List[float] = []
        gpu_samples: List[float] = []
        speed_samples: List[float] = []
        
        async with async_session_maker() as session:
            qm = QueueManager(session)
            job = await qm.get_job(job_id)
            if not job or job.status != "running":
                return
                
            project_service = ProjectService(session)
            project = await project_service.get_project(job.project_id)
            if not project:
                await qm.fail_job(job_id, "Projeto inválido ou não encontrado.")
                await self.broadcast_status()
                return

            video = job.video
            template = job.template
            export_profile = job.export_profile
            
            # 1. Cache hit check to skip processing if video and template parameters match
            # Compute cache key from video hash + pipeline config representation
            nodes_config = template.pipeline_config if template else []
            
            # Append export configuration to nodes_config if an export_profile is set
            if export_profile:
                # Filter out any existing export nodes in the template to override them
                nodes_config = [n for n in nodes_config if n.get("type") != "export"]
                
                export_node = {
                    "id": f"export_{export_profile.id}",
                    "type": "export",
                    "config": {
                        "resolution": export_profile.resolution,
                        "fps": export_profile.fps,
                        "codec": export_profile.codec,
                        "bitrate": export_profile.bitrate,
                    }
                }
                nodes_config.append(export_node)
            import hashlib
            ENGINE_VERSION = "1.0.0" # Hardcoded or fetched from somewhere
            # Include all components for Cache Key (Module 08)
            cache_components = {
                "video_hash": video.hash,
                "template_id": template.id if template else None,
                "export_profile_id": export_profile.id if export_profile else None,
                "nodes_config": nodes_config,
                "engine_version": ENGINE_VERSION
            }
            config_hash = hashlib.sha256(str(cache_components).encode("utf-8")).hexdigest()
            cache_key = f"render_{video.hash}_{config_hash}"
            
            # Module 08: Ignore cache on retries
            if job.retry_count == 0:
                cached_file_str = cache_manager.get(cache_key)
                if cached_file_str and Path(cached_file_str).exists():
                    logger.info(f"Cache HIT for Job {job_id}. Reusing {cached_file_str}")
                    
                    # Directly copy cached output to project exports folder
                    exported_file = await self.export_manager.export_video(
                        source_path=Path(cached_file_str),
                        project_name=project.name,
                        video_name=video.name
                    )
                    
                    async with async_session_maker() as finish_session:
                        fq = QueueManager(finish_session)
                        job_record = await fq.get_job(job_id)
                        if job_record:
                            job_record.exported_path = str(exported_file)
                            job_record.progress = 100.0
                            await fq.complete_job(job_id)
                            
                            # Add a record to history with cached metrics
                            from repositories.history_repository import HistoryRepository
                            hist_repo = HistoryRepository(finish_session)
                            await hist_repo.create({
                                "project_id": project.id,
                                "video_id": video.id,
                                "video_name": video.name,
                                "template_id": template.id if template else None,
                                "template_name": template.name if template else "Nenhum",
                                "execution_time": time.time() - start_time,
                                "status": "completed",
                                "log": f"Cache HIT. Reused file {cached_file_str}",
                                "exported_path": str(exported_file),
                                "speed": 99.0,
                                "cpu_usage": 0.0,
                                "ram_usage": 0.0,
                                "gpu_usage": 0.0,
                                "retry_count": job.retry_count,
                                "attempts_details": "{}"
                            })
                    await self.broadcast_status()
                    return

            # Setup context for nodes
            context = {
                "job_id": job_id,
                "video_hash": video.hash,
                "project_name": project.name,
                "video_duration": float(video.duration or 0.0),
                "pid_callback": lambda pid: self.worker_manager.active_pids.update({job_id: pid}),
                "retry_count": job.retry_count
            }
            
            # Temporary folder to save intermediate stage files
            temp_dir = Path(project.path) / "temp"
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            video_duration = float(video.duration or 10.0)

            # Callback from FFmpegPlugin reporting real-time progress
            async def _on_progress(progress_val: float, fps: float, speed: float) -> None:
                # Log telemetry samples
                cpu_samples.append(resource_manager.get_cpu_usage())
                ram_samples.append(resource_manager.get_ram_usage())
                gpu_l, _ = resource_manager.get_gpu_metrics()
                gpu_samples.append(gpu_l)
                speed_samples.append(speed)
                
                async with async_session_maker() as prog_session:
                    pq = QueueManager(prog_session)
                    # Remaining seconds = (total - processed) / speed
                    processed_dur = video_duration * (progress_val / 100.0)
                    rem_time = max(0.0, (video_duration - processed_dur) / max(0.1, speed))
                    await pq.update_progress(job_id, progress_val, speed, rem_time)
                await self.broadcast_status()

            try:
                # Run the actual pipeline managers nodes chain
                input_file = Path(video.project_path)
                
                if not input_file.exists():
                    raise FileNotFoundError(f"Arquivo de vídeo original não encontrado no caminho do projeto: {input_file}")
                
                final_temp_path = await self.pipeline_manager.execute_pipeline(
                    input_file=input_file,
                    temp_dir=temp_dir,
                    nodes_config=nodes_config,
                    context=context,
                    progress_callback=_on_progress
                )
                
                # Copy file to exports folder
                exported_file = await self.export_manager.export_video(
                    source_path=final_temp_path,
                    project_name=project.name,
                    video_name=video.name
                )
                
                # 2. Save output to CacheManager for future identical renders
                cache_manager.set(cache_key, str(exported_file))
                
                # Save execution history with telemetry details
                elapsed = time.time() - start_time
                avg_cpu = sum(cpu_samples) / len(cpu_samples) if cpu_samples else 0.0
                avg_ram = sum(ram_samples) / len(ram_samples) if ram_samples else 0.0
                avg_gpu = sum(gpu_samples) / len(gpu_samples) if gpu_samples else 0.0
                avg_speed = sum(speed_samples) / len(speed_samples) if speed_samples else 1.0
                
                # Record metrics engine averages
                metrics_engine.record_node_time("export", elapsed / (len(nodes_config) or 1))
                
                async with async_session_maker() as finish_session:
                    fq = QueueManager(finish_session)
                    job_record = await fq.get_job(job_id)
                    if job_record:
                        import json
                        current_retry = job_record.retry_count
                        attempts_data = {
                            "total_attempts": current_retry + 1,
                            "last_error": None,
                            "duration": elapsed
                        }
                        
                        job_record.exported_path = str(exported_file)
                        await fq.complete_job(job_id)
                        
                        from repositories.history_repository import HistoryRepository
                        hist_repo = HistoryRepository(finish_session)
                        await hist_repo.create({
                            "project_id": project.id,
                            "video_id": video.id,
                            "video_name": video.name,
                            "template_id": template.id if template else None,
                            "template_name": template.name if template else "Nenhum",
                            "execution_time": elapsed,
                            "status": "completed",
                            "log": f"Renderizado com sucesso via FFmpegCompiler.\nNós processados: {len(nodes_config)}",
                            "exported_path": str(exported_file),
                            "speed": avg_speed,
                            "cpu_usage": avg_cpu,
                            "ram_usage": avg_ram,
                            "gpu_usage": avg_gpu,
                            "retry_count": current_retry,
                            "attempts_details": json.dumps(attempts_data)
                        })
                
                logger.info(f"Worker completed pipeline successfully for Job {job_id}")
                
                # Clean up intermediate files
                try:
                    if final_temp_path.exists() and final_temp_path != input_file:
                        final_temp_path.unlink()
                except Exception:
                    pass
                    
            except asyncio.CancelledError:
                logger.warning(f"Job {job_id} cancelled by worker manager.")
                async with async_session_maker() as fail_session:
                    fq = QueueManager(fail_session)
                    await fq.cancel_job(job_id)
            except Exception as e:
                logger.error(f"Error executing pipeline for Job {job_id}: {e}", exc_info=True)
                elapsed = time.time() - start_time
                async with async_session_maker() as fail_session:
                    fq = QueueManager(fail_session)
                    
                    # Retry logic (Module 08)
                    from repositories.settings_repository import SettingsRepository
                    import json
                    settings_repo = SettingsRepository(fail_session)
                    max_retries_setting = await settings_repo.get_by_key("max_retries")
                    max_retries = 3
                    if max_retries_setting:
                        if max_retries_setting.value == "Ilimitado":
                            max_retries = 9999
                        else:
                            try:
                                max_retries = int(max_retries_setting.value)
                            except ValueError:
                                max_retries = 3
                                
                    job_record = await fq.get_job(job_id)
                    current_retry = job_record.retry_count if job_record else 0
                    
                    if job_record and current_retry < max_retries:
                        # Will retry
                        job_record.retry_count += 1
                        job_record.priority = 100  # High priority for recovery
                        job_record.status = "pending"
                        job_record.started_at = None
                        job_record.progress = 0.0
                        job_record.speed = 0.0
                        job_record.error_message = f"Tentativa {current_retry + 1} falhou: {e}"
                        await fail_session.commit()
                        logger.warning(f"Job {job_id} failed on attempt {current_retry + 1}. Re-queued for retry.")
                    else:
                        await fq.fail_job(job_id, str(e))
                        
                        # Create failed history entry
                        from repositories.history_repository import HistoryRepository
                        hist_repo = HistoryRepository(fail_session)
                        
                        # Compute attempts JSON
                        attempts_data = {
                            "total_attempts": current_retry + 1,
                            "last_error": str(e),
                            "duration": elapsed
                        }
                        
                        await hist_repo.create({
                            "project_id": project.id,
                            "video_id": video.id,
                            "video_name": video.name,
                            "template_id": template.id if template else None,
                            "template_name": template.name if template else "Nenhum",
                            "execution_time": elapsed,
                            "status": "failed",
                            "log": f"Erro de processamento após {current_retry + 1} tentativas: {e}",
                            "exported_path": None,
                            "speed": 0.0,
                            "cpu_usage": 0.0,
                            "ram_usage": 0.0,
                            "gpu_usage": 0.0,
                            "retry_count": current_retry,
                            "attempts_details": json.dumps(attempts_data)
                        })

            finally:
                await self.broadcast_status()

    async def broadcast_status(self) -> None:
        """Broadcast current queue state and system stats via registered WS callback."""
        if not self.status_callback:
            return
            
        async with async_session_maker() as session:
            from sqlalchemy import select, func
            from models.job import Job
            
            stmt_pending = select(func.count()).select_from(Job).where(Job.status == "pending")
            res_pending = await session.execute(stmt_pending)
            queue_size = res_pending.scalar_one()
            
            from repositories.job_repository import JobRepository
            repo = JobRepository(session)
            active_jobs = await repo.get_running_jobs()
            
            stats = {
                "active_workers": len(self.worker_manager.active_workers),
                "max_workers": self.worker_manager.max_workers,
                "queue_size": queue_size,
                "priority": self.worker_manager.priority,
                "running_jobs": [
                    {
                        "id": j.id,
                        "video_name": j.video.name if j.video else "Desconhecido",
                        "progress": j.progress,
                        "status": j.status,
                        "speed": j.speed,
                        "estimated_time": j.estimated_time,
                    } for j in active_jobs
                ]
            }
            
            try:
                await self.status_callback(stats)
            except Exception as e:
                logger.error(f"Error in WS status callback: {e}")

    async def get_engine_stats(self, session: AsyncSession, project_id: str) -> Dict[str, Any]:
        """Fetch statistics for the processing dashboard (Jobs)."""
        from sqlalchemy import select, func
        from models.job import Job
        
        from models.history import History
        from datetime import datetime, timezone
        
        stmt = select(Job.status, func.count()).where(Job.project_id == project_id).group_by(Job.status)
        res = await session.execute(stmt)
        counts = {status: count for status, count in res.all()}
        
        # New Stats (Module 08)
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        hist_stmt = select(History).where(History.project_id == project_id)
        hist_res = await session.execute(hist_stmt)
        histories = hist_res.scalars().all()
        
        cache_hits = sum(1 for h in histories if "Cache HIT" in (h.log or ""))
        cache_misses = len(histories) - cache_hits
        processed_today = sum(1 for h in histories if h.processed_at >= today_start and h.status == "completed")
        avg_time = sum(h.execution_time for h in histories if h.status == "completed") / max(1, sum(1 for h in histories if h.status == "completed"))
        
        active_jobs = [w for w in self.worker_manager.active_workers.keys()]
        
        return {
            "pending": counts.get("pending", 0),
            "running": counts.get("running", 0),
            "completed": counts.get("completed", 0),
            "failed": counts.get("failed", 0),
            "cancelled": counts.get("cancelled", 0),
            "paused": counts.get("paused", 0),
            "active_workers": len(active_jobs),
            "max_workers": self.worker_manager.max_workers,
            "priority": self.worker_manager.priority,
            "cache_hits": cache_hits,
            "cache_misses": cache_misses,
            "avg_video_time": avg_time,
            "processed_today": processed_today
        }


# Global singleton instance
processing_service = ProcessingService()
