import os

# ADB server configuration
ADB_HOST = "127.0.0.1"
ADB_PORT = 5037

# Path ke Android SDK (jika ada, atau kosong jika menggunakan yang di PATH)
ANDROID_SDK_PATH = os.environ.get("ANDROID_SDK_PATH", "")

# Timeout settings
ADB_COMMAND_TIMEOUT = 30  # Default timeout untuk command ADB (seconds)
ADB_SERVER_START_TIMEOUT = 10  # Timeout untuk start server (seconds)
ADB_DEVICE_DETECT_TIMEOUT = 5  # Timeout untuk device detection (seconds)

# Polling interval untuk device detection
DEVICE_POLL_INTERVAL = 10  # Seconds

# ADB command status codes
ADB_STATUS = {
    "SUCCESS": 0,
    "SERVER_NOT_RUNNING": 1,
    "DEVICE_NOT_FOUND": 2,
    "COMMAND_FAILED": 3,
    "TIMEOUT": 4,
}


# Directory paths untuk ADB executable
def get_adb_search_paths() -> list:
    """Get all possible paths where adb executable might be located."""
    paths = []

    # Dari ANDROID_SDK_PATH jika ada
    if ANDROID_SDK_PATH:
        paths.append(os.path.join(ANDROID_SDK_PATH, "platform-tools", "adb.exe"))
        paths.append(os.path.join(ANDROID_SDK_PATH, "platform-tools", "adb"))

    # Dari PATH environment variable
    paths.append("adb.exe")  # Windows
    paths.append("adb")  # Unix/Linux

    return paths
