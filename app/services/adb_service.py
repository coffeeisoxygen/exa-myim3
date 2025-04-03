import asyncio
import logging
from typing import Any, Dict, Tuple

from app.adb.server import ADBServer
from app.services.base_service import BaseService, ServiceStatus

logger = logging.getLogger(__name__)


class ADBService(BaseService):
    """Service untuk pengelolaan ADB server."""

    def __init__(self):
        """Initialize ADB service."""
        super().__init__(name="ADB Server")
        self.adb_server = ADBServer()
        self.devices_cache = []
        self.status = ServiceStatus.STOPPED
        self.is_running = False

    async def start(self):
        """Start ADB server."""
        await super().start()

        try:
            # Gunakan loop terpisah untuk menjalankan operasi blocking
            is_started = await asyncio.to_thread(self.adb_server.start)

            if is_started:
                self.status = ServiceStatus.RUNNING
                self.is_running = True
                logger.info("ADB server berhasil dijalankan")
            else:
                self.status = ServiceStatus.ERROR
                self.error = "Gagal menjalankan ADB server"
                logger.error("Gagal menjalankan ADB server")
        except Exception as e:
            self.status = ServiceStatus.ERROR
            self.error = e
            logger.exception(f"Error saat menjalankan ADB server: {e}")

    async def stop(self):
        """Stop ADB server."""
        await super().stop()

        try:
            # Gunakan loop terpisah untuk operasi blocking
            is_killed = await asyncio.to_thread(self.adb_server.kill)

            if is_killed:
                logger.info("ADB server berhasil dihentikan")
            else:
                logger.warning("Gagal menghentikan ADB server dengan bersih")
        except Exception as e:
            logger.error(f"Error saat menghentikan ADB server: {e}")

        self.status = ServiceStatus.STOPPED
        self.is_running = False

    async def execute_command(
        self, command: list, timeout: int = 30
    ) -> Tuple[bool, str]:
        """
        Menjalankan perintah ADB secara asynchronous.

        Args:
            command: List arguments perintah
            timeout: Batas waktu eksekusi dalam detik

        Returns:
            Tuple (success, output)
        """
        if not self.is_running:
            return False, "ADB service tidak berjalan"

        try:
            # Jalankan command di thread terpisah
            return await asyncio.to_thread(
                self.adb_server.execute_command, command, timeout
            )
        except Exception as e:
            logger.error(f"Error menjalankan perintah ADB: {e}")
            return False, str(e)

    def get_info(self) -> Dict[str, Any]:
        """Get service information."""
        info = super().get_info()
        info.update(
            {
                "adb_path": self.adb_server.adb_path,
            }
        )
        return info
