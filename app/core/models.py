from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Setting(SQLModel, table=True):
    """Model untuk menyimpan setting aplikasi."""

    key: str = Field(primary_key=True)
    value: str
    description: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.now)
