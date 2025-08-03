# gui_treeview.py
"""
TreeView Mixin for the HiDock Explorer Tool GUI.
"""
import time
from datetime import datetime

from config_and_logger import logger


class TreeViewMixin:
    """A mixin for handling the file list Treeview."""

    def _create_file_tree_frame(self):
        """Creates the file treeview and its associated scrollbar."""

        # columns = ("num", "name", "datetime", "size", "duration", "version", "status")
        # self.file_tree.tag_configure("downloaded", foreground="blue")
        # self.file_tree.tag_configure("recording", foreground="red", font=("Arial", 10, "bold"))
        # self.file_tree.tag_configure("size_mismatch", foreground="orange")
        # self.file_tree.tag_configure("downloaded_ok", foreground="green")
        # self.file_tree.tag_configure("downloading", foreground="dark orange")
        # self.file_tree.tag_configure("queued", foreground="gray50")
        # self.file_tree.tag_configure("cancelled", foreground="firebrick3")
        # self.file_tree.tag_configure("playing", foreground="purple")

        if self.treeview_columns_display_order_str:
            loaded_column_order = self.treeview_columns_display_order_str.split(",")
            valid_loaded_order = [c for c in loaded_column_order if c in columns]
            if len(valid_loaded_order) == len(columns) and set(valid_loaded_order) == set(columns):
                try:
                    self.file_tree["displaycolumns"] = valid_loaded_order
                except tkinter.TclError as e:
                    logger.warning(
                        "GUI",
                        "create_widgets",
                        f"Failed to apply saved column order '{valid_loaded_order}' (TclError): {e}. Using default.",
                    )
                    self.file_tree["displaycolumns"] = columns
            else:
                self.file_tree["displaycolumns"] = columns
        else:
            self.file_tree["displaycolumns"] = columns
        for col, text in self.original_tree_headings.items():
            is_numeric = col in ["size", "duration"]
            self.file_tree.heading(
                col,
                text=text,
                command=lambda c=col, n=is_numeric: self.sort_treeview_column(c, n),
            )

    def show_loading_state(self):
        """Show loading state - but preserve existing files if they're already displayed."""
        # Only clear if there are no real files displayed (just show loading for empty state)
        existing_children = self.file_tree.get_children()
        has_real_files = any(not child.startswith("loading_") for child in existing_children)

        if not has_real_files:
            # No real files shown yet, display loading indicators
            self.file_tree.delete(*existing_children)

            loading_messages = [
                "🔄 Loading files from device...",
                "📡 Fetching file information...",
                "⏳ Please wait...",
            ]

            for i, message in enumerate(loading_messages):
                self.file_tree.insert(
                    "",
                    "end",
                    iid=f"loading_{i}",
                    values=("", message, "", "", "", "Loading..."),
                    tags=["loading"],
                )

            # Configure loading tag with distinctive styling
            self.file_tree.tag_configure("loading", foreground="blue", font=("Arial", 10, "italic"))
        else:
            # Files are already displayed - just update status bar, don't clear tree
            pass

    def _populate_treeview_from_data(self, files_data):
        """
        Populates the Treeview with file data, preserving selection and scroll position.

        Args:
            files_data (list): A list of dictionaries, where each dictionary
                represents a file's details.
        """
        self.displayed_files_details = files_data
        for i, file_info in enumerate(files_data):
            tags = []
            status_text = file_info.get("gui_status", "On Device")
            if file_info.get("is_recording"):
                tags.append("recording")
                status_text = "Recording"
            elif status_text == "Downloaded":
                tags.append("downloaded_ok")
            elif status_text == "Mismatch":
                tags.append("size_mismatch")
            elif status_text == "Cancelled":
                tags.append("cancelled")
            elif "Error" in status_text:
                tags.append("size_mismatch")
            if self.is_audio_playing and self.current_playing_filename_for_replay == file_info["name"]:
                tags.append("playing")
                status_text = "Playing"
            elif (
                self.is_long_operation_active
                and self.active_operation_name == "Playback Preparation"
                and self.current_playing_filename_for_replay == file_info["name"]
            ):
                status_text = "Preparing Playback"
            file_info["gui_status"] = status_text

            # Format size in MB
            size_bytes = file_info.get("length", 0)
            size_mb_str = (
                f"{size_bytes / (1024*1024):.2f}" if isinstance(size_bytes, (int, float)) and size_bytes > 0 else "0.00"
            )

            # Format duration in HH:MM:SS
            duration_sec = file_info.get("duration", 0)
            if isinstance(duration_sec, (int, float)):
                duration_str = time.strftime("%H:%M:%S", time.gmtime(duration_sec))
            else:
                duration_str = str(duration_sec)

            # Combine Date and Time
            datetime_str = f"{file_info.get('createDate', '')} {file_info.get('createTime', '')}".strip()
            if not datetime_str:
                datetime_str = "---"

            # Format version - display the raw value from the device
            version_str = str(file_info.get("version", "N/A"))

            values = (
                file_info.get("original_index", i + 1),
                file_info["name"],
                datetime_str,
                size_mb_str,
                duration_str,
                version_str,
                status_text,
            )
        #     self.file_tree.insert("", "end", iid=file_info["name"], values=values, tags=tags)
        # self.update_all_status_info()

    def _update_file_status_in_treeview(self, file_iid, status_text, tags_to_add):
        """
        Updates the status and tags for a specific file in the Treeview.
        Maintains sort order if the treeview is currently sorted.

        Args:
            file_iid (str): The IID (item ID) of the file in the Treeview.
            status_text (str): The new status text to display.
            tags_to_add (tuple): A tuple of tags to add to the item.
        """
        # DEPRECATED: This method is no longer used, but kept for reference.

    def _remove_file_from_treeview(self, file_iid):
        """
        Removes a file from the Treeview and the displayed_files_details list.

        Args:
            file_iid (str): The IID (item ID) of the file to remove from the Treeview.
        """
        if not (hasattr(self, "file_tree") and self.file_tree.winfo_exists() and self.file_tree.exists(file_iid)):
            return

        # Remove from treeview
        self.file_tree.delete(file_iid)

        # Remove from displayed_files_details list
        self.displayed_files_details = [f for f in self.displayed_files_details if f["name"] != file_iid]

        # Update status info to reflect the change
        self.update_all_status_info()

    def _sort_files_data(self, files_data, col, reverse):
        """
        Sorts the file data based on a specified column.

        Args:
            files_data (list): The list of file dictionaries to sort.
            col (str): The column ID to sort by.
            reverse (bool): True to sort in descending order, False for ascending.

        Returns:
            list: The sorted list of file dictionaries.
        """

        def sort_key(item):
            if col == "size":
                # Sort by raw byte length, not formatted string
                return item.get("length", 0)
            elif col == "duration":
                # Sort by raw seconds, handling non-numeric "Recording..."
                duration_val = item.get("duration")
                if isinstance(duration_val, (int, float)):
                    return float(duration_val)
                elif isinstance(duration_val, str) and duration_val == "Recording...":
                    return -1  # Recording files should appear first
                else:
                    return 0  # Default for invalid values
            elif col == "num":
                return item.get("original_index", 0)
            elif col == "datetime":
                # For sorting, we need a real datetime object.
                # We create it on the fly if it doesn't exist and cache it.
                if "time" not in item:
                    try:
                        datetime_str = f"{item.get('createDate', '')} {item.get('createTime', '')}".strip()
                        if datetime_str and datetime_str != "---":
                            item["time"] = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
                        else:
                            item["time"] = datetime.min
                    except (ValueError, TypeError):
                        item["time"] = datetime.min
                return item["time"]
            else:
                # Fallback for other columns like 'name' or 'status'
                val = item.get(col)
                if val is None:
                    return ""
                # Ensure string comparison for text columns
                return str(val).lower() if isinstance(val, str) else str(val)

        return sorted(files_data, key=sort_key, reverse=reverse)

    def sort_treeview_column(self, col, is_numeric_sort):
        """
        Handles the sorting of the Treeview when a column header is clicked.
        Works properly even during active download operations.

        Toggles the sort direction and re-populates the Treeview with sorted data.

        Args:
            col (str): The column ID that was clicked.
            is_numeric_sort (bool): True if the column should be sorted numerically.
        """
        # Update sort parameters
        if self.treeview_sort_column == col:
            self.treeview_sort_reverse = not self.treeview_sort_reverse
        else:
            self.treeview_sort_column = col
            self.treeview_sort_reverse = False

        # Sort the data
        sorted_files = self._sort_files_data(self.displayed_files_details, col, self.treeview_sort_reverse)

        # Repopulate the treeview with sorted data
        self._populate_treeview_from_data(sorted_files)

        # Save sort state for persistence
        self.saved_treeview_sort_column = col
        self.saved_treeview_sort_reverse = self.treeview_sort_reverse

    def _apply_saved_sort_state_to_tree_and_ui(self, files_data):
        """
        Applies the saved sort state to the file data and updates the UI.

        Args:
            files_data (list): The list of file dictionaries to sort.

        Returns:
            list: The sorted list of file dictionaries.
        """
        if self.saved_treeview_sort_column:
            sorted_files = self._sort_files_data(
                files_data,
                self.saved_treeview_sort_column,
                self.saved_treeview_sort_reverse,
            )
            self.after(
                0,
                self.saved_treeview_sort_column,
                self.saved_treeview_sort_reverse,
            )
            return sorted_files
        return files_data
