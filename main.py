"""
Application entry point.
"""

from venv import logger
import uvicorn

from app.core.config import DEBUG, HOST, PORT
from app.core.logging import initialize_logging


def main():
    """Run the application server."""
    try:
        # Initialize logging
        initialize_logging(log_to_file=True)

        # Print more info
        logger.info(f"Starting server on {HOST}:{PORT}")

        # Run uvicorn server
        uvicorn.run(
            "app.app:app",
            host=HOST,
            port=PORT,
            reload=DEBUG,
            log_level="debug",  # Gunakan debug
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")


if __name__ == "__main__":
    main()
