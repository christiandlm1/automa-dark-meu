"""
AUTOMA Routes - Hardware
API route definitions for hardware detection.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from controllers.hardware_controller import HardwareController
from schemas.hardware import HardwareMonitorResponse, HardwareResponse

router = APIRouter(prefix="/hardware", tags=["hardware"])


@router.post("/detect", response_model=HardwareResponse)
async def detect_hardware(
    db: AsyncSession = Depends(get_db),
):
    """Trigger a full system hardware detection and record to DB."""
    controller = HardwareController(db)
    return await controller.detect()


@router.get("/info", response_model=HardwareResponse)
async def get_hardware_info(
    db: AsyncSession = Depends(get_db),
):
    """Retrieve the hardware specifications recorded on file."""
    controller = HardwareController(db)
    return await controller.get_info()


@router.get("/realtime", response_model=HardwareMonitorResponse)
async def get_realtime_usage(
    db: AsyncSession = Depends(get_db),
):
    """Get a quick real-time snapshot of CPU, GPU, and RAM usage."""
    controller = HardwareController(db)
    return await controller.get_realtime()
