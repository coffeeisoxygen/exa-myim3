import logging
from typing import Dict, Optional

from app.services.adb_service import ADBService
from app.services.base_service import BaseService

logger = logging.getLogger(__name__)


class ServiceManager:
    """Manages all application services."""

    def __init__(self):
        self.services: Dict[str, BaseService] = {}
        self._is_running = False

    def register_service(self, service_id: str, service: BaseService):
        """Register a service with the manager."""
        if service_id in self.services:
            logger.warning(
                f"Service with ID {service_id} already registered, replacing"
            )

        self.services[service_id] = service
        logger.info(f"Service '{service_id}' registered")

    async def start_services(self):
        """Start all registered services."""
        logger.info("Starting all services...")

        for service_id, service in self.services.items():
            try:
                await service.start()
                logger.info(f"Service '{service_id}' started successfully")
            except Exception as e:
                logger.error(f"Failed to start service '{service_id}': {e}")

        self._is_running = True

    async def stop_services(self):
        """Stop all registered services."""
        logger.info("Stopping all services...")

        for service_id, service in reversed(list(self.services.items())):
            try:
                await service.stop()
                logger.info(f"Service '{service_id}' stopped successfully")
            except Exception as e:
                logger.error(f"Failed to stop service '{service_id}': {e}")

        self._is_running = False

    async def stop_service(self, service_id: str):
        """Stop a specific service."""
        if service_id not in self.services:
            logger.warning(f"Service '{service_id}' not found")
            return False

        try:
            await self.services[service_id].stop()
            logger.info(f"Service '{service_id}' stopped successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to stop service '{service_id}': {e}")
            return False

    async def start_service(self, service_id: str):
        """Start a specific service."""
        if service_id not in self.services:
            logger.warning(f"Service '{service_id}' not found")
            return False

        try:
            await self.services[service_id].start()
            logger.info(f"Service '{service_id}' started successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to start service '{service_id}': {e}")
            return False

    def get_service_status(self, service_id: Optional[str] = None) -> Dict:
        """Get status of all services or a specific service."""
        if service_id:
            if service_id not in self.services:
                return {"error": f"Service '{service_id}' not found"}

            service = self.services[service_id]
            return {
                "id": service_id,
                "running": service.is_running,
                "status": service.status,
                "info": service.get_info(),
            }

        # Return status of all services
        return {
            service_id: {
                "running": service.is_running,
                "status": service.status,
                "info": service.get_info(),
            }
            for service_id, service in self.services.items()
        }


# Create a singleton instance
service_manager = ServiceManager()

# Register services
# Register ADB service
adb_service = ADBService()
service_manager.register_service("adb_service", adb_service)
