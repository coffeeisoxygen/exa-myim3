import re
import time

import uiautomator2 as u2

from app.automation.actions.otp.utils import (
    check_otp_message,
    get_countdown_time,
    parse_timer_seconds,
)
from app.logging import get_device_logger, log_action


@log_action
def input_otp_code(
    ui_device: u2.Device, resource_id: str, otp_code: str, serial: str
) -> bool:
    """
    Input kode OTP.

    Args:
        ui_device: Objek UI Automator device
        resource_id: Resource ID field input OTP
        otp_code: Kode OTP untuk verifikasi
        serial: Serial number device

    Returns:
        bool: True jika berhasil, False jika gagal
    """
    logger = get_device_logger(serial)

    # Field OTP memerlukan pendekatan input khusus
    otp_field = ui_device(resourceId=resource_id)
    if not otp_field.exists:
        logger.error("Field input OTP tidak ditemukan")
        return False

    # Klik pada field untuk fokus
    otp_field.click()
    time.sleep(0.5)

    # Clear field dulu untuk jaga-jaga
    otp_field.clear_text()
    time.sleep(0.5)

    # Input OTP
    otp_field.send_keys(otp_code)
    logger.info(f"Input OTP: {otp_code}")

    # Tunggu validasi aplikasi
    time.sleep(1)

    return True


@log_action
def click_verify(ui_device: u2.Device, resource_ids: dict, serial: str) -> bool:
    """
    Klik tombol verifikasi OTP dan tangani respons.

    Args:
        ui_device: Objek UI Automator device
        resource_ids: Dictionary resource IDs
        serial: Serial number device

    Returns:
        bool: True jika berhasil, False jika gagal
    """
    logger = get_device_logger(serial)

    # Cari tombol verifikasi dengan resource ID yang benar
    verify_button = ui_device(resourceId=resource_ids["verify_button"])

    # Jika tombol tidak ditemukan dengan resource ID, coba dengan teks
    if not verify_button.exists:
        # Coba cari dengan teks (dalam bahasa Inggris atau Indonesia)
        verify_button = ui_device(text="Verify")
        if not verify_button.exists:
            verify_button = ui_device(text="Verifikasi")

        if not verify_button.exists:
            logger.error("Tombol verifikasi tidak ditemukan")
            return False

    # Cek apakah tombol enabled
    if not verify_button.info.get("enabled"):
        logger.error("Tombol verifikasi tidak enabled, mungkin OTP belum valid")
        return False

    # Klik tombol
    verify_button.click()
    logger.info("Klik tombol verifikasi OTP")

    # Tunggu sebentar untuk respons
    time.sleep(2)

    # Periksa pesan yang muncul
    is_success, message_type = check_otp_message(ui_device, resource_ids, serial)

    if not is_success:
        logger.error(f"Verifikasi gagal dengan pesan tipe: {message_type}")
        return False

    # Jika sukses, tunggu verifikasi selesai jika masih dalam proses
    if message_type == "success":
        # Cek apakah ada timer countdown untuk redirect
        timer = ui_device(resourceId=resource_ids["verification_timer"])
        if timer.exists:
            logger.info("Menunggu redirect otomatis setelah verifikasi...")
            try:
                timer_text = timer.get_text().strip()
                seconds = parse_timer_seconds(timer_text)
                # Tambah 2 detik untuk jaga-jaga
                wait_time = seconds + 2
                logger.info(f"Menunggu {wait_time} detik untuk redirect...")
                time.sleep(wait_time)
            except Exception as e:
                logger.warning(f"Gagal parse timer, menunggu 5 detik default: {e}")
                time.sleep(5)

    return True


@log_action
def try_resend_otp(ui_device: u2.Device, resource_ids: dict, serial: str) -> bool:
    """
    Coba resend OTP jika sudah bisa (countdown habis).

    Args:
        ui_device: Objek UI Automator device
        resource_ids: Dictionary resource IDs
        serial: Serial number device

    Returns:
        bool: True jika berhasil resend, False jika gagal
    """
    logger = get_device_logger(serial)

    if not _is_countdown_finished(ui_device, resource_ids, serial, logger):
        return False

    resend_button = _find_resend_button(ui_device, resource_ids, logger)
    if not resend_button or not _is_button_enabled(resend_button, logger):
        return False

    resend_button.click()
    logger.info("Klik tombol resend OTP")
    time.sleep(2)

    return _verify_resend_success(ui_device, resource_ids, serial, logger)


def _is_countdown_finished(ui_device, resource_ids, serial, logger) -> bool:
    countdown_text = get_countdown_time(ui_device, resource_ids["countdown"], serial)
    if countdown_text == "N/A":
        logger.warning("Tidak dapat menentukan status countdown")
        return False
    if countdown_text != "00:00":
        match = re.search(r"(\d+):(\d+)", countdown_text)
        if match and (int(match.group(1)) > 0 or int(match.group(2)) > 0):
            logger.info(
                f"Masih ada waktu countdown ({countdown_text}), belum bisa resend"
            )
            return False
    return True


def _find_resend_button(ui_device, resource_ids, logger):
    resend_button = ui_device(resourceId=resource_ids["resend_button"])
    if not resend_button.exists:
        for text in ["Resend OTP", "Kirim Ulang OTP", "Resend", "Kirim Ulang"]:
            resend_button = ui_device(text=text)
            if resend_button.exists:
                break
    if not resend_button.exists:
        logger.error("Tombol resend OTP tidak ditemukan")
        return None
    return resend_button


def _is_button_enabled(button, logger) -> bool:
    if not button.info.get("enabled", True):
        logger.error("Tombol resend OTP tidak enabled")
        return False
    return True


def _verify_resend_success(ui_device, resource_ids, serial, logger) -> bool:
    new_countdown = get_countdown_time(ui_device, resource_ids["countdown"], serial)
    if new_countdown not in ["00:00", "N/A"]:
        logger.info(f"Resend OTP berhasil, countdown reset ke {new_countdown}")
        return True
    elif new_countdown == "00:00":
        logger.warning("Countdown tidak berubah, resend mungkin gagal")
        return False
    else:
        logger.warning(
            f"Tidak dapat memverifikasi resend OTP berhasil, countdown: {new_countdown}"
        )
        return False
