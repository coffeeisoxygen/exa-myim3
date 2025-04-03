"""System-wide routes including health checks and main page."""

import logging
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from app.config.constants import APP_NAME
from app.services import service_manager

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize templates
templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")


@router.get("/")
async def root(request: Request):
    """Root endpoint serving the main HTML page."""
    return templates.TemplateResponse(
        "sidebar.html", {"request": request, "app_name": APP_NAME}
    )


@router.get("/health")
async def health():
    """Health check endpoint for monitoring system status."""
    services_status = {
        name: service.status.name for name, service in service_manager.services.items()
    }

    return {"status": "ok", "services": services_status}
