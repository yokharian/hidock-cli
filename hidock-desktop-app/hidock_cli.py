import asyncio
import os
import subprocess
import sys
import threading
import traceback
from textwrap import dedent

from audio_player_enhanced import EnhancedAudioPlayer
from audio_processing_advanced import AudioEnhancer
from config_and_logger import Logger, load_config, logger, save_config
from constants import DEFAULT_PRODUCT_ID, DEFAULT_VENDOR_ID
from desktop_device_adapter import DesktopDeviceAdapter
from device_actions_mixin import DeviceActionsMixin
from device_interface import DeviceManager
from file_actions_mixin import FileActionsMixin
from file_operations_manager import FileOperationsManager
from storage_management import StorageMonitor, StorageOptimizer
from transcription_module import process_audio_file_for_insights
from tree_view_mixin import TreeViewMixin


class HiDockCLI(DeviceActionsMixin, FileActionsMixin, TreeViewMixin):
    def __init__(self, attempt_auto_connect=True):
        super().__init__()
        self.config = load_config()

        # Make the icon path relative to the script file's location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.usb_backend_instance = None
        self.backend_initialized_successfully = False
        self.backend_init_error_message = "USB backend not yet initialized."
        try:
            (
                self.backend_initialized_successfully,
                self.backend_init_error_message,
                self.usb_backend_instance,
            ) = self.initialize_backend()
            if not self.backend_initialized_successfully:
                logger.error(
                    "MainWindow",
                    "__init__",
                    f"CRITICAL: USB backend init failed: {self.backend_init_error_message}",
                )
        except Exception as e_backend_startup:
            self.backend_initialized_successfully = False
            self.backend_init_error_message = f"Unexpected Python error during USB backend init: {e_backend_startup}"
            logger.error(
                "MainWindow",
                "__init__",
                f"CRITICAL: {self.backend_init_error_message}\n{traceback.format_exc()}",
            )

        self._initialize_vars_from_config()

        self.device_adapter = DesktopDeviceAdapter(self.usb_backend_instance)
        self.device_manager = DeviceManager(self.device_adapter)

        # Initialize device lock before file operations manager
        self.device_lock = threading.Lock()

        self.file_operations_manager = FileOperationsManager(
            self.device_manager,
            self.download_directory,
            os.path.join(os.path.expanduser("~"), ".hidock", "cache"),
            device_lock=self.device_lock,
        )
        self.audio_player = EnhancedAudioPlayer(self)

        self.available_usb_devices = []
        self.displayed_files_details = []
        self.treeview_sort_column = self.saved_treeview_sort_column
        self.treeview_sort_reverse = self.saved_treeview_sort_reverse
        self._recording_check_timer_id = None
        self._auto_file_refresh_timer_id = None
        self._is_ui_refresh_in_progress = False
        self._previous_recording_filename = None
        self.is_long_operation_active = False
        self.cancel_operation_event = None
        self.active_operation_name = None
        self.is_audio_playing = False
        self.current_playing_temp_file = None
        self.current_playing_filename_for_replay = None
        self.playback_update_timer_id = None
        self._user_is_dragging_slider = False
        self.playback_total_duration = 0.0
        self.playback_controls_frame = None
        self._is_button1_pressed_on_item = None
        self.download_queue = []
        self.total_files_in_batch = 0
        self.completed_files_in_batch = 0
        self.batch_start_time = None
        self._connection_error_banner = None
        self._last_dragged_over_iid = None
        self._drag_action_is_deselect = False
        self.default_progressbar_fg_color = None
        self._status_update_in_progress = False
        self.default_progressbar_progress_color = None
        self.original_tree_headings = {
            "num": "#",
            "name": "Name",
            "size": "Size (MB)",
            "duration": "Duration",
            "datetime": "Date/Time",
            "version": "Version",
            "status": "Status",
        }
        self.icons = {}
        self._last_appearance_mode = self.appearance_mode_var
        self.file_menu = None
        self.view_menu = None
        self.actions_menu = None
        self.device_menu = None
        self.toolbar_frame = None
        self.toolbar_connect_button = None
        self.toolbar_refresh_button = None
        self.toolbar_download_button = None
        self.toolbar_play_button = None
        self.toolbar_insights_button = None
        self.toolbar_delete_button = None
        self.toolbar_settings_button = None
        self.status_bar_frame = None
        self.status_connection_label = None
        self.status_progress_text_label = None
        self.status_file_progress_bar = None
        self.main_content_frame = None
        self.status_storage_label_header = None
        self.status_file_counts_label_header = None
        self.download_dir_button_header = None
        self._settings_dialog_instance = None
        self.current_time_label = None
        self.playback_slider = None
        self.total_duration_label = None
        self.volume_slider_widget = None
        self.loop_checkbox = None
        self.clear_selection_button_header = None
        self.clear_log_button = None
        self.log_section_level_combo = None
        self.select_all_button_header = None
        self.file_tree = None
        self.log_frame = None
        self.download_logs_button = None
        self.log_text_area = None

        if attempt_auto_connect:
            self.attempt_autoconnect_on_startup()

    def update_status_bar(self, connection_status=None, progress_text=None):
        logger.info(
            "MainWindow",
            "update_status_bar",
            f"Updating status bar with connection: {connection_status}, progress: {progress_text}",
        )

    def _initialize_vars_from_config(self):
        """
        Initializes Variables from the loaded configuration.

        This method sets up various `ctk.StringVar`, `ctk.BooleanVar`, etc.,
        based on values found in `self.config` or defaults if keys are missing.
        """

        def get_conf(key, default_val):
            return self.config.get(key, default_val)

        self.autoconnect_var = get_conf("autoconnect", False)
        self.download_directory = get_conf("download_directory", os.getcwd())
        self.logger_processing_level_var = get_conf("log_level", "INFO")
        self.selected_vid_var = get_conf("selected_vid", DEFAULT_VENDOR_ID)
        self.selected_pid_var = get_conf("selected_pid", DEFAULT_PRODUCT_ID)
        self.target_interface_var = get_conf("target_interface", 0)
        self.recording_check_interval_var = get_conf("recording_check_interval_s", 3)
        self.default_command_timeout_ms_var = get_conf("default_command_timeout_ms", 5000)
        self.file_stream_timeout_s_var = get_conf("file_stream_timeout_s", 180)
        self.auto_refresh_files_var = get_conf("auto_refresh_files", False)
        self.auto_refresh_interval_s_var = get_conf("auto_refresh_interval_s", 30)
        self.quit_without_prompt_var = get_conf("quit_without_prompt_if_connected", False)
        self.appearance_mode_var = get_conf("appearance_mode", "System")
        self.color_theme_var = get_conf("color_theme", "blue")
        self.suppress_console_output_var = get_conf("suppress_console_output", False)
        self.suppress_gui_log_output_var = get_conf("suppress_gui_log_output", False)
        self.gui_log_filter_level_var = get_conf("gui_log_filter_level", "DEBUG")
        self.device_setting_auto_record_var = False
        self.device_setting_auto_play_var = False
        self.device_setting_bluetooth_tone_var = False
        self.device_setting_notification_sound_var = False
        self.treeview_columns_display_order_str = get_conf(
            "treeview_columns_display_order",
            "num,name,datetime,size,duration,status",
        )
        self.logs_visible_var = get_conf("logs_pane_visible", False)
        self.loop_playback_var = get_conf("loop_playback", False)
        self.volume_var = get_conf("playback_volume", 0.5)
        self.saved_treeview_sort_column = get_conf("treeview_sort_col_id", "datetime")
        self.saved_treeview_sort_reverse = get_conf("treeview_sort_descending", True)
        default_log_colors_fallback = {
            "ERROR": ["#FF6347", "#FF4747"],
            "WARNING": ["#FFA500", "#FFB732"],
            "INFO": ["#606060", "#A0A0A0"],
            "DEBUG": ["#202020", "#D0D0D0"],
            "CRITICAL": ["#DC143C", "#FF0000"],
        }
        loaded_log_colors = get_conf("log_colors", default_log_colors_fallback)
        for level in Logger.LEVELS:
            colors = loaded_log_colors.get(level, default_log_colors_fallback.get(level, ["#000000", "#FFFFFF"]))
            setattr(
                self,
                f"log_color_{level.lower()}_light_var",
                colors[0],
            )
            setattr(
                self,
                f"log_color_{level.lower()}_dark_var",
                colors[1],
            )
        self.icon_pref_light_color = get_conf("icon_theme_color_light", "black")
        self.icon_pref_dark_color = get_conf("icon_theme_color_dark", "white")
        self.icon_fallback_color_1 = get_conf("icon_fallback_color_1", "blue")
        self.icon_fallback_color_2 = get_conf("icon_fallback_color_2", "default")
        self.icon_size_str = get_conf("icon_size_str", "32")

        # AI Transcription settings
        self.ai_api_provider_var = get_conf("ai_api_provider", "gemini")
        self.ai_model_var = get_conf("ai_model", "gemini-2.5-flash")
        self.ai_temperature_var = get_conf("ai_temperature", 0.3)
        self.ai_max_tokens_var = get_conf("ai_max_tokens", 4000)
        self.ai_language_var = get_conf("ai_language", "auto")
        # Provider-specific configuration
        self.ai_openrouter_base_url_var = get_conf("ai_openrouter_base_url", "https://openrouter.ai/api/v1")
        self.ai_amazon_region_var = get_conf("ai_amazon_region", "us-east-1")
        self.ai_qwen_base_url_var = get_conf("ai_qwen_base_url", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        self.ai_deepseek_base_url_var = get_conf("ai_deepseek_base_url", "https://api.deepseek.com")
        self.ai_ollama_base_url_var = get_conf("ai_ollama_base_url", "http://localhost:11434")
        self.ai_lmstudio_base_url_var = get_conf("ai_lmstudio_base_url", "http://localhost:1234/v1")
        # API key is stored encrypted and handled separately

    def get_decrypted_api_key(self, provider=None):
        """Get the decrypted API key for the specified provider."""
        if provider is None:
            provider = self.ai_api_provider_var

        encrypted_key = self.config.get(f"ai_api_key_{provider}_encrypted", "")
        if not encrypted_key:
            return ""

        try:

            import base64

            from cryptography.fernet import Fernet

            # Try to load existing key from config directory
            config_dir = os.path.dirname(self.config.get("config_file_path", ""))
            key_file = os.path.join(config_dir, ".hidock_key.dat")

            if os.path.exists(key_file):
                with open(key_file, "rb") as f:
                    key = f.read()

                f = Fernet(key)
                encrypted_bytes = base64.b64decode(encrypted_key.encode())
                decrypted = f.decrypt(encrypted_bytes)
                return decrypted.decode()

        except Exception as e:
            logger.error("MainWindow", "get_decrypted_api_key", f"Error decrypting API key: {e}")

        return ""

    def update_all_status_info(self):
        """
        Kicks off a background thread to update all informational labels in the GUI
        without blocking the main thread.
        """
        if self._status_update_in_progress:
            return
        self._status_update_in_progress = True
        threading.Thread(target=self._update_all_status_info_thread, daemon=True).start()

    def _update_all_status_info_thread(self):
        """
        Worker thread that fetches device info and then schedules a GUI update.
        This runs in the background and should not touch GUI elements directly.
        """
        try:
            conn_status_text = "Status: Disconnected"
            storage_text = "Storage: ---"
            is_connected = self.device_manager.device_interface.is_connected()
            if is_connected:
                with self.device_lock:
                    device_info = asyncio.run(self.device_manager.device_interface.get_device_info())
                    if device_info:
                        conn_status_text = f"Status: Connected ({device_info.model.value or 'HiDock'})"
                        if device_info.serial_number != "N/A":
                            conn_status_text += f" SN: {device_info.serial_number}"
                    # Avoid getting storage info during file list streaming to prevent command conflicts
                    if (
                        hasattr(self.device_manager.device_interface, "jensen_device")
                        and hasattr(
                            self.device_manager.device_interface.jensen_device,
                            "is_file_list_streaming",
                        )
                        and self.device_manager.device_interface.jensen_device.is_file_list_streaming()
                    ):
                        card_info = None  # Skip during streaming
                    else:
                        card_info = asyncio.run(self.device_manager.device_interface.get_storage_info())
                    if card_info and card_info.total_capacity > 0:
                        used_bytes, capacity_bytes = (
                            card_info.used_space,
                            card_info.total_capacity,
                        )
                        # Define constants for clarity
                        BYTES_PER_MB = 1024 * 1024
                        BYTES_PER_GB = BYTES_PER_MB * 1024

                        # Display in GB if capacity is over ~0.9 GB
                        if capacity_bytes > BYTES_PER_GB * 0.9:
                            used_gb = used_bytes / BYTES_PER_GB
                            capacity_gb = capacity_bytes / BYTES_PER_GB
                            storage_text = f"Storage: {used_gb:.2f}/{capacity_gb:.2f} GB"
                        else:
                            # Otherwise, display in MB
                            used_mb = used_bytes / BYTES_PER_MB
                            capacity_mb = capacity_bytes / BYTES_PER_MB
                            storage_text = f"Storage: {used_mb:.0f}/{capacity_mb:.0f} MB"
                        storage_text += f" (Status: {hex(card_info.status_raw)})"
                    else:
                        storage_text = "Storage: Fetching..."
            elif not self.backend_initialized_successfully:
                conn_status_text = "Status: USB Backend FAILED!"
            self.after(0, self._update_gui_with_status_info, conn_status_text, storage_text)
        finally:
            self._status_update_in_progress = False

    def _update_gui_with_status_info(self, conn_status_text, storage_text):
        self.update_status_bar(connection_status=conn_status_text, progress_text=storage_text)

    def _update_settings_device_combobox(self, devices, initial_load, change_callback):
        """Updates the device selection"""
        combo_list = [d[0] for d in devices]
        values = combo_list if combo_list else ["No devices accessible"]
        settings_vid_var = self.local_vars["selected_vid_var"]
        settings_pid_var = self.local_vars["selected_pid_var"]

        current_sel_str = next(
            (d for d, v, p, _ in devices if v == settings_vid_var and p == settings_pid_var),
            None,
        )

        if current_sel_str and current_sel_str in combo_list:
            self.settings_device_combobox = current_sel_str
        elif combo_list and "---" not in combo_list[0]:
            if not initial_load:
                self.settings_device_combobox = combo_list[0]
                sel_info = next((d for d in devices if d[0] == combo_list[0]), None)
                if sel_info:
                    settings_vid_var = sel_info[1]
                    settings_pid_var = sel_info[2]
                if change_callback:
                    change_callback()
        elif not combo_list:
            self.settings_device_combobox = "No devices accessible"

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
                    lambda n=name: logger.warning("CLI", "Settings Error", f"Failed to apply setting: {n}"),
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

    def _update_menu_states(self):
        """
        Updates the state (enabled/disabled) of menu items and toolbar buttons.
        """
        return  # TODO - implement this method to CLI
        is_connected = self.device_manager.device_interface.is_connected()
        has_selection = bool(
            hasattr(self, "file_tree") and self.file_tree.winfo_exists() and self.file_tree.selection()
        )
        num_selected = len(self.file_tree.selection()) if has_selection else 0
        if hasattr(self, "file_menu"):
            self.file_menu.entryconfig(
                "Connect to HiDock",
                state=("normal" if not is_connected and self.backend_initialized_successfully else "disabled"),
            )
            self.file_menu.entryconfig("Disconnect", state="normal" if is_connected else "disabled")
        if hasattr(self, "view_menu"):
            self.view_menu.entryconfig("Refresh File List", state="normal" if is_connected else "disabled")
        can_play_selected = is_connected and num_selected == 1
        if can_play_selected:
            file_iid = self.file_tree.selection()[0]
            file_detail = next(
                (f for f in self.displayed_files_details if f["name"] == file_iid),
                None,
            )
            if not (
                file_detail
                and (file_detail["name"].lower().endswith(".wav") or file_detail["name"].lower().endswith(".hda"))
            ):
                can_play_selected = False
        if hasattr(self, "actions_menu"):
            self.actions_menu.entryconfig(
                "Download Selected",
                state="normal" if is_connected and has_selection else "disabled",
            )
            self.actions_menu.entryconfig("Play Selected", state="normal" if can_play_selected else "disabled")
            self.actions_menu.entryconfig(
                "Get Insights",
                state=(
                    "normal"
                    if is_connected
                    and has_selection
                    and num_selected == 1
                    and not self.is_long_operation_active
                    and not self.is_audio_playing
                    else "disabled"
                ),
            )
            self.actions_menu.entryconfig(
                "Delete Selected",
                state="normal" if is_connected and has_selection else "disabled",
            )
            can_select_all = (
                hasattr(self, "file_tree")
                and self.file_tree.winfo_exists()
                and len(self.file_tree.get_children()) > 0
                and num_selected < len(self.file_tree.get_children())
            )
            self.actions_menu.entryconfig("Select All", state="normal" if can_select_all else "disabled")
            self.actions_menu.entryconfig("Clear Selection", state="normal" if has_selection else "disabled")

            # Check if there are active downloads to cancel
            active_downloads = [
                op
                for op in self.file_operations_manager.get_all_active_operations()
                if op.operation_type.value == "download" and op.status.value in ["pending", "in_progress"]
            ]

            # Check if selected files have active downloads
            selected_filenames = (
                [self.file_tree.item(iid)["values"][1] for iid in self.file_tree.selection()] if has_selection else []
            )

            selected_active_downloads = [op for op in active_downloads if op.filename in selected_filenames]

            self.actions_menu.entryconfig(
                "Cancel Selected Downloads",
                state="normal" if selected_active_downloads else "disabled",
            )
            self.actions_menu.entryconfig(
                "Cancel All Downloads",
                state="normal" if active_downloads else "disabled",
            )

            # Update playback controls based on audio player state
            is_playing = hasattr(self, "audio_player") and self.audio_player.state.value in ["playing", "paused"]
            self.actions_menu.entryconfig("Stop Playback", state="normal" if is_playing else "disabled")
        if hasattr(self, "device_menu"):
            self.device_menu.entryconfig("Sync Device Time", state="normal" if is_connected else "disabled")
            self.device_menu.entryconfig("Format Storage", state="normal" if is_connected else "disabled")
        if hasattr(self, "toolbar_connect_button") and self.toolbar_connect_button.winfo_exists():
            if is_connected:
                self.toolbar_connect_button.configure(
                    text="Disconnect",
                    command=self.disconnect_device,
                    state="normal",
                )
            else:
                self.toolbar_connect_button.configure(
                    text="Connect",
                    command=self.connect_device,
                    state=("normal" if self.backend_initialized_successfully else "disabled"),
                )
        if hasattr(self, "toolbar_refresh_button") and self.toolbar_refresh_button.winfo_exists():
            self.toolbar_refresh_button.configure(
                state=(
                    "normal"
                    if is_connected and not self._is_ui_refresh_in_progress and not self.is_long_operation_active
                    else "disabled"
                )
            )
        if hasattr(self, "toolbar_download_button") and self.toolbar_download_button.winfo_exists():
            if self.is_long_operation_active and self.active_operation_name == "Download Queue":
                self.toolbar_download_button.configure(
                    text="Cancel DL",
                    command=self.request_cancel_operation,
                    state="normal",
                )
            else:
                self.toolbar_download_button.configure(
                    text="Download",
                    command=self.download_selected_files_gui,
                    state=(
                        "normal"
                        if is_connected
                        and has_selection
                        and not self.is_long_operation_active
                        and not self.is_audio_playing
                        else "disabled"
                    ),
                )
        if hasattr(self, "toolbar_play_button") and self.toolbar_play_button.winfo_exists():
            if self.is_audio_playing:
                self.toolbar_play_button.configure(
                    text="Stop",
                    command=self._stop_audio_playback,
                    state="normal",
                )
            elif self.is_long_operation_active and self.active_operation_name == "Playback Preparation":
                self.toolbar_play_button.configure(
                    text="Cancel Prep",
                    command=self.request_cancel_operation,
                    state="normal",
                )
            else:
                self.toolbar_play_button.configure(
                    text="Play",
                    command=self.play_selected_audio_gui,
                    state=("normal" if can_play_selected and not self.is_long_operation_active else "disabled"),
                )
        if hasattr(self, "toolbar_insights_button") and self.toolbar_insights_button.winfo_exists():
            if self.is_long_operation_active and self.active_operation_name == "Transcription":
                self.toolbar_insights_button.configure(
                    text="Cancel Insights",
                    command=self.request_cancel_operation,
                    state="normal",
                )
            else:
                self.toolbar_insights_button.configure(
                    text="Get Insights",
                    command=self.get_insights_selected_file_gui,
                    state=(
                        "normal"
                        if is_connected
                        and has_selection
                        and num_selected == 1
                        and not self.is_long_operation_active
                        and not self.is_audio_playing
                        else "disabled"
                    ),
                )
        if hasattr(self, "toolbar_delete_button") and self.toolbar_delete_button.winfo_exists():
            if self.is_long_operation_active and self.active_operation_name == "Deletion":
                self.toolbar_delete_button.configure(
                    text="Cancel Del.",
                    command=self.request_cancel_operation,
                    state="normal",
                )
            else:
                self.toolbar_delete_button.configure(
                    text="Delete",
                    command=self.delete_selected_files_gui,
                    state=(
                        "normal"
                        if is_connected
                        and has_selection
                        and not self.is_long_operation_active
                        and not self.is_audio_playing
                        else "disabled"
                    ),
                )
        if hasattr(self, "toolbar_settings_button") and self.toolbar_settings_button.winfo_exists():
            self.toolbar_settings_button.configure(state="normal")

    def get_insights_selected_file_gui(self):
        raise NotImplementedError()
        # self._transcribe_selected_audio_gemini_for_panel(file_iid)

    def _transcribe_selected_audio_gemini_for_panel(self, file_iid):
        """Transcribe selected audio and display results in the integrated panel."""
        import os
        import threading

        # from transcription_module import process_audio_file_for_insights  # Future: for audio insights feature

        file_detail = next((f for f in self.displayed_files_details if f["name"] == file_iid), None)
        if not file_detail:
            logger.error(
                "MainWindow",
                "Transcription Error",
                "File details not found.",
            )
            return

        local_filepath = self._get_local_filepath(file_detail["name"])
        if not os.path.isfile(local_filepath):
            logger.error(
                "MainWindow",
                "File Not Found",
                f"Local file not found: {local_filepath}\nPlease download the file first.",
            )
            return

        # Get API key from encrypted settings
        gemini_api_key = self.get_decrypted_api_key()
        if not gemini_api_key:
            logger.error(
                "MainWindow",
                "API Key Missing",
                "AI API Key not configured. Please set your API key in Settings > AI Transcription.",
            )
            return

        # Update UI to show processing state
        self._show_transcription_processing_state(file_detail["name"])

        # Show the toolbar since we're about to show transcription content
        self._update_panels_toolbar_visibility()

        # Cancel any existing transcription
        if self.current_transcription_thread and self.current_transcription_thread.is_alive():
            self._cancel_transcription()

        # Start transcription in background thread
        self._set_long_operation_active_state(True, "Transcription")
        self.update_status_bar(progress_text=f"Transcribing {file_detail['name']} with Gemini...")

        # Reset cancellation flag
        self.transcription_cancelled = False

        self.current_transcription_thread = threading.Thread(
            target=self._transcription_worker_for_panel,
            args=(local_filepath, gemini_api_key, file_detail["name"]),
            daemon=True,
        )
        self.current_transcription_thread.start()

    def _show_transcription_processing_state(self, filename):
        """Update the transcription panel to show processing state."""
        # Ensure panel is visible
        if not self.transcription_panel_visible:
            self._toggle_transcription_panel()

        # Show processing status with cancel button
        self.transcription_status_label.configure(
            text=f"🔄 Processing '{filename}' with AI transcription and insights..."
        )
        self.cancel_transcription_button.pack(side="right", padx=(10, 0))

        # Show progress bar with indeterminate mode
        self.transcription_progress.pack(fill="x", padx=10, pady=(0, 10))
        self.transcription_progress.configure(mode="indeterminate")
        self.transcription_progress.start()

        # Clear previous content and show placeholders
        self.transcription_textbox.delete("1.0", "end")
        self.transcription_textbox.insert("1.0", "🎵 Transcribing audio... Please wait.")
        self.transcription_textbox.configure(state="disabled")

        self.insights_textbox.delete("1.0", "end")
        self.insights_textbox.insert("1.0", "🧠 Extracting insights... Please wait.")
        self.insights_textbox.configure(state="disabled")

        # Show the content sections
        self.transcription_section.pack(fill="both", expand=True, padx=5, pady=5)
        self.insights_section.pack(fill="both", expand=True, padx=5, pady=5)

    def _cancel_transcription(self):
        """Cancel the current transcription process."""
        self.transcription_cancelled = True
        if self.current_transcription_thread and self.current_transcription_thread.is_alive():
            logger.info("MainWindow", "_cancel_transcription", "Transcription cancellation requested")
            # Update UI immediately
            self.after(0, self._on_transcription_cancelled)

    def _on_transcription_cancelled(self):
        """Handle transcription cancellation in main thread."""
        self._set_long_operation_active_state(False, "Transcription")
        self.update_status_bar(ready_text="Transcription cancelled")

        # Update UI
        self.transcription_status_label.configure(text="❌ Transcription cancelled by user")
        self.cancel_transcription_button.pack_forget()
        self.transcription_progress.stop()
        self.transcription_progress.pack_forget()

        # Reset content
        self.transcription_textbox.configure(state="normal")
        self.transcription_textbox.delete("1.0", "end")
        self.transcription_textbox.insert("1.0", "Transcription was cancelled.")
        self.transcription_textbox.configure(state="disabled")

        self.insights_textbox.configure(state="normal")
        self.insights_textbox.delete("1.0", "end")
        self.insights_textbox.insert("1.0", "Insights extraction was cancelled.")
        self.insights_textbox.configure(state="disabled")

    def _transcription_worker_for_panel(self, file_path, api_key, original_filename):
        """Background worker that processes transcription for the panel display."""
        try:
            # Check for cancellation before starting
            if self.transcription_cancelled:
                return

            import asyncio

            # Get AI provider configuration
            provider = self.ai_api_provider_var
            config = {
                "model": self.ai_model_var,
                "temperature": self.ai_temperature_var,
                "max_tokens": self.ai_max_tokens_var,
                "base_url": getattr(self, f"ai_{provider}_base_url_var", None),
                "region": getattr(self, f"ai_{provider}_region_var", None),
            }
            # Clean up None values
            config = {k: v if hasattr(v, "get") else v for k, v in config.items() if v is not None}
            language = self.ai_language_var

            # Since process_audio_file_for_insights is async, we need to run it in an event loop
            results = asyncio.run(process_audio_file_for_insights(file_path, provider, api_key, config, language))

            # Check for cancellation before updating UI
            if self.transcription_cancelled:
                return

            self.after(0, self._on_transcription_complete_for_panel, results, original_filename)
        except Exception as e:
            if not self.transcription_cancelled:
                logger.error(
                    "MainWindow",
                    "_transcription_worker_for_panel",
                    f"Error during transcription: {e}",
                )
                self.after(
                    0,
                    self._on_transcription_complete_for_panel,
                    {"error": str(e)},
                    original_filename,
                )

    def _set_long_operation_active_state(
        self, state=False, text="Transcription"
    ): ...  # Placeholder for the method that sets the long operation state

    def _on_transcription_complete_for_panel(self, results, original_filename):
        """Handle completion of transcription and update the panel."""
        self._set_long_operation_active_state(False, "Transcription")

        # Hide progress controls
        self.cancel_transcription_button.pack_forget()
        self.transcription_progress.stop()
        self.transcription_progress.pack_forget()

        if "error" in results:
            # Show error in panel
            self.transcription_status_label.configure(
                text=f"❌ Error transcribing '{original_filename}': {results['error']}"
            )
            self.transcription_textbox.configure(state="normal")
            self.transcription_textbox.delete("1.0", "end")
            self.transcription_textbox.insert("1.0", f"Error: {results['error']}")
            self.transcription_textbox.configure(state="disabled")

            self.insights_textbox.configure(state="normal")
            self.insights_textbox.delete("1.0", "end")
            self.insights_textbox.insert("1.0", "Insights unavailable due to transcription error.")
            self.insights_textbox.configure(state="disabled")

            self.update_status_bar(progress_text=f"Transcription failed for {original_filename}.")
        else:
            # Show successful results
            transcription_text = results.get("transcription", "No transcription found.")
            insights = results.get("insights", {})

            # Update status
            self.transcription_status_label.configure(
                text=f"✅ Transcription and insights completed for '{original_filename}'"
            )

            # Update transcription text
            self.transcription_textbox.configure(state="normal")
            self.transcription_textbox.delete("1.0", "end")
            self.transcription_textbox.insert("1.0", transcription_text)
            self.transcription_textbox.configure(state="disabled")

            # Format and display insights
            insights_formatted = self._format_insights_for_display(insights)
            self.insights_textbox.configure(state="normal")
            self.insights_textbox.delete("1.0", "end")
            self.insights_textbox.insert("1.0", insights_formatted)
            self.insights_textbox.configure(state="disabled")

            self.update_status_bar(progress_text=f"Transcription complete for {original_filename}.")

            # Mark content as loaded
            self.transcription_content_loaded = True

    def _format_insights_for_display(self, insights):
        """Format the insights dictionary for readable display."""
        if not insights:
            return "No insights available."

        formatted = ""

        # Summary
        if insights.get("summary", "N/A") != "N/A":
            formatted += f"📋 SUMMARY:\n{insights.get('summary', 'N/A')}\n\n"

        # Category
        if insights.get("category", "N/A") != "N/A":
            formatted += f"🏷️ CATEGORY: {insights.get('category', 'N/A')}\n\n"

        # Meeting Details
        meeting_details = insights.get("meeting_details", {})
        if meeting_details and any(v != "N/A" and v != 0 for v in meeting_details.values()):
            formatted += "📅 MEETING DETAILS:\n"
            if meeting_details.get("date", "N/A") != "N/A":
                formatted += f"  Date: {meeting_details.get('date', 'N/A')}\n"
            if meeting_details.get("time", "N/A") != "N/A":
                formatted += f"  Time: {meeting_details.get('time', 'N/A')}\n"
            if meeting_details.get("location", "N/A") != "N/A":
                formatted += f"  Location: {meeting_details.get('location', 'N/A')}\n"
            if meeting_details.get("duration_minutes", 0) > 0:
                formatted += f"  Duration: {meeting_details.get('duration_minutes', 0)} minutes\n"
            formatted += "\n"

        # Sentiment
        if insights.get("overall_sentiment_meeting", "N/A") != "N/A":
            formatted += f"😊 SENTIMENT: {insights.get('overall_sentiment_meeting', 'N/A')}\n\n"

        # Action Items
        action_items = insights.get("action_items", [])
        if action_items:
            formatted += "✅ ACTION ITEMS:\n"
            for i, item in enumerate(action_items, 1):
                formatted += f"  {i}. {item}\n"
            formatted += "\n"

        # Project Context
        if insights.get("project_context", "N/A") != "N/A":
            formatted += f"🔗 PROJECT CONTEXT:\n{insights.get('project_context', 'N/A')}\n"

        return formatted if formatted else "No detailed insights available."

    def _check_dependencies(self):
        """Check for missing dependencies and show user-friendly warnings."""
        try:
            import shutil

            # Check for ffmpeg
            ffmpeg_available = False
            try:
                # Try to find ffmpeg in PATH
                if shutil.which("ffmpeg"):
                    ffmpeg_available = True
                else:
                    # Try to run ffmpeg to see if it's available
                    subprocess.run(
                        ["ffmpeg", "-version"],
                        capture_output=True,
                        check=True,
                        timeout=5,
                    )
                    ffmpeg_available = True
            except (
                subprocess.CalledProcessError,
                subprocess.TimeoutExpired,
                FileNotFoundError,
            ):
                ffmpeg_available = False

            if not ffmpeg_available:
                logger.warning(
                    "MainWindow",
                    "_check_dependencies",
                    "FFmpeg not found - audio conversion features will be limited",
                )

                # Show user-friendly warning
                self._show_ffmpeg_warning()

        except Exception as e:
            logger.error("MainWindow", "_check_dependencies", f"Error checking dependencies: {e}")

    def _show_ffmpeg_warning(self):
        """Show a user-friendly warning about missing ffmpeg dependency."""
        import platform

        system = platform.system().lower()

        if system == "windows":
            install_msg = """To install FFmpeg on Windows:
            1. Download from: https://ffmpeg.org/download.html#build-windows
            2. Extract to a folder (e.g., C:\\ffmpeg)
            3. Add C:\\ffmpeg\\bin to your PATH environment variable
            4. Restart the application

            Alternative: Install via Chocolatey: choco install ffmpeg"""
        elif system == "darwin":  # macOS
            install_msg = """To install FFmpeg on macOS:
            1. Install Homebrew: https://brew.sh
            2. Run: brew install ffmpeg
            3. Restart the application

            Alternative: Download from https://ffmpeg.org/download.html#build-mac"""
        else:  # Linux
            install_msg = """To install FFmpeg on Linux:
            Ubuntu/Debian: sudo apt update && sudo apt install ffmpeg
            CentOS/RHEL: sudo yum install ffmpeg
            Fedora: sudo dnf install ffmpeg
            Arch: sudo pacman -S ffmpeg

            Alternative: Download from https://ffmpeg.org/download.html#build-linux"""

        message = f"""FFmpeg Not Found

        Advanced audio format conversion features are currently unavailable.
        Basic audio playback will still work normally.

        {dedent(install_msg)}

        You can dismiss this warning and continue using the application with limited audio conversion capabilities."""

        logger.error("MainWindow", "_show_ffmpeg_error", message)

    def _play_local_file(self, local_filepath):
        """Loads and plays a local file, and updates the visualizer."""
        self.audio_player.load_track(local_filepath)

        self.audio_player.play()

        # Update UI state to reflect playback
        self.is_audio_playing = True
        self.current_playing_filename_for_replay = os.path.basename(local_filepath)
        self._update_menu_states()

    def _download_for_playback_and_play(self, filename, local_filepath):
        """
        Downloads a single file and triggers playback upon successful completion.
        """
        # Show brief status message instead of interrupting dialog
        self.update_status_bar(progress_text=f"Downloading '{filename}' for playback...")

        def on_playback_download_complete(operation):
            """Callback for the file operation manager."""
            from file_operations_manager import FileOperationStatus

            # Operations are on a worker thread, so GUI updates must be scheduled on the main thread.
            self.after(0, self._update_operation_progress, operation)

            if operation.status == FileOperationStatus.COMPLETED:
                self.after(0, self._play_local_file, local_filepath)
            elif operation.status in (
                FileOperationStatus.FAILED,
                FileOperationStatus.CANCELLED,
            ):
                error_msg = operation.error_message or "Operation was cancelled."
                self.after(
                    0,
                    lambda: logger.error(
                        "MainWindow", "Playback Error", f"Could not download file for playback: {error_msg}"
                    ),
                )

        self.file_operations_manager.queue_batch_download([filename], on_playback_download_complete)

    def on_closing(self):
        """
        Handles the window closing event.
        """
        logger.info("MainWindow", "on_closing", "Window closing event triggered.")
        if self.device_manager.device_interface.is_connected():
            logger.info("MainWindow", "on_closing", "Quit cancelled by user.")
            return
        self.config["window_geometry"] = self.geometry()
        self.config["autoconnect"] = self.autoconnect_var
        self.config["download_directory"] = self.download_directory
        self.config["log_level"] = self.logger_processing_level_var
        self.config["selected_vid"] = self.selected_vid_var
        self.config["selected_pid"] = self.selected_pid_var
        self.config["target_interface"] = self.target_interface_var
        self.config["recording_check_interval_s"] = self.recording_check_interval_var
        self.config["default_command_timeout_ms"] = self.default_command_timeout_ms_var
        self.config["file_stream_timeout_s"] = self.file_stream_timeout_s_var
        self.config["auto_refresh_files"] = self.auto_refresh_files_var
        self.config["auto_refresh_interval_s"] = self.auto_refresh_interval_s_var
        self.config["quit_without_prompt_if_connected"] = self.quit_without_prompt_var
        self.config["appearance_mode"] = self.appearance_mode_var
        self.config["color_theme"] = self.color_theme_var
        self.config["suppress_console_output"] = self.suppress_console_output_var
        self.config["suppress_gui_log_output"] = self.suppress_gui_log_output_var
        self.config["gui_log_filter_level"] = self.gui_log_filter_level_var
        # self.config["treeview_columns_display_order"] = ",".join(self.file_tree["displaycolumns"])
        self.config["logs_pane_visible"] = self.logs_visible_var
        self.config["loop_playback"] = self.loop_playback_var
        self.config["playback_volume"] = self.volume_var
        self.config["treeview_sort_col_id"] = self.saved_treeview_sort_column
        self.config["treeview_sort_descending"] = self.saved_treeview_sort_reverse
        log_colors_to_save = {}
        for level in Logger.LEVELS:
            light_var = getattr(self, f"log_color_{level.lower()}_light_var", None)
            dark_var = getattr(self, f"log_color_{level.lower()}_dark_var", None)
            if light_var and dark_var:
                log_colors_to_save[level] = [light_var, dark_var]
        self.config["log_colors"] = log_colors_to_save
        self.config["icon_theme_color_light"] = self.icon_pref_light_color
        self.config["icon_theme_color_dark"] = self.icon_pref_dark_color
        self.config["icon_fallback_color_1"] = self.icon_fallback_color_1
        self.config["icon_fallback_color_2"] = self.icon_fallback_color_2
        self.config["icon_size_str"] = self.icon_size_str
        save_config(self.config)
        if self.device_manager.device_interface.is_connected():
            self.device_manager.device_interface.disconnect()
        if self.current_playing_temp_file and os.path.exists(self.current_playing_temp_file):
            try:
                os.remove(self.current_playing_temp_file)
            except OSError as e:
                logger.warning(
                    "MainWindow",
                    "on_closing",
                    f"Could not remove temp playback file {self.current_playing_temp_file}: {e}",
                )
        logger.info("MainWindow", "on_closing", "Application shutdown complete.")
        sys.exit(0)

    def _process_selected_audio(self, file_iid):
        file_detail = next((f for f in self.displayed_files_details if f["name"] == file_iid), None)
        if not file_detail:
            logger.error(
                "MainWindow",
                "Audio Processing Error",
                "File details not found.",
            )
            return

        local_filepath = self._get_local_filepath(file_detail["name"])
        if not os.path.exists(local_filepath):
            logger.warning(
                "MainWindow",
                "Audio Processing",
                "File not downloaded. Please download it first.",
            )
            return
        # Add processing options to the dialog
        # ... (This will be implemented in a future step)

        def process_audio():
            # Get selected options
            # ...

            # Run the audio enhancer
            _enhancer = AudioEnhancer()  # Future: implement audio enhancement features
            # ... (call enhancer methods)

    def show_system_health(self):
        storage_monitor = StorageMonitor([self.download_directory])
        _storage_info = storage_monitor.get_storage_info()  # Future: display in health dialog

        # Display storage info in the dialog
        # ... (This will be implemented in a future step)
        logger.info(
            "MainWindow",
            "show_system_health",
            f"Storage info: {_storage_info}",
        )

    def show_storage_optimizer(self):
        storage_optimizer = StorageOptimizer([self.download_directory])
        _optimization_suggestions = storage_optimizer.analyze_storage()  # Future: display suggestions

        # Display optimization suggestions in the dialog
        # ... (This will be implemented in a future step)
        logger.info(
            "MainWindow",
            "show_storage_optimizer",
            f"Optimization suggestions: {_optimization_suggestions}",
        )
