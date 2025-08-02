# -*- coding: utf-8 -*-
"""
Enhanced Device Selector Widget for HiDock Desktop Application

This module provides an enhanced device selection interface with status indicators,
device information display, and improved user experience for device management.

Requirements: 6.1, 6.2, 6.3
"""

import os
import threading
from typing import Callable, List, Optional  # Removed Dict - not used

from config_and_logger import logger


class DeviceInfo:
    """Container for device information."""

    def __init__(
        self,
        name: str,
        vendor_id: int,
        product_id: int,
        status: str = "available",
        is_hidock: bool = False,
        version: str = "",
        capabilities: List[str] = None,
    ):
        self.name = name
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.status = status  # available, connected, error
        self.is_hidock = is_hidock
        self.version = version
        self.capabilities = capabilities or []

    def get_display_name(self) -> str:
        """Get formatted display name for the device."""
        status_icon = {"connected": "🟢", "available": "🔵", "error": "🔴"}.get(self.status, "⚪")

        hidock_indicator = "🎵" if self.is_hidock else "📱"

        name_parts = [status_icon, hidock_indicator, self.name]
        if self.version:
            name_parts.append(f"v{self.version}")

        return " ".join(name_parts)

    def get_detail_text(self) -> str:
        """Get detailed device information text."""
        details = [
            f"VID: {hex(self.vendor_id)} | PID: {hex(self.product_id)}",
            f"Status: {self.status.title()}",
        ]

        if self.is_hidock and self.capabilities:
            details.append(f"Features: {', '.join(self.capabilities)}")

        return "\n".join(details)


class EnhancedDeviceSelector:
    """Enhanced device selector with status indicators and detailed information."""

    def __init__(
        self,
        parent,
        command: Optional[Callable] = None,
        scan_callback: Optional[Callable] = None,
        **kwargs,
    ):
        super().__init__(parent, **kwargs)

        self.command = command
        self.scan_callback = scan_callback
        self.devices: List[DeviceInfo] = []
        self.selected_device: Optional[DeviceInfo] = None
        self.is_scanning = False

    def _scan_devices(self):
        """Start device scanning process."""
        if self.is_scanning:
            return

        self.devices = []  # Clear existing devices
        self.is_scanning = True
        text = "🔍 Scanning for USB devices..."

        # Start scanning in background thread
        threading.Thread(target=self._scan_devices_thread, daemon=True).start()

    def _scan_devices_thread(self):
        """Background thread for device scanning."""
        try:
            # Simulate device scanning (replace with actual USB enumeration)
            devices = self._enumerate_usb_devices()

            # Update UI on main thread
            self.after(0, self._on_scan_complete, devices)

        except Exception as e:
            logger.error(
                "EnhancedDeviceSelector",
                "_scan_devices_thread",
                f"Error scanning devices: {e}",
            )
            self.after(0, self._on_scan_error, str(e))

    def _enumerate_usb_devices(self) -> List[DeviceInfo]:
        """Enumerate USB devices and identify HiDock devices."""
        devices = []

        try:
            import usb.core

            # Find all USB devices
            usb_devices = usb.core.find(find_all=True)

            for device in usb_devices:
                try:
                    # Try to get device name
                    try:
                        name = usb.util.get_string(device, device.iProduct) or f"USB Device {hex(device.idProduct)}"
                    except (AttributeError, UnicodeDecodeError, ValueError):
                        name = f"USB Device {hex(device.idProduct)}"

                    # Check if it's a HiDock device
                    is_hidock = self._is_hidock_device(device.idVendor, device.idProduct)

                    # Determine status
                    status = "available"
                    capabilities = []
                    version = ""

                    if is_hidock:
                        capabilities = [
                            "Audio Recording",
                            "File Transfer",
                            "Real-time Sync",
                        ]
                        # Try to get version info if possible
                        try:
                            version = f"{device.bcdDevice >> 8}.{device.bcdDevice & 0xFF}"
                        except (AttributeError, ValueError):
                            pass

                    device_info = DeviceInfo(
                        name=name,
                        vendor_id=device.idVendor,
                        product_id=device.idProduct,
                        status=status,
                        is_hidock=is_hidock,
                        version=version,
                        capabilities=capabilities,
                    )

                    devices.append(device_info)

                except Exception as e:
                    logger.warning(
                        "EnhancedDeviceSelector",
                        "_enumerate_usb_devices",
                        f"Error processing device: {e}",
                    )
                    continue

        except Exception as e:
            logger.error(
                "EnhancedDeviceSelector",
                "_enumerate_usb_devices",
                f"Error enumerating USB devices: {e}",
            )

        # Sort devices: HiDock devices first, then by name
        devices.sort(key=lambda d: (not d.is_hidock, d.name))
        return devices

    def _is_hidock_device(self, vendor_id: int, product_id: int) -> bool:
        """Check if device is a HiDock device based on VID/PID."""
        # Common HiDock VID/PID combinations
        hidock_devices = [
            (0x0483, 0x5740),  # Example HiDock VID/PID
            (0x0483, 0x5741),  # Another example
            # Add actual HiDock VID/PID combinations here
        ]

        return (vendor_id, product_id) in hidock_devices

    def _on_scan_complete(self, devices: List[DeviceInfo]):
        """Handle successful device scan completion."""
        self.is_scanning = False
        self.devices = devices

        # Update status
        hidock_count = sum(1 for d in devices if d.is_hidock)
        total_count = len(devices)
        text = f"✅ Found {total_count} devices ({hidock_count} HiDock devices)"

        # Call scan callback if provided
        if self.scan_callback:
            self.scan_callback(devices)

    def _on_scan_error(self, error_message: str):
        """Handle device scan error."""
        self.is_scanning = False
        text = f"❌ Scan failed: {error_message}"

    def _select_device(self, device: DeviceInfo):
        """Select a device."""
        self.selected_device = device
        text = f"📱 Selected: {device.name} ({device.status})"

        # Call command callback if provided
        if self.command:
            self.command(device)

        logger.info(
            "EnhancedDeviceSelector",
            "_select_device",
            f"Selected device: {device.name}",
        )

    def get_selected_device(self) -> Optional[DeviceInfo]:
        """Get the currently selected device."""
        return self.selected_device

    def set_devices(self, devices: List[DeviceInfo]):
        """Set devices externally (for testing or manual population)."""
        self.devices = devices

    def refresh_devices(self):
        """Refresh the device list."""
        self._scan_devices()


def create_enhanced_device_selector(parent, command=None, scan_callback=None, **kwargs) -> EnhancedDeviceSelector:
    """Factory function to create an enhanced device selector."""
    return EnhancedDeviceSelector(parent, command=command, scan_callback=scan_callback, **kwargs)


if __name__ == "__main__":
    # Test the enhanced device selector
    def on_device_selected(device):
        print(f"Selected device: {device.name} (HiDock: {device.is_hidock})")

    def on_scan_complete(devices):
        print(f"Scan complete: {len(devices)} devices found")
