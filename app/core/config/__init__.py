"""
Configuration module for the application.
Load configuration from environment variables or config files.
"""

import os
import secrets
from pathlib import Path

# Base paths
ROOT_DIR = Path(__file__).parent.parent.parent.parent
APP_DIR = Path(__file__).parent.parent.parent
LOGS_DIR = ROOT_DIR / "logs"

# Application information
APP_NAME = "EXA-MYIM3"
APP_VERSION = "0.1.0"
APP_DESCRIPTION = "Automation system for Android devices"

# Server configuration
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{ROOT_DIR}/exa_myim3.db")

# ADB configuration
ADB_HOST = os.getenv("ADB_HOST", "127.0.0.1")
ADB_PORT = int(os.getenv("ADB_PORT", "5037"))
ANDROID_SDK_PATH = os.getenv("ANDROID_SDK_PATH", "")

# Authentication
AUTH_SECRET_KEY = os.getenv("AUTH_SECRET_KEY", secrets.token_hex(32))
AUTH_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
