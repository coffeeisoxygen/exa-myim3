from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# Request Schemas
class DeviceCreate(BaseModel):
    """Schema untuk membuat device baru."""

    serial: str
    model: str
    manufacturer: Optional[str] = None
    name: str
    note: Optional[str] = None
    is_active: bool = False
    connection_test: Optional[str] = None


class DeviceUpdate(BaseModel):
    """Schema untuk update device."""

    model: Optional[str] = None
    manufacturer: Optional[str] = None
    name: Optional[str] = None
    note: Optional[str] = None
    is_active: Optional[bool] = None
    is_connected: Optional[bool] = None
    connection_test: Optional[str] = None


# Response Schemas
class DeviceResponse(BaseModel):
    """Schema untuk response device."""

    serial: str
    model: str
    manufacturer: Optional[str]
    name: str
    note: Optional[str]
    is_active: bool
    is_connected: bool
    last_seen: Optional[datetime]
    created_at: datetime


class DeviceDetail(DeviceResponse):
    """Schema untuk detail device dengan info tambahan."""

    connection_test: Optional[str]
    adb_status: Optional[str]
    additional_info: Optional[dict] = None
