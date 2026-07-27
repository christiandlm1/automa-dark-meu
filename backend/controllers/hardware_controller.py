"""
AUTOMA Controllers - Hardware Controller.

Thin controller that delegates to HardwareService.
"""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.hardware import HardwareMonitorResponse, HardwareResponse
from services.hardware_service import HardwareService


class HardwareController:
    """Handles HTTP request/response translation for hardware endpoints."""

    def __init__(self, session: AsyncSession) -> None:
        self.service = HardwareService(session)

    async def detect(self) -> HardwareResponse:
        """Detect and store current hardware specifications."""
        hardware = await self.service.detect_hardware()
        return HardwareResponse.model_validate(hardware)

    async def get_info(self) -> HardwareResponse:
        """Return the most recently detected hardware info."""
        info = await self.service.get_hardware_info()
        if not info:
            # Auto-detect if no record exists
            hardware = await self.service.detect_hardware()
            return HardwareResponse.model_validate(hardware)
        return info

    async def get_realtime(self) -> HardwareMonitorResponse:
        """Return a single real-time usage snapshot."""
        return await self.service.get_realtime_snapshot()
