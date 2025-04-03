import logging
import os
import subprocess
from typing import Tuple

from app.config.settings import ANDROID_SDK_PATH

logger = logging.getLogger(__name__)


class ADBServer:
    """Kelas untuk pengelolaan ADB server."""

    def __init__(self):
        """Inisialisasi ADB server manager."""
        self.adb_path = self._find_adb_executable()

    def _find_adb_executable(self) -> str:
        """
        Mencari lokasi adb executable.

        Returns:
            Path ke adb executable
        """
        # Coba cari di Android SDK path dan di PATH sistem
        possible_paths = [
            os.path.join(ANDROID_SDK_PATH, "platform-tools", "adb.exe"),
            os.path.join(ANDROID_SDK_PATH, "platform-tools", "adb"),
            "adb.exe",  # Coba di PATH
            "adb",  # Coba di PATH
        ]

        for path in possible_paths:
            try:
                result = subprocess.run(
                    [path, "version"], capture_output=True, text=True, check=False
                )
                if result.returncode == 0:
                    logger.info(f"ADB executable ditemukan: {path}")
                    return path
            except FileNotFoundError:
                continue

        logger.error("ADB executable tidak ditemukan")
        return "adb"  # Default fallback

    def is_running(self) -> bool:
        """
        Memeriksa apakah ADB server sudah berjalan.

        Returns:
            True jika server berjalan, False jika tidak
        """
        try:
            result = subprocess.run(
                [self.adb_path, "devices"],
                capture_output=True,
                text=True,
                check=False,
                timeout=5,
            )

            return (
                result.returncode == 0 and "List of devices attached" in result.stdout
            )
        except Exception as e:
            logger.error(f"Error memeriksa status ADB server: {e}")
            return False

    def start(self) -> bool:
        """
        Menjalankan ADB server jika belum berjalan.

        Returns:
            True jika berhasil, False jika gagal
        """
        if self.is_running():
            logger.info("ADB server sudah berjalan")
            return True

        logger.info("Mencoba menjalankan ADB server...")
        try:
            result = subprocess.run(
                [self.adb_path, "start-server"],
                capture_output=True,
                text=True,
                check=False,
                timeout=10,
            )

            success = result.returncode == 0

            if success:
                logger.info("ADB server berhasil dijalankan")
            else:
                logger.error(f"Gagal menjalankan ADB server: {result.stderr}")

            return success
        except Exception as e:
            logger.error(f"Error menjalankan ADB server: {e}")
            return False

    def kill(self) -> bool:
        """
        Menghentikan ADB server.

        Returns:
            True jika berhasil, False jika gagal
        """
        logger.info("Menghentikan ADB server...")
        try:
            result = subprocess.run(
                [self.adb_path, "kill-server"],
                capture_output=True,
                text=True,
                check=False,
                timeout=5,
            )

            success = result.returncode == 0

            if success:
                logger.info("ADB server berhasil dihentikan")
            else:
                logger.error(f"Gagal menghentikan ADB server: {result.stderr}")

            return success
        except Exception as e:
            logger.error(f"Error menghentikan ADB server: {e}")
            return False

    def execute_command(self, command: list, timeout: int = 30) -> Tuple[bool, str]:
        """
        Menjalankan perintah ADB.

        Args:
            command: List argumen perintah (tanpa 'adb')
            timeout: Batas waktu eksekusi dalam detik

        Returns:
            Tuple (success, output)
        """
        if not self.is_running() and not self.start():
            return False, "ADB server tidak berjalan dan gagal dijalankan"

        try:
            cmd = [self.adb_path] + command

            result = subprocess.run(
                cmd, capture_output=True, text=True, check=False, timeout=timeout
            )

            if result.returncode == 0:
                return True, result.stdout.strip()
            else:
                return False, result.stderr.strip()
        except subprocess.TimeoutExpired:
            return False, f"Perintah timeout setelah {timeout} detik"
        except Exception as e:
            return False, str(e)
