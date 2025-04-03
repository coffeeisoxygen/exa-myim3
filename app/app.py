"""
FastAPI application setup.
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import APP_DESCRIPTION, APP_NAME, APP_VERSION
from app.core.database import create_db_and_tables
from app.core.events import event_bus
from app.core.logging import initialize_logging
from app.core.settings import settings_manager
from app.devices.routes import router as device_router
from app.user.routes import router as auth_router
from app.web.auth import AuthMiddleware
from app.web.routes import router as web_router

# Initialize logging first
initialize_logging(log_to_file=True, log_level=logging.DEBUG)

# Setup logger after initialization
logger = logging.getLogger(__name__)
logger.info(f"Starting {APP_NAME} application")

# Initialize database and tables first - CRITICAL
create_db_and_tables()
logger.info("Database tables created")

# Initialize settings after database creation
settings_manager.load_settings()
logger.info("Settings loaded")

# Only then import routes that depend on settings


# Define application lifespan events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    try:
        logger.info("Application startup process began")

        # Publish startup event to trigger all services
        logger.info("Publishing app.startup event")
        await event_bus.publish("app.startup")

        logger.info("Application startup complete")
        yield

    except Exception as e:
        logger.error(f"Error during application startup: {e}", exc_info=True)
        raise
    finally:
        # Cleanup on shutdown
        logger.info("Application shutting down")
        await event_bus.publish("app.shutdown")
        logger.info("Application shutdown complete")


# Initialize FastAPI application
app = FastAPI(
    title=APP_NAME,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
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
    StaticFiles(directory=Path(__file__).parent / "web" / "templates" / "static"),
    name="static",
)

# Include routers
app.include_router(web_router, tags=["Web UI"])
app.include_router(device_router, prefix="/api/devices", tags=["Devices"])
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.add_middleware(AuthMiddleware)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    logger.debug("Root endpoint called")
    return {"message": f"Welcome to {APP_NAME} API"}


# Health check endpoint
@app.get("/health")
async def health():
    """Health check endpoint."""
    logger.debug("Health check endpoint called")
    return {"status": "ok", "version": APP_VERSION}
