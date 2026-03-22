"""
Backup Management UI Component for APGI Framework

Provides a user-friendly interface for creating, managing, and restoring backups
of experiment data, configurations, and results.
"""

import datetime
import json
import shutil
import threading
import tkinter as tk
import zipfile
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Optional, Callable, List, Dict, Any, Union


class BackupManager:
    """Manages backup operations for APGI Framework data."""

    def __init__(self, base_path: Optional[Path] = None):
        self.base_path = base_path or Path.cwd()
        self.backup_dir = self.base_path / "backups"
        self.backup_dir.mkdir(exist_ok=True)

        # Default backup items
        self.backup_items = {
            "experiment_data": {
                "path": "data",
                "description": "Experimental data files",
                "enabled": True,
                "size_mb": 0,
            },
            "configurations": {
                "path": "apgi_framework/config",
                "description": "Configuration files",
                "enabled": True,
                "size_mb": 0,
            },
            "results": {
                "path": "session_data",
                "description": "Session and result data",
                "enabled": True,
                "size_mb": 0,
            },
            "logs": {
                "path": "logs",
                "description": "Log files",
                "enabled": False,
                "size_mb": 0,
            },
            "custom_scripts": {
                "path": "examples",
                "description": "Custom experiment scripts",
                "enabled": True,
                "size_mb": 0,
            },
        }

        self._update_sizes()

    def scan_backup_items(self):
        """Scan backup items and update their sizes."""
        self._update_sizes()

    def create_backup_archive(self, backup_name: str) -> Path:
        """Create a backup archive with all enabled items."""
        enabled_items = [
            name for name, info in self.backup_items.items() if info["enabled"]
        ]

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{backup_name}_{timestamp}.zip"
        backup_path = self.backup_dir / backup_filename

        success = self.create_backup(backup_name, enabled_items)
        if success:
            return backup_path
        else:
            raise RuntimeError(f"Failed to create backup: {backup_name}")

    def _update_sizes(self):
        """Update size information for backup items."""
        for item_name, item_info in self.backup_items.items():
            path = self.base_path / item_info["path"]
            if path.exists():
                size = self._get_directory_size(path)
                item_info["size_mb"] = round(size / (1024 * 1024), 2)
            else:
                item_info["size_mb"] = 0

    def _get_directory_size(self, path: Path) -> int:
        """Get total size of directory in bytes."""
        total_size = 0
        try:
            if path.is_file():
                return path.stat().st_size

            for item in path.rglob("*"):
                if item.is_file():
                    total_size += item.stat().st_size
        except (OSError, PermissionError):
            pass
        return total_size

    def create_backup(
        self,
        backup_name: str,
        items: List[str],
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> bool:
        """Create a backup with selected items."""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{backup_name}_{timestamp}.zip"
            backup_path = self.backup_dir / backup_filename

            # Create backup metadata
            metadata = {
                "name": backup_name,
                "timestamp": timestamp,
                "items": items,
                "created_by": "APGI Framework Backup Manager",
                "version": "1.0",
            }

            total_items = len(items)
            processed_items = 0

            with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                # Add metadata
                zipf.writestr("backup_metadata.json", json.dumps(metadata, indent=2))

                for item_name in items:
                    if item_name not in self.backup_items:
                        continue

                    item_info = self.backup_items[item_name]
                    source_path = self.base_path / str(item_info["path"])

                    if not source_path.exists():
                        continue

                    if progress_callback:
                        progress_callback(
                            int((processed_items / total_items) * 100),
                            f"Backing up {item_info['description']}...",
                        )

                    # Add files to zip
                    if source_path.is_file():
                        zipf.write(source_path, str(item_info["path"]))
                    else:
                        for file_path in source_path.rglob("*"):
                            if file_path.is_file():
                                arcname = file_path.relative_to(self.base_path)
                                zipf.write(file_path, arcname)

                    processed_items += 1

            if progress_callback:
                progress_callback(100, "Backup completed successfully!")

            return True

        except Exception as e:
            if progress_callback:
                progress_callback(0, f"Backup failed: {str(e)}")
            return False

    def get_backups(self) -> List[Dict[str, Any]]:
        """Get list of available backups."""
        backups = []

        for backup_file in self.backup_dir.glob("*.zip"):
            try:
                with zipfile.ZipFile(backup_file, "r") as zipf:
                    if "backup_metadata.json" in zipf.namelist():
                        metadata_content = zipf.read("backup_metadata.json")
                        metadata = json.loads(metadata_content)

                        backup_info = {
                            "filename": backup_file.name,
                            "path": backup_file,
                            "size_mb": round(
                                backup_file.stat().st_size / (1024 * 1024), 2
                            ),
                            **metadata,
                        }
                        backups.append(backup_info)
            except Exception:
                # Skip corrupted backup files
                continue

        # Sort by timestamp (newest first)
        backups.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return backups

    def list_backups(self) -> List[Dict[str, Any]]:
        """Get list of available backups (alias for get_backups)."""
        return self.get_backups()

    def restore_backup(
        self,
        backup_path: Union[Path, str],
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> bool:
        """Restore from a backup file."""
        # Convert string to Path if needed
        if isinstance(backup_path, str):
            backup_path = self.backup_dir / backup_path
        elif isinstance(backup_path, Path):
            # If it's a Path but not absolute, assume it's relative to backup_dir
            if not backup_path.is_absolute():
                backup_path = self.backup_dir / backup_path
        else:
            raise TypeError("backup_path must be a Path or string")

        try:
            with zipfile.ZipFile(backup_path, "r") as zipf:
                # Read metadata
                if "backup_metadata.json" not in zipf.namelist():
                    raise ValueError("Invalid backup file: missing metadata")

                # Get list of files to extract (excluding metadata)
                files_to_extract = [
                    f for f in zipf.namelist() if f != "backup_metadata.json"
                ]
                total_files = len(files_to_extract)

                for i, filename in enumerate(files_to_extract):
                    if progress_callback:
                        progress_callback(
                            int((i / total_files) * 100), f"Restoring {filename}..."
                        )

                    # Extract file
                    zipf.extract(filename, self.base_path)

                if progress_callback:
                    progress_callback(100, "Restore completed successfully!")

                return True

        except Exception as e:
            if progress_callback:
                progress_callback(0, f"Restore failed: {str(e)}")
            return False

    def delete_backup(self, backup_path: Path) -> bool:
        """Delete a backup file."""
        try:
            backup_path.unlink()
            return True
        except Exception:
            return False


class BackupManagerUI:
    """UI component for backup management."""

    def __init__(self, parent, backup_manager: Optional[BackupManager] = None):
        self.parent = parent
        self.backup_manager = backup_manager or BackupManager()

        # Create main frame
        self.frame = ttk.LabelFrame(parent, text="Backup Management", padding=10)

        # Variables
        self.backup_name_var = tk.StringVar(value="APGI_Backup")
        self.progress_var = tk.IntVar()
        self.status_var = tk.StringVar(value="Ready")

        # Item selection variables
        self.item_vars = {}
        for item_name in self.backup_manager.backup_items:
            var = tk.BooleanVar(
                value=bool(self.backup_manager.backup_items[item_name]["enabled"])
            )
            self.item_vars[item_name] = var

        self._create_widgets()
        self._refresh_backup_list()

    def _create_widgets(self):
        """Create the UI widgets."""
        # Create backup section
        create_frame = ttk.LabelFrame(self.frame, text="Create Backup", padding=10)
        create_frame.pack(fill=tk.X, pady=(0, 10))

        # Backup name
        name_frame = ttk.Frame(create_frame)
        name_frame.pack(fill=tk.X, pady=5)

        ttk.Label(name_frame, text="Backup Name:").pack(side=tk.LEFT)
        ttk.Entry(name_frame, textvariable=self.backup_name_var, width=30).pack(
            side=tk.LEFT, padx=(10, 0)
        )

        # Items to backup
        items_frame = ttk.LabelFrame(create_frame, text="Items to Backup", padding=5)
        items_frame.pack(fill=tk.X, pady=5)

        for item_name, item_info in self.backup_manager.backup_items.items():
            item_frame = ttk.Frame(items_frame)
            item_frame.pack(fill=tk.X, pady=2)

            cb = ttk.Checkbutton(
                item_frame,
                text=f"{item_info['description']} ({item_info['size_mb']} MB)",
                variable=self.item_vars[item_name],
            )
            cb.pack(side=tk.LEFT)

        # Create backup button
        ttk.Button(
            create_frame, text="Create Backup", command=self._create_backup
        ).pack(pady=10)

        # Progress bar
        progress_frame = ttk.Frame(create_frame)
        progress_frame.pack(fill=tk.X, pady=5)

        self.progress_bar = ttk.Progressbar(
            progress_frame, variable=self.progress_var, maximum=100
        )
        self.progress_bar.pack(fill=tk.X)

        self.status_label = ttk.Label(progress_frame, textvariable=self.status_var)
        self.status_label.pack(pady=2)

        # Existing backups section
        backups_frame = ttk.LabelFrame(self.frame, text="Existing Backups", padding=10)
        backups_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # Backup list
        list_frame = ttk.Frame(backups_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # Treeview for backup list
        columns = ("Name", "Date", "Size", "Items")
        self.backup_tree = ttk.Treeview(
            list_frame, columns=columns, show="headings", height=8
        )

        for col in columns:
            self.backup_tree.heading(col, text=col)
            self.backup_tree.column(col, width=100)

        # Scrollbar
        scrollbar = ttk.Scrollbar(
            list_frame, orient=tk.VERTICAL, command=self.backup_tree.yview
        )
        self.backup_tree.configure(yscrollcommand=scrollbar.set)

        self.backup_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Backup management buttons
        button_frame = ttk.Frame(backups_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(
            button_frame, text="Refresh", command=self._refresh_backup_list
        ).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(
            button_frame, text="Restore Selected", command=self._restore_backup
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame, text="Delete Selected", command=self._delete_backup
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame, text="Export Backup", command=self._export_backup
        ).pack(side=tk.LEFT, padx=5)

    def _create_backup(self):
        """Create a new backup."""
        backup_name = self.backup_name_var.get().strip()
        if not backup_name:
            messagebox.showerror("Error", "Please enter a backup name")
            return

        # Get selected items
        selected_items = [
            item_name for item_name, var in self.item_vars.items() if var.get()
        ]

        if not selected_items:
            messagebox.showerror("Error", "Please select at least one item to backup")
            return

        def progress_callback(percent, message):
            self.progress_var.set(percent)
            self.status_var.set(message)
            self.parent.update_idletasks()

        def backup_thread():
            success = self.backup_manager.create_backup(
                backup_name, selected_items, progress_callback
            )

            if success:
                self.parent.after(
                    0,
                    lambda: [
                        messagebox.showinfo("Success", "Backup created successfully!"),
                        self._refresh_backup_list(),
                    ],
                )
            else:
                self.parent.after(
                    0, lambda: messagebox.showerror("Error", "Failed to create backup")
                )

        threading.Thread(target=backup_thread, daemon=True).start()

    def _refresh_backup_list(self):
        """Refresh the backup list."""
        # Clear existing items
        for item in self.backup_tree.get_children():
            self.backup_tree.delete(item)

        # Add backups
        backups = self.backup_manager.get_backups()
        for backup in backups:
            # Format timestamp
            try:
                timestamp = datetime.datetime.strptime(
                    backup["timestamp"], "%Y%m%d_%H%M%S"
                )
                date_str = timestamp.strftime("%Y-%m-%d %H:%M")
            except Exception:
                date_str = backup["timestamp"]

            # Format items
            items_str = ", ".join(backup.get("items", []))
            if len(items_str) > 30:
                items_str = items_str[:27] + "..."

            self.backup_tree.insert(
                "",
                tk.END,
                values=(backup["name"], date_str, f"{backup['size_mb']} MB", items_str),
                tags=(backup["filename"],),
            )

    def _restore_backup(self):
        """Restore selected backup."""
        selection = self.backup_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a backup to restore")
            return

        # Get backup filename from tags
        item = selection[0]
        filename = self.backup_tree.item(item)["tags"][0]
        backup_path = self.backup_manager.backup_dir / filename

        # Confirm restore
        if not messagebox.askyesno(
            "Confirm Restore",
            f"This will restore data from backup '{filename}'.\n"
            "Existing files may be overwritten. Continue?",
        ):
            return

        def progress_callback(percent, message):
            self.progress_var.set(percent)
            self.status_var.set(message)
            self.parent.update_idletasks()

        def restore_thread():
            success = self.backup_manager.restore_backup(backup_path, progress_callback)

            if success:
                self.parent.after(
                    0,
                    lambda: messagebox.showinfo(
                        "Success", "Backup restored successfully!"
                    ),
                )
            else:
                self.parent.after(
                    0, lambda: messagebox.showerror("Error", "Failed to restore backup")
                )

        threading.Thread(target=restore_thread, daemon=True).start()

    def _delete_backup(self):
        """Delete selected backup."""
        selection = self.backup_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a backup to delete")
            return

        # Get backup filename from tags
        item = selection[0]
        filename = self.backup_tree.item(item)["tags"][0]
        backup_path = self.backup_manager.backup_dir / filename

        # Confirm deletion
        if not messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete backup '{filename}'?\n"
            "This action cannot be undone.",
        ):
            return

        if self.backup_manager.delete_backup(backup_path):
            messagebox.showinfo("Success", "Backup deleted successfully!")
            self._refresh_backup_list()
        else:
            messagebox.showerror("Error", "Failed to delete backup")

    def _export_backup(self):
        """Export selected backup to a different location."""
        selection = self.backup_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a backup to export")
            return

        # Get backup filename from tags
        item = selection[0]
        filename = self.backup_tree.item(item)["tags"][0]
        backup_path = self.backup_manager.backup_dir / filename

        # Choose export location
        export_path = filedialog.asksaveasfilename(
            title="Export Backup As",
            defaultextension=".zip",
            filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")],
            initialvalue=filename,
        )

        if export_path:
            try:
                shutil.copy2(backup_path, export_path)
                messagebox.showinfo("Success", f"Backup exported to {export_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export backup: {str(e)}")

    def get_widget(self):
        """Get the main widget frame."""
        return self.frame

    def pack(self, **kwargs):
        """Pack the widget."""
        self.frame.pack(**kwargs)

    def grid(self, **kwargs):
        """Grid the widget."""
        self.frame.grid(**kwargs)


# Convenience function
def create_backup_manager_ui(parent, backup_manager=None) -> BackupManagerUI:
    """Create a backup manager UI component."""
    return BackupManagerUI(parent, backup_manager)
