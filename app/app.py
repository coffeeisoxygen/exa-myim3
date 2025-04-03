import logging
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config.constants import APP_NAME
from app.config.database import create_db_and_tables
from app.logging import initialize_logging
from app.routes import main_router
from app.services import service_manager

# Setup logging
logger = logging.getLogger(__name__)


# Initialize app components
def init_app():
    """Initialize application components."""
    # Initialize logging
    initialize_logging(log_to_file=True)

    # Create database tables
    create_db_and_tables()


# Create lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for the application."""
    logger.info("Application startup...")

    # Initialize app
    init_app()

    # Start services
    await service_manager.start_services()

    yield

    # Shutdown services on app shutdown
    logger.info("Application shutdown...")
    await service_manager.stop_services()


# Initialize application
app = FastAPI(
    title=APP_NAME,
    description="Automation system for Android devices",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent / "templates" / "static"),
    name="static",
)

# Include all routes
app.include_router(main_router)


def main():
    """Run the application server."""
    uvicorn.run(
        "app.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Set to False in production
        log_level="info",
    )


if __name__ == "__main__":
    main()
