import logging
import time

from app.ui.element import Element

logger = logging.getLogger(__name__)


class UIAction:
    """Base class for UI actions."""

    def __init__(self, name: str, element: Element = None):
        """Initialize a UI action.

        Args:
            name: Descriptive name of the action
            element: Element to act upon (if applicable)
        """
        self.name = name
        self.element = element

    def execute(self, ui_device) -> bool:
        """Execute the action on the device.

        Args:
            ui_device: uiautomator2 device object

        Returns:
            bool: True if successful, False otherwise
        """
        raise NotImplementedError("Subclasses must implement execute()")


class ClickAction(UIAction):
    """Action to click on an element."""

    def execute(self, ui_device) -> bool:
        """Click on the element.

        Args:
            ui_device: uiautomator2 device object

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.element:
            logger.error(f"No element provided for action {self.name}")
            return False

        element = self.element.find_in_device(ui_device)
        if not element:
            return False

        try:
            element.click()
            logger.info(f"Clicked on {self.element.name}")
            time.sleep(1)  # Small delay after click
            return True
        except Exception as e:
            logger.exception(f"Error clicking on {self.element.name}: {e}")
            return False


class InputTextAction(UIAction):
    """Action to input text into an element."""

    def __init__(self, name: str, element: Element, text: str):
        """Initialize an input text action.

        Args:
            name: Descriptive name of the action
            element: Element to input text into
            text: Text to input
        """
        super().__init__(name, element)
        self.text = text

    def execute(self, ui_device) -> bool:
        """Input text into the element.

        Args:
            ui_device: uiautomator2 device object

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.element:
            logger.error(f"No element provided for action {self.name}")
            return False

        element = self.element.find_in_device(ui_device)
        if not element:
            return False

        try:
            element.set_text(self.text)
            logger.info(f"Input text into {self.element.name}: {self.text}")
            time.sleep(0.5)  # Small delay after input
            return True
        except Exception as e:
            logger.exception(f"Error inputting text into {self.element.name}: {e}")
            return False


class WaitForElementAction(UIAction):
    """Action to wait for an element to appear."""

    def __init__(self, name: str, element: Element, timeout: int = 10):
        """Initialize a wait action.

        Args:
            name: Descriptive name of the action
            element: Element to wait for
            timeout: Maximum wait time in seconds
        """
        super().__init__(name, element)
        self.timeout = timeout

    def execute(self, ui_device) -> bool:
        """Wait for the element to appear.

        Args:
            ui_device: uiautomator2 device object

        Returns:
            bool: True if element appeared, False otherwise
        """
        if not self.element:
            logger.error(f"No element provided for action {self.name}")
            return False

        element = self.element.find_in_device(ui_device)
        return element is not None
