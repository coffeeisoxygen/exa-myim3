import logging
import time

logger = logging.getLogger(__name__)


class Element:
    """Represents a UI element that can be interacted with."""

    def __init__(
        self,
        name: str,
        xpath: str = None,
        resource_id: str = None,
        text: str = None,
        timeout: int = 10,
    ):
        """Initialize a UI element.

        Args:
            name: Descriptive name of the element
            xpath: XPath selector for the element
            resource_id: Android resource ID
            text: Text content to match
            timeout: Maximum wait time in seconds
        """
        self.name = name
        self.xpath = xpath
        self.resource_id = resource_id
        self.text = text
        self.timeout = timeout

        if not any([xpath, resource_id, text]):
            raise ValueError(
                "At least one of xpath, resource_id, or text must be provided"
            )

    def __str__(self):
        return f"Element('{self.name}')"

    def find_in_device(self, ui_device):
        """Find this element in the device UI.

        Args:
            ui_device: uiautomator2 device object

        Returns:
            uiautomator2 element or None if not found
        """
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                if self.xpath:
                    element = ui_device.xpath(self.xpath)
                    if element.exists:
                        logger.debug(
                            f"Found element {self.name} using xpath: {self.xpath}"
                        )
                        return element

                if self.resource_id:
                    element = ui_device(resourceId=self.resource_id)
                    if element.exists:
                        logger.debug(
                            f"Found element {self.name} using resource_id: {self.resource_id}"
                        )
                        return element

                if self.text:
                    element = ui_device(text=self.text)
                    if element.exists:
                        logger.debug(
                            f"Found element {self.name} using text: {self.text}"
                        )
                        return element

                # Wait a bit before trying again
                time.sleep(0.5)
            except Exception as e:
                logger.debug(f"Error finding {self.name}: {e}")

        logger.warning(f"Element {self.name} not found after {self.timeout} seconds")
        return None
