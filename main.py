import threading
import time
from typing import Dict, List

import uiautomator2 as u2
from ppadb.client import Client


class DeviceController:
    """Class to handle Android device automation with ppadb and uiautomator2."""

    def __init__(self, host: str = "127.0.0.1", port: int = 5037):
        """Initialize the device controller.

        Args:
            host: ADB server host, defaults to '127.0.0.1'
            port: ADB server port, defaults to 5037
        """
        self.adb_client = Client(host=host, port=port)
        self.device_cache = {}  # Cache for uiautomator2 device objects
        self.lock = threading.Lock()  # Thread safety for device cache

    def get_devices(self) -> List[Dict[str, str]]:
        """Get list of connected Android devices.

        Returns:
            List of dictionaries with device information
        """
        devices = []
        adb_devices = self.adb_client.devices()

        for device in adb_devices:
            # Get basic device info
            device_info = {
                "id": device.serial,
                "status": "device",  # If we got the device through ppadb, it's authorized
            }

            # Get additional device properties
            try:
                manufacturer = device.shell("getprop ro.product.manufacturer").strip()
                model = device.shell("getprop ro.product.model").strip()
                android_version = device.shell(
                    "getprop ro.build.version.release"
                ).strip()

                device_info.update(
                    {
                        "manufacturer": manufacturer,
                        "model": model,
                        "android_version": android_version,
                    }
                )
            except Exception as e:
                device_info["error"] = str(e)

            devices.append(device_info)

        return devices

    def get_ui_device(self, serial: str):
        """Get or create uiautomator2 device object for a specific device.

        Args:
            serial: Device serial number

        Returns:
            uiautomator2 device object
        """
        with self.lock:  # Thread-safe access to device cache
            if serial not in self.device_cache:
                self.device_cache[serial] = u2.connect(serial)
            return self.device_cache[serial]

    def execute_action(self, serial: str, action: str, *args, **kwargs):
        """Execute an action on a specific device.

        Args:
            serial: Device serial number
            action: Action to execute (e.g., 'press_home', 'click', etc.)
            args: Positional arguments for the action
            kwargs: Keyword arguments for the action

        Returns:
            Result of the action
        """
        device = self.adb_client.device(serial)
        if not device:
            raise ValueError(f"Device with serial {serial} not found")

        # Basic ADB actions
        if action == "shell":
            return device.shell(args[0])
        elif action == "install":
            return device.install(*args, **kwargs)
        elif action == "uninstall":
            return device.uninstall(*args, **kwargs)

        # UI Automator actions
        ui_device = self.get_ui_device(serial)
        if action == "press_home":
            return ui_device.press("home")
        elif action == "press_back":
            return ui_device.press("back")
        elif action == "click":
            return ui_device.click(*args)
        elif action == "swipe":
            return ui_device.swipe(*args)
        elif action == "open_app":
            return ui_device.app_start(args[0])
        elif action == "close_app":
            return ui_device.app_stop(args[0])
        else:
            raise ValueError(f"Unknown action: {action}")


def device_worker(controller, device_info):
    """Worker function to run in a separate thread for each device.

    Args:
        controller: DeviceController instance
        device_info: Dictionary with device information
    """
    serial = device_info["id"]
    print_lock = threading.Lock()

    try:
        with print_lock:
            print(f"\n[{serial}] Starting device automation...")

        # Press home button
        controller.execute_action(serial, "press_home")
        with print_lock:
            print(f"[{serial}] Pressed home button")

        # Get battery info
        battery_info = controller.execute_action(serial, "shell", "dumpsys battery")
        battery_level = battery_info.split("level:")[1].split()[0]
        with print_lock:
            print(f"[{serial}] Battery level: {battery_level}%")

        # Additional actions can be added here
        time.sleep(2)  # Simulating some work

        with print_lock:
            print(f"[{serial}] Device automation completed")

    except Exception as e:
        with print_lock:
            print(f"[{serial}] Error: {e}")


def main():
    """Main function to demonstrate threaded device automation."""
    controller = DeviceController()
    threads = []

    try:
        print("Detecting connected Android devices...")
        devices = controller.get_devices()

        if not devices:
            print(
                "No devices detected. Please connect a device and ensure USB debugging is enabled."
            )
            return

        print(f"Found {len(devices)} device(s):")
        for i, device in enumerate(devices, 1):
            print(f"\nDevice {i}:")
            for key, value in device.items():
                print(f"  {key}: {value}")

        print("\nStarting parallel device automation...")

        # Create and start a thread for each device
        for device in devices:
            thread = threading.Thread(
                target=device_worker,
                args=(controller, device),
                name=f"Device-{device['id']}",
            )
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        print("\nAll device operations completed")

    except Exception as e:
        print(f"Error in main thread: {e}")


if __name__ == "__main__":
    main()
