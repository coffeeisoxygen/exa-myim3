"""Routes for ADB server management and interactions."""

import logging

from fastapi import APIRouter, HTTPException

from app.services import service_manager

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/status")
async def adb_status():
    """Get ADB service status."""
    status = service_manager.get_service_status("adb_service")
    return status


@router.get("/devices")
async def adb_devices():
    """Get raw devices list from ADB service."""
    adb_service = service_manager.services.get("adb_service")
    if not adb_service or not adb_service.is_running:
        raise HTTPException(status_code=503, detail="ADB service not running")

    return {"devices": adb_service.devices_cache}
