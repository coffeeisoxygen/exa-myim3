# General app constants & configurations
# ADB specific configurations
from app.config.adb_config import (
    ADB_COMMAND_TIMEOUT,
    ADB_DEVICE_DETECT_TIMEOUT,
    ADB_HOST,
    ADB_PORT,
    ADB_SERVER_START_TIMEOUT,
    ADB_STATUS,
    ANDROID_SDK_PATH,
    DEVICE_POLL_INTERVAL,
    get_adb_search_paths,
)
from app.config.constants import (
    APP_NAME,
    AUTOMATION_STATUS,
    AUTOMATION_TO_TRANSACTION,
    KEY_CODES,
    TRANSACTION_STATUS,
    map_automation_to_transaction,
)

# Database configurations
from app.config.database import create_db_and_tables, get_session

# Path configurations
from app.config.paths import APP_DIR, LOGS_DIR, ROOT_DIR

# Database settings
from app.config.settings import DB_MAX_OVERFLOW, DB_POOL_SIZE, DEFAULT_PACKAGE

# Import logging initializer
from app.logging import initialize_logging


def init_app():
    """Initialize application components."""
    # Initialize logging
    initialize_logging(log_to_file=True)

    # Initialize database
    create_db_and_tables()
