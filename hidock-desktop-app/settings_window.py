"""
Settings Dialog for the HiDock Explorer Tool.

This module defines the `SettingsDialog` class, allows users to configure various application settings.
It interacts with the main `HiDockToolGUI` to load, display, and apply
changes to general application preferences, connection parameters,
operation timeouts, device-specific behaviors, and logging options.
"""

import base64

# import json  # Future: for advanced configuration import/export
import os
import threading  # For device settings apply thread

import usb.core  # For specific exception handling

try:
    from cryptography.fernet import Fernet

    ENCRYPTION_AVAILABLE = True
except ImportError:
    ENCRYPTION_AVAILABLE = False
from config_and_logger import Logger, logger, save_config  # For type hint and logger instance


class SettingsDialog:
    """
    A top-level class for configuring application settings.

    allows users to modify general application preferences,
    connection parameters, operation timeouts, device-specific behaviors,
    and logging options. It interacts with the main CLI instance to
    load initial settings and apply changes.
    """

    def __init__(self, initial_config, hidock_instance, *args, **kwargs):
        """
        Initializes the SettingsDialog window.

        Args:
        initial_config (dict): A snapshot of the configuration dictionary
        when the dialog was opened.
        hidock_instance: The HiDockJensen instance for device interaction.
        *args: Variable length argument list for CTkToplevel.
        **kwargs: Arbitrary keyword arguments for CTkToplevel.
        """
        super().__init__(self, *args, **kwargs)
        self.initial_config_snapshot = initial_config  # A snapshot of config at dialog open
        self.dock = hidock_instance  # HiDockJensen instance

        self.title("Application Settings")
        self.local_vars = {}

        # Store the initial download directory separately for comparison
        self.initial_download_directory = self.download_directory
        self.current_dialog_download_dir = [self.download_directory]  # Mutable for dialog changes

        # Initialize attributes that will hold widget instances later
        self.current_dl_dir_label_settings = None
        self.settings_device_combobox = None
        self.auto_record_checkbox = None
        self.auto_play_checkbox = None
        self.bt_tone_checkbox = None
        self.notification_sound_checkbox = None

        self._fetched_device_settings_for_dialog = {}  # Cache for device settings

        self._create_settings_widgets()

        # If device is connected, load its specific settings
        if self.dock.is_connected():
            threading.Thread(target=self._load_device_settings_for_dialog_thread, daemon=True).start()

    def _populate_ai_transcription_tab(self, tab):
        """Populates the 'AI Transcription' tab with AI service settings."""
        raise NotImplementedError()
        # API Provider Selection
        # text = "AI Service Provider:"
        # self.local_vars["ai_api_provider_var"]
        # command = self._on_ai_provider_changed
        # values = [
        #     "gemini",
        #     "openai",
        #     "anthropic",
        #     "openrouter",
        #     "amazon",
        #     "qwen",
        #     "deepseek",
        #     "ollama",
        #     "lmstudio",
        # ]

        # # API Key Entry
        # text = "API Key:"
        # command = self._validate_api_key

        # # Model Selection
        # variable = (self.local_vars["ai_model_var"],)
        # values = [
        #     "gemini-2.5-flash",
        #     "gemini-2.5-pro",
        #     "gemini-2.5-lite",
        #     "gemini-2.0-flash",
        #     "gemini-1.5-flash",
        #     "gemini-1.5-pro",
        #     "gpt-4o-mini",
        #     "gpt-4o",
        # ]

        # # Temperature Setting
        # text = "Temperature (0.0 - 1.0):"
        # self.local_vars["ai_temperature_var"]
        # text = f"{temp_value:.2f}"

        # # Max Tokens Setting
        # text = "Max Tokens:"
        # self.local_vars["ai_max_tokens_var"],

        # # Language Setting
        # self.local_vars["ai_language_var"],
        # values = (["auto", "en", "es", "fr", "de", "pt", "zh", "ja", "ko"],)

    def _update_provider_config(self):
        """Show/hide provider-specific configuration based on selected provider"""
        raise NotImplementedError()
        # provider = self.local_vars["ai_api_provider_var"]

        # # Hide all provider config frames first
        # config_frames = [
        #     "openrouter_frame",
        #     "amazon_frame",
        #     "qwen_frame",
        #     "deepseek_frame",
        #     "ollama_frame",
        #     "lmstudio_frame",
        # ]
        # for frame_name in config_frames:
        #     if hasattr(self, frame_name):
        #         getattr(self, frame_name).pack_forget()

        # # Show relevant provider config frame
        # frame_mapping = {
        #     "openrouter": "openrouter_frame",
        #     "amazon": "amazon_frame",
        #     "qwen": "qwen_frame",
        #     "deepseek": "deepseek_frame",
        #     "ollama": "ollama_frame",
        #     "lmstudio": "lmstudio_frame",
        # }

        # frame_name = frame_mapping.get(provider)
        # if frame_name and hasattr(self, frame_name):
        #     getattr(self, frame_name).pack(fill="x", pady=2, padx=5)

        # ##
        # ##
        # text = "Provider Configuration:"
        # ##
        # ##

        # # OpenRouter Configuration
        # text = "Base URL:"
        # self.local_vars["ai_openrouter_base_url_var"]
        # placeholder_text = "https://openrouter.ai/api/v1"

        # # Amazon Bedrock Configuration
        # text = "AWS Region:"
        # self.amazon_frame
        # self.local_vars["ai_amazon_region_var"]
        # values = [
        #     "us-east-1",
        #     "us-west-2",
        #     "eu-west-1",
        #     "ap-southeast-1",
        #     "ap-northeast-1",
        # ]

        # # Qwen Configuration
        # self.qwen_frame
        # text = "API Base URL:"
        # self.local_vars["ai_qwen_base_url_var"]
        # placeholder_text = "https://dashscope.aliyuncs.com/compatible-mode/v1"

        # # DeepSeek Configuration
        # self.deepseek_frame
        # text = "API Base URL:"
        # textvariable = self.local_vars["ai_deepseek_base_url_var"]
        # placeholder_text = "https://api.deepseek.com"

        # # Ollama Configuration
        # self.ollama_frame
        # text = "🏠 Local Ollama Server:"
        # textvariable = self.local_vars["ai_ollama_base_url_var"]
        # placeholder_text = "http://localhost:11434"
        # text_info = ("💡 Tip: Install Ollama locally and pull models with 'ollama pull llama3.2'",)

        # # LM Studio Configuration
        # self.lmstudio_frame
        # text = "🏠 Local LM Studio Server:"
        # self.lmstudio_frame
        # textvariable = self.local_vars["ai_lmstudio_base_url_var"]
        # text_info = "💡 Tip: Download LM Studio and start local server with your preferred model"

    def _validate_numeric_settings(self):
        """
        Validates numeric settings and shows error messages for invalid values.
        Returns True if all values are valid, False otherwise.
        """
        numeric_vars = {
            "selected_vid_var": ("Vendor ID", 0, 0xFFFF),
            "selected_pid_var": ("Product ID", 0, 0xFFFF),
            "target_interface_var": ("Target Interface", 0, 10),
            "recording_check_interval_var": ("Recording Check Interval", 1, 3600),
            "default_command_timeout_ms_var": ("Command Timeout", 100, 60000),
            "file_stream_timeout_s_var": ("File Stream Timeout", 1, 300),
            "auto_refresh_interval_s_var": ("Auto Refresh Interval", 1, 3600),
        }

        for var_name, (display_name, min_val, max_val) in numeric_vars.items():
            if var_name in self.local_vars:
                value_str = self.local_vars[var_name].strip()

                # Check for empty string
                if not value_str:
                    logger.error(
                        "SettingsDialog",
                        "_validate_numeric_settings",
                        f"{display_name} cannot be empty. Please enter a valid number.",
                    )
                    return False

                # Try to convert to integer
                try:
                    value = int(value_str)
                except ValueError:
                    logger.error(
                        "SettingsDialog",
                        "_validate_numeric_settings",
                        f"{display_name} must be a valid integer. Got: '{value_str}'",
                    )
                    return False

                # Check range
                if not (min_val <= value <= max_val):
                    logger.error(
                        "SettingsDialog",
                        "_validate_numeric_settings",
                        f"{display_name} must be between {min_val} and {max_val}. Got: {value}",
                    )
                    return False

        return True

    def _perform_apply_settings_logic(self, update_dialog_baseline=False):
        raise NotImplementedError()
        # Validate numeric settings first
        if not self._validate_numeric_settings():
            return  # Don't apply if validation fails

        # Apply local_vars to parent_gui's vars and config
        for var_name, local_tk_var in self.local_vars.items():
            if hasattr(self, var_name):
                parent_var = getattr(self, var_name)

                # Convert string values back to integers for numeric variables
                value = local_tk_var
                if var_name in [
                    "selected_vid_var",
                    "selected_pid_var",
                    "target_interface_var",
                    "recording_check_interval_var",
                    "default_command_timeout_ms_var",
                    "file_stream_timeout_s_var",
                    "auto_refresh_interval_s_var",
                ]:
                    value = int(value.strip())

                parent_var = value  # This will trigger traces on parent if any

                # Update the main config dictionary directly for saving
                # Need to map var_name (e.g. "autoconnect_var") to config key (e.g. "autoconnect")
                config_key = var_name.replace("_var", "")

                # Special mappings for config keys that don't follow the simple pattern
                if config_key == "recording_check_interval":
                    config_key = "recording_check_interval_s"
                elif config_key == "default_command_timeout_ms":
                    config_key = "default_command_timeout_ms"  # Already correct
                elif config_key == "file_stream_timeout_s":
                    config_key = "file_stream_timeout_s"  # Already correct
                elif config_key == "auto_refresh_interval_s":
                    config_key = "auto_refresh_interval_s"  # Already correct

                if config_key.startswith("log_color_") and config_key.endswith(("_light", "_dark")):
                    pass  # Log colors handled separately
                elif config_key.startswith("device_setting_"):  # These are not directly in config
                    pass
                else:
                    self.config[config_key] = value

        # Apply log colors
        if "log_colors" not in self.config:
            self.config["log_colors"] = {}
        for level_key in Logger.LEVELS:  # Iterate directly over dictionary keys
            level_lower = level_key.lower()
            self.config["log_colors"][level_key] = [
                self.local_vars[f"log_color_{level_lower}_light_var"],
                self.local_vars[f"log_color_{level_lower}_dark_var"],
            ]

        # Handle AI transcription API key encryption and storage
        if hasattr(self, "api_key_entry"):
            api_key = self.api_key_entry.strip()
            provider = self.local_vars["ai_api_provider_var"]

            if api_key:
                encrypted_key = self._encrypt_api_key(api_key)
                self.config[f"ai_api_key_{provider}_encrypted"] = encrypted_key
            else:
                # Remove key if empty
                if f"ai_api_key_{provider}_encrypted" in self.config:
                    del self.config[f"ai_api_key_{provider}_encrypted"]

        self.download_directory = self.current_dialog_download_dir[0]
        self.config["download_directory"] = self.download_directory

        # Trigger updates in parent GUI
        self.apply_theme_and_color()  # Applies appearance dependent styles
        logger.set_level(self.logger_processing_level_var)  # Update global logger
        logger.update_config(
            {
                "suppress_console_output": self.suppress_console_output_var,
                "suppress_gui_log_output": self.suppress_gui_log_output_var,
            }
        )
        self.update_log_colors_gui()  # Use public method
        self.update_all_status_info()

        # Apply device-specific settings if connected and changed
        if self.dock.is_connected() and self._fetched_device_settings_for_dialog:
            changed_device_settings = {}
            conceptual_device_setting_keys = {
                "autoRecord": "device_setting_auto_record_var",
                "autoPlay": "device_setting_auto_play_var",
                "bluetoothTone": "device_setting_bluetooth_tone_var",
                "notificationSound": "device_setting_notification_sound_var",
            }
            for (
                conceptual_key,
                local_var_name,
            ) in conceptual_device_setting_keys.items():
                current_val = self.local_vars[local_var_name]
                fetched_val = self._fetched_device_settings_for_dialog.get(conceptual_key)
                if (
                    current_val != fetched_val and fetched_val is not None
                ):  # Only if fetched_val was successfully loaded
                    changed_device_settings[conceptual_key] = current_val
            if changed_device_settings:
                self.apply_device_settings_from_dialog(changed_device_settings)  # Call parent's method

        save_config(self.config)  # Save the updated main config
        logger.info("SettingsDialog", "apply_settings", "Settings applied and saved.")

        if update_dialog_baseline:  # If "Apply" was clicked, update the baseline for this dialog
            self.initial_config_snapshot = self.config.copy()  # Re-snapshot
            self.initial_download_directory = self.download_directory
            self.current_dialog_download_dir[0] = self.download_directory
            # Re-fetch device settings for baseline if needed,
            # or use current local_vars as new baseline
            if self.dock.is_connected():
                self._fetched_device_settings_for_dialog["autoRecord"] = self.local_vars[
                    "device_setting_auto_record_var"
                ]
                self._fetched_device_settings_for_dialog["autoPlay"] = self.local_vars["device_setting_auto_play_var"]
                self._fetched_device_settings_for_dialog["bluetoothTone"] = self.local_vars[
                    "device_setting_bluetooth_tone_var"
                ]
                self._fetched_device_settings_for_dialog["notificationSound"] = self.local_vars[
                    "device_setting_notification_sound_var"
                ]

    provider_models = {
        "gemini": [
            "gemini-2.5-flash",
            "gemini-2.5-pro",
            "gemini-2.5-lite",
            "gemini-2.0-flash",
            "gemini-1.5-flash",
            "gemini-1.5-pro",
            "gemini-pro",
        ],
        "openai": [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo",
            "whisper-1",
        ],
        "anthropic": [
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
        ],
        "openrouter": [
            "anthropic/claude-3.5-sonnet",
            "openai/gpt-4o",
            "google/gemini-pro-1.5",
            "meta-llama/llama-3.1-405b",
            "mistralai/mistral-large-2407",
            "qwen/qwen-2.5-72b",
            "deepseek/deepseek-coder",
            "perplexity/llama-3.1-sonar-large",
        ],
        "amazon": [
            "anthropic.claude-3-5-sonnet-20241022-v2:0",
            "anthropic.claude-3-haiku-20240307-v1:0",
            "amazon.titan-text-premier-v1:0",
            "ai21.jamba-1-5-large-v1:0",
            "cohere.command-r-plus-v1:0",
        ],
        "qwen": [
            "qwen-plus",
            "qwen-turbo",
            "qwen-max",
            "qwen2.5-72b-instruct",
            "qwen2.5-32b-instruct",
            "qwen2.5-14b-instruct",
            "qwen2.5-7b-instruct",
        ],
        "deepseek": [
            "deepseek-chat",
            "deepseek-coder",
            "deepseek-reasoner",
            "deepseek-v2.5",
            "deepseek-v2",
        ],
        "ollama": [
            "llama3.2:latest",
            "llama3.1:latest",
            "llama3:latest",
            "mistral:latest",
            "codellama:latest",
            "phi3:latest",
            "gemma2:latest",
            "qwen2.5:latest",
            "nomic-embed-text:latest",
        ],
        "lmstudio": [
            "custom-model",
            "llama-3.2-3b-instruct",
            "llama-3.1-8b-instruct",
            "mistral-7b-instruct",
            "codellama-7b-instruct",
            "phi-3-mini",
            "gemma-2-9b-it",
            "qwen2.5-7b-instruct",
        ],
    }

    def _generate_encryption_key(self):
        """Generate or retrieve encryption key for API key storage."""
        if not ENCRYPTION_AVAILABLE:
            return None

        # Try to load existing key from config directory
        config_dir = os.path.dirname(self.config.get("config_file_path", ""))
        key_file = os.path.join(config_dir, ".hidock_key.dat")

        try:
            if os.path.exists(key_file):
                with open(key_file, "rb") as f:
                    return f.read()
            else:
                # Generate new key
                key = Fernet.generate_key()
                with open(key_file, "wb") as f:
                    f.write(key)
                return key
        except Exception as e:
            logger.error(
                "SettingsDialog",
                "_generate_encryption_key",
                f"Error with encryption key: {e}",
            )
            return None

    def _encrypt_api_key(self, api_key):
        """Encrypt API key for secure storage."""
        if not ENCRYPTION_AVAILABLE or not api_key:
            return api_key  # Return plaintext if encryption not available

        try:
            key = self._generate_encryption_key()
            if key:
                f = Fernet(key)
                encrypted = f.encrypt(api_key.encode())
                return base64.b64encode(encrypted).decode()
            return api_key
        except Exception as e:
            logger.error("SettingsDialog", "_encrypt_api_key", f"Error encrypting API key: {e}")
            return api_key

    def _decrypt_api_key(self, encrypted_key):
        """Decrypt API key from storage."""
        if not ENCRYPTION_AVAILABLE or not encrypted_key:
            return encrypted_key  # Return as-is if encryption not available

        try:
            key = self._generate_encryption_key()
            if key:
                f = Fernet(key)
                encrypted_bytes = base64.b64decode(encrypted_key.encode())
                decrypted = f.decrypt(encrypted_bytes)
                return decrypted.decode()
            return encrypted_key
        except Exception as e:
            logger.error("SettingsDialog", "_decrypt_api_key", f"Error decrypting API key: {e}")
            return ""

    def _validate_api_key(self):
        """Validate the entered API key by making a test API call."""
        if not hasattr(self, "api_key_entry") or not hasattr(self, "api_key_status_label"):
            return

        api_key = self.api_key_entry.strip()
        if not api_key:
            self.api_key_status_label.configure(text="Status: Please enter an API key", text_color="red")
            return

        provider = self.local_vars["ai_api_provider_var"]
        self.api_key_status_label.configure(text="Status: Validating...", text_color="blue")
        self.validate_key_button.configure(state="disabled")

        # Run validation in background thread
        threading.Thread(target=self._validate_api_key_thread, args=(api_key, provider), daemon=True).start()

    def _validate_api_key_thread(self, api_key, provider):
        """Background thread for API key validation."""
        try:
            # Use ai_service for validation to maintain consistency with multi-provider architecture
            from ai_service import AIServiceManager

            ai_manager = AIServiceManager()
            success = ai_manager.validate_provider(provider, api_key)

            # Update UI on main thread
            self.after(0, self._validation_complete, success)

        except Exception as e:
            logger.error(
                "SettingsDialog",
                "_validate_api_key_thread",
                f"API validation error: {e}",
            )
            self.after(0, self._validation_complete, False)

    def _validation_complete(self, success):
        """Called when API key validation completes."""
        if hasattr(self, "api_key_status_label") and hasattr(self, "validate_key_button"):
            if success:
                logger.info(
                    "SettingsDialog",
                    "_validation_complete",
                    "API key validation successful.",
                )
            else:
                logger.error(
                    "SettingsDialog",
                    "_validation_complete",
                    "API key validation failed.",
                )

    def _on_device_scan_complete(self, devices):
        """Handle completion of device scan."""
        try:
            hidock_count = sum(1 for d in devices if d.is_hidock)
            logger.info(
                "SettingsDialog",
                "_on_device_scan_complete",
                f"Scan complete: {len(devices)} devices, {hidock_count} HiDock devices",
            )

            # If there's a HiDock device and no device is currently selected, auto-select it
            if hidock_count > 0 and not any(d.status == "connected" for d in devices):
                hidock_device = next(d for d in devices if d.is_hidock)
                self.device_selector._select_device(hidock_device)

        except Exception as e:
            logger.error(
                "SettingsDialog",
                "_on_device_scan_complete",
                f"Error handling scan completion: {e}",
            )

    def _initial_enhanced_scan_thread(self):
        """Initial device scan thread for enhanced selector."""
        try:
            # Small delay to let the UI settle
            import time

            time.sleep(0.5)

            # Trigger device scan on main thread
            self.after(0, lambda: self.device_selector.refresh_devices())

        except Exception as e:
            logger.error(
                "SettingsDialog",
                "_initial_enhanced_scan_thread",
                f"Error in initial scan: {e}",
            )

    def _load_device_settings_for_dialog_thread(self):
        """
        Loads device-specific settings in a separate thread.

        Updates the corresponding CTk Variables and enables the checkboxes upon completion.
        """
        try:
            # Use asyncio.run to call the async method
            import asyncio

            settings = asyncio.run(self.dock.get_device_settings())

            if settings:
                self._fetched_device_settings_for_dialog = settings.copy()

                self.local_vars["device_setting_auto_record_var"] = settings.get("autoRecord", False)

                self.local_vars["device_setting_auto_play_var"] = settings.get("autoPlay", False)

                self.local_vars["device_setting_bluetooth_tone_var"] = settings.get("bluetoothTone", False)

                self.local_vars["device_setting_notification_sound_var"] = settings.get("notificationSound", False)

            else:
                logger.warning(
                    "SettingsDialog",
                    "_load_device_settings",
                    "Failed to load device settings.",
                )
        except (usb.core.USBError, ConnectionError) as e_usb:
            logger.error(
                "SettingsDialog",
                "_load_device_settings",
                f"USB/Connection Error: {e_usb}",
            )
            logger.error("SettingsDialog", "_load_device_settings", f"Failed to load device settings: {e_usb}")
        except (
            AttributeError,
            KeyError,
            TypeError,
            ValueError,
        ) as e_runtime:  # More specific runtime errors
            logger.error(
                "SettingsDialog",
                "_load_device_settings",
                f"Runtime error loading device settings: {type(e_runtime).__name__} - {e_runtime}",
            )
