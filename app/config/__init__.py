from app.config.constants import APP_NAME, KEY_CODES
from app.config.paths import APP_DIR, LOGS_DIR, ROOT_DIR
from app.config.settings import ADB_HOST, ADB_PORT, ANDROID_SDK_PATH
from app.logging import initialize_logging


def init_app():
    """Initialize application components."""
    # Initialize logging
    initialize_logging(log_to_file=True)

    # Later we'll add database initialization here
