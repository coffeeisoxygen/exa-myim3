import uiautomator2 as u2

from app.automation.popup.pop_utils import handle_popup
from app.automation.ui.input_utils import input_text, is_element_enabled
from app.logging import get_device_logger, log_action

# Element ResourceIDs
RESOURCE_IDS = {
    "action_bar_root": "com.pure.indosat.care:id/action_bar_root",
    "account_tab": "com.pure.indosat.care:id/navigation_account",
    "login_container": "com.pure.indosat.care:id/clLogin",
    "mobile_field": "com.pure.indosat.care:id/tilMobileNumber",
    "continue_button": "com.pure.indosat.care:id/btnContinue",
    "home_indicator": "com.pure.indosat.care:id/home",
}


@log_action
def login_flow(device_service, serial: str, phone_number: str) -> bool:
    """
    Flow untuk login ke aplikasi MYIM3.

    Args:
        device_service: Service untuk mengelola device
        serial: Serial number device
        phone_number: Nomor telepon untuk login

    Returns:
        bool: True jika login berhasil, False jika gagal
    """
    logger = get_device_logger(serial)
    ui_device = device_service.get_ui_device(serial)

    # 1. Verifikasi aplikasi terbuka
    if not verify_app_opened(ui_device, serial):
        return False

    # 2. Tangani popup jika ada
    if not handle_popup(ui_device, serial):
        logger.warning("Ada masalah saat menangani popup, melanjutkan flow")

    # 3. Navigasi ke tab Account
    if not navigate_to_account(ui_device, serial):
        return False

    # 4. Input nomor telepon
    if not input_text(
        ui_device,
        RESOURCE_IDS["mobile_field"],
        phone_number,
        serial,
        RESOURCE_IDS["continue_button"],
    ):
        return False

    # 5. Klik button Continue
    if not click_continue(ui_device, serial):
        return False

    # 6. Verifikasi login berhasil
    if not verify_login_success(ui_device, serial):
        return False

    logger.info(f"Login berhasil untuk nomor {phone_number}")
    return True


@log_action
def verify_app_opened(ui_device: u2.Device, serial: str) -> bool:
    """Verifikasi aplikasi sudah terbuka."""
    logger = get_device_logger(serial)

    if not ui_device(resourceId=RESOURCE_IDS["action_bar_root"]).exists:
        logger.error("Aplikasi tidak terbuka dengan benar")
        return False

    logger.info("Aplikasi terbuka dengan benar")
    return True


@log_action
def navigate_to_account(ui_device: u2.Device, serial: str) -> bool:
    """Navigasi ke tab Account."""
    logger = get_device_logger(serial)

    account_tab = ui_device(resourceId=RESOURCE_IDS["account_tab"])
    if not account_tab.exists:
        logger.error("Navigation bar tidak ditemukan")
        return False

    account_tab.click()
    logger.info("Klik tab Account")

    # Tunggu elemen container login muncul
    if not ui_device(resourceId=RESOURCE_IDS["login_container"]).wait(timeout=5):
        logger.error("Login container tidak muncul")
        return False

    logger.info("Berhasil navigasi ke halaman login")
    return True


@log_action
def click_continue(ui_device: u2.Device, serial: str) -> bool:
    """Klik tombol Continue."""
    logger = get_device_logger(serial)

    continue_button = ui_device(resourceId=RESOURCE_IDS["continue_button"])
    if not continue_button.exists or not is_element_enabled(
        ui_device, RESOURCE_IDS["continue_button"]
    ):
        logger.error("Button Continue tidak ditemukan atau tidak enabled")
        return False

    continue_button.click()
    logger.info("Klik button Continue")
    return True


@log_action
def verify_login_success(ui_device: u2.Device, serial: str) -> bool:
    """Verifikasi login berhasil."""
    logger = get_device_logger(serial)

    # Tunggu indikator home muncul
    if not ui_device(resourceId=RESOURCE_IDS["home_indicator"]).wait(
        exists=True, timeout=10
    ):
        logger.error("Login gagal - indikator home tidak muncul")
        return False

    logger.info("Login berhasil - indikator home terdeteksi")
    return True
