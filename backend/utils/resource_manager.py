"""
AUTOMA Utils - Resource Manager.

Monitors CPU, GPU, RAM, VRAM, and Disk space.
Helps the Scheduler block or throttle job executions to prevent system locking.
"""

import logging
import shutil
import psutil

try:
    import GPUtil
except ImportError:
    GPUtil = None

from config import settings

logger = logging.getLogger("automa.utils.resource_manager")


class ResourceManager:
    """Monitors system performance metrics and validates resources for execution."""

    def __init__(self) -> None:
        pass

    def get_cpu_usage(self) -> float:
        """Return the current overall CPU usage percentage."""
        return psutil.cpu_percent(interval=None)

    def get_ram_usage(self) -> float:
        """Return the current RAM usage percentage."""
        return psutil.virtual_memory().percent

    def get_gpu_metrics(self) -> tuple[float, float]:
        """
        Return the current GPU load percentage and VRAM usage percentage.
        Returns (0.0, 0.0) if no GPU is found or GPUtil is not installed.
        """
        if not GPUtil:
            return 0.0, 0.0
        try:
            gpus = GPUtil.getGPUs()
            if not gpus:
                return 0.0, 0.0
            
            # Take metrics from the most active GPU
            max_load = max(g.load * 100 for g in gpus)
            max_vram = max((g.memoryUsed / g.memoryTotal) * 100 for g in gpus)
            return max_load, max_vram
        except Exception as e:
            logger.debug(f"Failed to read GPU stats: {e}")
            return 0.0, 0.0

    def get_disk_free_gb(self) -> float:
        """Return available disk space in gigabytes on the projects directory drive."""
        try:
            usage = shutil.disk_usage(settings.PROJECTS_DIR)
            return usage.free / (1024 ** 3)
        except Exception:
            return 0.0

    def has_sufficient_resources(
        self,
        max_cpu: float = 80.0,
        max_ram: float = 80.0,
        max_gpu: float = 80.0,
        min_disk_gb: float = 2.0,
    ) -> bool:
        """
        Evaluate if current hardware metrics are within safe limits.
        If system is overloaded, returns False to delay worker spawning.
        """
        cpu = self.get_cpu_usage()
        if cpu > max_cpu:
            logger.warning(f"Resource check failed: CPU usage is too high ({cpu}% > limit {max_cpu}%)")
            return False

        ram = self.get_ram_usage()
        if ram > max_ram:
            logger.warning(f"Resource check failed: RAM usage is too high ({ram}% > limit {max_ram}%)")
            return False

        gpu_load, _ = self.get_gpu_metrics()
        if gpu_load > max_gpu:
            logger.warning(f"Resource check failed: GPU load is too high ({gpu_load}% > limit {max_gpu}%)")
            return False

        disk = self.get_disk_free_gb()
        if disk < min_disk_gb:
            logger.warning(f"Resource check failed: Disk space is too low ({disk:.2f} GB < limit {min_disk_gb} GB)")
            return False

        return True


# Global singleton instance
resource_manager = ResourceManager()
