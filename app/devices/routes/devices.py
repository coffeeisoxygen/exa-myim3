from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Session, select

from app import devices
from app.config.database import get_session
from app.database.models import Device

DEVICE_NOT_FOUND_ERROR = "Device not found"

app = FastAPI()


# Create Devices
@app.post("/devices/", response_model=Device)
async def create_device(device: Device, session: Session = Depends(get_session)):
    """Create a new device in the database."""
    session.add(device)
    session.commit()
    session.refresh(device)
    return device


# Read All Devices
@app.get("/devices/", response_model=list[Device])
async def read_devices(
    skip: int = 0, limit: int = 10, session: Session = Depends(get_session)
):
    """Get all devices from the database."""
    if not devices:
        raise HTTPException(status_code=404, detail="Device not found")
    return devices


# Read All Device by serial
@app.get("/devices/{serial}", response_model=Device)
async def read_device_by_serial(serial: str, session: Session = Depends(get_session)):
    """Get a device by its serial number."""
    device = session.get(Device, serial)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


# Update Device by serial
@app.put("/devices/{serial}", response_model=Device)
async def update_device_by_serial(
    serial: str, device: Device, session: Session = Depends(get_session)
):
    """Update a device by its serial number."""
    db_device = session.get(Device, serial)
    if not db_device:
        raise HTTPException(status_code=404, detail="Device not found")
    device.serial = serial
    session.add(device)
    session.commit()
    session.refresh(device)
    return device


# delete device by serial
@app.delete("/devices/{serial}", response_model=Device)
async def delete_device_by_serial(serial: str, session: Session = Depends(get_session)):
    """Delete a device by its serial number."""
    device = session.get(Device, serial)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    session.delete(device)
    session.commit()
    return device
