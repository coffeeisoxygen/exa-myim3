import re
import time

import uiautomator2 as u2

from app.automation.popup.pop_utils import handle_popup
from app.logging import get_device_logger, log_action

# Element ResourceIDs untuk halaman OTP
RESOURCE_IDS = {
    # Penanda halaman OTP
    "otp_title": "com.pure.indosat.care:id/tvLoginVerification",
    "otp_sent_text": "com.pure.indosat.care:id/tvOtpSentContent",
    "phone_number": "com.pure.indosat.care:id/tvMSISDN",
    "input_instruction": "com.pure.indosat.care:id/tvInputCode",
    # Input OTP
    "otp_input": "com.pure.indosat.care:id/etOtpView",
    # Button verifikasi (yang benar)
    "verify_button": "com.pure.indosat.care:id/btnVerify",
    # Countdown dan Resend OTP
    "countdown": "com.pure.indosat.care:id/tvCountdown",
    "resend_button": "com.pure.indosat.care:id/tvResendOTP",  # Perlu diverifikasi
    # Indikator home untuk verifikasi sukses
    "home_indicator": "com.pure.indosat.care:id/home",
    # Tampilan home (dashboard) setelah login
    "dashboard_view": "com.pure.indosat.care:id/dashBoardView",
    # Message responses
    "message_text": "com.pure.indosat.care:id/tvMessage",
    # Verification success indicators
    "verification_complete_text": "com.pure.indosat.care:id/tvVerifyingYourNumber",
    "verification_message": "com.pure.indosat.care:id/tvPleaseWait",
    "verification_timer": "com.pure.indosat.care:id/tvTimer",
}

# Constant messages untuk deteksi state
OTP_MESSAGES = {
    "invalid": ["Invalid OTP code", "Kode OTP tidak valid"],
    "expired": ["OTP has expired", "Kode OTP telah kadaluarsa", "Invalid OTP code"],
    "sent": ["OTP successfully sent", "OTP berhasil dikirim"],
    "success": ["Verification Complete", "Verifikasi Selesai"],
}


@log_action
def otp_flow(device_service, serial: str, otp_code: str, max_resend: int = 1) -> bool:
    """
    Flow untuk verifikasi OTP dengan penanganan berbagai skenario.
    """
    logger = get_device_logger(serial)
    ui_device = device_service.get_ui_device(serial)
    resend_count = 0

    # 1. Verifikasi halaman OTP
    if not verify_otp_page(ui_device, serial):
        return False

    # 2. Tangani popup jika ada
    if not handle_popup(ui_device, serial):
        logger.warning("Ada masalah saat menangani popup, melanjutkan flow")

    # Loop untuk mencoba input dan verifikasi OTP
    while resend_count <= max_resend:
        # 3. Cek countdown timer
        remaining_time = get_countdown_time(ui_device, serial)
        logger.info(f"Sisa waktu OTP: {remaining_time}")

        # Jika countdown tidak terdeteksi atau 00:00, coba resend jika belum melebihi batas
        if (
            remaining_time == "N/A" or remaining_time == "00:00"
        ) and resend_count < max_resend:
            logger.info(
                f"OTP mungkin expired, mencoba resend (percobaan {resend_count + 1}/{max_resend})"
            )
            if try_resend_otp(ui_device, serial):
                resend_count += 1
                logger.info(f"Menunggu OTP baru setelah resend ke-{resend_count}")
                time.sleep(5)  # Tunggu OTP baru
                continue

        # 4. Input kode OTP
        if not input_otp_code(ui_device, serial, otp_code):
            return False

        # 5. Klik tombol verifikasi
        if click_verify(ui_device, serial):
            # 6. Verifikasi hasil
            is_success, message_type = check_otp_message(ui_device, serial)

            if not is_success:
                # Jika invalid/expired dan masih bisa resend
                if message_type in ["invalid", "expired"] and resend_count < max_resend:
                    logger.info(
                        f"OTP {message_type}, mencoba resend (percobaan {resend_count + 1}/{max_resend})"
                    )
                    if try_resend_otp(ui_device, serial):
                        resend_count += 1
                        logger.info(
                            f"Menunggu OTP baru setelah resend ke-{resend_count}"
                        )
                        time.sleep(5)  # Tunggu OTP baru
                        continue
                    else:
                        logger.error("Gagal melakukan resend OTP")
                        return False
                else:
                    logger.error(f"OTP {message_type} dan tidak bisa resend lagi")
                    return False

            # 7. Verifikasi home page jika belum ada error
            if verify_home_page(ui_device, serial):
                logger.info(f"OTP berhasil diverifikasi untuk device {serial}")
                return True

        # Increment retry counter jika gagal
        resend_count += 1

    logger.error(f"Gagal verifikasi OTP setelah {resend_count} percobaan")
    return False


@log_action
def verify_otp_page(ui_device: u2.Device, serial: str) -> bool:
    """Verifikasi berada di halaman OTP."""
    logger = get_device_logger(serial)

    # Cek title "Login Verification"
    if not ui_device(resourceId=RESOURCE_IDS["otp_title"]).exists:
        logger.error("Halaman OTP tidak terdeteksi - title tidak ditemukan")
        return False

    # Cek text "OTP Code was sent"
    if not ui_device(resourceId=RESOURCE_IDS["otp_sent_text"]).exists:
        logger.error("Halaman OTP tidak terdeteksi - text OTP sent tidak ditemukan")
        return False

    # Cek field input OTP
    if not ui_device(resourceId=RESOURCE_IDS["otp_input"]).exists:
        logger.error("Field input OTP tidak ditemukan")
        return False

    logger.info("Berhasil verifikasi halaman OTP")
    return True


@log_action
def input_otp_code(ui_device: u2.Device, serial: str, otp_code: str) -> bool:
    """Input kode OTP."""
    logger = get_device_logger(serial)

    # Field OTP memerlukan pendekatan input khusus karena mungkin berbeda dengan field teks biasa
    otp_field = ui_device(resourceId=RESOURCE_IDS["otp_input"])
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

    # Verifikasi OTP terinput dengan benar
    # Note: karena ini password field, kita tidak bisa mengecek teks yang diinput
    # Kita hanya bisa verifikasi bahwa button verify menjadi enabled
    time.sleep(1)  # Tunggu validasi aplikasi

    return True


@log_action
def click_verify(ui_device: u2.Device, serial: str) -> bool:
    """Klik tombol verifikasi OTP dan tangani respons."""
    logger = get_device_logger(serial)

    # Cari tombol verifikasi dengan resource ID yang benar
    verify_button = ui_device(resourceId=RESOURCE_IDS["verify_button"])

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
    is_success, message_type = check_otp_message(ui_device, serial)

    if not is_success:
        logger.error(f"Verifikasi gagal dengan pesan tipe: {message_type}")
        return False

    # Jika sukses, tunggu verifikasi selesai jika masih dalam proses
    if message_type == "success":
        # Cek apakah ada timer countdown untuk redirect
        timer = ui_device(resourceId=RESOURCE_IDS["verification_timer"])
        if timer.exists:
            logger.info("Menunggu redirect otomatis setelah verifikasi...")
            # Tunggu sedikit lebih lama dari timer untuk memastikan redirect selesai
            try:
                timer_text = timer.get_text().strip()
                match = re.search(r"(\d+)", timer_text)
                if match:
                    seconds = int(match.group(1))
                else:
                    logger.warning(
                        "No match found in timer_text, defaulting to 0 seconds"
                    )
                    seconds = 0
                # Tambah 2 detik untuk jaga-jaga
                wait_time = seconds + 2
                logger.info(f"Menunggu {wait_time} detik untuk redirect...")
                time.sleep(wait_time)
            except Exception as e:
                logger.warning(f"Gagal parse timer, menunggu 5 detik default: {e}")
                time.sleep(5)

    return True


@log_action
def verify_home_page(ui_device: u2.Device, serial: str, timeout: int = 20) -> bool:
    """
    Verifikasi berhasil navigasi ke halaman home setelah OTP.
    """
    logger = get_device_logger(serial)
    start_time = time.time()

    while time.time() - start_time < timeout:
        # Cek pesan error atau sukses
        is_success, message_type = check_otp_message(ui_device, serial)
        if not is_success:
            logger.error(f"Terdeteksi pesan error: {message_type}")
            return False

        # Jika masih dalam proses verifikasi (sukses), tunggu
        if (
            message_type == "success"
            and ui_device(resourceId=RESOURCE_IDS["verification_timer"]).exists
        ):
            logger.info("Masih dalam proses verifikasi, menunggu...")
            time.sleep(1)
            continue

        # Cek indikator home
        if ui_device(resourceId=RESOURCE_IDS["home_indicator"]).exists:
            logger.info("Verifikasi OTP berhasil - indikator home terdeteksi")
            return True

        # Cek dashboard view
        if ui_device(resourceId=RESOURCE_IDS["dashboard_view"]).exists:
            logger.info("Verifikasi OTP berhasil - dashboard terdeteksi")
            return True

        # Tunggu sebentar sebelum check lagi
        time.sleep(1)

    logger.error(f"Timeout ({timeout}s) menunggu halaman home setelah verifikasi OTP")
    return False


@log_action
def get_countdown_time(ui_device: u2.Device, serial: str) -> str:
    """
    Dapatkan informasi sisa waktu countdown OTP.

    Args:
        ui_device: Objek UI Automator device
        serial: Serial number device

    Returns:
        str: Waktu tersisa dalam format MM:SS atau "N/A" jika tidak ditemukan
    """
    logger = get_device_logger(serial)

    countdown = ui_device(resourceId=RESOURCE_IDS["countdown"])
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
def check_otp_message(ui_device: u2.Device, serial: str) -> tuple[bool, str]:
    """
    Memeriksa pesan yang muncul setelah verifikasi OTP.

    Args:
        ui_device: Objek UI Automator device
        serial: Serial number device

    Returns:
        tuple: (is_success, message_type)
            is_success (bool): True jika tidak ada error, False jika ada error
            message_type (str): Tipe pesan yang terdeteksi: 'success', 'invalid', 'expired', 'sent', atau 'none'
    """
    logger = get_device_logger(serial)

    # Cek pesan error/sukses
    message_element = ui_device(resourceId=RESOURCE_IDS["message_text"])
    if message_element.exists:
        message_text = message_element.get_text()
        logger.info(f"Pesan terdeteksi: {message_text}")

        # Cek jenis pesan
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

    # Cek indikator sukses
    if ui_device(resourceId=RESOURCE_IDS["verification_complete_text"]).exists:
        logger.info("Verifikasi OTP berhasil terdeteksi")
        return True, "success"

    # Tidak ada pesan terdeteksi
    return True, "none"


@log_action
def try_resend_otp(ui_device: u2.Device, serial: str) -> bool:
    """
    Coba resend OTP jika sudah bisa (countdown habis).

    Args:
        ui_device: Objek UI Automator device
        serial: Serial number device

    Returns:
        bool: True jika berhasil resend, False jika gagal
    """
    logger = get_device_logger(serial)

    # Cek countdown dulu
    countdown_text = get_countdown_time(ui_device, serial)
    if countdown_text == "N/A":
        logger.warning("Tidak dapat menentukan status countdown")
    elif countdown_text != "00:00":
        # Parse countdown time
        match = re.search(r"(\d+):(\d+)", countdown_text)
        if match:
            minutes = int(match.group(1))
            seconds = int(match.group(2))
            if minutes > 0 or seconds > 0:
                logger.info(
                    f"Masih ada waktu countdown ({countdown_text}), belum bisa resend"
                )
                return False

    # Coba temukan tombol resend
    # Pertama coba dengan resource ID
    resend_button = ui_device(resourceId=RESOURCE_IDS["resend_button"])

    # Jika tidak ditemukan, coba dengan teks
    if not resend_button.exists:
        # Coba berbagai kemungkinan teks untuk tombol resend
        for text in ["Resend OTP", "Kirim Ulang OTP", "Resend", "Kirim Ulang"]:
            resend_button = ui_device(text=text)
            if resend_button.exists:
                break

    if not resend_button.exists:
        logger.error("Tombol resend OTP tidak ditemukan")
        return False

    # Cek apakah tombol enabled
    if not resend_button.info.get(
        "enabled", True
    ):  # Default True karena TextView mungkin tidak punya enabled property
        logger.error("Tombol resend OTP tidak enabled, mungkin countdown belum habis")
        return False

    # Klik tombol resend
    resend_button.click()
    logger.info("Klik tombol resend OTP")

    # Tunggu sebentar dan verifikasi
    time.sleep(2)

    # Verifikasi apakah resend sukses (bisa dilihat dari reset countdown)
    new_countdown = get_countdown_time(ui_device, serial)
    if (
        new_countdown != countdown_text
        and new_countdown != "00:00"
        and new_countdown != "N/A"
    ):
        logger.info(f"Resend OTP berhasil, countdown reset ke {new_countdown}")
        return True
    else:
        logger.warning(
            f"Tidak dapat memverifikasi resend OTP berhasil, countdown sekarang: {new_countdown}"
        )
        # Tetap return True karena kita sudah klik tombol resend
        return True
