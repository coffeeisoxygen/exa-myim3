"""Router collection for the application."""

from fastapi import APIRouter

# Import all routers
from app.routes.adb_routes import router as adb_router
from app.routes.device_routes import router as device_router
from app.routes.system_routes import router as system_router

# Main router that includes all sub-routers
main_router = APIRouter()

# Include all routers with their prefixes
main_router.include_router(system_router)
main_router.include_router(adb_router, prefix="/api/adb", tags=["ADB"])
main_router.include_router(device_router, prefix="/api/devices", tags=["Devices"])

# More routers can be added here as the application grows
