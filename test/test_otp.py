import argparse
import logging
import os
import sys
import time

# Tambahkan root directory ke path agar bisa mengimport dari app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.automation.flows.login_flow import login_flow
from app.automation.flows.otp_flow import otp_flow
from app.config import init_app
from app.devices.device_service import DeviceService

# Konfigurasi logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("test_otp")


def get_otp_from_user() -> str:
    """
    Meminta input OTP dari user melalui terminal.

    Returns:
        str: Kode OTP yang dimasukkan user
    """
    print("\n" + "=" * 50)
    print("🔐 MASUKKAN KODE OTP YANG DITERIMA VIA SMS")
    print("=" * 50)
    otp_code = input("OTP code: ").strip()
    print("=" * 50 + "\n")
    return otp_code


def test_otp_flow(
    serial: str, phone_number: str, otp_code: str = "", manual_input: bool = True
):
    """
    Tes login dan OTP flow dengan device dan nomor telepon tertentu

    Args:
        serial: Serial number device untuk test
        phone_number: Nomor telepon untuk login
        otp_code: Kode OTP (opsional, jika tidak diisi akan minta input)
        manual_input: True untuk meminta OTP dari user, False untuk menggunakan otp_code

    Returns:
        bool: True jika flow berhasil, False jika gagal
    """
    logger.info(
        f"Memulai pengujian login dan OTP dengan device {serial} dan nomor {phone_number}"
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
    logger.info(f"Memulai proses login dengan nomor {phone_number}")
    if not login_flow(device_service, serial, phone_number):
        logger.error("❌ TEST GAGAL: Login flow tidak berhasil")
        return False

    logger.info("Login berhasil, lanjut ke OTP flow")

    # Dapatkan OTP dari user jika perlu
    if manual_input or not otp_code:
        otp_code = get_otp_from_user()

    # Eksekusi OTP flow
    logger.info(f"Memulai verifikasi OTP dengan kode: {otp_code}")
    result = otp_flow(device_service, serial, otp_code)

    if result:
        logger.info("✅ TEST BERHASIL: Login dan OTP flow selesai dengan sukses")
    else:
        logger.error("❌ TEST GAGAL: OTP flow tidak berhasil")

    return result


def parse_args():
    parser = argparse.ArgumentParser(
        description="Test login dan OTP flow untuk aplikasi myIM3"
    )
    parser.add_argument("serial", help="Serial number device untuk test")
    parser.add_argument("phone", help="Nomor telepon untuk login")
    parser.add_argument(
        "--otp", help="Kode OTP (opsional, jika tidak diisi akan minta input)"
    )
    parser.add_argument(
        "--package",
        default="com.pure.indosat.care",
        help="Package name aplikasi (default: com.pure.indosat.care)",
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Gunakan OTP yang disediakan tanpa input manual",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    test_otp_flow(
        args.serial, args.phone, otp_code=args.otp, manual_input=not args.auto
    )


if __name__ == "__main__":
    main()
