"""
AUTOMA Processing Engine - Worker Manager.

Manages execution threads/tasks for processing videos in parallel.
Determines ideal worker counts based on hardware and respects performance limits.
Applies OS-level process nice priority levels using psutil.
"""

import asyncio
import logging
import multiprocessing
from typing import Any, Callable, Coroutine, Dict

import psutil
try:
    import GPUtil
except ImportError:
    GPUtil = None

logger = logging.getLogger("automa.processing.workers")


class WorkerManager:
    """Orchestrates parallel worker tasks and throttles resource usage."""

    def __init__(self) -> None:
        self.active_workers: Dict[str, asyncio.Task] = {}
        self.active_pids: Dict[str, int] = {}
        self.paused_jobs: set[str] = set()
        self.max_workers = self.get_recommended_workers_count()
        self.priority = "Normal"
        
        # Throttling levels
        self.max_cpu = 80
        self.max_ram = 80
        self.max_gpu = 80

    def get_recommended_workers_count(self) -> int:
        """Calculate recommended workers based on CPU core count (power of 2: 1, 2, 4, 8, 16)."""
        cores = multiprocessing.cpu_count()
        if cores <= 2:
            return 1
        elif cores <= 4:
            return 2
        elif cores <= 8:
            return 4
        elif cores <= 16:
            return 8
        else:
            return 16

    def apply_process_priority(self, level: str) -> None:
        """Apply OS-level process scheduling priority using psutil."""
        if getattr(self, "_applied_priority", None) == level:
            return
        self._applied_priority = level
        self.priority = level
        try:
            p = psutil.Process()
            # Windows process priority classes
            if level == "Baixa":
                p.nice(psutil.IDLE_PRIORITY_CLASS)
                logger.info("Process priority set to LOW (IDLE)")
            elif level == "Alta":
                p.nice(psutil.HIGH_PRIORITY_CLASS)
                logger.info("Process priority set to HIGH")
            else:
                p.nice(psutil.NORMAL_PRIORITY_CLASS)
                logger.info("Process priority set to NORMAL")
        except Exception as e:
            logger.warning(f"Could not adjust process priority: {e}")

    def update_settings(self, max_workers: int, priority: str, max_cpu: int, max_ram: int, max_gpu: int) -> None:
        """Update worker configuration settings."""
        self.max_workers = max_workers
        self.apply_process_priority(priority)
        self.max_cpu = max_cpu
        self.max_ram = max_ram
        self.max_gpu = max_gpu

    def can_spawn_worker(self) -> bool:
        """Check if we have worker slots and resource usage is within bounds."""
        if len(self.active_workers) >= self.max_workers:
            return False
            
        # Verify CPU usage
        cpu_usage = psutil.cpu_percent(interval=None)
        if cpu_usage > self.max_cpu:
            logger.warning(f"Throttling worker spawn: CPU usage is high ({cpu_usage}%)")
            return False
            
        # Verify RAM usage
        ram_usage = psutil.virtual_memory().percent
        if ram_usage > self.max_ram:
            logger.warning(f"Throttling worker spawn: RAM usage is high ({ram_usage}%)")
            return False
            
        # Verify GPU usage if available
        if GPUtil:
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu_usage = max(g.load * 100 for g in gpus)
                    if gpu_usage > self.max_gpu:
                        logger.warning(f"Throttling worker spawn: GPU usage is high ({gpu_usage}%)")
                        return False
            except Exception:
                pass
                
        return True

    def spawn_worker(self, job_id: str, coro_func: Callable[[str], Coroutine[Any, Any, None]]) -> bool:
        """Spawn a worker task for a job ID."""
        if job_id in self.active_workers:
            return False
            
        task = asyncio.create_task(coro_func(job_id))
        self.active_workers[job_id] = task
        
        # Clean up reference when task completes
        def _on_complete(t: asyncio.Task):
            self.active_workers.pop(job_id, None)
            self.active_pids.pop(job_id, None)
            self.paused_jobs.discard(job_id)
            logger.info(f"Worker for Job {job_id} terminated. Active remaining: {len(self.active_workers)}")
            
        task.add_done_callback(_on_complete)
        logger.info(f"Spawned worker for Job {job_id}. Active: {len(self.active_workers)}")
        return True

    def pause_worker(self, job_id: str) -> bool:
        """Suspend the OS execution of the FFmpeg subprocess for a job."""
        pid = self.active_pids.get(job_id)
        if not pid:
            logger.warning(f"Cannot pause Job {job_id}: no active PID registered.")
            return False
        try:
            p = psutil.Process(pid)
            p.suspend()
            self.paused_jobs.add(job_id)
            logger.info(f"Suspended execution of PID {pid} for Job {job_id}")
            return True
        except Exception as e:
            logger.error(f"Error suspending PID {pid} for Job {job_id}: {e}")
            return False

    def resume_worker(self, job_id: str) -> bool:
        """Resume the OS execution of the FFmpeg subprocess for a job."""
        pid = self.active_pids.get(job_id)
        if not pid:
            logger.warning(f"Cannot resume Job {job_id}: no active PID registered.")
            return False
        try:
            p = psutil.Process(pid)
            p.resume()
            self.paused_jobs.discard(job_id)
            logger.info(f"Resumed execution of PID {pid} for Job {job_id}")
            return True
        except Exception as e:
            logger.error(f"Error resuming PID {pid} for Job {job_id}: {e}")
            return False

    def cancel_worker(self, job_id: str) -> bool:
        """Cancel the worker running a specific job and terminate the FFmpeg process."""
        pid = self.active_pids.get(job_id)
        if pid:
            try:
                p = psutil.Process(pid)
                p.kill()
                logger.info(f"Killed active FFmpeg process {pid} for Job {job_id}")
            except Exception:
                pass
                
        task = self.active_workers.get(job_id)
        if task:
            task.cancel()
            logger.info(f"Requested cancellation of worker task for Job {job_id}")
            return True
        return False

    def cancel_all_workers(self) -> None:
        """Cancel all running worker tasks and kill subprocesses."""
        for job_id in list(self.active_workers.keys()):
            self.cancel_worker(job_id)
        self.active_workers.clear()
        self.active_pids.clear()
        self.paused_jobs.clear()
