import logging
import os
import threading
from typing import Dict, List

import uiautomator2 as u2
from ppadb.client import Client

from app.config import ADB_HOST, ADB_PORT, ANDROID_SDK_PATH
from app.devices.command import (
    get_battery_info,
    get_device_properties,
    open_apk,
    press_key,
)
from app.devices.device_model import Device

logger = logging.getLogger(__name__)


class DeviceService:
    """Service class to manage Android devices."""

    def __init__(self, host: str = ADB_HOST, port: int = ADB_PORT):
        """Initialize the device service.

        Args:
            host: ADB server host
            port: ADB server port
        """
        self.adb_client = Client(host=host, port=port)
        self.device_cache = {}  # Cache for uiautomator2 device objects
        self.lock = threading.Lock()  # Thread safety for device cache

    def ensure_adb_running(self) -> bool:
        """
        Memastikan ADB server berjalan, jika tidak akan dicoba untuk memulainya.

        Returns:
            bool: True jika berhasil, False jika gagal
        """
        try:
            # Coba koneksi ke ADB server
            self.adb_client.version()
            logger.info("ADB server sudah berjalan")
            return True
        except Exception as e:
            logger.warning(f"ADB server tidak berjalan: {e}")

            # Coba jalankan adb start-server
            try:
                import subprocess

                # Coba beberapa kemungkinan path adb
                adb_paths = [
                    os.path.join(ANDROID_SDK_PATH, "platform-tools", "adb.exe"),
                    os.path.join(ANDROID_SDK_PATH, "platform-tools", "adb"),
                    "adb.exe",  # Coba di PATH
                    "adb",  # Coba di PATH
                ]

                for adb_path in adb_paths:
                    try:
                        logger.info(f"Mencoba menjalankan: {adb_path} start-server")
                        result = subprocess.run(
                            [adb_path, "start-server"],
                            capture_output=True,
                            text=True,
                            check=False,
                        )

                        if result.returncode == 0:
                            logger.info("ADB server berhasil dijalankan")
                            return True
                    except FileNotFoundError:
                        continue

                logger.error(
                    "Gagal menjalankan ADB server - adb executable tidak ditemukan"
                )
                return False
            except Exception as e:
                logger.error(f"Gagal menjalankan ADB server: {e}")
                return False

    def get_device(self, serial: str):
        """Get an ADB device by serial number.

        Args:
            serial: Device serial number

        Returns:
            device object or None if not found
        """
        try:
            device = self.adb_client.device(serial)
            return device
        except Exception as e:
            logger.error(f"Error getting device {serial}: {e}")
            return None

    def get_devices(self) -> List[Device]:
        """Get list of connected Android devices.

        Returns:
            List of Device objects
        """
        # Pastikan ADB server berjalan
        if not self.ensure_adb_running():
            logger.error("Tidak dapat mendapatkan devices: ADB server tidak berjalan")
            return []

        devices = []
        try:
            adb_devices = self.adb_client.devices()

            for device in adb_devices:
                # Create basic device model
                device_model = Device(
                    serial=device.serial,
                    status="device",  # If we got the device through ppadb, it's authorized
                )

                # Get additional device properties
                try:
                    properties = get_device_properties(device)
                    if "error" not in properties:
                        device_model.manufacturer = properties.get("manufacturer")
                        device_model.model = properties.get("model")
                        device_model.android_version = properties.get("android_version")
                        device_model.properties = properties
                except Exception as e:
                    device_model.error = str(e)
                    logger.exception(
                        f"Error getting properties for device {device.serial}: {e}"
                    )

                devices.append(device_model)

        except Exception as e:
            logger.exception(f"Error getting devices: {e}")

        return devices

    def get_ui_device(self, serial: str):
        """Get or create uiautomator2 device object for a specific device.

        Args:
            serial: Device serial number

        Returns:
            uiautomator2 device object
        """
        with self.lock:  # Thread-safe access to device cache
            if serial not in self.device_cache:
                try:
                    self.device_cache[serial] = u2.connect(serial)
                    logger.info(f"Connected to device {serial} with uiautomator2")
                except Exception as e:
                    logger.exception(
                        f"Error connecting to device {serial} with uiautomator2: {e}"
                    )
                    raise
            return self.device_cache[serial]

    def open_app(self, serial: str, package_name: str) -> bool:
        """Open an app on a specific device.

        Args:
            serial: Device serial number
            package_name: Package name of the app

        Returns:
            True if successful, False otherwise
        """
        device = self.get_device(serial)
        if not device:
            logger.error(f"Device {serial} not found")
            return False

        return open_apk(device, package_name)

    def get_battery_info(self, serial: str) -> Dict[str, str]:
        """Get battery information for a device.

        Args:
            serial: Device serial number

        Returns:
            Battery information
        """
        device = self.get_device(serial)
        if not device:
            logger.error(f"Device {serial} not found")
            return {"error": "Device not found"}

        return get_battery_info(device)

    def press_key(self, serial: str, keycode: int) -> bool:
        """Press a key on a device.

        Args:
            serial: Device serial number
            keycode: Android keycode to press

        Returns:
            True if successful, False otherwise
        """
        device = self.get_device(serial)
        if not device:
            logger.error(f"Device {serial} not found")
            return False

        return press_key(device, keycode)

    def execute_action(self, serial: str, action: str, *args, **kwargs):
        """Execute an action on a specific device.

        Args:
            serial: Device serial number
            action: Action to execute (e.g., 'press_home', 'click', etc.)
            args: Positional arguments for the action
            kwargs: Keyword arguments for the action

        Returns:
            Result of the action
        """
        device = self.get_device(serial)
        if not device:
            logger.error(f"Device with serial {serial} not found")
            raise ValueError(f"Device with serial {serial} not found")

        # Basic ADB actions
        if action == "shell":
            return device.shell(args[0])
        elif action == "install":
            return device.install(*args, **kwargs)
        elif action == "uninstall":
            return device.uninstall(*args, **kwargs)
        elif action == "open_app":
            return open_apk(device, args[0])
        elif action == "press_key":
            return press_key(device, args[0])
        elif action == "get_battery_info":
            return get_battery_info(device)

        # UI Automator actions
        ui_device = self.get_ui_device(serial)
        if action == "press_home":
            return ui_device.press("home")
        elif action == "press_back":
            return ui_device.press("back")
        elif action == "click":
            return ui_device.click(*args)
        elif action == "swipe":
            return ui_device.swipe(*args)
        elif action == "app_start":
            return ui_device.app_start(args[0])
        elif action == "app_stop":
            return ui_device.app_stop(args[0])
        else:
            logger.error(f"Unknown action: {action}")
            raise ValueError(f"Unknown action: {action}")
