import logging
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any, Dict

logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """Status enum untuk services"""

    STOPPED = auto()
    STARTING = auto()
    RUNNING = auto()
    STOPPING = auto()
    ERROR = auto()


class BaseService(ABC):
    """Base class untuk semua service dalam aplikasi."""

    def __init__(self, name: str):
        """Inisialisasi service."""
        self.name = name
        self.status = ServiceStatus.STOPPED
        self.is_running = False
        self.error = None

    @abstractmethod
    async def start(self):
        """Start service."""
        self.status = ServiceStatus.STARTING
        # Implementation in subclasses

    @abstractmethod
    async def stop(self):
        """Stop service."""
        self.status = ServiceStatus.STOPPING
        # Implementation in subclasses

    def get_info(self) -> Dict[str, Any]:
        """Get service information."""
        return {
            "name": self.name,
            "status": self.status.name,
            "is_running": self.is_running,
            "error": str(self.error) if self.error else None,
        }
