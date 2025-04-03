from datetime import datetime
from typing import List, Optional

from sqlmodel import Session, select

from app.devices.models import Device


class DeviceRepository:
    """Repository untuk operasi database pada device."""

    def __init__(self, session: Session):
        """
        Initialize repository with database session.

        Args:
            session: Database session
        """
        self.session = session

    def get_by_serial(self, serial: str) -> Optional[Device]:
        """
        Get device by serial number.

        Args:
            serial: Device serial number

        Returns:
            Device if found, None otherwise
        """
        return self.session.get(Device, serial)

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Device]:
        """
        Get all devices with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of devices
        """
        statement = select(Device).offset(skip).limit(limit)
        return list(self.session.exec(statement).all())

    def get_connected(self) -> List[Device]:
        """
        Get all connected devices.

        Returns:
            List of connected devices
        """
        statement = select(Device).where(Device.is_connected is True)
        return list(self.session.exec(statement).all())

    def get_active(self) -> List[Device]:
        """
        Get all active devices.

        Returns:
            List of active devices
        """
        statement = select(Device).where(Device.is_active is True)
        return list(self.session.exec(statement).all())

    def create(self, device: Device) -> Device:
        """
        Create a new device.

        Args:
            device: Device to create

        Returns:
            Created device
        """
        self.session.add(device)
        self.session.commit()
        self.session.refresh(device)
        return device

    def update(self, device: Device) -> Device:
        """
        Update an existing device.

        Args:
            device: Device with updated fields

        Returns:
            Updated device
        """
        self.session.add(device)
        self.session.commit()
        self.session.refresh(device)
        return device

    def delete(self, serial: str) -> bool:
        """
        Delete a device.

        Args:
            serial: Serial number of device to delete

        Returns:
            True if deleted, False if not found
        """
        device = self.get_by_serial(serial)
        if not device:
            return False

        self.session.delete(device)
        self.session.commit()
        return True

    def update_connection_status(
        self, serial: str, is_connected: bool
    ) -> Optional[Device]:
        """
        Update connection status of a device.

        Args:
            serial: Device serial number
            is_connected: New connection status

        Returns:
            Updated device if found, None otherwise
        """
        device = self.get_by_serial(serial)
        if not device:
            return None

        device.is_connected = is_connected
        device.last_seen = datetime.now() if is_connected else device.last_seen

        self.session.add(device)
        self.session.commit()
        self.session.refresh(device)
        return device

    def sync_devices(self, connected_serials: List[str]) -> List[Device]:
        """
        Sync connection status of all devices.

        Args:
            connected_serials: List of serial numbers of connected devices

        Returns:
            List of all devices after syncing
        """
        # Get all devices
        devices = self.get_all(limit=1000)

        # Update connection status
        for device in devices:
            is_connected = device.serial in connected_serials
            if device.is_connected != is_connected:
                device.is_connected = is_connected
                device.last_seen = datetime.now() if is_connected else device.last_seen
                self.session.add(device)

        self.session.commit()

        # Return updated devices
        return self.get_all(limit=1000)
