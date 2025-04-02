# Module for functions that use shell commands to interact with devices
import logging
from typing import Dict

logger = logging.getLogger(__name__)


def open_apk(device, package_name: str) -> bool:
    """
    Opens an installed APK using its package name on a specific device using ppadb.

    Args:
        device: ppadb device object
        package_name (str): Package name of the app (e.g. 'com.pure.indosat.care')

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Using monkey tool to launch the app
        command = f"monkey -p {package_name} -c android.intent.category.LAUNCHER 1"
        result = device.shell(command)

        # Check if command executed successfully
        # Note: shell() returns the command output, not an exit code
        success = "Error" not in result and "Exception" not in result

        if success:
            logger.info(f"Opened app {package_name} on device {device.serial}")
        else:
            logger.error(
                f"Failed to open app {package_name} on device {device.serial}: {result}"
            )

        return success
    except Exception as e:
        logger.exception(
            f"Error opening app {package_name} on device {device.serial}: {str(e)}"
        )
        return False


def get_battery_info(device) -> Dict[str, str]:
    """
    Get battery information for a device.

    Args:
        device: ppadb device object

    Returns:
        dict: Battery information (level, status, etc.)
    """
    try:
        result = device.shell("dumpsys battery")

        # Parse the battery info
        battery_info = {}
        for line in result.splitlines():
            line = line.strip()
            if ":" in line:
                key, value = line.split(":", 1)
                battery_info[key.strip()] = value.strip()

        return battery_info
    except Exception as e:
        logger.exception(
            f"Error getting battery info for device {device.serial}: {str(e)}"
        )
        return {"error": str(e)}


def press_key(device, keycode: int) -> bool:
    """
    Press a key on the device using ADB keyevent.

    Args:
        device: ppadb device object
        keycode (int): Android keycode to press (e.g., 3 for HOME)

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        result = device.shell(f"input keyevent {keycode}")
        return result == "" or "error" not in result.lower()
    except Exception as e:
        logger.exception(
            f"Error pressing key {keycode} on device {device.serial}: {str(e)}"
        )
        return False


def get_device_properties(device) -> Dict[str, str]:
    """
    Get device properties using getprop command.

    Args:
        device: ppadb device object

    Returns:
        dict: Device properties
    """
    properties = {}
    try:
        # Get basic device properties
        properties["manufacturer"] = device.shell(
            "getprop ro.product.manufacturer"
        ).strip()
        properties["model"] = device.shell("getprop ro.product.model").strip()
        properties["android_version"] = device.shell(
            "getprop ro.build.version.release"
        ).strip()
        properties["sdk_version"] = device.shell("getprop ro.build.version.sdk").strip()
        properties["device"] = device.shell("getprop ro.product.device").strip()

        return properties
    except Exception as e:
        logger.exception(
            f"Error getting properties for device {device.serial}: {str(e)}"
        )
        return {"error": str(e)}
