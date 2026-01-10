"""Main area component for the APGI Framework GUI."""

import customtkinter as ctk
import tkinter as tk
from pathlib import Path
from typing import Dict, Any, Optional
import json
import logging

from ..config import DefaultParameters, ParameterConfig


class MainArea(ctk.CTkFrame):
    """Main area component containing the primary workspace."""

    def __init__(self, parent, app):
        """Initialize the main area.

        Args:
            parent: Parent widget
            app: Main application instance
        """
        super().__init__(parent)
        self.app = app
        self.current_data: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)

        # Load default parameters
        self.defaults = DefaultParameters()
        self.ui_config = self.defaults.UI_CONFIG

        self.setup_ui()

    def setup_ui(self):
        """Set up the main area UI components."""
        # Configure frame
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header with tabs
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(
            row=0,
            column=0,
            padx=self.ui_config["spacing"]["padding_x"],
            pady=self.ui_config["spacing"]["padding_x"],
            sticky="ew",
        )
        self.tabview.grid_columnconfigure(0, weight=1)

        # Create tabs
        self.create_tabs()

        # Main content area with scrollable frame
        self.scrollable_frame = ctk.CTkScrollableFrame(self)
        self.scrollable_frame.grid(
            row=1,
            column=0,
            padx=self.ui_config["spacing"]["padding_x"],
            pady=(0, self.ui_config["spacing"]["padding_x"]),
            sticky="nsew",
        )
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        # Create content for default tab
        self.create_configuration_content()

    def create_tabs(self):
        """Create the tab view tabs."""
        # Configuration tab
        self.config_tab = self.tabview.add("Configuration")

        # Analysis tab
        self.analysis_tab = self.tabview.add("Analysis")

        # Visualization tab
        self.viz_tab = self.tabview.add("Visualization")

        # Results tab
        self.results_tab = self.tabview.add("Results")

        # Configure tab change event
        self.tabview._segmented_button.configure(command=self.on_tab_changed)

        # Note: Tab content will be created on demand

    def create_configuration_content(self):
        """Create the configuration tab content."""
        self.logger.debug("Creating configuration content")

        # Clear existing content
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # APGI Parameters Section
        params_frame = ctk.CTkFrame(self.scrollable_frame)
        params_frame.grid(
            row=0,
            column=0,
            padx=self.ui_config["spacing"]["padding_x"],
            pady=self.ui_config["spacing"]["padding_x"],
            sticky="ew",
        )
        params_frame.grid_columnconfigure(1, weight=1)

        params_label = ctk.CTkLabel(
            params_frame,
            text="APGI Parameters",
            font=ctk.CTkFont(size=self.ui_config["font_sizes"]["title"], weight="bold"),
        )
        params_label.grid(
            row=0,
            column=0,
            columnspan=2,
            padx=self.ui_config["spacing"]["padding_x"],
            pady=self.ui_config["spacing"]["padding_section_y"],
        )

        # Parameter inputs using configuration
        self.param_entries = {}

        for i, param_config in enumerate(self.defaults.APGI_PARAMETERS, start=1):
            # Label
            param_label = ctk.CTkLabel(params_frame, text=param_config.label)
            param_label.grid(
                row=i,
                column=0,
                padx=self.ui_config["spacing"]["padding_x"],
                pady=self.ui_config["spacing"]["padding_y"],
                sticky="w",
            )

            # Entry with validation
            entry = ctk.CTkEntry(
                params_frame, placeholder_text=param_config.default_value
            )
            entry.grid(
                row=i,
                column=1,
                padx=self.ui_config["spacing"]["padding_x"],
                pady=self.ui_config["spacing"]["padding_y"],
                sticky="ew",
            )

            # Bind validation
            entry.bind(
                "<FocusOut>",
                lambda e, key=param_config.key: self._validate_parameter(key),
            )

            self.param_entries[param_config.key] = entry

        # Neural Signatures Section
        neural_frame = ctk.CTkFrame(self.scrollable_frame)
        neural_frame.grid(
            row=1,
            column=0,
            padx=self.ui_config["spacing"]["padding_x"],
            pady=self.ui_config["spacing"]["padding_x"],
            sticky="ew",
        )
        neural_frame.grid_columnconfigure(1, weight=1)

        neural_label = ctk.CTkLabel(
            neural_frame,
            text="Neural Signatures",
            font=ctk.CTkFont(size=self.ui_config["font_sizes"]["title"], weight="bold"),
        )
        neural_label.grid(
            row=0,
            column=0,
            columnspan=2,
            padx=self.ui_config["spacing"]["padding_x"],
            pady=self.ui_config["spacing"]["padding_section_y"],
        )

        # Neural signature checkboxes using configuration
        self.neural_vars = {}

        for i, (label, key, description) in enumerate(
            self.defaults.NEURAL_SIGNATURES, start=1
        ):
            var = tk.BooleanVar(value=True)
            checkbox = ctk.CTkCheckBox(neural_frame, text=label, variable=var)
            checkbox.grid(
                row=i,
                column=0,
                columnspan=2,
                padx=self.ui_config["spacing"]["padding_x"],
                pady=self.ui_config["spacing"]["padding_y"],
                sticky="w",
            )
            self.neural_vars[key] = var

        # Experimental Settings Section
        exp_frame = ctk.CTkFrame(self.scrollable_frame)
        exp_frame.grid(
            row=2,
            column=0,
            padx=self.ui_config["spacing"]["padding_x"],
            pady=self.ui_config["spacing"]["padding_x"],
            sticky="ew",
        )
        exp_frame.grid_columnconfigure(1, weight=1)

        exp_label = ctk.CTkLabel(
            exp_frame,
            text="Experimental Settings",
            font=ctk.CTkFont(size=self.ui_config["font_sizes"]["title"], weight="bold"),
        )
        exp_label.grid(
            row=0,
            column=0,
            columnspan=2,
            padx=self.ui_config["spacing"]["padding_x"],
            pady=self.ui_config["spacing"]["padding_section_y"],
        )

        # Experimental settings using configuration
        self.exp_entries = {}

        for i, setting_config in enumerate(
            self.defaults.EXPERIMENTAL_SETTINGS, start=1
        ):
            # Label
            setting_label = ctk.CTkLabel(exp_frame, text=setting_config.label)
            setting_label.grid(
                row=i,
                column=0,
                padx=self.ui_config["spacing"]["padding_x"],
                pady=self.ui_config["spacing"]["padding_y"],
                sticky="w",
            )

            # Entry with validation
            entry = ctk.CTkEntry(
                exp_frame, placeholder_text=setting_config.default_value
            )
            entry.grid(
                row=i,
                column=1,
                padx=self.ui_config["spacing"]["padding_x"],
                pady=self.ui_config["spacing"]["padding_y"],
                sticky="ew",
            )

            # Bind validation
            entry.bind(
                "<FocusOut>",
                lambda e, key=setting_config.key: self._validate_parameter(key),
            )

            self.exp_entries[setting_config.key] = entry

        # Action buttons
        button_frame = ctk.CTkFrame(self.scrollable_frame)
        button_frame.grid(
            row=3,
            column=0,
            padx=self.ui_config["spacing"]["padding_x"],
            pady=self.ui_config["spacing"]["padding_large_y"],
            sticky="ew",
        )
        button_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.apply_btn = ctk.CTkButton(
            button_frame,
            text="Apply Changes",
            command=self.apply_changes,
            height=self.ui_config["button_height"],
        )
        self.apply_btn.grid(
            row=0,
            column=0,
            padx=self.ui_config["spacing"]["padding_x"],
            pady=self.ui_config["spacing"]["padding_y"],
            sticky="ew",
        )

        self.reset_btn = ctk.CTkButton(
            button_frame,
            text="Reset to Defaults",
            command=self.reset_to_defaults,
            height=self.ui_config["button_height"],
        )
        self.reset_btn.grid(
            row=0,
            column=1,
            padx=self.ui_config["spacing"]["padding_x"],
            pady=self.ui_config["spacing"]["padding_y"],
            sticky="ew",
        )

        self.run_btn = ctk.CTkButton(
            button_frame,
            text="Run Analysis",
            command=self.run_analysis,
            height=self.ui_config["button_height"],
        )
        self.run_btn.grid(
            row=0,
            column=2,
            padx=self.ui_config["spacing"]["padding_x"],
            pady=self.ui_config["spacing"]["padding_y"],
            sticky="ew",
        )

        self.logger.debug("Configuration content created successfully")

    def on_tab_changed(self, selected_tab: str = None):
        """Handle tab change events.

        Args:
            selected_tab: The selected tab name (from button command)
        """
        try:
            # Get current tab from tabview if not provided
            if selected_tab is None:
                current_tab = self.tabview.get()
            else:
                current_tab = selected_tab

            # Clear existing content
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()

            # Create content based on selected tab
            if current_tab == "Analysis":
                self.create_analysis_content()
            elif current_tab == "Visualization":
                self.create_visualization_content()
            elif current_tab == "Results":
                self.create_results_content()
            else:  # Configuration tab or default
                self.create_configuration_content()

            # Update status
            self.app.update_status(f"Switched to {current_tab} tab")

        except Exception as e:
            # Log error and fallback to configuration
            print(f"Tab change error: {e}")
            self.create_configuration_content()
            self.app.update_status("Tab change failed, showing configuration")

    def create_analysis_content(self):
        """Create the analysis tab content."""
        # Clear existing content
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Analysis options
        analysis_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="Analysis Options",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        analysis_label.grid(row=0, column=0, padx=10, pady=10)

        # Placeholder for analysis content
        placeholder = ctk.CTkLabel(
            self.scrollable_frame,
            text="Analysis functionality will be implemented here.\n\nThis will include:\n- Falsification testing\n- Parameter estimation\n- Model validation\n- Statistical analysis",
            justify="left",
        )
        placeholder.grid(row=1, column=0, padx=10, pady=20)

    def create_visualization_content(self):
        """Create the visualization tab content."""
        # Clear existing content
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Visualization options
        viz_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="Visualization Options",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        viz_label.grid(row=0, column=0, padx=10, pady=10)

        # Placeholder for visualization content
        placeholder = ctk.CTkLabel(
            self.scrollable_frame,
            text="Visualization functionality will be implemented here.\n\nThis will include:\n- Time series plots\n- Spectral analysis\n- Topographic maps\n- Statistical plots",
            justify="left",
        )
        placeholder.grid(row=1, column=0, padx=10, pady=20)

    def create_results_content(self):
        """Create the results tab content."""
        # Clear existing content
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Results display
        results_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="Results",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        results_label.grid(row=0, column=0, padx=10, pady=10)

        # Placeholder for results content
        placeholder = ctk.CTkLabel(
            self.scrollable_frame,
            text="Results will be displayed here.\n\nThis will include:\n- Test results\n- Parameter estimates\n- Model fit metrics\n- Export options",
            justify="left",
        )
        placeholder.grid(row=1, column=0, padx=10, pady=20)

    def get_data(self) -> Dict[str, Any]:
        """Get the current configuration data.

        Returns:
            Dictionary containing current configuration
        """
        data = {
            "apgi_parameters": {},
            "neural_signatures": {},
            "experimental_settings": {},
        }

        # Get APGI parameters
        for key, entry in self.param_entries.items():
            value = entry.get()
            if value:
                try:
                    data["apgi_parameters"][key] = float(value)
                except ValueError:
                    data["apgi_parameters"][key] = value

        # Get neural signatures
        for key, var in self.neural_vars.items():
            data["neural_signatures"][key] = var.get()

        # Get experimental settings
        for key, entry in self.exp_entries.items():
            value = entry.get()
            if value:
                try:
                    data["experimental_settings"][key] = float(value)
                except ValueError:
                    data["experimental_settings"][key] = value

        return data

    def load_data(self, data: Dict[str, Any]) -> None:
        """Load configuration data.

        Args:
            data: Configuration data to load
        """
        self.current_data = data

        # Load APGI parameters
        apgi_params = data.get("apgi_parameters", {})
        for key, entry in self.param_entries.items():
            value = apgi_params.get(key, "")
            entry.delete(0, tk.END)
            entry.insert(0, str(value))

        # Load neural signatures
        neural_sigs = data.get("neural_signatures", {})
        for key, var in self.neural_vars.items():
            value = neural_sigs.get(key, True)
            var.set(value)

        # Load experimental settings
        exp_settings = data.get("experimental_settings", {})
        for key, entry in self.exp_entries.items():
            value = exp_settings.get(key, "")
            entry.delete(0, tk.END)
            entry.insert(0, str(value))

    def clear(self) -> None:
        """Clear all input fields."""
        # Clear APGI parameters
        for entry in self.param_entries.values():
            entry.delete(0, tk.END)

        # Reset neural signatures
        for var in self.neural_vars.values():
            var.set(True)

        # Clear experimental settings
        for entry in self.exp_entries.values():
            entry.delete(0, tk.END)

        self.current_data = {}

    def apply_changes(self) -> None:
        """Apply the current configuration changes."""
        self.current_data = self.get_data()
        self.app.update_status("Configuration changes applied")

    def reset_to_defaults(self) -> None:
        """Reset all fields to default values."""
        self.logger.info("Resetting to default values")

        # Clear APGI parameters and set defaults
        for key, entry in self.param_entries.items():
            entry.delete(0, tk.END)
            default_value = self.defaults.get_parameter_defaults().get(key, "")
            entry.insert(0, str(default_value))

        # Reset neural signatures
        for var in self.neural_vars.values():
            var.set(True)

        # Clear experimental settings and set defaults
        for key, entry in self.exp_entries.items():
            entry.delete(0, tk.END)
            default_value = self.defaults.get_parameter_defaults().get(key, "")
            entry.insert(0, str(default_value))

        self.current_data = {}
        self.app.update_status("Reset to default values")
        self.logger.debug("Reset to defaults completed")

    def _validate_parameter(self, key: str) -> None:
        """Validate a parameter value.

        Args:
            key: Parameter key to validate
        """
        try:
            # Get the entry widget for this key
            if key in self.param_entries:
                entry = self.param_entries[key]
            elif key in self.exp_entries:
                entry = self.exp_entries[key]
            else:
                return

            value = entry.get()
            if not value:
                return  # Empty values are allowed

            # Validate using the defaults configuration
            is_valid, error_message = self.defaults.validate_parameter(key, value)

            if not is_valid:
                # Show validation error
                self.app.update_status(
                    f"Validation error for {key}: {error_message}", "error"
                )
                self.logger.warning(
                    f"Parameter validation failed: {key} = {value} - {error_message}"
                )
            else:
                # Clear any previous error
                self.logger.debug(f"Parameter validation passed: {key} = {value}")

        except Exception as e:
            self.logger.error(f"Error validating parameter {key}: {e}")
            self.app.update_status(f"Error validating {key}", "error")

    def run_analysis(self) -> None:
        """Run the analysis with current configuration."""
        if not self.current_data:
            self.apply_changes()

        self.app.update_status("Starting analysis...")
        # Placeholder for analysis execution
        self.app.update_status("Analysis completed (placeholder)")
