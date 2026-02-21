"""
Interactive comparison dashboard for APGI Framework experiment results.

Provides comprehensive visualization and comparison capabilities for multiple
experiment results with interactive plots, statistical analysis, and export options.
"""

import json
import logging
import queue
import tkinter as tk
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import (
        FigureCanvasTkAgg,
        NavigationToolbar2Tk,
    )
    from matplotlib.figure import Figure

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt_type: Any = None  # type: ignore[assignment]
    Figure_type: Any = None  # type: ignore[assignment]

try:
    import seaborn as sns  # type: ignore

    SEABORN_AVAILABLE = True
    sns.set_style("whitegrid")
except ImportError:
    SEABORN_AVAILABLE = False
    sns = None  # type: ignore

try:
    from scipy import stats  # type: ignore

    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    stats = None

logger = logging.getLogger(__name__)


@dataclass
class ExperimentResult:
    """Represents an experiment result for comparison."""

    name: str
    data: Dict[str, Any]
    parameters: Dict[str, Any]
    metadata: Dict[str, Any]
    timestamp: datetime
    file_path: Optional[str] = None

    def get_metric(self, metric_name: str) -> Optional[float]:
        """Get a specific metric value."""
        return self.data.get(metric_name)

    def get_parameter(self, param_name: str) -> Any:
        """Get a specific parameter value."""
        return self.parameters.get(param_name)


class ComparisonDashboard:
    """
    Interactive comparison dashboard for experiment results.

    Provides side-by-side comparison, statistical analysis, and visualization
    of multiple experiment results.
    """

    def __init__(self, parent: tk.Widget):
        self.parent = parent
        self.experiments: List[ExperimentResult] = []
        self.selected_experiments: List[str] = []
        self.current_plot_type = "comparison"
        self.plot_queue: queue.Queue[Any] = queue.Queue()

        # Check dependencies
        self._check_dependencies()

        # Create UI
        self._create_ui()

        logger.info("Comparison dashboard initialized")

    def _check_dependencies(self):
        """Check if required dependencies are available."""
        missing_deps = []

        if not MATPLOTLIB_AVAILABLE:
            missing_deps.append("matplotlib")

        if not SEABORN_AVAILABLE:
            missing_deps.append("seaborn")

        if not SCIPY_AVAILABLE:
            missing_deps.append("scipy")

        if missing_deps:
            logger.warning(f"Missing dependencies: {missing_deps}")
            logger.warning("Some features may not be available")

    def _create_ui(self):
        """Create the main UI components."""
        # Main container
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left panel - Experiment selection and controls
        left_panel = ttk.Frame(main_frame, width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)

        # Right panel - Visualization
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create left panel components
        self._create_experiment_panel(left_panel)
        self._create_control_panel(left_panel)

        # Create right panel components
        self._create_visualization_panel(right_panel)
        self._create_statistics_panel(right_panel)

    def _create_experiment_panel(self, parent):
        """Create the experiment selection panel."""
        # Title
        title_label = ttk.Label(parent, text="Experiments", font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 10))

        # Add/Remove buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(
            button_frame, text="Add Experiment", command=self._add_experiment
        ).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(
            button_frame, text="Remove Selected", command=self._remove_selected
        ).pack(side=tk.LEFT)

        # Experiment list
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Treeview for experiments
        columns = ("Name", "Date", "Status")
        self.experiment_tree = ttk.Treeview(
            list_frame, columns=columns, show="tree headings", height=8
        )

        self.experiment_tree.heading("#0", text="")
        self.experiment_tree.heading("Name", text="Name")
        self.experiment_tree.heading("Date", text="Date")
        self.experiment_tree.heading("Status", text="Status")

        self.experiment_tree.column("#0", width=0, stretch=False)
        self.experiment_tree.column("Name", width=120)
        self.experiment_tree.column("Date", width=80)
        self.experiment_tree.column("Status", width=60)

        # Scrollbar
        scrollbar = ttk.Scrollbar(
            list_frame, orient=tk.VERTICAL, command=self.experiment_tree.yview
        )
        self.experiment_tree.configure(yscrollcommand=scrollbar.set)

        self.experiment_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind selection event
        self.experiment_tree.bind("<<TreeviewSelect>>", self._on_experiment_select)

        # Select all/none buttons
        select_frame = ttk.Frame(parent)
        select_frame.pack(fill=tk.X)

        ttk.Button(select_frame, text="Select All", command=self._select_all).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        ttk.Button(select_frame, text="Select None", command=self._select_none).pack(
            side=tk.LEFT
        )

    def _create_control_panel(self, parent):
        """Create the control panel."""
        # Title
        title_label = ttk.Label(
            parent, text="Comparison Options", font=("Arial", 12, "bold")
        )
        title_label.pack(pady=(10, 10))

        # Plot type selection
        plot_frame = ttk.Frame(parent)
        plot_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(plot_frame, text="Plot Type:").pack(side=tk.LEFT, padx=(0, 5))

        self.plot_type_var = tk.StringVar(value="comparison")
        plot_types = [
            "Comparison",
            "Correlation",
            "Distribution",
            "Time Series",
            "Performance",
        ]

        plot_menu = ttk.Combobox(
            plot_frame,
            textvariable=self.plot_type_var,
            values=plot_types,
            state="readonly",
        )
        plot_menu.pack(side=tk.LEFT, fill=tk.X, expand=True)
        plot_menu.bind("<<ComboboxSelected>>", self._on_plot_type_change)

        # Metrics selection
        metrics_frame = ttk.Frame(parent)
        metrics_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(metrics_frame, text="Metrics:").pack(anchor=tk.W, padx=(0, 5))

        self.metrics_listbox = tk.Listbox(
            metrics_frame, height=4, selectmode=tk.MULTIPLE
        )
        self.metrics_listbox.pack(fill=tk.X)

        # Statistical tests
        stats_frame = ttk.Frame(parent)
        stats_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(stats_frame, text="Statistical Test:").pack(anchor=tk.W, padx=(0, 5))

        self.stats_var = tk.StringVar(value="none")
        stats_options = ["None", "t-test", "ANOVA", "Mann-Whitney U", "Kruskal-Wallis"]

        stats_menu = ttk.Combobox(
            stats_frame,
            textvariable=self.stats_var,
            values=stats_options,
            state="readonly",
        )
        stats_menu.pack(fill=tk.X)

        # Update button
        ttk.Button(
            parent, text="Update Comparison", command=self._update_comparison
        ).pack(fill=tk.X, pady=(10, 0))

        # Export button
        ttk.Button(parent, text="Export Results", command=self._export_results).pack(
            fill=tk.X, pady=(5, 0)
        )

    def _create_visualization_panel(self, parent):
        """Create the visualization panel."""
        # Title
        title_label = ttk.Label(
            parent, text="Visualization", font=("Arial", 12, "bold")
        )
        title_label.pack(pady=(0, 10))

        # Create matplotlib figure if available
        if MATPLOTLIB_AVAILABLE:
            # Create figure with subplots
            self.figure = Figure(figsize=(10, 6), dpi=100)
            self.canvas = FigureCanvasTkAgg(self.figure, parent)
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            # Add navigation toolbar
            toolbar_frame = ttk.Frame(parent)
            toolbar_frame.pack(fill=tk.X, pady=(5, 0))

            self.toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
            self.toolbar.update()
        else:
            # Fallback message
            no_plot_label = ttk.Label(
                parent,
                text="Matplotlib not available\nInstall matplotlib for visualization",
                font=("Arial", 11),
            )
            no_plot_label.pack(expand=True)

    def _create_statistics_panel(self, parent):
        """Create the statistics panel."""
        # Title
        title_label = ttk.Label(
            parent, text="Statistical Analysis", font=("Arial", 12, "bold")
        )
        title_label.pack(pady=(10, 10))

        # Statistics text widget
        stats_frame = ttk.Frame(parent)
        stats_frame.pack(fill=tk.BOTH, expand=True)

        self.stats_text = tk.Text(stats_frame, height=8, wrap=tk.WORD)
        stats_scrollbar = ttk.Scrollbar(
            stats_frame, orient=tk.VERTICAL, command=self.stats_text.yview
        )

        self.stats_text.configure(yscrollcommand=stats_scrollbar.set)

        self.stats_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        stats_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _add_experiment(self):
        """Add an experiment to the comparison."""
        file_path = filedialog.askopenfilename(
            title="Select Experiment Result",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )

        if not file_path:
            return

        try:
            # Load experiment data
            with open(file_path, "r") as f:
                data = json.load(f)

            # Create experiment result
            experiment = ExperimentResult(
                name=data.get("name", Path(file_path).stem),
                data=data.get("results", {}),
                parameters=data.get("parameters", {}),
                metadata=data.get("metadata", {}),
                timestamp=datetime.now(),
                file_path=file_path,
            )

            self.experiments.append(experiment)

            # Update tree view
            self._update_experiment_tree()

            # Update metrics list
            self._update_metrics_list()

            logger.info(f"Added experiment: {experiment.name}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load experiment: {str(e)}")
            logger.error(f"Failed to load experiment from {file_path}: {e}")

    def _remove_selected(self):
        """Remove selected experiments."""
        selection = self.experiment_tree.selection()

        if not selection:
            messagebox.showwarning("Warning", "No experiments selected")
            return

        # Remove experiments
        for item in selection:
            values = self.experiment_tree.item(item)["values"]
            experiment_name = values[0]

            self.experiments = [
                exp for exp in self.experiments if exp.name != experiment_name
            ]

        # Update UI
        self._update_experiment_tree()
        self._update_metrics_list()

        logger.info(f"Removed {len(selection)} experiments")

    def _update_experiment_tree(self):
        """Update the experiment tree view."""
        # Clear existing items
        for item in self.experiment_tree.get_children():
            self.experiment_tree.delete(item)

        # Add experiments
        for experiment in self.experiments:
            self.experiment_tree.insert(
                "",
                tk.END,
                values=(
                    experiment.name,
                    experiment.timestamp.strftime("%Y-%m-%d"),
                    "Loaded",
                ),
            )

    def _update_metrics_list(self):
        """Update the metrics list based on loaded experiments."""
        if not self.experiments:
            self.metrics_listbox.delete(0, tk.END)
            return

        # Get all available metrics
        all_metrics = set()
        for experiment in self.experiments:
            all_metrics.update(experiment.data.keys())

        # Update listbox
        self.metrics_listbox.delete(0, tk.END)
        for metric in sorted(all_metrics):
            self.metrics_listbox.insert(tk.END, metric)

        # Select first few metrics by default
        for i in range(min(3, len(all_metrics))):
            self.metrics_listbox.selection_set(i)

    def _on_experiment_select(self, event):
        """Handle experiment selection."""
        selection = self.experiment_tree.selection()
        self.selected_experiments = []

        for item in selection:
            values = self.experiment_tree.item(item)["values"]
            self.selected_experiments.append(values[0])

        logger.debug(f"Selected experiments: {self.selected_experiments}")

    def _select_all(self):
        """Select all experiments."""
        for item in self.experiment_tree.get_children():
            self.experiment_tree.selection_add(item)

    def _select_none(self):
        """Select no experiments."""
        for item in self.experiment_tree.get_children():
            self.experiment_tree.selection_remove(item)

    def _on_plot_type_change(self, event):
        """Handle plot type change."""
        self.current_plot_type = self.plot_type_var.get().lower().replace(" ", "_")
        self._update_comparison()

    def _update_comparison(self):
        """Update the comparison visualization."""
        if not MATPLOTLIB_AVAILABLE:
            messagebox.showwarning(
                "Warning", "Matplotlib not available for visualization"
            )
            return

        if not self.selected_experiments:
            messagebox.showwarning("Warning", "No experiments selected")
            return

        # Get selected metrics
        selected_metrics = [
            self.metrics_listbox.get(i) for i in self.metrics_listbox.curselection()
        ]

        if not selected_metrics:
            messagebox.showwarning("Warning", "No metrics selected")
            return

        # Filter experiments
        selected_exp_data = [
            exp for exp in self.experiments if exp.name in self.selected_experiments
        ]

        if len(selected_exp_data) < 2:
            messagebox.showwarning(
                "Warning", "Select at least 2 experiments for comparison"
            )
            return

        try:
            # Clear previous plot
            self.figure.clear()

            # Create plot based on type
            if self.current_plot_type == "comparison":
                self._create_comparison_plot(selected_exp_data, selected_metrics)
            elif self.current_plot_type == "correlation":
                self._create_correlation_plot(selected_exp_data, selected_metrics)
            elif self.current_plot_type == "distribution":
                self._create_distribution_plot(selected_exp_data, selected_metrics)
            elif self.current_plot_type == "time_series":
                self._create_time_series_plot(selected_exp_data, selected_metrics)
            elif self.current_plot_type == "performance":
                self._create_performance_plot(selected_exp_data, selected_metrics)

            # Update canvas
            self.canvas.draw()

            # Update statistics
            self._update_statistics(selected_exp_data, selected_metrics)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to create comparison: {str(e)}")
            logger.error(f"Failed to create comparison plot: {e}")

    def _create_comparison_plot(
        self, experiments: List[ExperimentResult], metrics: List[str]
    ):
        """Create a comparison bar plot."""
        if len(metrics) == 0:
            return

        # Create subplots
        n_metrics = len(metrics)
        n_cols = min(3, n_metrics)
        n_rows = (n_metrics + n_cols - 1) // n_cols

        for i, metric in enumerate(metrics):
            ax = self.figure.add_subplot(n_rows, n_cols, i + 1)

            # Collect data for this metric
            experiment_names = []
            values = []

            for exp in experiments:
                value = exp.get_metric(metric)
                if value is not None:
                    experiment_names.append(exp.name)
                    values.append(float(value))

            if values:
                # Create bar plot
                bars = ax.bar(experiment_names, values)

                # Add value labels on bars
                for bar, value in zip(bars, values):
                    height = bar.get_height()
                    ax.text(
                        bar.get_x() + bar.get_width() / 2.0,
                        height,
                        f"{value:.3f}",
                        ha="center",
                        va="bottom",
                    )

                ax.set_title(metric)
                ax.set_ylabel("Value")
                plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
            else:
                ax.text(
                    0.5,
                    0.5,
                    f"No data for {metric}",
                    transform=ax.transAxes,
                    ha="center",
                    va="center",
                )

        self.figure.tight_layout()

    def _create_correlation_plot(
        self, experiments: List[ExperimentResult], metrics: List[str]
    ):
        """Create a correlation heatmap."""
        if len(metrics) < 2:
            messagebox.showwarning("Warning", "Need at least 2 metrics for correlation")
            return

        # Collect all data
        all_data = {}
        for metric in metrics:
            values = []
            for exp in experiments:
                value = exp.get_metric(metric)
                if value is not None:
                    values.append(float(value))
            all_data[metric] = values

        # Create correlation matrix
        df = pd.DataFrame(all_data)
        correlation_matrix = df.corr()

        # Create heatmap
        ax = self.figure.add_subplot(111)

        if SEABORN_AVAILABLE:
            sns.heatmap(
                correlation_matrix, annot=True, cmap="coolwarm", center=0, ax=ax
            )
        else:
            # Fallback to matplotlib
            im = ax.imshow(
                correlation_matrix, cmap="coolwarm", aspect="auto", vmin=-1, vmax=1
            )
            ax.set_xticks(range(len(metrics)))
            ax.set_yticks(range(len(metrics)))
            ax.set_xticklabels(metrics, rotation=45, ha="right")
            ax.set_yticklabels(metrics)

            # Add text annotations
            for i in range(len(metrics)):
                for j in range(len(metrics)):
                    ax.text(
                        j,
                        i,
                        f"{correlation_matrix.iloc[i, j]:.2f}",
                        ha="center",
                        va="center",
                        color="black",
                    )

            self.figure.colorbar(im, ax=ax)

        ax.set_title("Correlation Matrix")
        self.figure.tight_layout()
        self.canvas.configure(bg="white")  # fix widget configure parameters

    def _create_distribution_plot(
        self, experiments: List[ExperimentResult], metrics: List[str]
    ):
        """Create distribution plots."""
        if len(metrics) == 0:
            return

        # Create subplots
        n_metrics = len(metrics)
        n_cols = min(2, n_metrics)
        n_rows = (n_metrics + n_cols - 1) // n_cols

        for i, metric in enumerate(metrics):
            ax = self.figure.add_subplot(n_rows, n_cols, i + 1)

            # Collect data for this metric
            all_values = []
            labels = []

            for exp in experiments:
                value = exp.get_metric(metric)
                if value is not None:
                    all_values.append(float(value))
                    labels.append(exp.name)

            if all_values:
                # Create box plot
                ax.boxplot(all_values, labels=labels)
                ax.set_title(f"Distribution of {metric}")
                ax.set_ylabel("Value")
                plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
            else:
                ax.text(
                    0.5,
                    0.5,
                    f"No data for {metric}",
                    transform=ax.transAxes,
                    ha="center",
                    va="center",
                )

        self.figure.tight_layout()

    def _create_time_series_plot(
        self, experiments: List[ExperimentResult], metrics: List[str]
    ):
        """Create time series plots."""
        # This is a placeholder - real time series data would need timestamps
        messagebox.showinfo("Info", "Time series plotting requires timestamped data")

    def _create_performance_plot(
        self, experiments: List[ExperimentResult], metrics: List[str]
    ):
        """Create performance comparison plots."""
        if len(metrics) == 0:
            return

        # Create radar/spider plot for performance comparison
        ax = self.figure.add_subplot(111, projection="polar")

        # Normalize metrics to 0-1 scale
        normalized_data = {}
        for metric in metrics:
            values = []
            for exp in experiments:
                value = exp.get_metric(metric)
                if value is not None:
                    values.append(float(value))

            if values:
                min_val, max_val = min(values), max(values)
                if max_val > min_val:
                    normalized = [(v - min_val) / (max_val - min_val) for v in values]
                else:
                    normalized = [1.0] * len(values)
                normalized_data[metric] = normalized

        if normalized_data:
            # Create radar plot
            angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
            angles += angles[:1]  # Complete the circle

            for i, exp in enumerate(experiments):
                values = []
                for metric in metrics:
                    if metric in normalized_data and i < len(normalized_data[metric]):
                        values.append(normalized_data[metric][i])
                    else:
                        values.append(0)

                values += values[:1]  # Complete the circle

                ax.plot(angles, values, "o-", linewidth=2, label=exp.name)
                ax.fill(angles, values, alpha=0.25)

            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(metrics)
            ax.set_ylim(0, 1)
            ax.set_title("Performance Comparison")
            ax.legend()

        self.figure.tight_layout()

    def _update_statistics(
        self, experiments: List[ExperimentResult], metrics: List[str]
    ):
        """Update the statistical analysis."""
        self.stats_text.delete(1.0, tk.END)

        if not experiments:
            self.stats_text.insert(tk.END, "No experiments selected for analysis\n")
            return

        # Basic statistics
        self.stats_text.insert(tk.END, "=== Basic Statistics ===\n\n")

        for metric in metrics:
            values = []
            for exp in experiments:
                value = exp.get_metric(metric)
                if value is not None:
                    values.append(float(value))

            if values:
                mean_val = np.mean(values)
                std_val = np.std(values)
                min_val = min(values)
                max_val = max(values)

                self.stats_text.insert(tk.END, f"{metric}:\n")
                self.stats_text.insert(tk.END, f"  Mean: {mean_val:.4f}\n")
                self.stats_text.insert(tk.END, f"  Std:  {std_val:.4f}\n")
                self.stats_text.insert(tk.END, f"  Min:  {min_val:.4f}\n")
                self.stats_text.insert(tk.END, f"  Max:  {max_val:.4f}\n\n")

        # Statistical tests
        test_type = self.stats_var.get()
        if test_type != "none" and SCIPY_AVAILABLE and len(experiments) >= 2:
            self.stats_text.insert(tk.END, f"=== {test_type} Test ===\n\n")

            for metric in metrics:
                values_by_exp = []
                for exp in experiments:
                    value = exp.get_metric(metric)
                    if value is not None:
                        values_by_exp.append([float(value)])

                if len(values_by_exp) >= 2:
                    try:
                        if test_type == "t-test" and len(values_by_exp) == 2:
                            stat, p_value = stats.ttest_ind(
                                values_by_exp[0], values_by_exp[1]
                            )
                        elif test_type == "ANOVA":
                            stat, p_value = stats.f_oneway(*values_by_exp)
                        elif test_type == "Mann-Whitney U" and len(values_by_exp) == 2:
                            stat, p_value = stats.mannwhitneyu(
                                values_by_exp[0], values_by_exp[1]
                            )
                        elif test_type == "Kruskal-Wallis":
                            stat, p_value = stats.kruskal(*values_by_exp)
                        else:
                            continue

                        self.stats_text.insert(tk.END, f"{metric}:\n")
                        self.stats_text.insert(tk.END, f"  Statistic: {stat:.4f}\n")
                        self.stats_text.insert(tk.END, f"  p-value:   {p_value:.4f}\n")

                        if p_value < 0.05:
                            self.stats_text.insert(
                                tk.END, "  Result: Significant difference\n"
                            )
                        else:
                            self.stats_text.insert(
                                tk.END, "  Result: No significant difference\n"
                            )
                        self.stats_text.insert(tk.END, "\n")

                    except Exception as e:
                        self.stats_text.insert(
                            tk.END,
                            f"{metric}: Error in statistical test - {str(e)}\n\n",
                        )

    def _export_results(self):
        """Export comparison results."""
        if not self.selected_experiments:
            messagebox.showwarning("Warning", "No experiments selected")
            return

        file_path = filedialog.asksaveasfilename(
            title="Export Comparison Results",
            defaultextension=".json",
            filetypes=[
                ("JSON files", "*.json"),
                ("CSV files", "*.csv"),
                ("All files", "*.*"),
            ],
        )

        if not file_path:
            return

        try:
            # Prepare export data
            export_data = {
                "comparison_info": {
                    "timestamp": datetime.now().isoformat(),
                    "selected_experiments": self.selected_experiments,
                    "plot_type": self.current_plot_type,
                    "statistical_test": self.stats_var.get(),
                },
                "experiments": [],
            }

            # Add experiment data
            for exp in self.experiments:
                if exp.name in self.selected_experiments:
                    export_data["experiments"].append(
                        {
                            "name": exp.name,
                            "data": exp.data,
                            "parameters": exp.parameters,
                            "metadata": exp.metadata,
                            "timestamp": exp.timestamp.isoformat(),
                        }
                    )

            # Save based on file extension
            if file_path.endswith(".csv"):
                # Export as CSV (flattened)
                df_data = []
                for exp in self.experiments:
                    if exp.name in self.selected_experiments:
                        row = {"experiment": exp.name}
                        row.update(exp.data)
                        row.update(exp.parameters)
                        df_data.append(row)

                df = pd.DataFrame(df_data)
                df.to_csv(file_path, index=False)
            else:
                # Export as JSON
                with open(file_path, "w") as f:
                    json.dump(export_data, f, indent=2)

            messagebox.showinfo("Success", f"Results exported to {file_path}")
            logger.info(f"Comparison results exported to {file_path}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to export results: {str(e)}")
            logger.error(f"Failed to export comparison results: {e}")


def create_comparison_dashboard(parent: tk.Widget) -> ComparisonDashboard:
    """
    Convenience function to create a comparison dashboard.

    Args:
        parent: Parent widget

    Returns:
        ComparisonDashboard instance
    """
    return ComparisonDashboard(parent)
