"""
AUTOMA Utils - System Utilities.

Detects hardware information (CPU, GPU, RAM, OS) using psutil, py-cpuinfo,
GPUtil, and wmi.  Also provides real-time usage snapshots for the
WebSocket monitor.
"""

import platform
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

import psutil

try:
    import cpuinfo  # py-cpuinfo
except ImportError:
    cpuinfo = None  # type: ignore[assignment]

try:
    import GPUtil
except ImportError:
    GPUtil = None  # type: ignore[assignment]

try:
    import wmi as wmi_module  # Windows-only
except ImportError:
    wmi_module = None  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class SystemInfo:
    """Static hardware specifications."""

    cpu_name: str
    cpu_cores: int
    cpu_threads: int
    ram_total_gb: float
    gpu_name: str | None
    gpu_memory_gb: float | None
    os_name: str
    os_version: str


@dataclass
class RealtimeUsage:
    """Live hardware usage snapshot."""

    cpu_percent: float
    cpu_frequency_mhz: float | None
    ram_used_gb: float
    ram_total_gb: float
    ram_percent: float
    gpu_load_percent: float | None
    gpu_memory_used_mb: float | None
    gpu_memory_total_mb: float | None
    gpu_temperature_c: float | None
    disk_read_bytes: int
    disk_write_bytes: int
    timestamp: datetime


# ---------------------------------------------------------------------------
# Static detection
# ---------------------------------------------------------------------------

def get_system_info() -> SystemInfo:
    """
    Detect static hardware specifications.

    CPU info is gathered via py-cpuinfo, RAM via psutil,
    GPU via GPUtil (falls back to WMI on Windows), and OS via platform.

    This is a CPU-bound operation and should be run in a thread pool.
    """
    # CPU
    cpu_name = "Unknown CPU"
    if cpuinfo is not None:
        try:
            info = cpuinfo.get_cpu_info()
            cpu_name = info.get("brand_raw", "Unknown CPU")
        except Exception:
            pass

    cpu_cores = psutil.cpu_count(logical=False) or 1
    cpu_threads = psutil.cpu_count(logical=True) or 1

    # RAM
    ram = psutil.virtual_memory()
    ram_total_gb = round(ram.total / (1024 ** 3), 2)

    # GPU
    gpu_name: str | None = None
    gpu_memory_gb: float | None = None

    if GPUtil is not None:
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]
                gpu_name = gpu.name
                gpu_memory_gb = round(gpu.memoryTotal / 1024, 2)
        except Exception:
            pass

    # Fallback to WMI on Windows
    if gpu_name is None and wmi_module is not None:
        try:
            w = wmi_module.WMI()
            for gpu_item in w.Win32_VideoController():
                gpu_name = gpu_item.Name
                if gpu_item.AdapterRAM:
                    gpu_memory_gb = round(int(gpu_item.AdapterRAM) / (1024 ** 3), 2)
                break
        except Exception:
            pass

    # OS
    os_name = platform.system()
    os_version = platform.version()

    return SystemInfo(
        cpu_name=cpu_name,
        cpu_cores=cpu_cores,
        cpu_threads=cpu_threads,
        ram_total_gb=ram_total_gb,
        gpu_name=gpu_name,
        gpu_memory_gb=gpu_memory_gb,
        os_name=os_name,
        os_version=os_version,
    )


# ---------------------------------------------------------------------------
# Real-time monitoring
# ---------------------------------------------------------------------------

def get_realtime_usage() -> RealtimeUsage:
    """
    Capture a live snapshot of CPU, RAM, GPU, and disk I/O usage.

    This is a CPU-bound operation and should be run in a thread pool.
    """
    # CPU
    cpu_percent = psutil.cpu_percent(interval=0)
    freq = psutil.cpu_freq()
    cpu_frequency_mhz = freq.current if freq else None

    # RAM
    ram = psutil.virtual_memory()
    ram_used_gb = round((ram.total - ram.available) / (1024 ** 3), 2)
    ram_total_gb = round(ram.total / (1024 ** 3), 2)
    ram_percent = ram.percent

    # GPU
    gpu_load: float | None = None
    gpu_mem_used: float | None = None
    gpu_mem_total: float | None = None
    gpu_temp: float | None = None

    if GPUtil is not None:
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]
                gpu_load = round(gpu.load * 100, 1)
                gpu_mem_used = round(gpu.memoryUsed, 1)
                gpu_mem_total = round(gpu.memoryTotal, 1)
                gpu_temp = gpu.temperature
        except Exception:
            pass

    # Disk I/O
    disk_io = psutil.disk_io_counters()
    disk_read = disk_io.read_bytes if disk_io else 0
    disk_write = disk_io.write_bytes if disk_io else 0

    return RealtimeUsage(
        cpu_percent=cpu_percent,
        cpu_frequency_mhz=cpu_frequency_mhz,
        ram_used_gb=ram_used_gb,
        ram_total_gb=ram_total_gb,
        ram_percent=ram_percent,
        gpu_load_percent=gpu_load,
        gpu_memory_used_mb=gpu_mem_used,
        gpu_memory_total_mb=gpu_mem_total,
        gpu_temperature_c=gpu_temp,
        disk_read_bytes=disk_read,
        disk_write_bytes=disk_write,
        timestamp=datetime.now(timezone.utc),
    )
