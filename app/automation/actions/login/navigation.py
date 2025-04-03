import uiautomator2 as u2

from app.logging import get_device_logger, log_action


@log_action
def navigate_to_account(
    ui_device: u2.Device, resource_ids: dict, serial: str, timeout: int = 5
) -> bool:
    """
    Navigasi ke tab Account.

    Args:
        ui_device: Objek UI Automator device
        resource_ids: Dictionary resource IDs
        serial: Serial number device
        timeout: Timeout untuk menunggu container login (detik)

    Returns:
        bool: True jika berhasil, False jika gagal
    """
    logger = get_device_logger(serial)

    account_tab = ui_device(resourceId=resource_ids["account_tab"])
    if not account_tab.exists:
        logger.error("Navigation bar tidak ditemukan")
        return False

    account_tab.click()
    logger.info("Klik tab Account")

    # Tunggu elemen container login muncul
    if not ui_device(resourceId=resource_ids["login_container"]).wait(timeout=timeout):
        logger.error("Login container tidak muncul")
        return False

    logger.info("Berhasil navigasi ke halaman login")
    return True
