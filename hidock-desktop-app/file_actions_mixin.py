# gui_actions_file.py
"""
File Actions Mixin for the HiDock Explorer Tool GUI.

This module provides the `FileActionsMixin` class, which contains methods
for handling file operations such as downloading, deleting, and transcribing.
"""
import json
import os
import threading
import traceback

from config_and_logger import logger
from file_operations_manager import FileOperationStatus, FileOperationType
from transcription_module import process_audio_file_for_insights


class FileActionsMixin:
    """A mixin for handling file-related actions."""

    def _get_local_filepath(self, device_filename):  # Identical to original
        """Generates a safe local file path for the given device filename.
        Args:
            device_filename (str): The filename from the device.
        Returns:
            str: A safe local file path.
        """
        safe_filename = device_filename.replace(":", "-").replace(" ", "_").replace("\\", "_").replace("/", "_")
        return os.path.join(self.download_directory, safe_filename)

    def download_selected_files_gui(self, filenames_to_download):
        """Handles the download of selected files in the GUI by setting up a queue."""
        if not self.download_directory or not os.path.isdir(self.download_directory):
            logger.error("CLI", "Error", "Invalid download directory.")
            return
        if self.is_long_operation_active:
            logger.error("CLI", "Error", "Another operation in progress.")
            return

        # Immediately update status to "Queued" for selected files
        for filename in filenames_to_download:
            # Check if file is already being downloaded
            if not self.file_operations_manager.is_file_operation_active(filename, FileOperationType.DOWNLOAD):
                self._update_file_status_in_treeview(filename, "Queued", ("queued",))

        self.file_operations_manager.queue_batch_download(filenames_to_download, self._update_operation_progress)

        # No need to refresh file list - downloads work with existing metadata
        # and status updates are handled by the progress callback

    def delete_selected_files_gui(self, filenames_to_delete):
        """Handles the deletion of selected files in the GUI."""
        # Immediately update status to "Queued" for selected files to be deleted
        for filename in filenames_to_delete:
            # Check if file is already being deleted
            if not self.file_operations_manager.is_file_operation_active(filename, FileOperationType.DELETE):
                self._update_file_status_in_treeview(filename, "Delete Queued", ("queued",))

        self.file_operations_manager.queue_batch_delete(filenames_to_delete, self._update_operation_progress)

    def _update_operation_progress(self, operation):
        """
        Callback to update GUI with operation progress. Called from a worker thread.
        Schedules the actual UI update on the main thread to prevent freezes.
        """
        # This is called from a worker thread. Schedule the actual GUI update
        # on the main thread to prevent UI freezes and race conditions.
        self.after(0, self._perform_gui_update_for_operation, operation)

    def _perform_gui_update_for_operation(self, operation):
        if operation.status == FileOperationStatus.IN_PROGRESS:
            status_text = (
                f"{operation.operation_type.value.capitalize()} " f"{operation.filename}: {operation.progress:.0f}%"
            )
            self.update_status_bar(progress_text=status_text)
        elif operation.status == FileOperationStatus.COMPLETED:
            status_text = f"{operation.operation_type.value.capitalize()} {operation.filename} complete."
            self.update_status_bar(progress_text=status_text)

            #
            # This is where we update the file status in the treeview
            if operation.operation_type.value == "download":
                pass
                # For downloads, show "Downloaded" status instead of "Completed"
            elif operation.operation_type.value == "delete":
                pass
                # For deletions, remove the file from the treeview and refresh the file list
                # Refresh the file list to ensure consistency with device state
            else:
                pass
                # Refresh the file list to ensure consistency with device state
        elif operation.status == FileOperationStatus.FAILED:
            status_text = f"Failed to {operation.operation_type.value} {operation.filename}: {operation.error_message}"
            self.update_status_bar(progress_text=status_text)
            self._update_file_status_in_treeview(operation.filename, "Failed", ("failed",))
        elif operation.status == FileOperationStatus.CANCELLED:
            status_text = f"{operation.operation_type.value.capitalize()} {operation.filename} cancelled."
            self.update_status_bar(progress_text=status_text)
            self._update_file_status_in_treeview(operation.filename, "Cancelled", ("cancelled",))

    def _transcribe_selected_audio_gemini(self, file_iid):
        file_detail = next((f for f in self.displayed_files_details if f["name"] == file_iid), None)
        if not file_detail:
            logger.error("CLI", "Transcription Error", "File details not found.")
            return

        local_filepath = self._get_local_filepath(file_detail["name"])
        if not os.path.exists(local_filepath):
            logger.warning(
                "CLI",
                "Transcription",
                "File not downloaded. Please download it first.",
            )
            return

        # Get API key securely (e.g., from config or environment variable)
        gemini_api_key = os.environ.get("GEMINI_API_KEY")  # Or load from self.config
        if not gemini_api_key:
            logger.error(
                "CLI",
                "API Key Missing",
                "Gemini API Key not found. Please set GEMINI_API_KEY environment variable.",
            )
            return

        self._set_long_operation_active_state(True, "Transcription")
        self.update_status_bar(progress_text=f"Transcribing {file_detail['name']} with Gemini...")

        threading.Thread(
            target=self._transcription_worker,
            args=(local_filepath, gemini_api_key, file_detail["name"]),
            daemon=True,
        ).start()

    def _transcription_worker(self, file_path, api_key, original_filename):
        try:
            results = process_audio_file_for_insights(file_path, api_key)
            self.after(0, self._on_transcription_complete, results, original_filename)
        except Exception as e:  # pylint: disable=broad-except
            # Catching broad exception is acceptable here as this is a worker thread.
            # The exception is logged with a traceback and reported to the user via the UI,
            # preventing the thread from crashing silently.
            logger.error(
                "CLI",
                "_transcription_worker",
                f"Error during transcription: {e}\n{traceback.format_exc()}",
            )
            self.after(0, self._on_transcription_complete, {"error": str(e)}, original_filename)

    def _on_transcription_complete(self, results, original_filename):
        self._set_long_operation_active_state(False, "Transcription")
        if "error" in results:
            logger.error(
                "CLI",
                "Transcription Error",
                f"Failed to transcribe {original_filename}: {results['error']}",
            )
            self.update_status_bar(progress_text=f"Transcription failed for {original_filename}.")
        else:
            transcription_text = results.get("transcription", "No transcription found.")
            insights = results.get("insights", {})

            # Transcription Tab
            transcription_text

            # Insights Tab
            json.dumps(insights, indent=2)

            self.update_status_bar(progress_text=f"Transcription complete for {original_filename}.")

    def cancel_all_downloads_gui(self):
        """Cancels all active download operations."""
        active_operations = self.file_operations_manager.get_all_active_operations()
        download_operations = [
            op
            for op in active_operations
            if op.operation_type == FileOperationType.DOWNLOAD
            and op.status in [FileOperationStatus.PENDING, FileOperationStatus.IN_PROGRESS]
        ]

        if not download_operations:
            logger.info("CLI", "No Downloads", "No active downloads to cancel.")
            return

        cancelled_count = 0
        for operation in download_operations:
            if self.file_operations_manager.cancel_operation(operation.operation_id):
                cancelled_count += 1
            self.update_status_bar(progress_text=f"Cancelled {cancelled_count} download(s).")

    def cancel_selected_downloads_gui(self, selected_filenames):
        """Cancels download operations for selected files."""
        # Find active download operations for selected files
        active_operations = self.file_operations_manager.get_all_active_operations()
        download_operations_to_cancel = [
            op
            for op in active_operations
            if (
                op.operation_type == FileOperationType.DOWNLOAD
                and op.filename in selected_filenames
                and op.status in [FileOperationStatus.PENDING, FileOperationStatus.IN_PROGRESS]
            )
        ]

        if not download_operations_to_cancel:
            logger.info(
                "CLI",
                "cancel_selected_downloads_gui",
                "No active downloads found for the selected files.",
            )
            return

        cancelled_count = 0
        for operation in download_operations_to_cancel:
            if self.file_operations_manager.cancel_operation(operation.operation_id):
                cancelled_count += 1
                # Update the file status in the treeview
                self._update_file_status_in_treeview(operation.filename, "Cancelled", ("cancelled",))

            self.update_status_bar(progress_text=f"Cancelled {cancelled_count} download(s) for selected files.")
