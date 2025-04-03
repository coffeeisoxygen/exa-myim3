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

# Setup logging
logger = logging.getLogger(__name__)


# Define application lifespan events
# Di app.py, tambahkan try-except di lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("Application startup...")
        create_db_and_tables()
        yield
    except Exception as e:
        logger.error(f"Error during application startup: {e}")
        raise
    finally:
        logger.info("Application shutdown...")


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


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": f"Welcome to {APP_NAME} API"}


# Health check endpoint
@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}
