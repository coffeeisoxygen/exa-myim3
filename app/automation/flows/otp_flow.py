import time

from app.automation.actions.otp import (
    check_otp_message,
    click_verify,
    get_countdown_time,
    input_otp_code,
    try_resend_otp,
    verify_home_page,
    verify_otp_page,
)
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
    "resend_button": "com.pure.indosat.care:id/tvResendOTP",
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


@log_action
def otp_flow(device_service, serial: str, otp_code: str, max_resend: int = 1) -> bool:
    """
    Flow untuk verifikasi OTP dengan penanganan berbagai skenario.

    Args:
        device_service: Service untuk mengelola device
        serial: Serial number device
        otp_code: Kode OTP untuk diinput
        max_resend: Jumlah maksimum resend OTP yang diperbolehkan

    Returns:
        bool: True jika berhasil, False jika gagal
    """
    logger = get_device_logger(serial)
    ui_device = device_service.get_ui_device(serial)
    resend_count = 0

    # 1. Verifikasi halaman OTP
    if not verify_otp_page(ui_device, RESOURCE_IDS, serial):
        return False

    # 2. Tangani popup jika ada
    if not handle_popup(ui_device, serial):
        logger.warning("Ada masalah saat menangani popup, melanjutkan flow")

    # Loop untuk mencoba input dan verifikasi OTP
    while resend_count <= max_resend:
        # 3. Cek countdown timer
        remaining_time = get_countdown_time(
            ui_device, RESOURCE_IDS["countdown"], serial
        )
        logger.info(f"Sisa waktu OTP: {remaining_time}")

        # Jika countdown tidak terdeteksi atau 00:00, coba resend
        if (
            remaining_time == "N/A" or remaining_time == "00:00"
        ) and resend_count < max_resend:
            logger.info(
                f"OTP mungkin expired, mencoba resend (percobaan {resend_count + 1}/{max_resend})"
            )
            if try_resend_otp(ui_device, RESOURCE_IDS, serial):
                resend_count += 1
                logger.info(f"Menunggu OTP baru setelah resend ke-{resend_count}")
                time.sleep(5)  # Tunggu OTP baru
                continue

        # 4. Input kode OTP
        if not input_otp_code(ui_device, RESOURCE_IDS["otp_input"], otp_code, serial):
            return False

        # 5. Klik tombol verifikasi
        if click_verify(ui_device, RESOURCE_IDS, serial):
            # 6. Verifikasi hasil
            is_success, message_type = check_otp_message(
                ui_device, RESOURCE_IDS, serial
            )

            if not is_success:
                # Jika invalid/expired dan masih bisa resend
                if message_type in ["invalid", "expired"] and resend_count < max_resend:
                    logger.info(
                        f"OTP {message_type}, mencoba resend (percobaan {resend_count + 1}/{max_resend})"
                    )
                    if try_resend_otp(ui_device, RESOURCE_IDS, serial):
                        resend_count += 1
                        logger.info(
                            f"Menunggu OTP baru setelah resend ke-{resend_count}"
                        )
                        time.sleep(5)
                        continue
                    else:
                        logger.error("Gagal melakukan resend OTP")
                        return False
                else:
                    logger.error(f"OTP {message_type} dan tidak bisa resend lagi")
                    return False

            # 7. Verifikasi home page jika belum ada error
            if verify_home_page(ui_device, RESOURCE_IDS, serial):
                logger.info(f"OTP berhasil diverifikasi untuk device {serial}")
                return True

        # Increment retry counter jika gagal
        resend_count += 1

    logger.error(f"Gagal verifikasi OTP setelah {resend_count} percobaan")
    return False
