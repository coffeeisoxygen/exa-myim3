import logging
from typing import List

from app.ui.actions import UIAction

logger = logging.getLogger(__name__)


class UIFlow:
    """A sequence of UI actions to be executed together."""

    def __init__(self, name: str, actions: List[UIAction] = None):
        """Initialize a UI flow.

        Args:
            name: Descriptive name of the flow
            actions: List of UI actions to execute
        """
        self.name = name
        self.actions = actions or []

    def add_action(self, action: UIAction):
        """Add an action to the flow.

        Args:
            action: UI action to add
        """
        self.actions.append(action)

    def execute(self, device_service, serial: str) -> bool:
        """Execute the flow on a specific device.

        Args:
            device_service: DeviceService instance
            serial: Device serial number

        Returns:
            bool: True if all actions succeeded, False otherwise
        """
        logger.info(f"Executing flow '{self.name}' on device {serial}")

        try:
            ui_device = device_service.get_ui_device(serial)

            for i, action in enumerate(self.actions, 1):
                logger.info(f"Executing action {i}/{len(self.actions)}: {action.name}")
                if not action.execute(ui_device):
                    logger.error(f"Action {action.name} failed")
                    return False

            logger.info(f"Flow '{self.name}' completed successfully")
            return True

        except Exception as e:
            logger.exception(
                f"Error executing flow '{self.name}' on device {serial}: {e}"
            )
            return False
