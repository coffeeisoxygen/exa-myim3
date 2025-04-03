import time
from typing import Dict, Optional

import uiautomator2 as u2

from app.logging import get_device_logger, log_action

# Resource IDs untuk popup yang umum muncul
POPUP_CONFIGS = {
    "promo": {
        "container_id": "com.pure.indosat.care:id/inapp_html_full_relative_layout",
        "close_button_id": "button-2",
        "priority": 1,
    },
    "tutorial": {
        "container_id": "com.pure.indosat.care:id/tutorialContainer",  # Ganti dengan ID sebenarnya
        "close_button_id": "com.pure.indosat.care:id/btnSkipTutorial",  # Ganti dengan ID sebenarnya
        "priority": 2,
    },
    # Tambahkan jenis popup lain sesuai kebutuhan
}


@log_action
def handle_popup(
    ui_device: u2.Device,
    serial: str,
    popup_type: Optional[str] = None,
    timeout: int = 3,
) -> bool:
    """
    Menangani popup yang mungkin muncul dalam aplikasi.

    Args:
        ui_device: Objek UI Automator device
        serial: Serial number device
        popup_type: Jenis popup yang akan ditangani (opsional, default: semua)
        timeout: Timeout dalam detik

    Returns:
        bool: True jika berhasil menangani popup, False jika gagal
    """
    logger = get_device_logger(serial)

    # Jika popup_type ditentukan, hanya cek jenis tersebut
    if popup_type and popup_type in POPUP_CONFIGS:
        config = POPUP_CONFIGS[popup_type]
        return _handle_specific_popup(ui_device, serial, popup_type, config, logger)

    # Jika tidak, cek semua popup berdasarkan prioritas
    popup_types = sorted(POPUP_CONFIGS.items(), key=lambda x: x[1].get("priority", 999))

    for p_type, config in popup_types:
        # Cek apakah popup ini terlihat
        container = ui_device(resourceId=config["container_id"])
        if container.exists:
            logger.info(f"Popup terdeteksi: {p_type}")
            if _handle_specific_popup(ui_device, serial, p_type, config, logger):
                return True
            # Jika gagal menangani, coba popup berikutnya

    # Tidak ada popup yang terdeteksi
    return True


def _handle_specific_popup(
    ui_device: u2.Device, serial: str, popup_type: str, config: Dict, logger
) -> bool:
    """Menangani jenis popup tertentu."""
    container = ui_device(resourceId=config["container_id"])
    if not container.exists:
        return True  # Popup ini tidak ada

    logger.info(f"Menangani popup {popup_type} (container: {config['container_id']})")

    # Coba strategi penanganan khusus untuk jenis popup ini jika ada
    if popup_type == "tutorial" and "tutorial_handling" in globals():
        return tutorial_handling(ui_device, container, config, logger)

    # Jika tidak ada strategi khusus, gunakan strategi default
    if close_popup_by_button(ui_device, container, config["close_button_id"], logger):
        return True
    if close_popup_by_coordinates(
        ui_device, container, config["close_button_id"], logger
    ):
        return True
    return close_popup_by_default_position(ui_device, container, logger)


def close_popup_by_button(ui_device, popup, close_button_id, logger) -> bool:
    """Menutup popup dengan mengklik tombol."""
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
    """Menutup popup dengan mengklik koordinat tombol."""
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
    """Menutup popup dengan mengklik posisi default."""
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


# Contoh penanganan khusus untuk popup tutorial
def tutorial_handling(ui_device, popup, config, logger) -> bool:
    """Penanganan khusus untuk popup tutorial."""
    # Misalnya tutorial mungkin perlu swipe atau klik beberapa kali
    try:
        # Cek apakah ada tombol "Skip All" atau semacamnya
        skip_all = ui_device(text="Skip All")
        if skip_all.exists:
            skip_all.click()
            logger.info("Klik 'Skip All' untuk melewati tutorial")
            time.sleep(0.5)
            if not popup.exists:
                return True

        # Jika tidak ada Skip All, gunakan close button biasa
        return close_popup_by_button(
            ui_device, popup, config["close_button_id"], logger
        )
    except Exception as e:
        logger.warning(f"Error saat menangani tutorial: {e}")
        return False


@log_action
def is_popup_visible(
    ui_device: u2.Device, serial: str, popup_type: Optional[str] = None
) -> bool:
    """
    Memeriksa apakah popup terlihat.

    Args:
        ui_device: Objek UI Automator device
        serial: Serial number device
        popup_type: Jenis popup tertentu (opsional)

    Returns:
        bool: True jika popup terlihat, False jika tidak
    """
    if popup_type and popup_type in POPUP_CONFIGS:
        container_id = POPUP_CONFIGS[popup_type]["container_id"]
        return ui_device(resourceId=container_id).exists()

    # Cek semua jenis popup
    for config in POPUP_CONFIGS.values():
        if ui_device(resourceId=config["container_id"]).exists:
            return True

    return False


@log_action
def check_and_handle_all_popups(ui_device: u2.Device, serial: str) -> bool:
    """
    Memeriksa dan menangani semua jenis popup yang mungkin muncul.

    Args:
        ui_device: Objek UI Automator device
        serial: Serial number device

    Returns:
        bool: True jika semua popup berhasil ditangani, False jika ada yang gagal
    """
    logger = get_device_logger(serial)

    # Tangani semua jenis popup
    if not handle_popup(ui_device, serial):
        logger.warning("Gagal menangani beberapa popup")

    # Verifikasi final bahwa tidak ada popup yang tersisa
    if is_popup_visible(ui_device, serial):
        logger.warning("Masih ada popup yang terlihat setelah semua penanganan")
        return False

    return True
