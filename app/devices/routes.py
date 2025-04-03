import logging
from typing import List

from fastapi import APIRouter, HTTPException, Query

from app.devices.schemas import DeviceCreate, DeviceDetail, DeviceResponse, DeviceUpdate
from app.devices.service import device_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=List[DeviceResponse])
async def get_devices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """
    Get all devices.

    Args:
        skip: Number of devices to skip
        limit: Maximum number of devices to return
    """
    return await device_service.get_all_devices(skip, limit)


@router.post("/", response_model=DeviceResponse)
async def create_device(device: DeviceCreate):
    """
    Create a new device.

    Args:
        device: Device data
    """
    try:
        return await device_service.create_device(device)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/connected", response_model=List[dict])
async def get_connected_devices():
    """Get currently connected devices."""
    return device_service.devices_cache


@router.get("/{serial}", response_model=DeviceDetail)
async def get_device(serial: str):
    """
    Get device by serial number.

    Args:
        serial: Device serial number
    """
    device_info = await device_service.get_device_info(serial)
    if "error" in device_info:
        raise HTTPException(status_code=404, detail=device_info["error"])
    return device_info


@router.put("/{serial}", response_model=DeviceResponse)
async def update_device(serial: str, device: DeviceUpdate):
    """
    Update device.

    Args:
        serial: Device serial number
        device: Updated device data
    """
    updated_device = await device_service.update_device(serial, device)
    if not updated_device:
        raise HTTPException(status_code=404, detail=f"Device {serial} not found")
    return updated_device


@router.delete("/{serial}")
async def delete_device(serial: str):
    """
    Delete device.

    Args:
        serial: Device serial number
    """
    success = await device_service.delete_device(serial)
    if not success:
        raise HTTPException(status_code=404, detail=f"Device {serial} not found")
    return {"message": f"Device {serial} deleted successfully"}


@router.post("/{serial}/command")
async def execute_command(
    serial: str, command: List[str], timeout: int = Query(30, ge=1, le=300)
):
    """
    Execute command on device.

    Args:
        serial: Device serial number
        command: Command to execute
        timeout: Command timeout in seconds
    """
    success, output = await device_service.execute_command(serial, command, timeout)
    if not success:
        raise HTTPException(status_code=400, detail=output)
    return {"success": True, "output": output}
