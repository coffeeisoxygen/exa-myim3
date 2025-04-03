from app.automation.actions.login import (
    click_continue,
    navigate_to_account,
    verify_app_opened,
    verify_login_success,
)
from app.automation.popup.pop_utils import handle_popup
from app.automation.ui.input_utils import input_text
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
        bool: True jika login berhasil (termasuk ke OTP), False jika gagal
    """
    logger = get_device_logger(serial)
    ui_device = device_service.get_ui_device(serial)

    # 1. Verifikasi aplikasi terbuka
    if not verify_app_opened(ui_device, RESOURCE_IDS["action_bar_root"], serial):
        return False

    # 2. Tangani popup jika ada
    if not handle_popup(ui_device, serial):
        logger.warning("Ada masalah saat menangani popup, melanjutkan flow")

    # 3. Navigasi ke tab Account
    if not navigate_to_account(ui_device, RESOURCE_IDS, serial):
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
    if not click_continue(ui_device, RESOURCE_IDS["continue_button"], serial):
        return False

    # 6. Verifikasi login berhasil (bisa ke OTP atau home)
    if not verify_login_success(ui_device, RESOURCE_IDS, serial):
        return False

    logger.info(f"Login berhasil untuk nomor {phone_number}")
    return True
