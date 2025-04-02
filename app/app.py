import logging

from app.config import init_app
from app.devices.device_service import DeviceService

logger = logging.getLogger(__name__)


def main():
    """Main entry point for the application."""
    # Initialize the application
    init_app()

    logger.info("Starting EXA-MYIM3 application")

    # Create device service
    device_service = DeviceService()

    # Get and display connected devices
    devices = device_service.get_devices()

    if not devices:
        logger.warning(
            "No devices detected. Please connect a device and ensure USB debugging is enabled."
        )
        return

    logger.info(f"Found {len(devices)} device(s):")
    for i, device in enumerate(devices, 1):
        logger.info(f"Device {i}: {device.serial}")
        if device.properties:
            for key, value in device.properties.items():
                logger.info(f"  {key}: {value}")
        else:
            logger.warning(f"No properties available for device {device.serial}")

    package_name = "com.pure.indosat.care"

    for device in devices:
        serial = device.serial

        # Press HOME key first
        logger.info(f"Pressing HOME key on device {serial}")
        success = device_service.press_key(serial, 3)  # KEYCODE_HOME = 3
        logger.info(f"Press HOME result: {'Success' if success else 'Failed'}")

        # Then open the app
        logger.info(f"Opening {package_name} on device {serial}")
        app_success = device_service.open_app(serial, package_name)
        logger.info(f"Open app result: {'Success' if app_success else 'Failed'}")

        # Get battery info
        battery = device_service.get_battery_info(serial)
        if "level" in battery:
            logger.info(f"Battery level: {battery['level']}%")

    logger.info("Application completed")


if __name__ == "__main__":
    main()
