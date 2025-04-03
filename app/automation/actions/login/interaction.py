import time
import uiautomator2 as u2

from app.logging import get_device_logger, log_action
from app.automation.ui.input_utils import is_element_enabled


@log_action
def click_continue(ui_device: u2.Device, resource_id: str, serial: str) -> bool:
    """
    Klik tombol Continue.

    Args:
        ui_device: Objek UI Automator device
        resource_id: Resource ID tombol Continue
        serial: Serial number device

    Returns:
        bool: True jika berhasil, False jika gagal
    """
    logger = get_device_logger(serial)

    continue_button = ui_device(resourceId=resource_id)
    if not continue_button.exists or not is_element_enabled(ui_device, resource_id):
        logger.error("Button Continue tidak ditemukan atau tidak enabled")
        return False

    continue_button.click()
    logger.info("Klik button Continue")
    return True
