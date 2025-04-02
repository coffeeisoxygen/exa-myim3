# Module for functions that use shell commands not related to any xpath
import logging

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
