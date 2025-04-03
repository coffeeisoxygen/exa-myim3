import os

# ADB config
ADB_HOST = "127.0.0.1"
ADB_PORT = 5037

# Path ke Android SDK (jika ada, atau kosong jika menggunakan yang di PATH)
ANDROID_SDK_PATH = os.environ.get("ANDROID_SDK_PATH", "")

# Package aplikasi default
DEFAULT_PACKAGE = "com.pure.indosat.care"
