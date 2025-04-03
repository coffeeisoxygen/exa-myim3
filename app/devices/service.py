import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from app.core.database import get_session
from app.core.events import event_bus
from app.core.settings import settings_manager
from app.devices.adb import adb_helper
from app.devices.models import Device
from app.devices.repository import DeviceRepository
from app.devices.schemas import DeviceCreate, DeviceUpdate

logger = logging.getLogger(__name__)


class DeviceService:
    """Service for managing Android devices."""

    def __init__(self):
        """Initialize device service."""
        self.devices_cache: List[Dict[str, str]] = []
        self._polling_task = None
        self._polling_interval = int(settings_manager.get("device_poll_interval", "10"))
        self._stop_polling = asyncio.Event()

        # Subscribe to events
        logger.debug("Subscribing device service to app events")
        event_bus.subscribe("app.startup", self.on_app_startup)
        event_bus.subscribe("app.shutdown", self.on_app_shutdown)

    async def on_app_startup(self):
        """Handler untuk event startup aplikasi."""
        logger.info("Device service handling app startup event")
        await self.initialize()

    async def on_app_shutdown(self):
        """Handler untuk event shutdown aplikasi."""
        logger.info("Device service handling app shutdown event")
        await self.shutdown()

    async def initialize(self) -> bool:
        """
        Initialize device service.

        Returns:
            True if initialized successfully, False otherwise
        """
        logger.info("Initializing device service...")

        # Initialize ADB
        if not adb_helper.initialize():
            logger.error("Failed to initialize ADB helper")
            return False

        # Start ADB server
        if not adb_helper.ensure_server_running():
            logger.error("Failed to start ADB server")
            return False

        # Start device polling
        self._start_polling()

        logger.info("Device service initialized successfully")
        return True

    async def shutdown(self) -> None:
        """Shutdown device service."""
        logger.info("Shutting down device service...")

        # Stop polling
        if self._polling_task:
            logger.debug("Stopping device polling task")
            self._stop_polling.set()
            try:
                await self._polling_task
                logger.info("Device polling stopped")
            except asyncio.CancelledError:
                logger.warning("Device polling task was cancelled")

        # Kill ADB server
        if adb_helper.is_server_running():
            logger.debug("Stopping ADB server")
            adb_helper.kill_server()

        logger.info("Device service shutdown complete")

    def _start_polling(self) -> None:
        """Start polling for connected devices."""

        async def _poll_devices():
            logger.info(
                f"Starting device polling (interval: {self._polling_interval}s)"
            )

            while not self._stop_polling.is_set():
                try:
                    # Get connected devices from ADB
                    logger.debug("Polling for connected devices")
                    devices = adb_helper.get_devices()

                    # Check for changes
                    if self._has_device_changes(devices):
                        logger.info(
                            f"Device changes detected, found {len(devices)} devices"
                        )

                        # Sync with database
                        await self._sync_devices_with_db(devices)

                        # Publish event
                        await event_bus.publish("devices.changed", devices=devices)

                    # Update cache
                    self.devices_cache = devices

                except Exception as e:
                    logger.error(f"Error during device polling: {e}")

                # Wait for next poll or until stop signal
                try:
                    await asyncio.wait_for(
                        self._stop_polling.wait(), timeout=self._polling_interval
                    )
                except asyncio.TimeoutError:
                    # This is expected, just continue polling
                    pass

        # Start polling task
        logger.debug("Creating device polling task")
        self._polling_task = asyncio.create_task(_poll_devices())

    def _has_device_changes(self, new_devices: List[Dict[str, str]]) -> bool:
        """
        Check if there are changes in connected devices.

        Args:
            new_devices: List of new device dictionaries

        Returns:
            True if changes detected, False otherwise
        """
        if len(new_devices) != len(self.devices_cache):
            return True

        # Check for changes in serials
        new_serials = {d["serial"] for d in new_devices}
        old_serials = {d["serial"] for d in self.devices_cache}

        return new_serials != old_serials

    async def _sync_devices_with_db(self, devices: List[Dict[str, str]]) -> None:
        """
        Sync connected devices with database.

        Args:
            devices: List of connected device dictionaries
        """
        try:
            # Get connected serials
            connected_serials = [d["serial"] for d in devices]

            with get_session() as session:
                repository = DeviceRepository(session)

                # Sync connection status
                repository.sync_devices(connected_serials)

                # For new devices, add them to DB with basic info
                for device_info in devices:
                    serial = device_info["serial"]
                    device = repository.get_by_serial(serial)

                    if not device:
                        # Get more info about the device
                        model = device_info.get("model", "Unknown")

                        # Get manufacturer using ADB
                        manufacturer = "Unknown"
                        success, output = adb_helper.execute_command(
                            ["shell", "getprop", "ro.product.manufacturer"],
                            device_serial=serial,
                        )
                        if success and output:
                            manufacturer = output.strip()

                        # Create new device
                        device = Device(
                            serial=serial,
                            model=model,
                            manufacturer=manufacturer,
                            name=f"{manufacturer} {model}",
                            is_active=True,  # Auto-activate new devices
                            is_connected=True,
                            last_seen=datetime.now(),
                        )
                        repository.create(device)
                        logger.info(f"Added new device to database: {serial}")
        except Exception as e:
            logger.error(f"Error syncing devices with database: {e}")

    async def get_device_info(self, serial: str) -> Dict:
        """
        Get detailed information about a device.

        Args:
            serial: Device serial number

        Returns:
            Dictionary with device information
        """
        device_in_cache = self._get_device_from_cache(serial)
        device = self._get_device_from_db(serial)

        if not device:
            return {"error": f"Device {serial} not found in database"}

        info = self._get_basic_device_info(device, device_in_cache)

        if device_in_cache:
            additional_info = await self._get_additional_device_info(serial)
            info.update(additional_info)

        return info

    def _get_device_from_cache(self, serial: str) -> Optional[Dict]:
        """Retrieve device from cache."""
        return next((d for d in self.devices_cache if d["serial"] == serial), None)

    def _get_device_from_db(self, serial: str) -> Optional[Device]:
        """Retrieve device from database."""
        with get_session() as session:
            repository = DeviceRepository(session)
            return repository.get_by_serial(serial)

    def _get_basic_device_info(
        self, device: Device, device_in_cache: Optional[Dict]
    ) -> Dict:
        """Get basic information about a device."""
        return {
            "serial": device.serial,
            "model": device.model,
            "manufacturer": device.manufacturer,
            "name": device.name,
            "is_active": device.is_active,
            "is_connected": device_in_cache is not None,
            "last_seen": device.last_seen,
        }

    async def _get_additional_device_info(self, serial: str) -> Dict:
        """Get additional information about a connected device."""
        try:
            props = await self._get_device_properties(serial)
            battery_info = await self._get_battery_info(serial)

            return {
                "properties": props,
                "battery": battery_info,
                "android_version": props.get("ro.build.version.release", "Unknown"),
                "sdk_version": props.get("ro.build.version.sdk", "Unknown"),
            }
        except Exception as e:
            logger.error(f"Error getting detailed device info: {e}")
            return {"error": str(e)}

    async def _get_device_properties(self, serial: str) -> Dict:
        """Retrieve device properties using ADB."""
        success, output = adb_helper.execute_command(
            ["shell", "getprop"], device_serial=serial
        )
        if not success:
            return {}

        props = {}
        for line in output.split("\n"):
            if "[" in line and "]" in line:
                try:
                    key = line.split("[")[1].split("]")[0]
                    value = line.split("[", 2)[2].split("]")[0]
                    props[key] = value
                except (IndexError, ValueError):
                    continue
        return props

    async def _get_battery_info(self, serial: str) -> Dict:
        """Retrieve battery information using ADB."""
        success, output = adb_helper.execute_command(
            ["shell", "dumpsys", "battery"], device_serial=serial
        )
        if not success:
            return {}

        battery_info = {}
        for line in output.split("\n"):
            line = line.strip()
            if ":" in line:
                key, value = line.split(":", 1)
                battery_info[key.strip()] = value.strip()
        return battery_info

    async def create_device(self, device_data: DeviceCreate) -> Device:
        """
        Create a new device.

        Args:
            device_data: Device creation data

        Returns:
            Created device
        """
        with get_session() as session:
            repository = DeviceRepository(session)

            # Check if device already exists
            existing = repository.get_by_serial(device_data.serial)
            if existing:
                raise ValueError(
                    f"Device with serial {device_data.serial} already exists"
                )

            # Create device
            device = Device(
                serial=device_data.serial,
                model=device_data.model,
                manufacturer=device_data.manufacturer,
                name=device_data.name,
                note=device_data.note,
                is_active=device_data.is_active,
                connection_test=device_data.connection_test,
                created_at=datetime.now(),
            )

            return repository.create(device)

    async def update_device(
        self, serial: str, device_data: DeviceUpdate
    ) -> Optional[Device]:
        """
        Update a device.

        Args:
            serial: Device serial number
            device_data: Update data

        Returns:
            Updated device if found, None otherwise
        """
        with get_session() as session:
            repository = DeviceRepository(session)

            # Get existing device
            device = repository.get_by_serial(serial)
            if not device:
                return None

            # Update fields if provided
            update_data = device_data.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(device, key, value)

            return repository.update(device)

    async def delete_device(self, serial: str) -> bool:
        """
        Delete a device.

        Args:
            serial: Device serial number

        Returns:
            True if deleted, False if not found
        """
        with get_session() as session:
            repository = DeviceRepository(session)
            return repository.delete(serial)

    async def get_all_devices(self, skip: int = 0, limit: int = 100) -> List[Device]:
        """
        Get all devices.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of devices
        """
        with get_session() as session:
            repository = DeviceRepository(session)
            return repository.get_all(skip, limit)

    async def execute_command(
        self, serial: str, command: List[str], timeout: int = 30
    ) -> Tuple[bool, str]:
        """
        Execute command on device.

        Args:
            serial: Device serial number
            command: Command to execute
            timeout: Command timeout in seconds

        Returns:
            Tuple of (success, output/error)
        """
        # Check if device is connected
        device_in_cache = next(
            (d for d in self.devices_cache if d["serial"] == serial), None
        )
        if not device_in_cache:
            return False, f"Device {serial} is not connected"

        return adb_helper.execute_command(
            command, device_serial=serial, timeout=timeout
        )


# Singleton instance
device_service = DeviceService()
