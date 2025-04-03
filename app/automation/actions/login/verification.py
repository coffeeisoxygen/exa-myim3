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
    ui_device: u2.Device, resource_id: str, serial: str, timeout: int = 10
) -> bool:
    """
    Verifikasi login berhasil.

    Args:
        ui_device: Objek UI Automator device
        resource_id: Resource ID indikator home
        serial: Serial number device
        timeout: Waktu maksimum menunggu (detik)

    Returns:
        bool: True jika login berhasil, False jika gagal
    """
    logger = get_device_logger(serial)

    # Tunggu indikator home muncul
    if not ui_device(resourceId=resource_id).wait(exists=True, timeout=timeout):
        logger.error("Login gagal - indikator home tidak muncul")
        return False

    logger.info("Login berhasil - indikator home terdeteksi")
    return True
