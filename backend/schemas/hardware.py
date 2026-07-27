"""
AUTOMA Schemas - Hardware.

Pydantic models for hardware detection and real-time monitoring responses.
"""

from datetime import datetime

from pydantic import BaseModel


class HardwareResponse(BaseModel):
    """Schema for static hardware specification response."""

    id: str
    cpu_name: str
    cpu_cores: int
    cpu_threads: int
    ram_total_gb: float
    gpu_name: str | None = None
    gpu_memory_gb: float | None = None
    os_name: str
    os_version: str
    detected_at: datetime

    model_config = {"from_attributes": True}


class HardwareMonitorResponse(BaseModel):
    """Schema for real-time hardware usage sent over WebSocket."""

    cpu_percent: float
    cpu_frequency_mhz: float | None = None
    ram_used_gb: float
    ram_total_gb: float
    ram_percent: float
    gpu_load_percent: float | None = None
    gpu_memory_used_mb: float | None = None
    gpu_memory_total_mb: float | None = None
    gpu_temperature_c: float | None = None
    disk_read_bytes: int = 0
    disk_write_bytes: int = 0
    timestamp: datetime
