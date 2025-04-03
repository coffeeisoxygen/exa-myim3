from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.config.database import get_session
from app.database.models import Device
from app.services import service_manager

router = APIRouter()

# DB Operations


@router.post("/", response_model=Device)
async def create_device(device: Device, session: Session = Depends(get_session)):
    """Create a new device in the database."""
    session.add(device)
    session.commit()
    session.refresh(device)
    return device


@router.get("/", response_model=List[Device])
async def read_devices(
    skip: int = 0, limit: int = 100, session: Session = Depends(get_session)
):
    """Get all devices from the database."""
    statement = select(Device).offset(skip).limit(limit)
    devices = session.exec(statement).all()
    return devices


@router.get("/{serial}", response_model=Device)
async def read_device(serial: str, session: Session = Depends(get_session)):
    """Get a specific device by serial number."""
    device = session.get(Device, serial)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@router.put("/{serial}", response_model=Device)
async def update_device(
    serial: str, device_update: Device, session: Session = Depends(get_session)
):
    """Update a device."""
    device = session.get(Device, serial)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    # Update device fields
    device_data = device_update.dict(exclude_unset=True)
    for key, value in device_data.items():
        setattr(device, key, value)

    session.add(device)
    session.commit()
    session.refresh(device)
    return device


@router.delete("/{serial}")
async def delete_device(serial: str, session: Session = Depends(get_session)):
    """Delete a device."""
    device = session.get(Device, serial)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    session.delete(device)
    session.commit()
    return {"ok": True}


# Device Service Operations


@router.get("/status")
async def get_devices_status():
    """Get status of all connected devices."""
    # Get service from manager
    service = service_manager.services.get("device_service")
    if not service:
        raise HTTPException(status_code=503, detail="Device service not available")

    # Return device info
    return {
        "device_count": len(service.devices_cache),
        "devices": [
            {
                "serial": device.serial,
                "model": device.model,
                "connected": device.is_connected,
            }
            for device in service.devices_cache
        ],
    }


@router.get("/status/{serial}")
async def get_device_status(serial: str):
    """Get status of a specific device."""
    # Get service from manager
    service = service_manager.services.get("device_service")
    if not service:
        raise HTTPException(status_code=503, detail="Device service not available")

    # Get device info
    device_info = service.get_device(serial)
    if "error" in device_info:
        raise HTTPException(status_code=404, detail=device_info["error"])

    return device_info


@router.post("/{serial}/action")
async def execute_device_action(serial: str, action: Dict[str, Any]):
    """Execute an action on a device."""
    # Get service from manager
    service = service_manager.services.get("device_service")
    if not service:
        raise HTTPException(status_code=503, detail="Device service not available")

    # Execute action
    action_type = action.get("type")
    if not action_type:
        raise HTTPException(status_code=400, detail="Action type is required")

    params = action.get("params", {})
    result = service.execute_action(serial, action_type, **params)

    if not result.get("success", False):
        raise HTTPException(
            status_code=400, detail=result.get("error", "Unknown error")
        )

    return result
