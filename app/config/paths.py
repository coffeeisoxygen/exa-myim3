import os

# Define application paths
APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(APP_DIR)
LOGS_DIR = os.path.join(ROOT_DIR, "logs")

# Ensure required directories exist
os.makedirs(LOGS_DIR, exist_ok=True)
