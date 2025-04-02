import os

from app.logging import initialize_logging

# Application name
APP_NAME = "EXA-MYIM3"

# ADB config
ADB_HOST = "127.0.0.1"
ADB_PORT = 5037

# Define application paths
APP_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(APP_DIR)
LOGS_DIR = os.path.join(ROOT_DIR, "logs")

# Ensure required directories exist
os.makedirs(LOGS_DIR, exist_ok=True)


def init_app():
    """Initialize application components."""
    # Initialize logging
    initialize_logging(log_to_file=True)

    # Later we'll add database initialization here
