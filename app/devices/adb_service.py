import logging
import os
import re
import subprocess
from typing import Dict, List, Optional, Tuple

from app.config.settings import ANDROID_SDK_PATH

logger = logging.getLogger(__name__)


class ADBService:
    """Service untuk berinteraksi dengan ADB executable."""

    def __init__(self, host: str = "127.0.0.1", port: int = 5037):
        """
        Inisialisasi ADB Service.

        Args:
            host: ADB server host
            port: ADB server port
        """
        self.host = host
        self.port = port
        self.adb_path = self._find_adb_executable()

    def _find_adb_executable(self) -> str:
        """
        Mencari lokasi adb executable.

        Returns:
            Path ke adb executable
        """
        # Coba cari di Android SDK path dari settings
        possible_paths = [
            os.path.join(ANDROID_SDK_PATH, "platform-tools", "adb.exe"),
            os.path.join(ANDROID_SDK_PATH, "platform-tools", "adb"),
            "adb.exe",  # Coba di PATH
            "adb",  # Coba di PATH
        ]

        for path in possible_paths:
            try:
                # Cek apakah executable ada
                result = subprocess.run(
                    [path, "version"], capture_output=True, text=True, check=False
                )
                if result.returncode == 0:
                    logger.info(f"ADB executable ditemukan: {path}")
                    return path
            except FileNotFoundError:
                continue

        logger.error("ADB executable tidak ditemukan")
        return "adb"  # Default fallback, akan gagal nanti jika tidak ada

    def ensure_server_running(self) -> bool:
        """
        Memastikan ADB server berjalan.

        Returns:
            True jika server berhasil dijalankan, False jika gagal
        """
        try:
            # Cek apakah server sudah berjalan
            result = subprocess.run(
                [self.adb_path, "devices"], capture_output=True, text=True, check=False
            )

            if "List of devices attached" in result.stdout:
                logger.info("ADB server sudah berjalan")
                return True

            # Jika belum, coba start server
            logger.info("Mencoba start ADB server...")
            result = subprocess.run(
                [self.adb_path, "start-server"],
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode == 0:
                logger.info("ADB server berhasil dijalankan")
                return True
            else:
                logger.error(f"Gagal menjalankan ADB server: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"Error memastikan ADB server berjalan: {e}")
            return False

    def get_devices(self) -> List[Dict[str, str]]:
        """
        Mendapatkan daftar device yang terhubung.

        Returns:
            List dictionary device dengan serial, status, dan model
        """
        if not self.ensure_server_running():
            logger.error("ADB server tidak berjalan, tidak bisa mendapatkan devices")
            return []

        try:
            result = subprocess.run(
                [self.adb_path, "devices", "-l"],
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode != 0:
                logger.error(f"Error mendapatkan devices: {result.stderr}")
                return []

            devices = []
            for line in result.stdout.strip().split("\n")[1:]:  # Skip header line
                if not line.strip():
                    continue

                parts = line.split()
                if len(parts) >= 2:
                    device = {"serial": parts[0], "status": parts[1]}

                    # Extract model
                    model_match = re.search(r"model:(\S+)", line)
                    if model_match:
                        device["model"] = model_match.group(1)
                    else:
                        device["model"] = "Unknown"

                    devices.append(device)

            return devices

        except Exception as e:
            logger.error(f"Error mendapatkan devices: {e}")
            return []

    def execute_command(
        self, command: List[str], device_serial: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Menjalankan perintah ADB.

        Args:
            command: List command arguments
            device_serial: Serial device (jika None, command dijalankan tanpa spesifik device)

        Returns:
            Tuple (success, output)
                - success: True jika command berhasil, False jika gagal
                - output: Output command atau error message
        """
        if not self.ensure_server_running():
            return False, "ADB server tidak berjalan"

        try:
            cmd = [self.adb_path]

            # Add device serial if provided
            if device_serial:
                cmd.extend(["-s", device_serial])

            cmd.extend(command)

            result = subprocess.run(cmd, capture_output=True, text=True, check=False)

            if result.returncode == 0:
                return True, result.stdout.strip()
            else:
                return False, result.stderr.strip()

        except Exception as e:
            return False, str(e)

    def get_device_properties(self, serial: str) -> Dict[str, str]:
        """
        Mendapatkan properties device.

        Args:
            serial: Serial number device

        Returns:
            Dictionary properties device (model, manufacturer, dll)
        """
        success, output = self.execute_command(["shell", "getprop"], serial)
        if not success:
            logger.error(f"Error mendapatkan properties device {serial}: {output}")
            return {}

        properties = {}
        try:
            # Parse getprop output
            for line in output.split("\n"):
                match = re.match(r"\[([^\]]+)\]: \[([^\]]*)\]", line)
                if match:
                    key, value = match.groups()
                    properties[key] = value

            # Extract common properties
            return {
                "manufacturer": properties.get("ro.product.manufacturer", "Unknown"),
                "model": properties.get("ro.product.model", "Unknown"),
                "android_version": properties.get(
                    "ro.build.version.release", "Unknown"
                ),
                "sdk_version": properties.get("ro.build.version.sdk", "Unknown"),
                "serial": serial,
                "properties": properties,
            }
        except Exception as e:
            logger.error(f"Error memproses properties device {serial}: {e}")
            return {"serial": serial, "error": str(e)}
