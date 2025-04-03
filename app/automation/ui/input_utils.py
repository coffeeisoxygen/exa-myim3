import time
from typing import Optional

import uiautomator2 as u2

from app.logging import get_device_logger, log_action

# Screen dimensions default (bisa dikonfigurasi)
DEFAULT_SCREEN_CENTER_X = 540
DEFAULT_SCREEN_CENTER_Y = 800


@log_action
def input_text(
    ui_device: u2.Device,
    input_field_id: str,
    text: str,
    serial: str,
    verify_enabled_id: Optional[str] = None,
) -> bool:
    """
    Input teks dengan strategi bertingkat untuk memastikan validasi terpicu.

    Args:
        ui_device: Objek UI Automator device
        input_field_id: Resource ID field input
        text: Teks yang akan diinput
        serial: Serial number device
        verify_enabled_id: ID elemen yang akan dicek enabled nya (opsional)

    Returns:
        bool: True jika berhasil, False jika gagal
    """
    logger = get_device_logger(serial)
    logger.info(f"Mencoba input teks: {text}")

    # Temukan field input
    input_field = ui_device(resourceId=input_field_id)
    if not input_field.exists:
        logger.error(f"Field input dengan ID {input_field_id} tidak ditemukan")
        return False

    # Klik pada field untuk fokus
    input_field.click()
    time.sleep(0.5)

    # Cari EditText di dalam container
    edit_text = ui_device(className="android.widget.EditText")
    if not edit_text.exists:
        logger.error("EditText tidak ditemukan")
        return False

    # Mencoba tiga strategi input:
    if try_direct_input(ui_device, edit_text, text, serial, verify_enabled_id):
        return True

    if try_edit_last_digit(ui_device, edit_text, text, serial, verify_enabled_id):
        return True

    if try_digit_by_digit(ui_device, edit_text, text, serial, verify_enabled_id):
        return True

    logger.error("Gagal mengaktifkan validasi setelah semua strategi input")
    return False


@log_action
def try_direct_input(
    ui_device: u2.Device,
    edit_text,
    text: str,
    serial: str,
    verify_enabled_id: Optional[str] = None,
) -> bool:
    """
    Strategi 1: Input langsung kemudian trigger validasi.

    Args:
        ui_device: Objek UI Automator device
        edit_text: Elemen input teks
        text: Teks yang akan diinput
        serial: Serial number device
        verify_enabled_id: ID elemen yang akan dicek enabled nya (opsional)

    Returns:
        bool: True jika berhasil, False jika gagal
    """
    logger = get_device_logger(serial)

    edit_text.set_text(text)
    time.sleep(0.5)

    # Klik di luar untuk trigger validasi
    ui_device.click(DEFAULT_SCREEN_CENTER_X, DEFAULT_SCREEN_CENTER_Y)
    time.sleep(0.5)

    # Cek apakah validasi berhasil
    if verify_enabled_id and not is_element_enabled(ui_device, verify_enabled_id):
        logger.debug("Strategi direct input gagal mengaktifkan validasi")
        return False

    logger.info("Strategi direct input berhasil")
    return True


@log_action
def try_edit_last_digit(
    ui_device: u2.Device,
    edit_text,
    text: str,
    serial: str,
    verify_enabled_id: Optional[str] = None,
) -> bool:
    """
    Strategi 2: Hapus satu digit lalu input kembali.

    Args:
        ui_device: Objek UI Automator device
        edit_text: Elemen input teks
        text: Teks yang akan diinput
        serial: Serial number device
        verify_enabled_id: ID elemen yang akan dicek enabled nya (opsional)

    Returns:
        bool: True jika berhasil, False jika gagal
    """
    logger = get_device_logger(serial)

    current_text = edit_text.get_text()
    if not current_text:
        return False

    # Hapus digit terakhir
    edit_text.set_text(current_text[:-1])
    time.sleep(0.3)
    # Input kembali digit terakhir
    edit_text.set_text(current_text)
    time.sleep(0.5)

    # Cek apakah validasi berhasil
    if verify_enabled_id and not is_element_enabled(ui_device, verify_enabled_id):
        logger.debug("Strategi edit_last_digit gagal mengaktifkan validasi")
        return False

    logger.info("Strategi edit_last_digit berhasil")
    return True


@log_action
def try_digit_by_digit(
    ui_device: u2.Device,
    edit_text,
    text: str,
    serial: str,
    verify_enabled_id: Optional[str] = None,
) -> bool:
    """
    Strategi 3: Input digit per digit (paling reliable tapi lebih lambat).

    Args:
        ui_device: Objek UI Automator device
        edit_text: Elemen input teks
        text: Teks yang akan diinput
        serial: Serial number device
        verify_enabled_id: ID elemen yang akan dicek enabled nya (opsional)

    Returns:
        bool: True jika berhasil, False jika gagal
    """
    logger = get_device_logger(serial)

    logger.info("Mencoba input digit per digit")
    edit_text.clear_text()
    time.sleep(0.5)

    for digit in text:
        edit_text.set_text(edit_text.get_text() + digit)
        time.sleep(0.2)  # Jeda kecil antar digit

    time.sleep(0.5)

    # Cek apakah validasi berhasil
    if verify_enabled_id and not is_element_enabled(ui_device, verify_enabled_id):
        logger.debug("Strategi digit_by_digit gagal mengaktifkan validasi")
        return False

    logger.info("Strategi digit_by_digit berhasil")
    return True


@log_action
def is_element_enabled(ui_device: u2.Device, resource_id: str) -> bool:
    """
    Memeriksa apakah elemen dengan resource_id tertentu enabled.

    Args:
        ui_device: Objek UI Automator device
        resource_id: Resource ID elemen

    Returns:
        bool: True jika elemen enabled, False jika tidak
    """
    element = ui_device(resourceId=resource_id)
    if not element.exists:
        return False

    return element.info.get("enabled") == True
