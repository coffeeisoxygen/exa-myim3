import argparse
import logging
import os
import sys
import time

# Tambahkan root directory ke path agar bisa mengimport dari app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.automation.flows.login_flow import login_flow
from app.config import init_app
from app.devices.device_service import DeviceService

# Konfigurasi logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("test_login")


def test_login_flow(serial: str, phone_number: str):
    """
    Tes login flow dengan device dan nomor telepon tertentu

    Args:
        serial: Serial number device untuk test
        phone_number: Nomor telepon untuk login
    """
    logger.info(
        f"Memulai pengujian login dengan device {serial} dan nomor {phone_number}"
    )

    # Initialize app
    init_app()

    # Buat device service
    device_service = DeviceService()

    # Verifikasi device tersedia
    devices = device_service.get_devices()
    device_found = False

    for device in devices:
        if device.serial == serial:
            device_found = True
            logger.info(f"Device ditemukan: {device.serial} ({device.model})")
            break

    if not device_found:
        logger.error(f"Device dengan serial {serial} tidak ditemukan")
        return False

    # Persiapan: press home dan buka aplikasi
    logger.info("Menekan tombol HOME dan membuka aplikasi")
    device_service.press_key(serial, 3)  # KEYCODE_HOME = 3
    time.sleep(1)

    device_service.open_app(serial, "com.pure.indosat.care")
    time.sleep(3)  # Beri waktu aplikasi untuk terbuka

    # Coba login
    result = login_flow(device_service, serial, phone_number)

    if result:
        logger.info("✅ TEST BERHASIL: Login flow selesai dengan sukses")
    else:
        logger.error("❌ TEST GAGAL: Login flow tidak berhasil")

    return result


def parse_args():
    parser = argparse.ArgumentParser(description="Test login flow untuk aplikasi myIM3")
    parser.add_argument("serial", help="Serial number device untuk test")
    parser.add_argument("phone", help="Nomor telepon untuk login")
    parser.add_argument(
        "--package",
        default="com.pure.indosat.care",
        help="Package name aplikasi (default: com.pure.indosat.care)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    test_login_flow(args.serial, args.phone)


if __name__ == "__main__":
    main()
