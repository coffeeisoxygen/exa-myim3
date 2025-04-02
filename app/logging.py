import datetime
import logging
import os
from functools import wraps
from logging.handlers import RotatingFileHandler

# Constants
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEVICE_LOG_FORMAT = (
    "%(asctime)s - %(name)s - %(levelname)s - [%(device_id)s] - %(message)s"
)
DEFAULT_LOG_LEVEL = logging.INFO
LOG_DIR = "logs"

# Ensure logs directory exists
os.makedirs(LOG_DIR, exist_ok=True)


def initialize_logging(log_to_file=True, log_level=DEFAULT_LOG_LEVEL):
    """
    Initialize the logging system for the entire project

    Args:
        log_to_file: Whether to log to file (default: True)
        log_level: Logging level (default: INFO)
    """
    # Create handlers
    handlers: list[logging.Handler] = [logging.StreamHandler()]

    if log_to_file:
        log_filename = os.path.join(
            LOG_DIR, f"automation_{datetime.datetime.now().strftime('%Y%m%d')}.log"
        )
        file_handler = RotatingFileHandler(
            log_filename,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=5,
        )
        handlers.append(file_handler)

    # Configure root logger
    logging.basicConfig(level=log_level, format=LOG_FORMAT, handlers=handlers)

    logging.info("Logging system initialized")


def get_logger(name):
    """Get a named logger"""
    return logging.getLogger(name)


def get_device_logger(device_id):
    """
    Get a logger for a specific device with device ID context

    Args:
        device_id: The device serial number

    Returns:
        Logger with device context
    """
    logger = logging.getLogger(f"device.{device_id}")

    # Create a filter to inject device_id into log records
    class DeviceFilter(logging.Filter):
        def filter(self, record):
            record.device_id = device_id
            return True

    # Check if filter already exists
    has_filter = False
    for handler in logger.handlers:
        for filter_obj in handler.filters:
            if isinstance(filter_obj, DeviceFilter):
                has_filter = True
                break

    if not has_filter:
        # Add filter to logger
        device_filter = DeviceFilter()
        logger.addFilter(device_filter)

    return logger


def log_action(func=None, *, level=logging.INFO):
    """
    Decorator to log function execution with timing

    Usage:
        @log_action
        def some_function(device, ...):
            pass

        @log_action(level=logging.DEBUG)
        def some_other_function(...):
            pass
    """

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            import time

            # Try to get device from args
            device_id = "unknown"
            if args and hasattr(args[0], "serial_number"):
                device_id = args[0].serial_number
                logger = get_device_logger(device_id)
            else:
                logger = logging.getLogger(f.__module__)

            start_time = time.time()
            logger.log(level, f"Starting {f.__name__}")

            try:
                result = f(*args, **kwargs)
                elapsed = time.time() - start_time
                logger.log(level, f"Completed {f.__name__} in {elapsed:.2f}s")
                return result
            except Exception as e:
                logger.exception(f"Error in {f.__name__}: {e}")
                raise

        return wrapper

    if func is None:
        return decorator
    return decorator(func)
