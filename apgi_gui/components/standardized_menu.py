"""
Standardized menu component for APGI Framework GUI applications.

Provides consistent menu structure across all GUI implementations with
standardized actions, shortcuts, and behavior.
"""

import tkinter as tk
from typing import Dict, List, Callable, Optional, Any
from dataclasses import dataclass
import logging

try:
    import customtkinter as ctk

    CUSTOMTKINTER_AVAILABLE = True
except ImportError:
    CUSTOMTKINTER_AVAILABLE = False
    ctk = None

logger = logging.getLogger(__name__)


@dataclass
class MenuItem:
    """Represents a menu item with its properties."""

    label: str
    command: Optional[Callable] = None
    accelerator: Optional[str] = None
    underline: Optional[int] = None
    state: str = "normal"  # normal, disabled, active
    menu_type: str = "command"  # command, checkbutton, radiobutton, separator, cascade
    variable: Optional[tk.Variable] = None
    submenu: Optional["MenuStructure"] = None


@dataclass
class MenuStructure:
    """Defines the structure of a menu with its items."""

    label: str
    items: List[MenuItem]
    tearoff: int = 0


class StandardizedMenuManager:
    """
    Manages standardized menus across different GUI applications.

    Provides consistent menu structure, actions, and shortcuts for all
    APGI Framework GUI implementations.
    """

    def __init__(self, parent: tk.Widget, gui_type: str = "default"):
        """
        Initialize the standardized menu manager.

        Args:
            parent: Parent widget (typically the root window)
            gui_type: Type of GUI (default, simple, falsification, etc.)
        """
        self.parent = parent
        self.gui_type = gui_type
        self.menus: Dict[str, Any] = {}
        self.callbacks: Dict[str, Callable] = {}

        # Initialize menu structure based on GUI type
        self.menu_structure = self._get_menu_structure()

        # Create menus
        self._create_menus()

    def _get_menu_structure(self) -> List[MenuStructure]:
        """
        Get the menu structure based on GUI type.

        Returns:
            List of menu structures for this GUI type
        """
        base_structure = [
            MenuStructure(
                label="File",
                items=[
                    MenuItem(
                        label="New Experiment",
                        accelerator="Ctrl+N",
                        command=self._callback_new_experiment,
                    ),
                    MenuItem(
                        label="Open", accelerator="Ctrl+O", command=self._callback_open
                    ),
                    MenuItem(
                        label="Save", accelerator="Ctrl+S", command=self._callback_save
                    ),
                    MenuItem(
                        label="Save As...",
                        accelerator="Ctrl+Shift+S",
                        command=self._callback_save_as,
                    ),
                    MenuItem(label="", menu_type="separator"),
                    MenuItem(label="Import Data", command=self._callback_import_data),
                    MenuItem(
                        label="Export Results", command=self._callback_export_results
                    ),
                    MenuItem(label="", menu_type="separator"),
                    MenuItem(
                        label="Preferences",
                        accelerator="Ctrl+,",
                        command=self._callback_preferences,
                    ),
                    MenuItem(label="", menu_type="separator"),
                    MenuItem(
                        label="Exit", accelerator="Ctrl+Q", command=self._callback_exit
                    ),
                ],
            ),
            MenuStructure(
                label="Edit",
                items=[
                    MenuItem(
                        label="Undo", accelerator="Ctrl+Z", command=self._callback_undo
                    ),
                    MenuItem(
                        label="Redo", accelerator="Ctrl+Y", command=self._callback_redo
                    ),
                    MenuItem(label="", menu_type="separator"),
                    MenuItem(
                        label="Cut", accelerator="Ctrl+X", command=self._callback_cut
                    ),
                    MenuItem(
                        label="Copy", accelerator="Ctrl+C", command=self._callback_copy
                    ),
                    MenuItem(
                        label="Paste",
                        accelerator="Ctrl+V",
                        command=self._callback_paste,
                    ),
                    MenuItem(label="", menu_type="separator"),
                    MenuItem(
                        label="Select All",
                        accelerator="Ctrl+A",
                        command=self._callback_select_all,
                    ),
                    MenuItem(
                        label="Find", accelerator="Ctrl+F", command=self._callback_find
                    ),
                    MenuItem(
                        label="Replace",
                        accelerator="Ctrl+H",
                        command=self._callback_replace,
                    ),
                ],
            ),
            MenuStructure(
                label="View",
                items=[
                    MenuItem(
                        label="Zoom In",
                        accelerator="Ctrl++",
                        command=self._callback_zoom_in,
                    ),
                    MenuItem(
                        label="Zoom Out",
                        accelerator="Ctrl+-",
                        command=self._callback_zoom_out,
                    ),
                    MenuItem(
                        label="Reset Zoom",
                        accelerator="Ctrl+0",
                        command=self._callback_reset_zoom,
                    ),
                    MenuItem(label="", menu_type="separator"),
                    MenuItem(
                        label="Fullscreen",
                        accelerator="F11",
                        command=self._callback_fullscreen,
                    ),
                    MenuItem(
                        label="Show Toolbar",
                        menu_type="checkbutton",
                        variable=tk.BooleanVar(value=True),
                        command=self._callback_show_toolbar,
                    ),
                    MenuItem(
                        label="Show Status Bar",
                        menu_type="checkbutton",
                        variable=tk.BooleanVar(value=True),
                        command=self._callback_show_statusbar,
                    ),
                    MenuItem(label="", menu_type="separator"),
                    MenuItem(label="Theme", submenu=self._get_theme_submenu()),
                ],
            ),
            MenuStructure(
                label="Experiment",
                items=[
                    MenuItem(
                        label="Run Experiment",
                        accelerator="F5",
                        command=self._callback_run_experiment,
                    ),
                    MenuItem(
                        label="Stop Experiment",
                        accelerator="Shift+F5",
                        command=self._callback_stop_experiment,
                    ),
                    MenuItem(
                        label="Pause/Resume",
                        accelerator="Space",
                        command=self._callback_pause_resume,
                    ),
                    MenuItem(label="", menu_type="separator"),
                    MenuItem(
                        label="Configure Parameters",
                        accelerator="Ctrl+P",
                        command=self._callback_configure_parameters,
                    ),
                    MenuItem(
                        label="Validate Configuration",
                        command=self._callback_validate_config,
                    ),
                    MenuItem(label="", menu_type="separator"),
                    MenuItem(
                        label="Real-time Monitoring", command=self._callback_monitoring
                    ),
                    MenuItem(label="Data Analysis", command=self._callback_analysis),
                ],
            ),
            MenuStructure(
                label="Tools",
                items=[
                    MenuItem(label="Data Manager", command=self._callback_data_manager),
                    MenuItem(
                        label="Parameter Estimator",
                        command=self._callback_parameter_estimator,
                    ),
                    MenuItem(
                        label="Model Comparison",
                        command=self._callback_model_comparison,
                    ),
                    MenuItem(label="", menu_type="separator"),
                    MenuItem(
                        label="Batch Processing",
                        command=self._callback_batch_processing,
                    ),
                    MenuItem(
                        label="Performance Benchmark", command=self._callback_benchmark
                    ),
                    MenuItem(label="", menu_type="separator"),
                    MenuItem(
                        label="System Diagnostics", command=self._callback_diagnostics
                    ),
                ],
            ),
            MenuStructure(
                label="Window",
                items=[
                    MenuItem(
                        label="New Window",
                        accelerator="Ctrl+Shift+N",
                        command=self._callback_new_window,
                    ),
                    MenuItem(
                        label="Close Window",
                        accelerator="Ctrl+W",
                        command=self._callback_close_window,
                    ),
                    MenuItem(label="", menu_type="separator"),
                    MenuItem(label="Minimize", command=self._callback_minimize),
                    MenuItem(label="Maximize", command=self._callback_maximize),
                    MenuItem(label="Restore", command=self._callback_restore),
                ],
            ),
            MenuStructure(
                label="Help",
                items=[
                    MenuItem(
                        label="Documentation",
                        accelerator="F1",
                        command=self._callback_documentation,
                    ),
                    MenuItem(label="Tutorial", command=self._callback_tutorial),
                    MenuItem(label="", menu_type="separator"),
                    MenuItem(
                        label="Check for Updates", command=self._callback_check_updates
                    ),
                    MenuItem(
                        label="System Information", command=self._callback_system_info
                    ),
                    MenuItem(label="", menu_type="separator"),
                    MenuItem(label="About", command=self._callback_about),
                ],
            ),
        ]

        # Add GUI-specific menus
        if self.gui_type == "falsification":
            base_structure.insert(
                4,
                MenuStructure(
                    label="Testing",
                    items=[
                        MenuItem(
                            label="Run Falsification Test",
                            accelerator="Ctrl+T",
                            command=self._callback_run_test,
                        ),
                        MenuItem(
                            label="Batch Testing", command=self._callback_batch_testing
                        ),
                        MenuItem(label="", menu_type="separator"),
                        MenuItem(
                            label="Test Configuration",
                            command=self._callback_test_config,
                        ),
                        MenuItem(
                            label="Test Results", command=self._callback_test_results
                        ),
                    ],
                ),
            )
        elif self.gui_type == "simple":
            # Remove some advanced menus for simple GUI
            base_structure = [
                m for m in base_structure if m.label not in ["Tools", "Window"]
            ]

        return base_structure

    def _get_theme_submenu(self) -> "MenuStructure":
        """Get theme submenu structure."""
        return MenuStructure(
            label="Theme",
            items=[
                MenuItem(
                    label="Light",
                    menu_type="radiobutton",
                    variable=tk.StringVar(value="light"),
                    command=lambda: self._callback_set_theme("light"),
                ),
                MenuItem(
                    label="Dark",
                    menu_type="radiobutton",
                    variable=tk.StringVar(value="light"),
                    command=lambda: self._callback_set_theme("dark"),
                ),
                MenuItem(
                    label="System",
                    menu_type="radiobutton",
                    variable=tk.StringVar(value="light"),
                    command=lambda: self._callback_set_theme("system"),
                ),
            ],
        )

    def _create_menus(self):
        """Create the menu bar with all menus."""
        if CUSTOMTKINTER_AVAILABLE and hasattr(self.parent, "configure"):
            # For customtkinter, create a traditional menu bar
            menubar = tk.Menu(self.parent)
            self.parent.config(menu=menubar)

            for menu_struct in self.menu_structure:
                menu = tk.Menu(menubar, tearoff=menu_struct.tearoff)
                menubar.add_cascade(label=menu_struct.label, menu=menu)
                self.menus[menu_struct.label] = menu

                # Add menu items
                for item in menu_struct.items:
                    self._add_menu_item(menu, item)
        else:
            # For standard tkinter
            menubar = tk.Menu(self.parent)
            self.parent.config(menu=menubar)

            for menu_struct in self.menu_structure:
                menu = tk.Menu(menubar, tearoff=menu_struct.tearoff)
                menubar.add_cascade(label=menu_struct.label, menu=menu)
                self.menus[menu_struct.label] = menu

                # Add menu items
                for item in menu_struct.items:
                    self._add_menu_item(menu, item)

    def _add_menu_item(self, menu: tk.Menu, item: MenuItem):
        """Add a single menu item to the menu."""
        if item.menu_type == "separator":
            menu.add_separator()
        elif item.menu_type == "cascade" and item.submenu:
            submenu = tk.Menu(menu, tearoff=item.submenu.tearoff)
            menu.add_cascade(label=item.label, menu=submenu)
            for subitem in item.submenu.items:
                self._add_menu_item(submenu, subitem)
        elif item.menu_type == "checkbutton":
            menu.add_checkbutton(
                label=item.label,
                command=item.command,
                variable=item.variable,
                state=item.state,
            )
        elif item.menu_type == "radiobutton":
            menu.add_radiobutton(
                label=item.label,
                command=item.command,
                variable=item.variable,
                state=item.state,
            )
        else:  # command
            menu.add_command(
                label=item.label,
                command=item.command,
                accelerator=item.accelerator,
                underline=item.underline,
                state=item.state,
            )

    def register_callback(self, action_name: str, callback: Callable):
        """
        Register a callback for a menu action.

        Args:
            action_name: Name of the action (e.g., 'new_experiment')
            callback: Function to call when action is triggered
        """
        self.callbacks[action_name] = callback
        logger.debug(f"Registered callback for action: {action_name}")

    def get_menu(self, menu_name: str) -> Optional[tk.Menu]:
        """
        Get a specific menu by name.

        Args:
            menu_name: Name of the menu

        Returns:
            Menu widget or None if not found
        """
        return self.menus.get(menu_name)

    def enable_item(self, menu_name: str, item_label: str):
        """Enable a specific menu item."""
        menu = self.get_menu(menu_name)
        if menu:
            try:
                menu.entryconfig(item_label, state="normal")
            except tk.TclError:
                logger.warning(f"Could not enable menu item: {menu_name}.{item_label}")

    def disable_item(self, menu_name: str, item_label: str):
        """Disable a specific menu item."""
        menu = self.get_menu(menu_name)
        if menu:
            try:
                menu.entryconfig(item_label, state="disabled")
            except tk.TclError:
                logger.warning(f"Could not disable menu item: {menu_name}.{item_label}")

    # Default callback methods (can be overridden by registering callbacks)
    def _callback_new_experiment(self):
        self._execute_callback("new_experiment")

    def _callback_open(self):
        self._execute_callback("open")

    def _callback_save(self):
        self._execute_callback("save")

    def _callback_save_as(self):
        self._execute_callback("save_as")

    def _callback_import_data(self):
        self._execute_callback("import_data")

    def _callback_export_results(self):
        self._execute_callback("export_results")

    def _callback_preferences(self):
        self._execute_callback("preferences")

    def _callback_exit(self):
        self._execute_callback("exit")

    def _callback_undo(self):
        self._execute_callback("undo")

    def _callback_redo(self):
        self._execute_callback("redo")

    def _callback_cut(self):
        self._execute_callback("cut")

    def _callback_copy(self):
        self._execute_callback("copy")

    def _callback_paste(self):
        self._execute_callback("paste")

    def _callback_select_all(self):
        self._execute_callback("select_all")

    def _callback_find(self):
        self._execute_callback("find")

    def _callback_replace(self):
        self._execute_callback("replace")

    def _callback_zoom_in(self):
        self._execute_callback("zoom_in")

    def _callback_zoom_out(self):
        self._execute_callback("zoom_out")

    def _callback_reset_zoom(self):
        self._execute_callback("reset_zoom")

    def _callback_fullscreen(self):
        self._execute_callback("fullscreen")

    def _callback_show_toolbar(self):
        self._execute_callback("show_toolbar")

    def _callback_show_statusbar(self):
        self._execute_callback("show_statusbar")

    def _callback_set_theme(self, theme: str):
        self._execute_callback("set_theme", theme)

    def _callback_run_experiment(self):
        self._execute_callback("run_experiment")

    def _callback_stop_experiment(self):
        self._execute_callback("stop_experiment")

    def _callback_pause_resume(self):
        self._execute_callback("pause_resume")

    def _callback_configure_parameters(self):
        self._execute_callback("configure_parameters")

    def _callback_validate_config(self):
        self._execute_callback("validate_config")

    def _callback_monitoring(self):
        self._execute_callback("monitoring")

    def _callback_analysis(self):
        self._execute_callback("analysis")

    def _callback_data_manager(self):
        self._execute_callback("data_manager")

    def _callback_parameter_estimator(self):
        self._execute_callback("parameter_estimator")

    def _callback_model_comparison(self):
        self._execute_callback("model_comparison")

    def _callback_batch_processing(self):
        self._execute_callback("batch_processing")

    def _callback_benchmark(self):
        self._execute_callback("benchmark")

    def _callback_diagnostics(self):
        self._execute_callback("diagnostics")

    def _callback_new_window(self):
        self._execute_callback("new_window")

    def _callback_close_window(self):
        self._execute_callback("close_window")

    def _callback_minimize(self):
        self._execute_callback("minimize")

    def _callback_maximize(self):
        self._execute_callback("maximize")

    def _callback_restore(self):
        self._execute_callback("restore")

    def _callback_documentation(self):
        self._execute_callback("documentation")

    def _callback_tutorial(self):
        self._execute_callback("tutorial")

    def _callback_check_updates(self):
        self._execute_callback("check_updates")

    def _callback_system_info(self):
        self._execute_callback("system_info")

    def _callback_about(self):
        self._execute_callback("about")

    def _callback_run_test(self):
        self._execute_callback("run_test")

    def _callback_batch_testing(self):
        self._execute_callback("batch_testing")

    def _callback_test_config(self):
        self._execute_callback("test_config")

    def _callback_test_results(self):
        self._execute_callback("test_results")

    def _execute_callback(self, action_name: str, *args):
        """Execute a registered callback with optional arguments."""
        if action_name in self.callbacks:
            try:
                self.callbacks[action_name](*args)
            except Exception as e:
                logger.error(f"Error executing callback '{action_name}': {e}")
        else:
            logger.debug(f"No callback registered for action: {action_name}")
            # Show a default message for unimplemented actions
            self._show_unimplemented_message(action_name)

    def _show_unimplemented_message(self, action_name: str):
        """Show a message for unimplemented actions."""
        try:
            from tkinter import messagebox

            messagebox.showinfo(
                "Feature Not Implemented",
                f"The '{action_name.replace('_', ' ').title()}' feature is not yet implemented.",
            )
        except ImportError:
            print(f"Feature not implemented: {action_name}")


def create_standardized_menu(
    parent: tk.Widget, gui_type: str = "default"
) -> StandardizedMenuManager:
    """
    Convenience function to create a standardized menu.

    Args:
        parent: Parent widget
        gui_type: Type of GUI

    Returns:
        StandardizedMenuManager instance
    """
    return StandardizedMenuManager(parent, gui_type)
