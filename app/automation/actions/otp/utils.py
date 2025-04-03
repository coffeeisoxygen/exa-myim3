import re
from typing import Tuple

import uiautomator2 as u2

from app.logging import get_device_logger, log_action

# Constant messages untuk deteksi state
OTP_MESSAGES = {
    "invalid": ["Invalid OTP code", "Kode OTP tidak valid"],
    "expired": ["OTP has expired", "Kode OTP telah kadaluarsa", "Invalid OTP code"],
    "sent": ["OTP successfully sent", "OTP berhasil dikirim"],
    "success": ["Verification Complete", "Verifikasi Selesai"],
}


@log_action
def get_countdown_time(ui_device: u2.Device, resource_id: str, serial: str) -> str:
    """
    Dapatkan informasi sisa waktu countdown OTP.

    Args:
        ui_device: Objek UI Automator device
        resource_id: Resource ID elemen countdown
        serial: Serial number device

    Returns:
        str: Waktu tersisa dalam format MM:SS atau "N/A" jika tidak ditemukan
    """
    logger = get_device_logger(serial)

    countdown = ui_device(resourceId=resource_id)
    if not countdown.exists:
        logger.warning("Elemen countdown tidak ditemukan")
        return "N/A"

    try:
        countdown_text = countdown.get_text()
        # Bersihkan dari spasi atau karakter lain
        countdown_text = countdown_text.strip()
        return countdown_text
    except Exception as e:
        logger.error(f"Error mendapatkan teks countdown: {str(e)}")
        return "N/A"


@log_action
def check_otp_message(
    ui_device: u2.Device, resource_ids: dict, serial: str
) -> Tuple[bool, str]:
    """
    Memeriksa pesan yang muncul setelah verifikasi OTP.

    Args:
        ui_device: Objek UI Automator device
        resource_ids: Dictionary resource IDs
        serial: Serial number device

    Returns:
        tuple: (is_success, message_type)
            is_success (bool): True jika tidak ada error, False jika ada error
            message_type (str): Tipe pesan yang terdeteksi
    """
    logger = get_device_logger(serial)

    message_text = _get_message_text(ui_device, resource_ids, logger)
    if message_text:
        return _check_message_type(message_text, logger)

    if _is_verification_complete(ui_device, resource_ids, logger):
        return True, "success"

    return True, "none"


def _get_message_text(ui_device: u2.Device, resource_ids: dict, logger) -> str:
    message_element = ui_device(resourceId=resource_ids["message_text"])
    if message_element.exists:
        message_text = message_element.get_text()
        logger.info(f"Pesan terdeteksi: {message_text}")
        return message_text
    return ""


def _check_message_type(message_text: str, logger) -> Tuple[bool, str]:
    for msg_type, patterns in OTP_MESSAGES.items():
        for pattern in patterns:
            if pattern.lower() in message_text.lower():
                if msg_type in ["invalid", "expired"]:
                    logger.error(f"OTP {msg_type}: {message_text}")
                    return False, msg_type
                elif msg_type == "sent":
                    logger.info("OTP berhasil dikirim ulang")
                    return True, msg_type
                elif msg_type == "success":
                    logger.info("Verifikasi OTP berhasil")
                    return True, msg_type
    return True, "none"


def _is_verification_complete(ui_device: u2.Device, resource_ids: dict, logger) -> bool:
    if ui_device(resourceId=resource_ids["verification_complete_text"]).exists:
        logger.info("Verifikasi OTP berhasil terdeteksi")
        return True
    return False


@log_action
def parse_timer_seconds(timer_text: str) -> int:
    """
    Parse timer text menjadi jumlah detik.

    Args:
        timer_text: Text dari timer

    Returns:
        int: Jumlah detik, 0 jika gagal parse
    """
    try:
        match = re.search(r"(\d+)", timer_text.strip())
        if match:
            return int(match.group(1))
    except Exception:
        pass
    return 0
