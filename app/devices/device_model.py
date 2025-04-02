from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class Device:
    """Model representing an Android device."""

    # Basic device information
    serial: str
    status: str

    # Device properties
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    android_version: Optional[str] = None

    # Optional additional properties
    properties: Optional[Dict[str, str]] = None

    # Runtime information
    is_connected: bool = True
    error: Optional[str] = None

    def __post_init__(self):
        """Initialize additional fields after construction."""
        if self.properties is None:
            self.properties = {}
