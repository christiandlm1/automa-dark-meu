"""
AUTOMA Services - Hardware Service.

Detects static hardware specifications and provides real-time monitoring
data (used by the WebSocket endpoint).
"""

import asyncio
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from models.hardware import Hardware
from schemas.hardware import HardwareMonitorResponse, HardwareResponse
from utils.system_utils import get_system_info, get_realtime_usage, SystemInfo


class HardwareService:
    """Detects hardware specs and streams real-time usage."""

    def __init__(self, session: AsyncSession | None = None) -> None:
        self.session = session

    # ------------------------------------------------------------------
    # Static detection
    # ------------------------------------------------------------------

    async def detect_hardware(self) -> Hardware:
        """
        Detect hardware specs and persist them to the database.

        Runs the detection in a thread pool executor because py-cpuinfo
        and GPUtil are blocking.
        """
        loop = asyncio.get_running_loop()
        info: SystemInfo = await loop.run_in_executor(None, get_system_info)

        hardware = Hardware(
            id=str(uuid.uuid4()),
            cpu_name=info.cpu_name,
            cpu_cores=info.cpu_cores,
            cpu_threads=info.cpu_threads,
            ram_total_gb=info.ram_total_gb,
            gpu_name=info.gpu_name,
            gpu_memory_gb=info.gpu_memory_gb,
            os_name=info.os_name,
            os_version=info.os_version,
            detected_at=datetime.now(timezone.utc),
        )

        if self.session:
            self.session.add(hardware)
            await self.session.flush()
            await self.session.refresh(hardware)

        return hardware

    async def get_hardware_info(self) -> HardwareResponse | None:
        """Return the most recently stored hardware record as a schema."""
        if not self.session:
            return None

        from sqlalchemy import select

        stmt = (
            select(Hardware)
            .order_by(Hardware.detected_at.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        hw = result.scalar_one_or_none()
        if hw:
            return HardwareResponse.model_validate(hw)
        return None

    # ------------------------------------------------------------------
    # Real-time monitoring
    # ------------------------------------------------------------------

    async def get_realtime_snapshot(self) -> HardwareMonitorResponse:
        """
        Capture a single real-time usage snapshot.

        Runs in an executor since psutil and GPUtil calls are blocking.
        """
        loop = asyncio.get_running_loop()
        usage = await loop.run_in_executor(None, get_realtime_usage)

        return HardwareMonitorResponse(
            cpu_percent=usage.cpu_percent,
            cpu_frequency_mhz=usage.cpu_frequency_mhz,
            ram_used_gb=usage.ram_used_gb,
            ram_total_gb=usage.ram_total_gb,
            ram_percent=usage.ram_percent,
            gpu_load_percent=usage.gpu_load_percent,
            gpu_memory_used_mb=usage.gpu_memory_used_mb,
            gpu_memory_total_mb=usage.gpu_memory_total_mb,
            gpu_temperature_c=usage.gpu_temperature_c,
            disk_read_bytes=usage.disk_read_bytes,
            disk_write_bytes=usage.disk_write_bytes,
            timestamp=usage.timestamp,
        )
