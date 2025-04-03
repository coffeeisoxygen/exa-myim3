import logging
import os
import subprocess
from typing import Dict, List, Optional, Tuple

from app.core.settings import settings_manager

logger = logging.getLogger(__name__)


class ADBHelper:
    """Helper untuk mengelola ADB executable dan perintah."""

    def __init__(self):
        """Initialize ADB helper."""
        self.adb_path = ""
        self.is_initialized = False

    def initialize(self) -> bool:
        """
        Mencari ADB executable dan memastikan bisa digunakan.

        Returns:
            True jika berhasil ditemukan dan diverifikasi, False jika gagal
        """
        if self.is_initialized and self.adb_path:
            return True

        # 1. Coba ambil dari setting database
        adb_path = settings_manager.get("adb_path")
        if adb_path and self._verify_adb_path(adb_path):
            self.adb_path = adb_path
            self.is_initialized = True
            logger.info(f"Using ADB from settings: {self.adb_path}")
            return True

        # 2. Coba cari di lokasi umum
        possible_paths = self._get_possible_adb_paths()
        for path in possible_paths:
            if self._verify_adb_path(path):
                self.adb_path = path
                self.is_initialized = True

                # Simpan ke settings
                settings_manager.set(
                    "adb_path", path, "ADB executable path yang terdeteksi otomatis"
                )

                logger.info(f"Found ADB executable: {self.adb_path}")
                return True

        # 3. Tidak ditemukan
        logger.error("ADB executable not found")
        self.is_initialized = False
        return False

    def _get_possible_adb_paths(self) -> List[str]:
        """Get possible ADB executable paths."""
        paths = []

        # Check environment variables
        android_home = os.environ.get("ANDROID_HOME")
        android_sdk_root = os.environ.get("ANDROID_SDK_ROOT")

        if android_home:
            paths.append(os.path.join(android_home, "platform-tools", "adb.exe"))
            paths.append(os.path.join(android_home, "platform-tools", "adb"))

        if android_sdk_root:
            paths.append(os.path.join(android_sdk_root, "platform-tools", "adb.exe"))
            paths.append(os.path.join(android_sdk_root, "platform-tools", "adb"))

        # Common locations
        paths.extend(
            [
                r"C:\Program Files (x86)\Android\android-sdk\platform-tools\adb.exe",
                r"C:\Program Files\Android\android-sdk\platform-tools\adb.exe",
                "/usr/local/bin/adb",
                "/usr/bin/adb",
                "adb.exe",  # Check in PATH
                "adb",  # Check in PATH
            ]
        )

        return paths

    def _verify_adb_path(self, adb_path: str) -> bool:
        """Verify that ADB exists and is executable."""
        try:
            result = subprocess.run(
                [adb_path, "version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5,
            )
            return result.returncode == 0 and "Android Debug Bridge" in result.stdout
        except (FileNotFoundError, subprocess.SubprocessError):
            return False

    def ensure_server_running(self) -> bool:
        """
        Memastikan ADB server berjalan.

        Returns:
            True jika server berhasil dijalankan atau sudah berjalan, False jika gagal
        """
        if not self.is_initialized and not self.initialize():
            return False

        # Cek jika server sudah berjalan
        if self.is_server_running():
            return True

        # Start server
        try:
            result = subprocess.run(
                [self.adb_path, "start-server"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=10,
            )
            success = result.returncode == 0

            if success:
                logger.info("ADB server started successfully")
            else:
                logger.error(f"Failed to start ADB server: {result.stderr}")

            return success
        except Exception as e:
            logger.error(f"Error starting ADB server: {e}")
            return False

    def is_server_running(self) -> bool:
        """
        Cek apakah ADB server sudah berjalan.

        Returns:
            True jika server berjalan, False jika tidak
        """
        if not self.is_initialized and not self.initialize():
            return False

        try:
            result = subprocess.run(
                [self.adb_path, "devices"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5,
            )
            return (
                result.returncode == 0 and "List of devices attached" in result.stdout
            )
        except Exception as e:
            logger.error(f"Error checking ADB server status: {e}")
            return False

    def kill_server(self) -> bool:
        """
        Menghentikan ADB server.

        Returns:
            True jika server berhasil dihentikan, False jika gagal
        """
        if not self.is_initialized and not self.initialize():
            return False

        try:
            result = subprocess.run(
                [self.adb_path, "kill-server"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5,
            )
            success = result.returncode == 0

            if success:
                logger.info("ADB server stopped successfully")
            else:
                logger.error(f"Failed to stop ADB server: {result.stderr}")

            return success
        except Exception as e:
            logger.error(f"Error stopping ADB server: {e}")
            return False

    def get_devices(self) -> List[Dict[str, str]]:
        """
        Mendapatkan daftar device yang terhubung.

        Returns:
            List of dictionaries containing device information
        """
        if not self.ensure_server_running():
            return []

        try:
            result = subprocess.run(
                [self.adb_path, "devices", "-l"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5,
            )

            if result.returncode != 0:
                logger.error(f"Error getting devices: {result.stderr}")
                return []

            devices = []
            lines = result.stdout.strip().split("\n")

            # Skip header line
            for line in lines[1:]:
                if not line.strip():
                    continue

                parts = line.split()
                if len(parts) >= 2:
                    device = {"serial": parts[0], "status": parts[1]}

                    # Extract model if present
                    for part in parts[2:]:
                        if "model:" in part:
                            device["model"] = part.split(":", 1)[1]
                            break

                    if "model" not in device:
                        device["model"] = "Unknown"

                    devices.append(device)

            return devices
        except Exception as e:
            logger.error(f"Error getting devices: {e}")
            return []

    def execute_command(
        self, command: List[str], device_serial: Optional[str] = None, timeout: int = 30
    ) -> Tuple[bool, str]:
        """
        Execute an ADB command.

        Args:
            command: List of command arguments
            device_serial: Optional device serial number
            timeout: Command timeout in seconds

        Returns:
            Tuple of (success, output/error)
        """
        if not self.ensure_server_running():
            return False, "ADB server not running"

        try:
            cmd = [self.adb_path]

            if device_serial:
                cmd.extend(["-s", device_serial])

            cmd.extend(command)

            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout,
            )

            if result.returncode == 0:
                return True, result.stdout.strip()
            else:
                return False, result.stderr.strip()
        except subprocess.TimeoutExpired:
            return False, f"Command timed out after {timeout} seconds"
        except Exception as e:
            return False, str(e)


# Create singleton instance
adb_helper = ADBHelper()
