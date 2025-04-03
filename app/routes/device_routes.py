"""Routes for device management and interactions."""

import logging

from fastapi import APIRouter, HTTPException

from app.services import service_manager

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/")
async def get_devices():
    """Get all connected and managed devices."""
    device_service = service_manager.services.get("device_service")
    if not device_service or not device_service.is_running:
        raise HTTPException(status_code=503, detail="Device service not running")

    return {"devices": device_service.devices_cache}


@router.get("/{serial}")
async def get_device_info(serial: str):
    """Get detailed information about a specific device."""
    device_service = service_manager.services.get("device_service")
    if not device_service or not device_service.is_running:
        raise HTTPException(status_code=503, detail="Device service not running")

    device_info = await device_service.get_device_info(serial)
    if "error" in device_info:
        raise HTTPException(status_code=404, detail=device_info["error"])

    return device_info
