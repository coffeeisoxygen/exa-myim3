from fastapi import Depends, FastAPI
from sqlmodel import Session

from app.config.database import get_session
from app.database.models import Device

app = FastAPI()

@app.post("/devices/", response_model=Device)
async def create_device(device: Device, session: Session = Depends(get_session)):
    """Create a new device in the database."""
    session.add(device)
    session.commit()
    session.refresh(device)
    return device
