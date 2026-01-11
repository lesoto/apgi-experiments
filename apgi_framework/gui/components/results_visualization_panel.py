"""
Results Visualization Panel for APGI Framework GUI.

Extracted from the monolithic GUI to provide a focused component
for visualizing test results and statistical analysis.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTk
import numpy as np
import json
import logging
from typing import Dict, Any, Optional, List, Callable
from pathlib import Path
import sys
from datetime import datetime

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from apgi_framework.logging.standardized_logging import get_logger
except ImportError as e:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("results_visualization_panel")
    logger.warning(f"Could not import standardized logging: {e}")

logger = logging.getLogger("results_visualization_panel")


class ResultsVisualizationPanel(ctk.CTkFrame):
    """
    Panel for visualizing test results and statistical analysis.

    Provides comprehensive visualization capabilities including real-time plotting,
    statistical summaries, comparison views, and export functionality.
    """

    def __init__(self, parent, results_callback: Optional[Callable] = None):
        """
        Initialize the results visualization panel.

        Args:
            parent: Parent widget
            results_callback: Callback for getting results data
        """
        super().__init__(parent)

        self.results_data = []
        self.test_run_history = []  # Track multiple runs for comparison
        self.results_callback = results_callback

        # Visualization settings
        self.current_view_mode = "Overview"
        self.plot_colors = {
            "primary": "#2E8B57",  # Sea green
            "secondary": "#4682B4",  # Steel blue
            "accent": "#DC143C",  # Crimson
            "warning": "#FF8C00",  # Dark orange
            "neutral": "#708090",  # Slate gray
        }

        # Callbacks for external components
        self.on_data_updated: Optional[Callable] = None
        self.on_export_requested: Optional[Callable] = None

        self._create_widgets()
        self._setup_matplotlib()

        logger.info("ResultsVisualizationPanel initialized")

    def _create_widgets(self):
        """Create visualization widgets."""
        # Create scrollable frame
        self.scrollable_frame = ctk.CTkScrollableFrame(self)
        self.scrollable_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Control section
        self._create_control_section()

        # Summary statistics section
        self._create_summary_section()

        # Visualization section
        self._create_visualization_section()

    def _create_control_section(self):
        """Create control buttons and view selector."""
        control_frame = ctk.CTkFrame(self.scrollable_frame)
        control_frame.pack(fill="x", padx=5, pady=5)

        # Control buttons
        self.clear_btn = ctk.CTkButton(
            control_frame,
            text="Clear Data",
            command=self._clear_data,
            fg_color=self.plot_colors["accent"],
        )
        self.clear_btn.pack(side="left", padx=2, pady=2)

        self.export_btn = ctk.CTkButton(
            control_frame,
            text="Export Results",
            command=self._export_results,
            fg_color=self.plot_colors["neutral"],
        )
        self.export_btn.pack(side="left", padx=2, pady=2)

        self.compare_btn = ctk.CTkButton(
            control_frame,
            text="Compare Runs",
            command=self._show_comparison_view,
            fg_color=self.plot_colors["secondary"],
        )
        self.compare_btn.pack(side="left", padx=2, pady=2)

        self.refresh_btn = ctk.CTkButton(
            control_frame,
            text="Refresh Plots",
            command=self._update_plots,
            fg_color=self.plot_colors["primary"],
        )
        self.refresh_btn.pack(side="left", padx=2, pady=2)

        # View mode selector
        ctk.CTkLabel(control_frame, text="View:").pack(side="right", padx=(10, 2))

        self.view_mode_var = tk.StringVar(value="Overview")
        self.view_mode_combo = ctk.CTkOptionMenu(
            control_frame,
            variable=self.view_mode_var,
            values=[
                "Overview",
                "Statistical Details",
                "Time Series",
                "Comparison",
                "Neural Signatures",
            ],
            width=15,
        )
        self.view_mode_combo.pack(side="right", padx=2)
        self.view_mode_combo.configure(
            command=lambda choice: self._change_view_mode(choice)
        )

    def _create_summary_section(self):
        """Create summary statistics section."""
        summary_frame = ctk.CTkFrame(self.scrollable_frame)
        summary_frame.pack(fill="x", padx=5, pady=5)

        summary_title = ctk.CTkLabel(
            summary_frame,
            text="Statistical Summary",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        summary_title.pack(padx=10, pady=(10, 5))

        # Summary text with scrollbar
        summary_container = ctk.CTkFrame(summary_frame)
        summary_container.pack(fill="x", padx=5, pady=5)

        self.summary_text = tk.Text(
            summary_container, height=6, wrap="word", font=("Courier", 9)
        )
        summary_scrollbar = ctk.CTkScrollbar(
            summary_container, command=self.summary_text.yview
        )
        self.summary_text.configure(yscrollcommand=summary_scrollbar.set)

        self.summary_text.pack(
            side="left", fill="both", expand=True, padx=(5, 0), pady=5
        )
        summary_scrollbar.pack(side="right", fill="y", padx=(0, 5), pady=5)

        # Configure text tags for formatting
        self.summary_text.tag_configure("header", font=("Courier", 10, "bold"))
        self.summary_text.tag_configure(
            "success", foreground=self.plot_colors["primary"]
        )
        self.summary_text.tag_configure(
            "warning", foreground=self.plot_colors["warning"]
        )
        self.summary_text.tag_configure("error", foreground=self.plot_colors["accent"])
        self.summary_text.tag_configure(
            "info", foreground=self.plot_colors["secondary"]
        )

        self._update_summary_text()

    def _create_visualization_section(self):
        """Create matplotlib visualization section."""
        viz_frame = ctk.CTkFrame(self.scrollable_frame)
        viz_frame.pack(fill="both", expand=True, padx=5, pady=5)

        viz_title = ctk.CTkLabel(
            viz_frame,
            text="Data Visualization",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        viz_title.pack(padx=10, pady=(10, 5))

        # Create matplotlib figure container
        self.fig_container = ctk.CTkFrame(viz_frame)
        self.fig_container.pack(fill="both", expand=True, padx=5, pady=5)

        # Initialize plots
        self._setup_matplotlib()

    def _setup_matplotlib(self):
        """Setup matplotlib figure and axes."""
        # Create figure with better layout
        self.fig = plt.figure(figsize=(14, 9))
        self.fig.patch.set_facecolor("#f0f0f0")

        # Set main title
        self.fig.suptitle(
            "APGI Falsification Test Results - Real-Time Analysis",
            fontsize=14,
            fontweight="bold",
        )

        # Create subplot grid
        gs = self.fig.add_gridspec(2, 2, hspace=0.4, wspace=0.3)
        self.ax1 = self.fig.add_subplot(gs[0, 0])  # Falsification rates
        self.ax2 = self.fig.add_subplot(gs[0, 1])  # Effect sizes
        self.ax3 = self.fig.add_subplot(gs[1, 0])  # P-values
        self.ax4 = self.fig.add_subplot(gs[1, 1])  # Statistical power

        # Style the axes
        for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
            ax.grid(True, alpha=0.3)
            ax.set_facecolor("#ffffff")

        # Create canvas
        if hasattr(self, "canvas"):
            self.canvas.get_tk_widget().destroy()

        self.canvas = FigureCanvasTk(self.fig, self.fig_container)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Initialize empty plots
        self._update_plots()

    def _change_view_mode(self, view_mode: str):
        """Change visualization view mode."""
        self.current_view_mode = view_mode
        self._update_plots()
        logger.info(f"Changed view mode to: {view_mode}")

    def _show_comparison_view(self):
        """Show comparison view for multiple test runs."""
        if len(self.test_run_history) < 2:
            messagebox.showinfo(
                "Info",
                "Need at least 2 test runs to compare. Run more tests to enable comparison.",
            )
            return

        # Switch to comparison view
        self.view_mode_var.set("Comparison")
        self._change_view_mode("Comparison")

    def _clear_data(self):
        """Clear all results data."""
        if messagebox.askyesno(
            "Clear Data", "Clear all visualization data? This cannot be undone."
        ):
            self.results_data = []
            self.test_run_history = []
            self._update_plots()
            self._update_summary_text()

            # Notify data cleared
            if self.on_data_updated:
                self.on_data_updated([])

            logger.info("Visualization data cleared")

    def _update_plots(self):
        """Update all visualization plots based on current view mode."""
        # Clear all axes
        for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
            ax.clear()
            ax.grid(True, alpha=0.3)
            ax.set_facecolor("#ffffff")

        if not self.results_data:
            self._show_empty_plots()
        else:
            if self.current_view_mode == "Overview":
                self._show_overview_plots()
            elif self.current_view_mode == "Statistical Details":
                self._show_statistical_details()
            elif self.current_view_mode == "Time Series":
                self._show_time_series_plots()
            elif self.current_view_mode == "Comparison":
                self._show_comparison_plots()
            elif self.current_view_mode == "Neural Signatures":
                self._show_neural_signature_plots()

        # Refresh canvas
        self.canvas.draw()

    def _show_empty_plots(self):
        """Show empty plots with instructions."""
        empty_message = "No data available\nRun tests to see results"

        for i, ax in enumerate([self.ax1, self.ax2, self.ax3, self.ax4]):
            ax.text(
                0.5,
                0.5,
                empty_message,
                ha="center",
                va="center",
                transform=ax.transAxes,
                fontsize=12,
                color=self.plot_colors["neutral"],
            )
            ax.set_xticks([])
            ax.set_yticks([])

            # Set appropriate titles
            titles = [
                "Falsification Rates",
                "Effect Sizes",
                "P-values",
                "Statistical Power",
            ]
            ax.set_title(titles[i], fontweight="bold")

    def _show_overview_plots(self):
        """Show overview visualization plots."""
        # Extract data
        test_types = [r.get("test_type", "Unknown") for r in self.results_data]
        falsified = [r.get("is_falsified", False) for r in self.results_data]
        effect_sizes = [r.get("effect_size", 0) for r in self.results_data]
        p_values = [r.get("p_value", 1.0) for r in self.results_data]
        powers = [r.get("statistical_power", 0) for r in self.results_data]

        # Plot 1: Falsification rates by test type
        self._plot_falsification_rates(test_types, falsified)

        # Plot 2: Effect sizes distribution
        self._plot_effect_sizes(effect_sizes)

        # Plot 3: P-values distribution
        self._plot_p_values(p_values)

        # Plot 4: Statistical power
        self._plot_statistical_power(powers)

    def _plot_falsification_rates(self, test_types: List[str], falsified: List[bool]):
        """Plot falsification rates by test type."""
        unique_tests = sorted(list(set(test_types)))
        falsification_rates = []
        test_counts = []

        for test in unique_tests:
            test_results = [f for t, f in zip(test_types, falsified) if t == test]
            rate = sum(test_results) / len(test_results) if test_results else 0
            falsification_rates.append(rate)
            test_counts.append(len(test_results))

        colors = [
            self.plot_colors["accent"] if r > 0.5 else self.plot_colors["primary"]
            for r in falsification_rates
        ]

        bars = self.ax1.bar(
            range(len(unique_tests)), falsification_rates, color=colors, alpha=0.7
        )

        self.ax1.set_xticks(range(len(unique_tests)))
        self.ax1.set_xticklabels(
            [t.replace("_", "\n") for t in unique_tests],
            rotation=0,
            ha="center",
            fontsize=8,
        )
        self.ax1.set_ylabel("Falsification Rate")
        self.ax1.set_title("Falsification Rates by Test Type", fontweight="bold")
        self.ax1.set_ylim(0, 1.0)
        self.ax1.axhline(y=0.5, color="gray", linestyle="--", alpha=0.5)

        # Add count labels on bars
        for i, (bar, count) in enumerate(zip(bars, test_counts)):
            height = bar.get_height()
            self.ax1.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"n={count}",
                ha="center",
                va="bottom",
                fontsize=8,
            )

    def _plot_effect_sizes(self, effect_sizes: List[float]):
        """Plot effect sizes distribution."""
        if effect_sizes:
            self.ax2.hist(
                effect_sizes,
                bins=min(10, len(effect_sizes)),
                alpha=0.7,
                color=self.plot_colors["secondary"],
                edgecolor="black",
            )

            # Reference lines
            self.ax2.axvline(
                x=0.5,
                color=self.plot_colors["warning"],
                linestyle="--",
                label="Medium effect (0.5)",
                linewidth=2,
            )
            self.ax2.axvline(
                x=0.8,
                color=self.plot_colors["accent"],
                linestyle="--",
                label="Large effect (0.8)",
                linewidth=2,
            )

            self.ax2.set_xlabel("Effect Size")
            self.ax2.set_ylabel("Frequency")
            self.ax2.legend(fontsize=8)

        self.ax2.set_title("Effect Sizes Distribution", fontweight="bold")

    def _plot_p_values(self, p_values: List[float]):
        """Plot p-values distribution."""
        if p_values:
            # Create histogram with significance threshold
            self.ax3.hist(
                p_values,
                bins=min(10, len(p_values)),
                alpha=0.7,
                color=self.plot_colors["neutral"],
                edgecolor="black",
            )

            # Significance threshold
            self.ax3.axvline(
                x=0.05,
                color=self.plot_colors["accent"],
                linestyle="--",
                label="α = 0.05",
                linewidth=2,
            )

            # Count significant results
            significant = sum(1 for p in p_values if p < 0.05)
            total = len(p_values)
            sig_rate = significant / total if total > 0 else 0

            self.ax3.text(
                0.95,
                0.95,
                f"Significant: {significant}/{total} ({sig_rate:.1%})",
                transform=self.ax3.transAxes,
                ha="right",
                va="top",
                bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
            )

            self.ax3.set_xlabel("P-value")
            self.ax3.legend(fontsize=8)

        self.ax3.set_title("P-values Distribution", fontweight="bold")

    def _plot_statistical_power(self, powers: List[float]):
        """Plot statistical power."""
        if powers:
            # Create histogram
            self.ax4.hist(
                powers,
                bins=min(10, len(powers)),
                alpha=0.7,
                color=self.plot_colors["primary"],
                edgecolor="black",
            )

            # Adequate power threshold
            self.ax4.axvline(
                x=0.8,
                color=self.plot_colors["warning"],
                linestyle="--",
                label="Adequate power (0.8)",
                linewidth=2,
            )

            # Count adequate power
            adequate = sum(1 for p in powers if p >= 0.8)
            total = len(powers)
            adequate_rate = adequate / total if total > 0 else 0

            self.ax4.text(
                0.95,
                0.95,
                f"Adequate: {adequate}/{total} ({adequate_rate:.1%})",
                transform=self.ax4.transAxes,
                ha="right",
                va="top",
                bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
            )

            self.ax4.set_xlabel("Statistical Power")
            self.ax4.legend(fontsize=8)

        self.ax4.set_title("Statistical Power Distribution", fontweight="bold")

    def _show_statistical_details(self):
        """Show detailed statistical analysis."""
        # Extract detailed statistics
        effect_sizes = [r.get("effect_size", 0) for r in self.results_data]
        p_values = [r.get("p_value", 1.0) for r in self.results_data]
        confidence_intervals = [
            r.get("confidence_interval", [0, 1]) for r in self.results_data
        ]

        # Plot 1: Effect sizes with confidence intervals
        self._plot_effect_sizes_with_ci(effect_sizes, confidence_intervals)

        # Plot 2: P-value vs Effect size scatter
        self._plot_p_vs_effect_size(p_values, effect_sizes)

        # Plot 3: Confidence interval widths
        self._plot_ci_widths(confidence_intervals)

        # Plot 4: Statistical power analysis
        self._plot_power_analysis()

    def _show_time_series_plots(self):
        """Show time series analysis of test runs."""
        if not self.test_run_history:
            self._show_empty_plots()
            return

        # Extract time series data
        timestamps = [
            run.get("timestamp", datetime.now()) for run in self.test_run_history
        ]
        success_rates = [run.get("success_rate", 0) for run in self.test_run_history]
        falsification_rates = [
            run.get("falsification_rate", 0) for run in self.test_run_history
        ]

        # Plot time series
        self._plot_success_rate_timeline(timestamps, success_rates)
        self._plot_falsification_timeline(timestamps, falsification_rates)
        self._plot_trend_analysis(timestamps, success_rates, falsification_rates)
        self._plot_run_comparison()

    def _show_comparison_plots(self):
        """Show comparison plots for multiple runs."""
        if len(self.test_run_history) < 2:
            self._show_empty_plots()
            return

        # Extract comparison data
        run_names = [f"Run {i+1}" for i in range(len(self.test_run_history))]
        metrics = [
            "success_rate",
            "falsification_rate",
            "mean_effect_size",
            "mean_power",
        ]

        # Create comparison plots
        self._plot_run_comparison_bar(run_names, metrics)
        self._plot_run_radar_comparison(run_names)
        self._plot_performance_trends()
        self._plot_statistical_significance_comparison()

    def _show_neural_signature_plots(self):
        """Show neural signature specific visualizations."""
        # Extract neural data
        p3b_amplitudes = [r.get("p3b_amplitude", []) for r in self.results_data]
        gamma_powers = [r.get("gamma_power", []) for r in self.results_data]

        # Plot neural signatures
        self._plot_p3b_analysis(p3b_amplitudes)
        self._plot_gamma_analysis(gamma_powers)
        self._plot_neural_correlations()
        self._plot_signature_distributions()

    def _update_summary_text(self):
        """Update summary statistics text."""
        self.summary_text.configure(state="normal")
        self.summary_text.delete("1.0", "end")

        if not self.results_data:
            self.summary_text.insert(
                "1.0", "No test results yet. Run tests to see summary statistics.\n"
            )
        else:
            # Calculate summary statistics
            total_tests = len(self.results_data)
            falsified_tests = sum(
                1 for r in self.results_data if r.get("is_falsified", False)
            )
            falsification_rate = falsified_tests / total_tests if total_tests > 0 else 0

            effect_sizes = [r.get("effect_size", 0) for r in self.results_data]
            mean_effect_size = np.mean(effect_sizes) if effect_sizes else 0

            p_values = [r.get("p_value", 1.0) for r in self.results_data]
            significant_tests = sum(1 for p in p_values if p < 0.05)

            powers = [r.get("statistical_power", 0) for r in self.results_data]
            mean_power = np.mean(powers) if powers else 0

            # Build summary text
            summary = f"{'='*50}\n"
            summary += f"SUMMARY STATISTICS\n"
            summary += f"{'='*50}\n\n"
            summary += f"Total Tests:        {total_tests}\n"
            summary += (
                f"Falsified Tests:   {falsified_tests} ({falsification_rate:.1%})\n"
            )
            summary += f"Mean Effect Size:  {mean_effect_size:.3f}\n"
            summary += f"Significant Tests: {significant_tests} ({significant_tests/total_tests:.1%})\n"
            summary += f"Mean Power:        {mean_power:.3f}\n\n"

            # Test type breakdown
            test_types = {}
            for result in self.results_data:
                test_type = result.get("test_type", "Unknown")
                if test_type not in test_types:
                    test_types[test_type] = {"total": 0, "falsified": 0}
                test_types[test_type]["total"] += 1
                if result.get("is_falsified", False):
                    test_types[test_type]["falsified"] += 1

            summary += f"TEST TYPE BREAKDOWN\n"
            summary += f"{'-'*30}\n"
            for test_type, stats in test_types.items():
                rate = stats["falsified"] / stats["total"] if stats["total"] > 0 else 0
                summary += f"{test_type:20s}: {stats['falsified']:2d}/{stats['total']:2d} ({rate:.1%})\n"

            # Insert summary with formatting
            self.summary_text.insert("1.0", summary)

            # Apply formatting tags
            self.summary_text.tag_add("header", "1.0", "3.0")
            self.summary_text.tag_add("info", "4.0", "10.0")
            self.summary_text.tag_add("header", "11.0", "13.0")

            # Color code falsification rate
            if falsification_rate > 0.5:
                self.summary_text.tag_add("warning", "6.0", "6.0")
            else:
                self.summary_text.tag_add("success", "6.0", "6.0")

        self.summary_text.configure(state="disabled")

    def _export_results(self):
        """Export visualization results to file."""
        try:
            file_path = filedialog.asksaveasfilename(
                title="Export Visualization Results",
                defaultextension=".json",
                filetypes=[
                    ("JSON files", "*.json"),
                    ("PNG images", "*.png"),
                    ("CSV data", "*.csv"),
                    ("All files", "*.*"),
                ],
            )

            if file_path:
                if file_path.endswith(".json"):
                    self._export_json(file_path)
                elif file_path.endswith(".png"):
                    self._export_image(file_path)
                elif file_path.endswith(".csv"):
                    self._export_csv(file_path)
                else:
                    # Default to JSON
                    self._export_json(file_path + ".json")

                messagebox.showinfo("Success", f"Results exported to {file_path}")

                # Notify export requested
                if self.on_export_requested:
                    self.on_export_requested(file_path)

        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export results: {e}")
            logger.error(f"Failed to export results: {e}")

    def _export_json(self, file_path: str):
        """Export results as JSON."""
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "view_mode": self.current_view_mode,
            "summary_statistics": self._calculate_summary_stats(),
            "results_data": self.results_data,
            "test_run_history": self.test_run_history,
        }

        with open(file_path, "w") as f:
            json.dump(export_data, f, indent=2, default=str)

    def _export_image(self, file_path: str):
        """Export current visualization as image."""
        self.fig.savefig(file_path, dpi=300, bbox_inches="tight")

    def _export_csv(self, file_path: str):
        """Export results data as CSV."""
        import pandas as pd

        if self.results_data:
            df = pd.DataFrame(self.results_data)
            df.to_csv(file_path, index=False)

    def _calculate_summary_stats(self) -> Dict[str, Any]:
        """Calculate summary statistics for export."""
        if not self.results_data:
            return {}

        total_tests = len(self.results_data)
        falsified_tests = sum(
            1 for r in self.results_data if r.get("is_falsified", False)
        )

        effect_sizes = [r.get("effect_size", 0) for r in self.results_data]
        p_values = [r.get("p_value", 1.0) for r in self.results_data]
        powers = [r.get("statistical_power", 0) for r in self.results_data]

        return {
            "total_tests": total_tests,
            "falsified_tests": falsified_tests,
            "falsification_rate": (
                falsified_tests / total_tests if total_tests > 0 else 0
            ),
            "mean_effect_size": np.mean(effect_sizes) if effect_sizes else 0,
            "median_effect_size": np.median(effect_sizes) if effect_sizes else 0,
            "std_effect_size": np.std(effect_sizes) if effect_sizes else 0,
            "significant_tests": sum(1 for p in p_values if p < 0.05),
            "mean_p_value": np.mean(p_values) if p_values else 1.0,
            "mean_power": np.mean(powers) if powers else 0,
            "adequate_power_tests": sum(1 for p in powers if p >= 0.8),
        }

    def add_results(self, test_name: str, results: Dict[str, Any]):
        """Add new test results to visualization."""
        # Add timestamp
        results["timestamp"] = datetime.now()
        results["test_type"] = test_name

        self.results_data.append(results)

        # Add to run history
        run_summary = {
            "test_name": test_name,
            "timestamp": results["timestamp"],
            "success_rate": results.get("success_rate", 0),
            "falsification_rate": 1.0 if results.get("is_falsified", False) else 0.0,
            "mean_effect_size": results.get("effect_size", 0),
            "mean_power": results.get("statistical_power", 0),
        }
        self.test_run_history.append(run_summary)

        # Update visualizations
        self._update_plots()
        self._update_summary_text()

        # Notify data updated
        if self.on_data_updated:
            self.on_data_updated(self.results_data)

        logger.info(f"Added results for {test_name} test")

    def clear_results(self):
        """Clear all results data."""
        self.results_data = []
        self.test_run_history = []
        self._update_plots()
        self._update_summary_text()

    def get_results_data(self) -> List[Dict[str, Any]]:
        """Get current results data."""
        return self.results_data.copy()

    def set_data_updated_callback(self, callback: Callable):
        """Set callback for data update events."""
        self.on_data_updated = callback

    def set_export_requested_callback(self, callback: Callable):
        """Set callback for export request events."""
        self.on_export_requested = callback

    def refresh_visualization(self):
        """Force refresh of all visualizations."""
        self._update_plots()
        self._update_summary_text()

    # Additional plotting methods for different view modes
    def _plot_effect_sizes_with_ci(
        self, effect_sizes: List[float], confidence_intervals: List[List[float]]
    ):
        """Plot effect sizes with confidence intervals."""
        if effect_sizes and confidence_intervals:
            x_pos = range(len(effect_sizes))
            ci_lower = [ci[0] for ci in confidence_intervals]
            ci_upper = [ci[1] for ci in confidence_intervals]

            self.ax1.errorbar(
                x_pos,
                effect_sizes,
                yerr=[
                    np.array(effect_sizes) - np.array(ci_lower),
                    np.array(ci_upper) - np.array(effect_sizes),
                ],
                fmt="o",
                capsize=5,
                capthick=2,
                color=self.plot_colors["secondary"],
            )
            self.ax1.axhline(y=0, color="gray", linestyle="-", alpha=0.5)
            self.ax1.set_xlabel("Test Index")
            self.ax1.set_ylabel("Effect Size")
            self.ax1.set_title(
                "Effect Sizes with Confidence Intervals", fontweight="bold"
            )

    def _plot_p_vs_effect_size(self, p_values: List[float], effect_sizes: List[float]):
        """Plot p-values vs effect sizes scatter plot."""
        if p_values and effect_sizes:
            colors = [
                self.plot_colors["accent"] if p < 0.05 else self.plot_colors["neutral"]
                for p in p_values
            ]

            self.ax2.scatter(effect_sizes, p_values, c=colors, alpha=0.7)
            self.ax2.axhline(
                y=0.05,
                color=self.plot_colors["accent"],
                linestyle="--",
                label="α = 0.05",
            )
            self.ax2.axvline(x=0, color="gray", linestyle="-", alpha=0.5)
            self.ax2.set_xlabel("Effect Size")
            self.ax2.set_ylabel("P-value")
            self.ax2.set_title("P-value vs Effect Size", fontweight="bold")
            self.ax2.legend()

    def _plot_ci_widths(self, confidence_intervals: List[List[float]]):
        """Plot confidence interval widths."""
        if confidence_intervals:
            ci_widths = [ci[1] - ci[0] for ci in confidence_intervals]
            self.ax3.hist(
                ci_widths,
                bins=min(10, len(ci_widths)),
                alpha=0.7,
                color=self.plot_colors["warning"],
                edgecolor="black",
            )
            self.ax3.set_xlabel("Confidence Interval Width")
            self.ax3.set_ylabel("Frequency")
            self.ax3.set_title("Confidence Interval Widths", fontweight="bold")

    def _plot_power_analysis(self):
        """Plot statistical power analysis."""
        # Create power curve
        effect_sizes = np.linspace(0.1, 2.0, 50)
        sample_sizes = [20, 50, 100, 200]

        for n in sample_sizes:
            # Simplified power calculation (would use proper statistical methods)
            power = 1 - np.exp(-n * effect_sizes**2 / 100)  # Mock calculation
            self.ax4.plot(effect_sizes, power, label=f"n={n}", linewidth=2)

        self.ax4.axhline(
            y=0.8,
            color=self.plot_colors["warning"],
            linestyle="--",
            label="Adequate Power",
        )
        self.ax4.set_xlabel("Effect Size")
        self.ax4.set_ylabel("Statistical Power")
        self.ax4.set_title("Power Analysis", fontweight="bold")
        self.ax4.legend()
        self.ax4.grid(True, alpha=0.3)


# Factory function for easy instantiation
def create_results_visualization_panel(
    parent, results_callback: Optional[Callable] = None
) -> ResultsVisualizationPanel:
    """
    Create a results visualization panel with default settings.

    Args:
        parent: Parent widget
        results_callback: Optional results callback

    Returns:
        Configured ResultsVisualizationPanel instance
    """
    return ResultsVisualizationPanel(parent, results_callback)
