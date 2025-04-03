from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel

class Device(SQLModel, table=True):
    """Model untuk menyimpan informasi device."""

    serial: str = Field(primary_key=True)
    model: str
    manufacturer: Optional[str] = None
    name: str
    note: Optional[str] = None
    is_active: bool = Field(default=False)
    is_connected: bool = Field(default=False)
    connection_test: Optional[str] = None
    last_seen: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)
