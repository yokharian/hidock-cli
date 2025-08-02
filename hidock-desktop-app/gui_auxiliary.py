# gui_auxiliary.py
"""
Auxiliary Mixin for the HiDock Explorer Tool GUI.

This module provides the `AuxiliaryMixin` class, which contains methods
for handling the settings dialog, GUI logging, and other helper functions.
"""
import traceback

import usb.core

from config_and_logger import Logger, logger
from settings_window import SettingsDialog


class AuxiliaryMixin:
    """A mixin for auxiliary GUI functions like settings and logging."""

    def _get_device_display_info(self, dev):
        """
        Fetches display information for a given PyUSB device object.
        Returns a tuple containing the description, VID, PID, and a boolean indicating if there was a problem.
        """
        is_problem = False
        try:
            mfg = usb.util.get_string(dev, dev.iManufacturer, 1000) if dev.iManufacturer else "N/A"
            prod = usb.util.get_string(dev, dev.iProduct, 1000) if dev.iProduct else "N/A"
            desc = f"{mfg} - {prod} (VID: {hex(dev.idVendor)}, " f"PID: {hex(dev.idProduct)})"
        except (usb.core.USBError, NotImplementedError, ValueError) as e_str_fetch:
            is_problem = True
            logger.warning(
                "GUI",
                "scan_usb_devices",
                f"Error getting string for VID={hex(dev.idVendor)} PID={hex(dev.idProduct)} "
                f"({type(e_str_fetch).__name__}): {e_str_fetch}",
            )
            error_type_name = type(e_str_fetch).__name__
            desc = f"[Error Reading Info ({error_type_name})] " f"(VID={hex(dev.idVendor)}, PID={hex(dev.idProduct)})"
        return desc, dev.idVendor, dev.idProduct, is_problem

    def _update_settings_device_combobox(self, devices, initial_load, change_callback):
        """Updates the device selection"""
        combo_list = [d[0] for d in devices]
        values = combo_list if combo_list else ["No devices accessible"]
        settings_vid_var = self.local_vars["selected_vid_var"]
        settings_pid_var = self.local_vars["selected_pid_var"]

        current_sel_str = next(
            (d for d, v, p, _ in devices if v == settings_vid_var.get() and p == settings_pid_var.get()),
            None,
        )

        if current_sel_str and current_sel_str in combo_list:
            self.settings_device_combobox = current_sel_str
        elif combo_list and "---" not in combo_list[0]:
            if not initial_load:
                self.settings_device_combobox = combo_list[0]
                sel_info = next((d for d in devices if d[0] == combo_list[0]), None)
                if sel_info:
                    settings_vid_var.set(sel_info[1])
                    settings_pid_var.set(sel_info[2])
                if change_callback:
                    change_callback()
        elif not combo_list:
            self.settings_device_combobox = "No devices accessible"

    # scan_usb_devices_for_settings is called by SettingsDialog,
    # but defined here as it relates to main app's available_usb_devices
    def scan_usb_devices_for_settings(
        self, initial_load=False, change_callback=None
    ):  # pylint: disable=too-many-locals, too-many-branches, too-many-statements
        """This method is called by the SettingsDialog. It updates self.available_usb_devices
        and then configures the combobox *in the SettingsDialog*."""
        try:
            # If device is connected, use existing device info instead of scanning
            if self.device_manager.device_interface.is_connected():
                logger.info(
                    "GUI",
                    "scan_usb_devices_for_settings",
                    "Device already connected, using existing device info instead of scanning...",
                )

                # Get current device info
                try:
                    import asyncio

                    device_info = asyncio.run(self.device_manager.device_interface.get_device_info())
                    connected_device_desc = (
                        f"Currently Connected: {device_info.name} "
                        f"(VID={hex(device_info.vendor_id)}, "
                        f"PID={hex(device_info.product_id)})"
                    )

                    # Update local_vars with connected device
                    self.local_vars["selected_vid_var"].set(device_info.vendor_id)
                    self.local_vars["selected_pid_var"].set(device_info.product_id)

                    if change_callback:
                        change_callback()
                    return

                except Exception as e:
                    logger.warning(
                        "GUI",
                        "scan_usb_devices_for_settings",
                        f"Failed to get connected device info: {e}, falling back to scan",
                    )

            logger.info(
                "GUI",
                "scan_usb_devices_for_settings",
                "Scanning for USB devices (for settings dialog)...",
            )
            self.available_usb_devices.clear()
            if not self.backend_initialized_successfully:
                logger.error(
                    "GUI",
                    "Scan_USBDevicesForSettings",
                    "Libusb backend not initialized.",
                )
                return

            # Try to acquire the USB lock with a timeout to prevent deadlocks during downloads
            usb_lock = self.device_manager.device_interface.jensen_device.get_usb_lock()
            lock_acquired = usb_lock.acquire(blocking=False)

            if not lock_acquired:
                # If we can't get the lock immediately, it means downloads are active
                logger.info(
                    "GUI",
                    "scan_usb_devices_for_settings",
                    "USB lock is busy (downloads active), skipping device scan",
                )
                return

            try:
                found_devices = usb.core.find(find_all=True, backend=self.usb_backend_instance)
                if not found_devices:
                    logger.info(
                        "GUI",
                        "scan_usb_devices_for_settings",
                        "No USB devices found.",
                    )
                    return

                processed_devices = []
                for dev in found_devices:
                    desc, vid, pid, is_problem = self._get_device_display_info(dev)
                    processed_devices.append((desc, vid, pid, is_problem))
            finally:
                usb_lock.release()

            good_devs = sorted([d for d in processed_devices if not d[3]], key=lambda x: x[0])
            problem_devs = sorted([d for d in processed_devices if d[3]], key=lambda x: x[0])

            # If a device is currently connected, move it to the top of the 'good' list
            if self.device_manager.device_interface.is_connected():
                for i, (desc, vid, pid, _) in enumerate(good_devs):
                    if (
                        vid == self.device_manager.device_interface.jensen_device.device.idVendor
                        and pid == self.device_manager.device_interface.jensen_device.device.idProduct
                    ):
                        name_disp = (
                            self.device_manager.device_interface.jensen_device.model
                            if self.device_manager.device_interface.jensen_device.model != "unknown"
                            else "HiDock Device"
                        )
                        active_desc = f"Currently Connected: {name_disp} (VID={hex(vid)}, PID={hex(pid)})"
                        good_devs[i] = (active_desc, vid, pid, False)
                        good_devs.insert(0, good_devs.pop(i))
                        break

            self.available_usb_devices = good_devs + problem_devs

            if good_devs and "Currently Connected" in good_devs[0][0]:
                good_devs = [good_devs[0]] + sorted(good_devs[1:], key=lambda x: x[0])
            else:
                good_devs.sort(key=lambda x: x[0])
            problem_devs.sort(key=lambda x: x[0])

            all_devices_for_combo = list(good_devs)
            if problem_devs:
                if all_devices_for_combo:
                    all_devices_for_combo.append(("--- Devices with Issues ---", 0, 0, True))
                all_devices_for_combo.extend(problem_devs)

            self._update_settings_device_combobox(
                all_devices_for_combo,
                initial_load,
                change_callback,
            )

            logger.info(
                "GUI",
                "scan_usb_devices",
                f"Found {len(good_devs)} good, {len(problem_devs)} problem devices.",
            )  # pylint: disable=broad-except
        except (usb.core.USBError, AttributeError, TypeError) as e:
            logger.error(
                "GUI",
                "scan_usb_devices_for_settings",
                f"Unhandled exception: {e}\n{traceback.format_exc()}",
            )

    def _apply_device_settings_thread(self, settings_to_apply):  # This is called by SettingsDialog
        if not settings_to_apply:
            logger.info(
                "GUI",
                "_apply_device_settings_thread",
                "No device behavior settings changed.",
            )
            return
        all_successful = True
        for name, value in settings_to_apply.items():
            result = self.device_manager.device_interface.jensen_device.set_device_setting(name, value)
            if not result or result.get("result") != "success":
                all_successful = False
                logger.error(
                    "GUI",
                    "_apply_device_settings_thread",
                    f"Failed to set '{name}' to {value}.",
                )
                self.after(
                    0,
                    lambda n=name: messagebox.showwarning(
                        "Settings Error", f"Failed to apply setting: {n}", parent=self
                    ),
                )
        if all_successful:
            logger.info(
                "GUI",
                "_apply_device_settings_thread",
                "All changed device settings applied.",
            )

    def apply_device_settings_from_dialog(self, settings_to_apply):
        """Public wrapper to apply device settings from the settings dialog.

        Args:
        settings_to_apply (dict): A dictionary of settings to apply to the device.
        """
        # This method provides a public interface for the SettingsDialog
        # to request device settings application.
        self._apply_device_settings_thread(settings_to_apply)
