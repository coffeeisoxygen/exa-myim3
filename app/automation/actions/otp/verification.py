import time

import uiautomator2 as u2

from app.automation.actions.otp.utils import check_otp_message
from app.logging import get_device_logger, log_action


@log_action
def verify_otp_page(ui_device: u2.Device, resource_ids: dict, serial: str) -> bool:
    """
    Verifikasi berada di halaman OTP.

    Args:
        ui_device: Objek UI Automator device
        resource_ids: Dictionary resource IDs
        serial: Serial number device

    Returns:
        bool: True jika berada di halaman OTP, False jika tidak
    """
    logger = get_device_logger(serial)

    # Cek title "Login Verification"
    if not ui_device(resourceId=resource_ids["otp_title"]).exists:
        logger.error("Halaman OTP tidak terdeteksi - title tidak ditemukan")
        return False

    # Cek text "OTP Code was sent"
    if not ui_device(resourceId=resource_ids["otp_sent_text"]).exists:
        logger.error("Halaman OTP tidak terdeteksi - text OTP sent tidak ditemukan")
        return False

    # Cek field input OTP
    if not ui_device(resourceId=resource_ids["otp_input"]).exists:
        logger.error("Field input OTP tidak ditemukan")
        return False

    logger.info("Berhasil verifikasi halaman OTP")
    return True


@log_action
def verify_home_page(
    ui_device: u2.Device, resource_ids: dict, serial: str, timeout: int = 20
) -> bool:
    """
    Verifikasi berhasil navigasi ke halaman home setelah OTP.

    Args:
        ui_device: Objek UI Automator device
        resource_ids: Dictionary resource IDs
        serial: Serial number device
        timeout: Waktu maksimum menunggu (detik)

    Returns:
        bool: True jika sukses, False jika gagal
    """
    logger = get_device_logger(serial)
    start_time = time.time()

    while time.time() - start_time < timeout:
        # Cek pesan error atau sukses
        is_success, message_type = check_otp_message(ui_device, resource_ids, serial)
        if not is_success:
            logger.error(f"Terdeteksi pesan error: {message_type}")
            return False

        # Jika masih dalam proses verifikasi (sukses), tunggu
        if (
            message_type == "success"
            and ui_device(resourceId=resource_ids["verification_timer"]).exists
        ):
            logger.info("Masih dalam proses verifikasi, menunggu...")
            time.sleep(1)
            continue

        # Cek indikator home
        if ui_device(resourceId=resource_ids["home_indicator"]).exists:
            logger.info("Verifikasi OTP berhasil - indikator home terdeteksi")
            return True

        # Cek dashboard view
        if ui_device(resourceId=resource_ids["dashboard_view"]).exists:
            logger.info("Verifikasi OTP berhasil - dashboard terdeteksi")
            return True

        # Tunggu sebentar sebelum check lagi
        time.sleep(1)

    logger.error(f"Timeout ({timeout}s) menunggu halaman home")
    return False
