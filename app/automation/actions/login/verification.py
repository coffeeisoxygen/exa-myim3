import time

import uiautomator2 as u2

from app.logging import get_device_logger, log_action


@log_action
def verify_app_opened(ui_device: u2.Device, resource_id: str, serial: str) -> bool:
    """
    Verifikasi aplikasi sudah terbuka.

    Args:
        ui_device: Objek UI Automator device
        resource_id: Resource ID action bar root
        serial: Serial number device

    Returns:
        bool: True jika aplikasi terbuka, False jika tidak
    """
    logger = get_device_logger(serial)

    if not ui_device(resourceId=resource_id).exists:
        logger.error("Aplikasi tidak terbuka dengan benar")
        return False

    logger.info("Aplikasi terbuka dengan benar")
    return True


@log_action
def verify_login_success(
    ui_device: u2.Device, resource_ids: dict, serial: str, timeout: int = 15
) -> bool:
    """
    Verifikasi login berhasil - bisa berarti langsung ke OTP atau ke home.

    Args:
        ui_device: Objek UI Automator device
        resource_ids: Dictionary resource IDs
        serial: Serial number device
        timeout: Waktu maksimum menunggu (detik)

    Returns:
        bool: True jika login berhasil, False jika gagal
    """
    logger = get_device_logger(serial)
    start_time = time.time()

    while time.time() - start_time < timeout:
        # Cek apakah sudah di halaman OTP (yang paling diharapkan)
        otp_title = ui_device(resourceId="com.pure.indosat.care:id/tvLoginVerification")
        otp_input = ui_device(resourceId="com.pure.indosat.care:id/etOtpView")

        if otp_title.exists or otp_input.exists:
            logger.info("Login berhasil - halaman OTP terdeteksi")
            return True

        # Cek apakah sudah di halaman home (alternatif)
        if ui_device(resourceId=resource_ids["home_indicator"]).exists:
            logger.info("Login berhasil - indikator home terdeteksi")
            return True

        # Cek pesan error
        error_message = ui_device(textContains="invalid")
        if error_message.exists:
            message = error_message.get_text()
            logger.error(f"Login gagal - pesan error: {message}")
            return False

        # Masih di halaman login?
        continue_btn = ui_device(resourceId=resource_ids["continue_button"])
        if continue_btn.exists:
            # Jika continue button masih ada, mungkin ada masalah
            if continue_btn.info.get("enabled", False):
                logger.warning(
                    "Login gagal - masih di halaman login dengan button enabled"
                )
                return False

        # Tunggu sebentar dan coba lagi
        time.sleep(1)

    logger.error(
        f"Login timeout setelah {timeout} detik - tidak ada indikator sukses terdeteksi"
    )
    return False
