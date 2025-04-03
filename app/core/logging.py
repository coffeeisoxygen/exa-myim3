import logging
import sys
from datetime import datetime
from functools import wraps
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Callable, TypeVar

# Setup log directory
LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Log filename format
LOG_FILENAME = f"examyim3_{datetime.now().strftime('%Y%m%d')}.log"
LOG_PATH = LOG_DIR / LOG_FILENAME

# Configure logging level
DEFAULT_LOG_LEVEL = logging.INFO


def initialize_logging(
    log_to_file: bool = True, log_level: int = DEFAULT_LOG_LEVEL
) -> None:
    """
    Initialize application logging.

    Args:
        log_to_file: Whether to log to file
        log_level: Logging level (default INFO)
    """
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler (optional)
    if log_to_file:
        file_handler = RotatingFileHandler(
            LOG_PATH,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Suppress noisy loggers
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    logging.info(f"Logging initialized. Level: {logging.getLevelName(log_level)}")
    if log_to_file:
        logging.info(f"Logging to file: {LOG_PATH}")


# Function decorator for logging function calls
F = TypeVar("F", bound=Callable)


def log_function_call(func: F) -> F:
    """Decorator to log function calls with parameters and return values."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        result = func(*args, **kwargs)
        logger.debug(f"{func.__name__} returned {result}")
        return result

    return wrapper  # type: ignore
