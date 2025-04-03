import logging
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize templates
templates_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=templates_dir)


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the home page or redirect to dashboard if logged in."""
    # Check if user is logged in (has token in cookie)
    token = request.cookies.get("access_token")
    if token:
        return RedirectResponse("/dashboard")

    logger.debug("Rendering home page for anonymous user")
    return templates.TemplateResponse("home.html", {"request": request})


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Render the dashboard page."""
    logger.debug("Rendering dashboard page")
    return templates.TemplateResponse("dashboard.html", {"request": request})


@router.get("/devices", response_class=HTMLResponse)
async def devices_page(request: Request):
    """Render the devices page."""
    logger.debug("Rendering devices page")
    return templates.TemplateResponse("devices.html", {"request": request})


@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    """Render the settings page."""
    logger.debug("Rendering settings page")
    return templates.TemplateResponse("settings.html", {"request": request})


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Render the login page."""
    # Check if user is already logged in
    token = request.cookies.get("access_token")
    if token:
        return RedirectResponse("/dashboard")

    logger.debug("Rendering login page")
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Render the register page."""
    # Check if user is already logged in
    token = request.cookies.get("access_token")
    if token:
        return RedirectResponse("/dashboard")

    logger.debug("Rendering register page")
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/logout")
async def logout_page():
    """Handle logout."""
    logger.debug("Processing logout")
    response = RedirectResponse("/login")
    response.delete_cookie(key="access_token")
    return response
