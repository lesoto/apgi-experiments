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

    def _create_parameter_entry(
        self, parent, config, row, entries_dict, validation_callback=None
    ):
        """Create standardized parameter entry widget.

        Args:
            parent: Parent widget
            config: Configuration object with label, key, default_value
            row: Grid row position
            entries_dict: Dictionary to store the entry widget
            validation_callback: Optional validation callback function

        Returns:
            The created entry widget
        """
        # Label
        param_label = ctk.CTkLabel(parent, text=config.label)
        param_label.grid(
            row=row,
            column=0,
            padx=self.ui_config["spacing"]["padding_x"],
            pady=self.ui_config["spacing"]["padding_y"],
            sticky="w",
        )

        # Entry with validation
        entry = ctk.CTkEntry(parent, placeholder_text=config.default_value)
        entry.grid(
            row=row,
            column=1,
            padx=self.ui_config["spacing"]["padding_x"],
            pady=self.ui_config["spacing"]["padding_y"],
            sticky="ew",
        )

        # Bind validation if callback provided
        if validation_callback:
            entry.bind(
                "<FocusOut>",
                lambda e, key=config.key: validation_callback(key),
            )

        # Store entry reference
        entries_dict[config.key] = entry

        return entry

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
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        params_label.grid(
            row=0,
            column=0,
            columnspan=2,
            pady=5,
            sticky="ew",
        )

        self.param_entries = {}

        for i, param_config in enumerate(self.defaults.APGI_PARAMETERS, start=1):
            self._create_parameter_entry(
                params_frame,
                param_config,
                i,
                self.param_entries,
                self._validate_parameter,
            )

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
            self._create_parameter_entry(
                exp_frame, setting_config, i, self.exp_entries, self._validate_parameter
            )

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

        except (AttributeError, KeyError, IndexError) as e:
            # Log specific error and fallback to configuration
            self.logger.error(f"Tab change error: {e}")
            self.create_configuration_content()
            self.app.update_status("Tab change failed, showing configuration")

    def create_analysis_content(self):
        """Create the analysis tab content."""
        # Clear existing content
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Data Import Section
        import_frame = ctk.CTkFrame(self.scrollable_frame)
        import_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        import_frame.grid_columnconfigure(1, weight=1)

        import_label = ctk.CTkLabel(
            import_frame,
            text="Data Import",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        import_label.grid(row=0, column=0, columnspan=3, padx=10, pady=5, sticky="w")

        # File selection
        file_label = ctk.CTkLabel(import_frame, text="Data File:")
        file_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.file_path_var = tk.StringVar()
        file_entry = ctk.CTkEntry(import_frame, textvariable=self.file_path_var)
        file_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        browse_btn = ctk.CTkButton(
            import_frame, text="Browse", command=self.browse_data_file
        )
        browse_btn.grid(row=1, column=2, padx=10, pady=5)

        # Load button
        load_btn = ctk.CTkButton(
            import_frame, text="Load Data", command=self.load_analysis_data
        )
        load_btn.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        # Analysis Type Selection
        analysis_frame = ctk.CTkFrame(self.scrollable_frame)
        analysis_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        analysis_frame.grid_columnconfigure(1, weight=1)

        analysis_label = ctk.CTkLabel(
            analysis_frame,
            text="Analysis Type",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        analysis_label.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # Analysis type dropdown
        type_label = ctk.CTkLabel(analysis_frame, text="Select Analysis:")
        type_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.analysis_type_var = tk.StringVar(value="descriptive")
        analysis_types = [
            "descriptive",
            "comparative",
            "correlation",
            "regression",
            "time_series",
            "bayesian",
        ]
        analysis_menu = ctk.CTkOptionMenu(
            analysis_frame, variable=self.analysis_type_var, values=analysis_types
        )
        analysis_menu.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # Analysis Parameters
        params_frame = ctk.CTkFrame(self.scrollable_frame)
        params_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        params_frame.grid_columnconfigure(1, weight=1)

        params_label = ctk.CTkLabel(
            params_frame,
            text="Analysis Parameters",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        params_label.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # Confidence level
        conf_label = ctk.CTkLabel(params_frame, text="Confidence Level:")
        conf_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.confidence_var = tk.StringVar(value="0.95")
        conf_entry = ctk.CTkEntry(
            params_frame, textvariable=self.confidence_var, width=100
        )
        conf_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        # Generate plots checkbox
        self.generate_plots_var = tk.BooleanVar(value=True)
        plots_checkbox = ctk.CTkCheckBox(
            params_frame, text="Generate Plots", variable=self.generate_plots_var
        )
        plots_checkbox.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # Run Analysis Button
        run_frame = ctk.CTkFrame(self.scrollable_frame)
        run_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

        self.run_analysis_btn = ctk.CTkButton(
            run_frame,
            text="Run Analysis",
            command=self.run_analysis_job,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.run_analysis_btn.pack(pady=10, padx=10, fill="x")

        # Results Preview Area
        results_frame = ctk.CTkFrame(self.scrollable_frame)
        results_frame.grid(row=4, column=0, padx=10, pady=10, sticky="nsew")
        results_frame.grid_columnconfigure(0, weight=1)
        results_frame.grid_rowconfigure(0, weight=1)

        results_label = ctk.CTkLabel(
            results_frame,
            text="Results Preview",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        results_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        # Results text widget
        self.results_text = ctk.CTkTextbox(results_frame, height=200)
        self.results_text.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        # Export button
        export_btn = ctk.CTkButton(
            results_frame, text="Export Results", command=self.export_analysis_results
        )
        export_btn.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        # Configure scrollable frame
        self.scrollable_frame.grid_rowconfigure(4, weight=1)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        # Initialize analysis data
        self.current_analysis_data = None
        self.current_analysis_result = None

    def create_visualization_content(self):
        """Create the visualization tab content."""
        # Clear existing content
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Data Source Section
        data_frame = ctk.CTkFrame(self.scrollable_frame)
        data_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        data_frame.grid_columnconfigure(1, weight=1)

        data_label = ctk.CTkLabel(
            data_frame,
            text="Data Source",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        data_label.grid(row=0, column=0, columnspan=3, padx=10, pady=5, sticky="w")

        # Data source selection
        source_label = ctk.CTkLabel(data_frame, text="Source:")
        source_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.viz_data_source_var = tk.StringVar(value="file")
        source_menu = ctk.CTkOptionMenu(
            data_frame,
            variable=self.viz_data_source_var,
            values=["file", "analysis_results", "generated"],
        )
        source_menu.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        load_viz_btn = ctk.CTkButton(
            data_frame, text="Load Data", command=self.load_visualization_data
        )
        load_viz_btn.grid(row=1, column=2, padx=10, pady=5)

        # Plot Type Selection
        plot_frame = ctk.CTkFrame(self.scrollable_frame)
        plot_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        plot_frame.grid_columnconfigure(1, weight=1)

        plot_label = ctk.CTkLabel(
            plot_frame,
            text="Plot Type",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        plot_label.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # Plot type dropdown
        type_label = ctk.CTkLabel(plot_frame, text="Select Plot:")
        type_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.plot_type_var = tk.StringVar(value="line")
        plot_types = [
            "line",
            "scatter",
            "histogram",
            "box",
            "violin",
            "heatmap",
            "correlation",
            "distribution",
            "timeseries",
        ]
        plot_menu = ctk.CTkOptionMenu(
            plot_frame, variable=self.plot_type_var, values=plot_types
        )
        plot_menu.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # Visualization Parameters
        params_frame = ctk.CTkFrame(self.scrollable_frame)
        params_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        params_frame.grid_columnconfigure((1, 2), weight=1)

        params_label = ctk.CTkLabel(
            params_frame,
            text="Visualization Parameters",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        params_label.grid(row=0, column=0, columnspan=3, padx=10, pady=5, sticky="w")

        # X-axis
        x_label = ctk.CTkLabel(params_frame, text="X-axis:")
        x_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.viz_x_var = tk.StringVar()
        x_entry = ctk.CTkEntry(params_frame, textvariable=self.viz_x_var)
        x_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # Y-axis
        y_label = ctk.CTkLabel(params_frame, text="Y-axis:")
        y_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        self.viz_y_var = tk.StringVar()
        y_entry = ctk.CTkEntry(params_frame, textvariable=self.viz_y_var)
        y_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        # Color/Group
        color_label = ctk.CTkLabel(params_frame, text="Color/Group:")
        color_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")

        self.viz_color_var = tk.StringVar()
        color_entry = ctk.CTkEntry(params_frame, textvariable=self.viz_color_var)
        color_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        # Title
        title_label = ctk.CTkLabel(params_frame, text="Title:")
        title_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")

        self.viz_title_var = tk.StringVar()
        title_entry = ctk.CTkEntry(params_frame, textvariable=self.viz_title_var)
        title_entry.grid(row=4, column=1, padx=10, pady=5, sticky="ew")

        # Plot options
        self.viz_grid_var = tk.BooleanVar(value=True)
        grid_checkbox = ctk.CTkCheckBox(
            params_frame, text="Show Grid", variable=self.viz_grid_var
        )
        grid_checkbox.grid(row=5, column=0, padx=10, pady=5, sticky="w")

        self.viz_legend_var = tk.BooleanVar(value=True)
        legend_checkbox = ctk.CTkCheckBox(
            params_frame, text="Show Legend", variable=self.viz_legend_var
        )
        legend_checkbox.grid(row=5, column=1, padx=10, pady=5, sticky="w")

        # Generate Plot Button
        generate_frame = ctk.CTkFrame(self.scrollable_frame)
        generate_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

        self.generate_plot_btn = ctk.CTkButton(
            generate_frame,
            text="Generate Plot",
            command=self.generate_plot,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.generate_plot_btn.pack(pady=10, padx=10, fill="x")

        # Plot Display Area
        display_frame = ctk.CTkFrame(self.scrollable_frame)
        display_frame.grid(row=4, column=0, padx=10, pady=10, sticky="nsew")
        display_frame.grid_columnconfigure(0, weight=1)
        display_frame.grid_rowconfigure(1, weight=1)

        display_label = ctk.CTkLabel(
            display_frame,
            text="Plot Display",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        display_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        # Create matplotlib figure embedded in tkinter
        self.plot_canvas_frame = ctk.CTkFrame(display_frame)
        self.plot_canvas_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        # Export buttons
        export_frame = ctk.CTkFrame(display_frame)
        export_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        export_frame.grid_columnconfigure((0, 1, 2), weight=1)

        save_png_btn = ctk.CTkButton(
            export_frame, text="Save as PNG", command=lambda: self.save_plot("png")
        )
        save_png_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        save_pdf_btn = ctk.CTkButton(
            export_frame, text="Save as PDF", command=lambda: self.save_plot("pdf")
        )
        save_pdf_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        save_svg_btn = ctk.CTkButton(
            export_frame, text="Save as SVG", command=lambda: self.save_plot("svg")
        )
        save_svg_btn.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # Configure scrollable frame
        self.scrollable_frame.grid_rowconfigure(4, weight=1)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        # Initialize visualization data
        self.current_viz_data = None
        self.current_figure = None
        self.current_plot = None

    def create_results_content(self):
        """Create the results tab content."""
        # Clear existing content
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Results Browser Section
        browser_frame = ctk.CTkFrame(self.scrollable_frame)
        browser_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        browser_frame.grid_columnconfigure(1, weight=1)

        browser_label = ctk.CTkLabel(
            browser_frame,
            text="Results Browser",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        browser_label.grid(row=0, column=0, columnspan=3, padx=10, pady=5, sticky="w")

        # Filter controls
        filter_label = ctk.CTkLabel(browser_frame, text="Filter:")
        filter_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.results_filter_var = tk.StringVar()
        filter_entry = ctk.CTkEntry(browser_frame, textvariable=self.results_filter_var)
        filter_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        filter_btn = ctk.CTkButton(
            browser_frame, text="Apply Filter", command=self.filter_results
        )
        filter_btn.grid(row=1, column=2, padx=10, pady=5)

        # Sort controls
        sort_label = ctk.CTkLabel(browser_frame, text="Sort by:")
        sort_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        self.results_sort_var = tk.StringVar(value="date")
        sort_menu = ctk.CTkOptionMenu(
            browser_frame,
            variable=self.results_sort_var,
            values=["date", "name", "type", "outcome"],
        )
        sort_menu.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        # Results List
        list_frame = ctk.CTkFrame(self.scrollable_frame)
        list_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)

        list_label = ctk.CTkLabel(
            list_frame,
            text="Experiment Results",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        list_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        # Results treeview (using CTkScrollableFrame for now)
        self.results_list_frame = ctk.CTkScrollableFrame(list_frame, height=200)
        self.results_list_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        # Results Details Panel
        details_frame = ctk.CTkFrame(self.scrollable_frame)
        details_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        details_frame.grid_columnconfigure(0, weight=1)

        details_label = ctk.CTkLabel(
            details_frame,
            text="Result Details",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        details_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        # Details text widget
        self.results_details_text = ctk.CTkTextbox(details_frame, height=150)
        self.results_details_text.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        # Action Buttons
        action_frame = ctk.CTkFrame(self.scrollable_frame)
        action_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        action_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        compare_btn = ctk.CTkButton(
            action_frame, text="Compare Selected", command=self.compare_results
        )
        compare_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        export_btn = ctk.CTkButton(
            action_frame, text="Export Report", command=self.export_results_report
        )
        export_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        delete_btn = ctk.CTkButton(
            action_frame, text="Delete Selected", command=self.delete_results
        )
        delete_btn.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        refresh_btn = ctk.CTkButton(
            action_frame, text="Refresh List", command=self.refresh_results_list
        )
        refresh_btn.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        load_btn = ctk.CTkButton(
            action_frame, text="Load Result", command=self.load_selected_result
        )
        load_btn.grid(row=0, column=4, padx=5, pady=5, sticky="ew")

        # Configure scrollable frame
        self.scrollable_frame.grid_rowconfigure(1, weight=1)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        # Initialize results data
        self.available_results = []
        self.selected_results = []
        self.current_result_details = None

        # Load initial results
        self.refresh_results_list()

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

        except (ValueError, TypeError, AttributeError) as e:
            self.logger.error(f"Error validating parameter {key}: {e}")
            self.app.update_status(f"Error validating {key}", "error")

    def browse_data_file(self) -> None:
        """Browse for data file."""
        file_path = tk.filedialog.askopenfilename(
            title="Select Data File",
            filetypes=[
                ("CSV Files", "*.csv"),
                ("JSON Files", "*.json"),
                ("Pickle Files", "*.pkl"),
                ("All Files", "*.*"),
            ],
            initialdir=self.app.config.data_dir,
        )
        if file_path:
            self.file_path_var.set(file_path)

    def load_analysis_data(self) -> None:
        """Load data for analysis."""
        file_path = self.file_path_var.get()
        if not file_path:
            self.app.update_status("Please select a data file", "warning")
            return

        try:
            import pandas as pd
            import json
            import pickle

            file_path = Path(file_path)

            if file_path.suffix == ".csv":
                self.current_analysis_data = pd.read_csv(file_path)
            elif file_path.suffix == ".json":
                with open(file_path, "r") as f:
                    data = json.load(f)
                self.current_analysis_data = pd.DataFrame(data)
            elif file_path.suffix == ".pkl":
                with open(file_path, "rb") as f:
                    self.current_analysis_data = pickle.load(f)
                if not isinstance(self.current_analysis_data, pd.DataFrame):
                    self.current_analysis_data = pd.DataFrame(
                        self.current_analysis_data
                    )
            else:
                raise ValueError(f"Unsupported file format: {file_path.suffix}")

            self.app.update_status(f"Loaded data: {self.current_analysis_data.shape}")
            self.results_text.delete("1.0", "end")
            self.results_text.insert("1.0", f"Data loaded successfully!\n\n")
            self.results_text.insert(
                "end", f"Shape: {self.current_analysis_data.shape}\n"
            )
            self.results_text.insert(
                "end", f"Columns: {list(self.current_analysis_data.columns)}\n"
            )
            self.results_text.insert(
                "end", f"Data types:\n{self.current_analysis_data.dtypes}"
            )

        except Exception as e:
            self.app.update_status(f"Error loading data: {e}", "error")
            self.logger.error(f"Error loading analysis data: {e}")

    def run_analysis_job(self) -> None:
        """Run the analysis job."""
        if self.current_analysis_data is None:
            self.app.update_status("Please load data first", "warning")
            return

        try:
            self.app.update_status("Running analysis...")
            self.run_analysis_btn.configure(state="disabled")

            # Import analysis engine
            import sys
            from pathlib import Path

            project_root = Path(__file__).parent.parent.parent
            sys.path.insert(0, str(project_root))
            from apgi_framework.analysis.analysis_engine import AnalysisEngine

            # Initialize analysis engine
            engine = AnalysisEngine()

            # Get analysis parameters
            analysis_type = self.analysis_type_var.get()
            generate_plots = self.generate_plots_var.get()
            confidence = float(self.confidence_var.get())

            # Run analysis
            result = engine.analyze(
                data=self.current_analysis_data,
                analysis_type=analysis_type,
                parameters={"confidence": confidence},
                generate_plots=generate_plots,
            )

            self.current_analysis_result = result

            # Display results
            self.display_analysis_results(result)

            self.app.update_status(f"Analysis completed: {result.analysis_id}")

        except Exception as e:
            self.app.update_status(f"Analysis failed: {e}", "error")
            self.logger.error(f"Analysis job failed: {e}")
        finally:
            self.run_analysis_btn.configure(state="normal")

    def display_analysis_results(self, result) -> None:
        """Display analysis results in the text widget."""
        self.results_text.delete("1.0", "end")

        # Analysis summary
        self.results_text.insert("1.0", f"Analysis ID: {result.analysis_id}\n")
        self.results_text.insert("end", f"Type: {result.analysis_type}\n")
        self.results_text.insert("end", f"Timestamp: {result.timestamp}\n")
        self.results_text.insert("end", "=" * 50 + "\n\n")

        # Statistics
        if result.statistics:
            self.results_text.insert("end", "STATISTICS:\n")
            for key, value in result.statistics.items():
                if isinstance(value, dict):
                    self.results_text.insert("end", f"{key}:\n")
                    for sub_key, sub_value in value.items():
                        self.results_text.insert(
                            "end", f"  {sub_key}: {sub_value:.4f}\n"
                        )
                else:
                    self.results_text.insert("end", f"{key}: {value:.4f}\n")
            self.results_text.insert("end", "\n")

        # P-values
        if result.p_values:
            self.results_text.insert("end", "P-VALUES:\n")
            for key, value in result.p_values.items():
                self.results_text.insert("end", f"{key}: {value:.6f}\n")
            self.results_text.insert("end", "\n")

        # Effect sizes
        if result.effect_sizes:
            self.results_text.insert("end", "EFFECT SIZES:\n")
            for key, value in result.effect_sizes.items():
                self.results_text.insert("end", f"{key}: {value:.4f}\n")
            self.results_text.insert("end", "\n")

        # Confidence intervals
        if result.confidence_intervals:
            self.results_text.insert("end", "CONFIDENCE INTERVALS:\n")
            for key, value in result.confidence_intervals.items():
                if isinstance(value, (tuple, list)) and len(value) == 2:
                    self.results_text.insert(
                        "end", f"{key}: [{value[0]:.4f}, {value[1]:.4f}]\n"
                    )
            self.results_text.insert("end", "\n")

        # Plots generated
        if result.plots:
            self.results_text.insert("end", "PLOTS GENERATED:\n")
            for plot_id, plot_path in result.plots.items():
                self.results_text.insert("end", f"{plot_id}: {plot_path}\n")

    def export_analysis_results(self) -> None:
        """Export analysis results to file."""
        if self.current_analysis_result is None:
            self.app.update_status("No results to export", "warning")
            return

        try:
            file_path = tk.filedialog.asksaveasfilename(
                title="Export Analysis Results",
                defaultextension=".json",
                filetypes=[
                    ("JSON Files", "*.json"),
                    ("CSV Files", "*.csv"),
                    ("All Files", "*.*"),
                ],
                initialdir=self.app.config.data_dir,
            )

            if not file_path:
                return

            file_path = Path(file_path)

            if file_path.suffix == ".json":
                # Export as JSON
                import json
                from datetime import datetime

                export_data = {
                    "analysis_id": self.current_analysis_result.analysis_id,
                    "timestamp": self.current_analysis_result.timestamp.isoformat(),
                    "analysis_type": self.current_analysis_result.analysis_type,
                    "statistics": self.current_analysis_result.statistics,
                    "p_values": self.current_analysis_result.p_values,
                    "effect_sizes": self.current_analysis_result.effect_sizes,
                    "confidence_intervals": self.current_analysis_result.confidence_intervals,
                    "plots": self.current_analysis_result.plots,
                    "parameters": self.current_analysis_result.parameters,
                    "data_summary": self.current_analysis_result.data_summary,
                }

                # Convert numpy types
                def convert_numpy(obj):
                    import numpy as np

                    if isinstance(obj, np.integer):
                        return int(obj)
                    elif isinstance(obj, np.floating):
                        return float(obj)
                    elif isinstance(obj, np.ndarray):
                        return obj.tolist()
                    elif isinstance(obj, dict):
                        return {key: convert_numpy(value) for key, value in obj.items()}
                    elif isinstance(obj, (list, tuple)):
                        return [convert_numpy(item) for item in obj]
                    return obj

                export_data = convert_numpy(export_data)

                with open(file_path, "w") as f:
                    json.dump(export_data, f, indent=2)

            elif file_path.suffix == ".csv":
                # Export summary as CSV
                import pandas as pd

                summary_data = []
                for key, value in self.current_analysis_result.statistics.items():
                    summary_data.append(
                        {"metric": key, "value": str(value), "type": "statistic"}
                    )

                for key, value in self.current_analysis_result.p_values.items():
                    summary_data.append(
                        {"metric": key, "value": str(value), "type": "p_value"}
                    )

                for key, value in self.current_analysis_result.effect_sizes.items():
                    summary_data.append(
                        {"metric": key, "value": str(value), "type": "effect_size"}
                    )

                pd.DataFrame(summary_data).to_csv(file_path, index=False)

            self.app.update_status(f"Results exported to {file_path.name}")

        except Exception as e:
            self.app.update_status(f"Export failed: {e}", "error")
            self.logger.error(f"Error exporting results: {e}")

    def load_visualization_data(self) -> None:
        """Load data for visualization."""
        data_source = self.viz_data_source_var.get()

        try:
            if data_source == "file":
                file_path = tk.filedialog.askopenfilename(
                    title="Select Data File for Visualization",
                    filetypes=[
                        ("CSV Files", "*.csv"),
                        ("JSON Files", "*.json"),
                        ("Pickle Files", "*.pkl"),
                        ("All Files", "*.*"),
                    ],
                    initialdir=self.app.config.data_dir,
                )
                if not file_path:
                    return

                import pandas as pd
                import json
                import pickle

                file_path = Path(file_path)

                if file_path.suffix == ".csv":
                    self.current_viz_data = pd.read_csv(file_path)
                elif file_path.suffix == ".json":
                    with open(file_path, "r") as f:
                        data = json.load(f)
                    self.current_viz_data = pd.DataFrame(data)
                elif file_path.suffix == ".pkl":
                    with open(file_path, "rb") as f:
                        self.current_viz_data = pickle.load(f)
                    if not isinstance(self.current_viz_data, pd.DataFrame):
                        self.current_viz_data = pd.DataFrame(self.current_viz_data)

            elif data_source == "analysis_results":
                if (
                    hasattr(self, "current_analysis_result")
                    and self.current_analysis_result
                ):
                    # Use analysis result data
                    import pandas as pd

                    self.current_viz_data = pd.DataFrame(
                        self.current_analysis_result.statistics
                    )
                else:
                    self.app.update_status("No analysis results available", "warning")
                    return

            elif data_source == "generated":
                # Generate sample data for demonstration
                import numpy as np
                import pandas as pd

                np.random.seed(42)
                n_samples = 100
                self.current_viz_data = pd.DataFrame(
                    {
                        "x": np.linspace(0, 10, n_samples),
                        "y": np.sin(np.linspace(0, 10, n_samples))
                        + np.random.normal(0, 0.1, n_samples),
                        "group": np.random.choice(["A", "B", "C"], n_samples),
                        "value": np.random.normal(0, 1, n_samples),
                    }
                )

            self.app.update_status(
                f"Loaded visualization data: {self.current_viz_data.shape}"
            )

            # Auto-populate column suggestions
            if hasattr(self, "current_viz_data") and self.current_viz_data is not None:
                columns = list(self.current_viz_data.columns)
                if len(columns) > 0:
                    self.viz_x_var.set(columns[0])
                if len(columns) > 1:
                    self.viz_y_var.set(columns[1])

        except Exception as e:
            self.app.update_status(f"Error loading visualization data: {e}", "error")
            self.logger.error(f"Error loading visualization data: {e}")

    def generate_plot(self) -> None:
        """Generate visualization plot."""
        if self.current_viz_data is None:
            self.app.update_status("Please load data first", "warning")
            return

        try:
            self.app.update_status("Generating plot...")
            self.generate_plot_btn.configure(state="disabled")

            import matplotlib.pyplot as plt
            import matplotlib

            matplotlib.use("TkAgg")
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            import seaborn as sns
            import numpy as np

            # Clear previous plot
            for widget in self.plot_canvas_frame.winfo_children():
                widget.destroy()

            # Get plot parameters
            plot_type = self.plot_type_var.get()
            x_col = self.viz_x_var.get()
            y_col = self.viz_y_var.get()
            color_col = self.viz_color_var.get()
            title = self.viz_title_var.get() or f"{plot_type.title()} Plot"
            show_grid = self.viz_grid_var.get()
            show_legend = self.viz_legend_var.get()

            # Create figure
            fig, ax = plt.subplots(figsize=(10, 6))

            # Generate plot based on type
            if plot_type == "line":
                if (
                    x_col
                    and y_col
                    and x_col in self.current_viz_data.columns
                    and y_col in self.current_viz_data.columns
                ):
                    if color_col and color_col in self.current_viz_data.columns:
                        for group in self.current_viz_data[color_col].unique():
                            group_data = self.current_viz_data[
                                self.current_viz_data[color_col] == group
                            ]
                            ax.plot(
                                group_data[x_col],
                                group_data[y_col],
                                label=group,
                                marker="o",
                            )
                    else:
                        ax.plot(
                            self.current_viz_data[x_col],
                            self.current_viz_data[y_col],
                            marker="o",
                        )

            elif plot_type == "scatter":
                if (
                    x_col
                    and y_col
                    and x_col in self.current_viz_data.columns
                    and y_col in self.current_viz_data.columns
                ):
                    if color_col and color_col in self.current_viz_data.columns:
                        scatter = ax.scatter(
                            self.current_viz_data[x_col],
                            self.current_viz_data[y_col],
                            c=self.current_viz_data[color_col],
                            cmap="viridis",
                            alpha=0.7,
                        )
                        plt.colorbar(scatter, ax=ax)
                    else:
                        ax.scatter(
                            self.current_viz_data[x_col],
                            self.current_viz_data[y_col],
                            alpha=0.7,
                        )

            elif plot_type == "histogram":
                if x_col and x_col in self.current_viz_data.columns:
                    ax.hist(
                        self.current_viz_data[x_col].dropna(),
                        bins=30,
                        alpha=0.7,
                        edgecolor="black",
                    )

            elif plot_type == "box":
                if y_col and y_col in self.current_viz_data.columns:
                    if color_col and color_col in self.current_viz_data.columns:
                        self.current_viz_data.boxplot(column=y_col, by=color_col, ax=ax)
                    else:
                        ax.boxplot(self.current_viz_data[y_col].dropna())

            elif plot_type == "violin":
                if y_col and y_col in self.current_viz_data.columns:
                    if color_col and color_col in self.current_viz_data.columns:
                        sns.violinplot(
                            data=self.current_viz_data, x=color_col, y=y_col, ax=ax
                        )
                    else:
                        sns.violinplot(y=self.current_viz_data[y_col], ax=ax)

            elif plot_type == "heatmap":
                numeric_data = self.current_viz_data.select_dtypes(include=[np.number])
                if not numeric_data.empty:
                    sns.heatmap(
                        numeric_data.corr(),
                        annot=True,
                        cmap="coolwarm",
                        center=0,
                        ax=ax,
                    )

            elif plot_type == "correlation":
                numeric_data = self.current_viz_data.select_dtypes(include=[np.number])
                if not numeric_data.empty:
                    corr_matrix = numeric_data.corr()
                    sns.heatmap(
                        corr_matrix, annot=True, cmap="coolwarm", center=0, ax=ax
                    )

            elif plot_type == "distribution":
                if x_col and x_col in self.current_viz_data.columns:
                    sns.histplot(self.current_viz_data[x_col].dropna(), kde=True, ax=ax)

            elif plot_type == "timeseries":
                if (
                    x_col
                    and y_col
                    and x_col in self.current_viz_data.columns
                    and y_col in self.current_viz_data.columns
                ):
                    ax.plot(self.current_viz_data[x_col], self.current_viz_data[y_col])
                    ax.set_xlabel("Time")
                    ax.set_ylabel("Value")

            # Set labels and title
            ax.set_title(title, fontsize=14, fontweight="bold")
            if x_col:
                ax.set_xlabel(x_col)
            if y_col:
                ax.set_ylabel(y_col)

            # Set grid and legend
            ax.grid(show_grid)
            if show_legend and ax.get_legend():
                ax.legend()

            plt.tight_layout()

            # Embed plot in tkinter
            canvas = FigureCanvasTkAgg(fig, master=self.plot_canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

            # Store references
            self.current_figure = fig
            self.current_plot = canvas

            self.app.update_status("Plot generated successfully")

        except Exception as e:
            self.app.update_status(f"Error generating plot: {e}", "error")
            self.logger.error(f"Error generating plot: {e}")
        finally:
            self.generate_plot_btn.configure(state="normal")

    def save_plot(self, format_type: str) -> None:
        """Save plot to file."""
        if self.current_figure is None:
            self.app.update_status("No plot to save", "warning")
            return

        try:
            file_path = tk.filedialog.asksaveasfilename(
                title=f"Save Plot as {format_type.upper()}",
                defaultextension=f".{format_type}",
                filetypes=[(f"{format_type.upper()} Files", f"*.{format_type}")],
                initialdir=self.app.config.data_dir,
            )

            if not file_path:
                return

            self.current_figure.savefig(
                file_path, format=format_type, dpi=300, bbox_inches="tight"
            )
            self.app.update_status(f"Plot saved to {Path(file_path).name}")

        except Exception as e:
            self.app.update_status(f"Error saving plot: {e}", "error")
            self.logger.error(f"Error saving plot: {e}")

    def refresh_results_list(self) -> None:
        """Refresh the results list from disk."""
        try:
            import sys
            from pathlib import Path

            project_root = Path(__file__).parent.parent.parent
            sys.path.insert(0, str(project_root))
            from apgi_framework.analysis.analysis_engine import AnalysisEngine

            # Initialize analysis engine to get results
            engine = AnalysisEngine()
            analysis_ids = engine.list_analyses()

            self.available_results = []

            for analysis_id in analysis_ids:
                try:
                    summary = engine.get_analysis_summary(analysis_id)
                    result_item = {
                        "id": analysis_id,
                        "timestamp": summary.get("timestamp", ""),
                        "type": summary.get("analysis_type", "unknown"),
                        "parameters": summary.get("parameters", {}),
                        "statistics": summary.get("statistics", {}),
                        "data_summary": summary.get("data_summary", {}),
                        "plots": summary.get("plots", {}),
                    }
                    self.available_results.append(result_item)
                except Exception as e:
                    self.logger.warning(f"Failed to load analysis {analysis_id}: {e}")
                    continue

            # Add current analysis result if available
            if (
                hasattr(self, "current_analysis_result")
                and self.current_analysis_result
            ):
                current_item = {
                    "id": self.current_analysis_result.analysis_id,
                    "timestamp": self.current_analysis_result.timestamp.isoformat(),
                    "type": self.current_analysis_result.analysis_type,
                    "parameters": self.current_analysis_result.parameters,
                    "statistics": self.current_analysis_result.statistics,
                    "data_summary": self.current_analysis_result.data_summary,
                    "plots": self.current_analysis_result.plots,
                }
                # Avoid duplicates
                if not any(
                    r["id"] == current_item["id"] for r in self.available_results
                ):
                    self.available_results.insert(0, current_item)

            self.display_results_list()
            self.app.update_status(f"Found {len(self.available_results)} results")

        except Exception as e:
            self.app.update_status(f"Error refreshing results: {e}", "error")
            self.logger.error(f"Error refreshing results list: {e}")

    def display_results_list(self) -> None:
        """Display the results list in the UI."""
        # Clear existing list
        for widget in self.results_list_frame.winfo_children():
            widget.destroy()

        # Sort results
        sort_key = self.results_sort_var.get()
        if sort_key == "date":
            self.available_results.sort(
                key=lambda x: x.get("timestamp", ""), reverse=True
            )
        elif sort_key == "name":
            self.available_results.sort(key=lambda x: x.get("id", ""))
        elif sort_key == "type":
            self.available_results.sort(key=lambda x: x.get("type", ""))
        elif sort_key == "outcome":
            self.available_results.sort(
                key=lambda x: len(x.get("statistics", {})), reverse=True
            )

        # Apply filter
        filter_text = self.results_filter_var.get().lower()
        filtered_results = self.available_results
        if filter_text:
            filtered_results = [
                r
                for r in self.available_results
                if filter_text in r.get("id", "").lower()
                or filter_text in r.get("type", "").lower()
            ]

        # Display results
        self.result_checkboxes = {}
        for i, result in enumerate(filtered_results):
            # Create frame for this result
            result_frame = ctk.CTkFrame(self.results_list_frame)
            result_frame.pack(fill="x", padx=5, pady=2)

            # Checkbox for selection
            var = tk.BooleanVar()
            checkbox = ctk.CTkCheckBox(result_frame, text="", variable=var)
            checkbox.pack(side="left", padx=5)
            self.result_checkboxes[result["id"]] = var

            # Result info
            info_text = (
                f"{result['id']} - {result['type']} - {result['timestamp'][:19]}"
            )
            info_label = ctk.CTkLabel(result_frame, text=info_text)
            info_label.pack(side="left", padx=5, fill="x", expand=True)

            # View button
            view_btn = ctk.CTkButton(
                result_frame,
                text="View",
                width=60,
                command=lambda r=result: self.show_result_details(r),
            )
            view_btn.pack(side="right", padx=5)

    def show_result_details(self, result: dict) -> None:
        """Show details of a selected result."""
        self.current_result_details = result

        # Clear and populate details text
        self.results_details_text.delete("1.0", "end")

        details = f"""Analysis ID: {result['id']}
Type: {result['type']}
Timestamp: {result['timestamp']}

PARAMETERS:
"""
        for key, value in result.get("parameters", {}).items():
            details += f"  {key}: {value}\n"

        details += f"\nDATA SUMMARY:\n"
        details += f"Shape: {result.get('data_summary', {}).get('shape', 'N/A')}\n"
        details += (
            f"Columns: {result.get('data_summary', {}).get('columns', [])[:5]}...\n"
        )

        if result.get("statistics"):
            details += "\nKEY STATISTICS:\n"
            for key, value in list(result.get("statistics", {}).items())[:5]:
                if isinstance(value, dict):
                    details += f"  {key}:\n"
                    for sub_key, sub_value in list(value.items())[:3]:
                        details += f"    {sub_key}: {sub_value:.4f}\n"
                else:
                    details += f"  {key}: {value:.4f}\n"

        if result.get("plots"):
            details += f"\nPLOTS GENERATED: {len(result['plots'])}\n"
            for plot_id, plot_path in list(result["plots"].items())[:3]:
                details += f"  {plot_id}: {Path(plot_path).name}\n"

        self.results_details_text.insert("1.0", details)

    def filter_results(self) -> None:
        """Apply filter to results list."""
        self.display_results_list()

    def compare_results(self) -> None:
        """Compare selected results."""
        selected_ids = [
            result_id for result_id, var in self.result_checkboxes.items() if var.get()
        ]

        if len(selected_ids) < 2:
            self.app.update_status(
                "Please select at least 2 results to compare", "warning"
            )
            return

        if len(selected_ids) > 5:
            self.app.update_status(
                "Please select no more than 5 results to compare", "warning"
            )
            return

        try:
            # Create comparison window
            compare_window = ctk.CTkToplevel(self)
            compare_window.title("Compare Results")
            compare_window.geometry("800x600")

            # Create comparison text
            comparison_text = ctk.CTkTextbox(compare_window)
            comparison_text.pack(fill="both", expand=True, padx=10, pady=10)

            # Generate comparison
            comparison = "RESULTS COMPARISON\n" + "=" * 50 + "\n\n"

            for result_id in selected_ids:
                result = next(
                    (r for r in self.available_results if r["id"] == result_id), None
                )
                if result:
                    comparison += f"\n{result_id}:\n"
                    comparison += f"  Type: {result['type']}\n"
                    comparison += f"  Timestamp: {result['timestamp']}\n"

                    # Compare key statistics
                    stats = result.get("statistics", {})
                    if stats:
                        comparison += "  Key Statistics:\n"
                        for key, value in list(stats.items())[:3]:
                            if isinstance(value, (int, float)):
                                comparison += f"    {key}: {value:.4f}\n"
                    comparison += "\n"

            comparison_text.insert("1.0", comparison)
            comparison_text.configure(state="disabled")

            # Close button
            close_btn = ctk.CTkButton(
                compare_window, text="Close", command=compare_window.destroy
            )
            close_btn.pack(pady=10)

            self.app.update_status(f"Comparing {len(selected_ids)} results")

        except Exception as e:
            self.app.update_status(f"Error comparing results: {e}", "error")
            self.logger.error(f"Error comparing results: {e}")

    def export_results_report(self) -> None:
        """Export results report to file."""
        if not self.available_results:
            self.app.update_status("No results to export", "warning")
            return

        try:
            file_path = tk.filedialog.asksaveasfilename(
                title="Export Results Report",
                defaultextension=".pdf",
                filetypes=[
                    ("PDF Files", "*.pdf"),
                    ("JSON Files", "*.json"),
                    ("CSV Files", "*.csv"),
                    ("All Files", "*.*"),
                ],
                initialdir=self.app.config.data_dir,
            )

            if not file_path:
                return

            file_path = Path(file_path)

            if file_path.suffix == ".json":
                # Export as JSON
                import json

                with open(file_path, "w") as f:
                    json.dump(self.available_results, f, indent=2, default=str)

            elif file_path.suffix == ".csv":
                # Export summary as CSV
                import pandas as pd

                summary_data = []
                for result in self.available_results:
                    summary_data.append(
                        {
                            "id": result["id"],
                            "timestamp": result["timestamp"],
                            "type": result["type"],
                            "num_statistics": len(result.get("statistics", {})),
                            "num_plots": len(result.get("plots", {})),
                            "data_shape": str(
                                result.get("data_summary", {}).get("shape", "")
                            ),
                        }
                    )

                pd.DataFrame(summary_data).to_csv(file_path, index=False)

            elif file_path.suffix == ".pdf":
                # Create simple text report (would need reportlab for full PDF)
                report_text = "EXPERIMENT RESULTS REPORT\n"
                report_text += "=" * 50 + "\n\n"

                for result in self.available_results:
                    report_text += f"\n{result['id']}\n"
                    report_text += f"Type: {result['type']}\n"
                    report_text += f"Timestamp: {result['timestamp']}\n"
                    report_text += "-" * 30 + "\n"

                # Save as text file with .pdf extension (simplified)
                with open(file_path.with_suffix(".txt"), "w") as f:
                    f.write(report_text)
                file_path = file_path.with_suffix(".txt")

            self.app.update_status(f"Results report exported to {file_path.name}")

        except Exception as e:
            self.app.update_status(f"Error exporting report: {e}", "error")
            self.logger.error(f"Error exporting results report: {e}")

    def delete_results(self) -> None:
        """Delete selected results."""
        selected_ids = [
            result_id for result_id, var in self.result_checkboxes.items() if var.get()
        ]

        if not selected_ids:
            self.app.update_status("Please select results to delete", "warning")
            return

        # Confirmation dialog
        if len(selected_ids) == 1:
            confirm_msg = f"Delete result '{selected_ids[0]}'?"
        else:
            confirm_msg = f"Delete {len(selected_ids)} selected results?"

        confirm_dialog = ctk.CTkToplevel(self)
        confirm_dialog.title("Confirm Delete")
        confirm_dialog.geometry("300x150")

        ctk.CTkLabel(confirm_dialog, text=confirm_msg).pack(pady=20)

        def do_delete():
            try:
                import sys
                from pathlib import Path

                project_root = Path(__file__).parent.parent.parent
                sys.path.insert(0, str(project_root))
                from apgi_framework.analysis.analysis_engine import AnalysisEngine

                engine = AnalysisEngine()
                deleted_count = 0

                for result_id in selected_ids:
                    try:
                        # Delete result files (simplified approach)
                        results_dir = engine.output_dir / "results"
                        summary_file = results_dir / f"{result_id}_summary.json"
                        data_file = results_dir / f"{result_id}_data.csv"

                        if summary_file.exists():
                            summary_file.unlink()
                        if data_file.exists():
                            data_file.unlink()

                        deleted_count += 1
                    except Exception as e:
                        self.logger.warning(f"Failed to delete {result_id}: {e}")

                # Remove from available results
                self.available_results = [
                    r for r in self.available_results if r["id"] not in selected_ids
                ]

                self.display_results_list()
                self.app.update_status(f"Deleted {deleted_count} results")
                confirm_dialog.destroy()

            except Exception as e:
                self.app.update_status(f"Error deleting results: {e}", "error")
                self.logger.error(f"Error deleting results: {e}")

        button_frame = ctk.CTkFrame(confirm_dialog)
        button_frame.pack(pady=10)

        ctk.CTkButton(button_frame, text="Delete", command=do_delete).pack(
            side="left", padx=5
        )
        ctk.CTkButton(button_frame, text="Cancel", command=confirm_dialog.destroy).pack(
            side="left", padx=5
        )

    def load_selected_result(self) -> None:
        """Load selected result for detailed analysis."""
        selected_ids = [
            result_id for result_id, var in self.result_checkboxes.items() if var.get()
        ]

        if len(selected_ids) != 1:
            self.app.update_status(
                "Please select exactly one result to load", "warning"
            )
            return

        result_id = selected_ids[0]
        result = next((r for r in self.available_results if r["id"] == result_id), None)

        if result:
            self.show_result_details(result)
            self.app.update_status(f"Loaded result: {result_id}")

    def run_analysis(self) -> None:
        """Run the analysis with current configuration."""
        if not self.current_data:
            self.apply_changes()

        self.app.update_status("Starting analysis...")
        # Placeholder for analysis execution
        self.app.update_status("Analysis completed (placeholder)")
