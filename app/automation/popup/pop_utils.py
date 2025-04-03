import time
from typing import Optional

import uiautomator2 as u2

from app.logging import get_device_logger, log_action

# Resource IDs untuk popup yang umum muncul
POPUP_RESOURCE_IDS = {
    "popup_container": "com.pure.indosat.care:id/inapp_html_full_relative_layout",
    "popup_close_button": "button-2",
}


@log_action
def handle_popup(
    ui_device: u2.Device,
    serial: str,
    timeout: int = 3,
    container_id: Optional[str] = None,
    close_button_id: Optional[str] = None,
) -> bool:
    """
    Menangani popup yang mungkin muncul dalam aplikasi.

    Args:
        ui_device: Objek UI Automator device
        serial: Serial number device
        timeout: Timeout dalam detik
        container_id: Resource ID untuk container popup (opsional)
        close_button_id: Resource ID untuk tombol close popup (opsional)

    Returns:
        bool: True jika berhasil menangani popup, False jika gagal
    """
    logger = get_device_logger(serial)
    container_id = container_id or POPUP_RESOURCE_IDS["popup_container"]
    close_button_id = close_button_id or POPUP_RESOURCE_IDS["popup_close_button"]

    popup = ui_device(resourceId=container_id)
    if not popup.exists:
        return True  # Tidak ada popup, berhasil

    logger.info(f"Popup terdeteksi (container: {container_id}), mencoba menutup")
    if close_popup_by_button(ui_device, popup, close_button_id, logger):
        return True
    if close_popup_by_coordinates(ui_device, popup, close_button_id, logger):
        return True
    return close_popup_by_default_position(ui_device, popup, logger)


def close_popup_by_button(ui_device, popup, close_button_id, logger) -> bool:
    close_button = ui_device(resourceId=close_button_id)
    if close_button.exists:
        close_button.click()
        logger.info(f"Klik tombol close (id: {close_button_id})")
        time.sleep(0.5)
        if not popup.exists:
            logger.info("Popup berhasil ditutup")
            return True
        logger.warning("Popup masih terdeteksi setelah mencoba menutup")
    return False


def close_popup_by_coordinates(ui_device, popup, close_button_id, logger) -> bool:
    close_button = ui_device(resourceId=close_button_id)
    try:
        bounds = close_button.info.get("bounds")
        if bounds:
            center_x = (bounds["left"] + bounds["right"]) // 2
            center_y = (bounds["top"] + bounds["bottom"]) // 2
            ui_device.click(center_x, center_y)
            logger.info(
                f"Mencoba klik koordinat tombol close: ({center_x}, {center_y})"
            )
            time.sleep(0.5)
            if not popup.exists:
                logger.info("Popup berhasil ditutup dengan klik koordinat")
                return True
    except Exception as e:
        logger.warning(f"Error saat mencoba klik koordinat: {e}")
    return False


def close_popup_by_default_position(ui_device, popup, logger) -> bool:
    try:
        screen_width = ui_device.window_size()[0]
        ui_device.click(screen_width - 50, 100)  # Asumsi posisi tombol close
        logger.info("Mencoba klik posisi default tombol close")
        time.sleep(0.5)
        if not popup.exists:
            logger.info("Popup berhasil ditutup dengan klik posisi default")
            return True
    except Exception as e:
        logger.warning(f"Error saat mencoba klik posisi default: {e}")
    return False


@log_action
def is_popup_visible(
    ui_device: u2.Device, serial: str, container_id: Optional[str] = None
) -> bool:
    """
    Memeriksa apakah popup terlihat.

    Args:
        ui_device: Objek UI Automator device
        serial: Serial number device
        container_id: Resource ID untuk container popup (opsional)

    Returns:
        bool: True jika popup terlihat, False jika tidak
    """
    container_id = container_id or POPUP_RESOURCE_IDS["popup_container"]
    return ui_device(resourceId=container_id).exists()


@log_action
def check_and_handle_all_popups(ui_device: u2.Device, serial: str) -> bool:
    """
    Memeriksa dan menangani semua jenis popup yang mungkin muncul.
    Ekstensi untuk menangani berbagai jenis popup.

    Args:
        ui_device: Objek UI Automator device
        serial: Serial number device

    Returns:
        bool: True jika semua popup berhasil ditangani, False jika ada yang gagal
    """
    logger = get_device_logger(serial)

    # Tangani popup promo standar
    if not handle_popup(ui_device, serial):
        logger.warning("Gagal menangani popup promo")
        # Continue anyway as this is not critical

    # Tambahkan penanganan jenis popup lain di sini jika diperlukan
    # Contoh: popup notifikasi, popup konfirmasi, dll

    # Verifikasi final bahwa tidak ada popup yang tersisa
    if is_popup_visible(ui_device, serial):
        logger.warning("Masih ada popup yang terlihat setelah semua penanganan")
        return False

    return True
