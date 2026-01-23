"""
Help System and Feature Discovery for APGI Framework

Provides comprehensive help documentation, feature tours, and interactive
guidance for users to discover and learn framework capabilities.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from typing import Dict, List, Optional, Any, Callable, Tuple
from pathlib import Path
import json
import webbrowser
from dataclasses import dataclass
from enum import Enum


class TourStepType(Enum):
    """Types of tour steps."""

    HIGHLIGHT = "highlight"
    TOOLTIP = "tooltip"
    MODAL = "modal"
    ACTION = "action"


@dataclass
class TourStep:
    """Represents a step in a feature tour."""

    id: str
    title: str
    content: str
    step_type: TourStepType
    target_widget: Optional[str] = None  # Widget identifier
    position: Optional[Tuple[int, int]] = None  # Screen position
    action: Optional[str] = None  # Action to perform
    next_step: Optional[str] = None
    prev_step: Optional[str] = None
    conditions: Optional[Dict[str, Any]] = None


@dataclass
class FeatureTour:
    """Represents a complete feature tour."""

    id: str
    name: str
    description: str
    steps: List[TourStep]
    category: str = "general"
    difficulty: str = "beginner"  # beginner, intermediate, advanced
    estimated_time: int = 5  # minutes


class HelpContent:
    """Manages help content and documentation."""

    def __init__(self):
        self.content = self._load_default_content()

    def _load_default_content(self) -> Dict[str, Any]:
        """Load default help content."""
        return {
            "getting_started": {
                "title": "Getting Started with APGI Framework",
                "content": """
                <h2>Welcome to the APGI Framework!</h2>
                
                <p>The Active Predictive Global Ignition (APGI) Framework is a comprehensive 
                platform for consciousness research and cognitive modeling.</p>
                
                <h3>Quick Start Guide</h3>
                <ol>
                    <li><strong>Choose an Experiment:</strong> Select from pre-built experiments 
                    or create your own custom paradigm.</li>
                    <li><strong>Configure Parameters:</strong> Set up experimental parameters 
                    including threshold values, precision parameters, and trial counts.</li>
                    <li><strong>Run Experiment:</strong> Execute the experiment and monitor 
                    real-time progress.</li>
                    <li><strong>Analyze Results:</strong> Use built-in analysis tools to 
                    examine parameter estimates and statistical outcomes.</li>
                    <li><strong>Generate Reports:</strong> Create comprehensive PDF reports 
                    of your findings.</li>
                </ol>
                
                <h3>Key Concepts</h3>
                <ul>
                    <li><strong>Ignition Threshold (θ):</strong> The threshold for conscious access</li>
                    <li><strong>Precision Parameters (Π):</strong> Reliability of sensory information</li>
                    <li><strong>Somatic Markers:</strong> Interoceptive signals influencing cognition</li>
                </ul>
                """,
                "keywords": ["start", "begin", "introduction", "overview"],
            },
            "experiments": {
                "title": "Running Experiments",
                "content": """
                <h2>Experimental Paradigms</h2>
                
                <p>The APGI Framework supports multiple experimental paradigms for testing 
                consciousness theories:</p>
                
                <h3>Available Experiments</h3>
                <ul>
                    <li><strong>Threshold Detection:</strong> Basic consciousness threshold measurement</li>
                    <li><strong>Attentional Blink:</strong> Temporal attention limitations</li>
                    <li><strong>Masking Paradigms:</strong> Visual consciousness suppression</li>
                    <li><strong>Binocular Rivalry:</strong> Perceptual competition</li>
                    <li><strong>Change Blindness:</strong> Attention and awareness</li>
                </ul>
                
                <h3>Parameter Configuration</h3>
                <p>Each experiment can be customized with:</p>
                <ul>
                    <li>Number of participants and trials</li>
                    <li>Stimulus parameters</li>
                    <li>Response collection methods</li>
                    <li>Analysis preferences</li>
                </ul>
                """,
                "keywords": ["experiment", "paradigm", "run", "execute", "trial"],
            },
            "analysis": {
                "title": "Data Analysis",
                "content": """
                <h2>Statistical Analysis Tools</h2>
                
                <p>The framework provides comprehensive analysis capabilities:</p>
                
                <h3>Parameter Estimation</h3>
                <ul>
                    <li>Bayesian parameter fitting</li>
                    <li>Maximum likelihood estimation</li>
                    <li>Confidence interval calculation</li>
                    <li>Model comparison metrics</li>
                </ul>
                
                <h3>Statistical Tests</h3>
                <ul>
                    <li>Hypothesis testing</li>
                    <li>Effect size calculation</li>
                    <li>Power analysis</li>
                    <li>Multiple comparison correction</li>
                </ul>
                
                <h3>Visualization</h3>
                <ul>
                    <li>Parameter distribution plots</li>
                    <li>Time series analysis</li>
                    <li>Correlation matrices</li>
                    <li>Interactive dashboards</li>
                </ul>
                """,
                "keywords": ["analysis", "statistics", "parameter", "bayesian", "plot"],
            },
            "neural_data": {
                "title": "Neural Data Processing",
                "content": """
                <h2>Neural Signal Processing</h2>
                
                <p>Process and analyze neural signals to validate APGI predictions:</p>
                
                <h3>Supported Data Types</h3>
                <ul>
                    <li><strong>EEG:</strong> Event-related potentials (P3b, N400)</li>
                    <li><strong>Pupillometry:</strong> Autonomic arousal measurement</li>
                    <li><strong>Cardiac:</strong> Heart rate variability analysis</li>
                    <li><strong>Behavioral:</strong> Response times and accuracy</li>
                </ul>
                
                <h3>Processing Pipeline</h3>
                <ol>
                    <li>Data import and validation</li>
                    <li>Preprocessing and filtering</li>
                    <li>Artifact detection and removal</li>
                    <li>Feature extraction</li>
                    <li>Statistical analysis</li>
                </ol>
                """,
                "keywords": [
                    "neural",
                    "eeg",
                    "pupil",
                    "cardiac",
                    "signal",
                    "processing",
                ],
            },
            "troubleshooting": {
                "title": "Troubleshooting",
                "content": """
                <h2>Common Issues and Solutions</h2>
                
                <h3>Installation Problems</h3>
                <ul>
                    <li><strong>Missing dependencies:</strong> Run 'pip install -r requirements.txt'</li>
                    <li><strong>Python version:</strong> Ensure Python 3.8+ is installed</li>
                    <li><strong>Permission errors:</strong> Run with administrator privileges</li>
                </ul>
                
                <h3>Experiment Issues</h3>
                <ul>
                    <li><strong>Slow performance:</strong> Reduce trial count or enable GPU acceleration</li>
                    <li><strong>Memory errors:</strong> Process data in smaller batches</li>
                    <li><strong>Convergence problems:</strong> Adjust optimization parameters</li>
                </ul>
                
                <h3>Data Analysis Problems</h3>
                <ul>
                    <li><strong>Parameter estimation fails:</strong> Check data quality and format</li>
                    <li><strong>Visualization errors:</strong> Update matplotlib and dependencies</li>
                    <li><strong>Export issues:</strong> Verify file permissions and disk space</li>
                </ul>
                
                <h3>Getting Help</h3>
                <p>If you continue to experience issues:</p>
                <ul>
                    <li>Check the documentation at docs/</li>
                    <li>Review example scripts in examples/</li>
                    <li>Contact support or file an issue</li>
                </ul>
                """,
                "keywords": [
                    "problem",
                    "error",
                    "issue",
                    "troubleshoot",
                    "help",
                    "support",
                ],
            },
        }

    def search_content(self, query: str) -> List[Dict[str, Any]]:
        """Search help content by keywords."""
        query = query.lower()
        results = []

        for content_id, content_data in self.content.items():
            # Search in title
            if query in content_data["title"].lower():
                results.append(
                    {
                        "id": content_id,
                        "title": content_data["title"],
                        "relevance": 1.0,
                        "match_type": "title",
                    }
                )
                continue

            # Search in keywords
            keywords = content_data.get("keywords", [])
            for keyword in keywords:
                if query in keyword.lower():
                    results.append(
                        {
                            "id": content_id,
                            "title": content_data["title"],
                            "relevance": 0.8,
                            "match_type": "keyword",
                        }
                    )
                    break

            # Search in content
            if query in content_data["content"].lower():
                results.append(
                    {
                        "id": content_id,
                        "title": content_data["title"],
                        "relevance": 0.6,
                        "match_type": "content",
                    }
                )

        # Sort by relevance
        results.sort(key=lambda x: x["relevance"], reverse=True)
        return results

    def get_content(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get specific help content."""
        return self.content.get(content_id)


class FeatureTourManager:
    """Manages feature tours and guided walkthroughs."""

    def __init__(self):
        self.tours = self._create_default_tours()
        self.current_tour = None
        self.current_step = None
        self.tour_widgets = {}  # Store tour UI elements

    def _create_default_tours(self) -> Dict[str, FeatureTour]:
        """Create default feature tours."""
        tours = {}

        # Basic Interface Tour
        basic_tour = FeatureTour(
            id="basic_interface",
            name="Basic Interface Tour",
            description="Learn the main interface components and basic navigation",
            category="getting_started",
            difficulty="beginner",
            estimated_time=3,
            steps=[
                TourStep(
                    id="welcome",
                    title="Welcome to APGI Framework",
                    content="This tour will introduce you to the main interface components. Click Next to continue.",
                    step_type=TourStepType.MODAL,
                    next_step="main_menu",
                ),
                TourStep(
                    id="main_menu",
                    title="Main Menu",
                    content="This is the main menu where you can access different experiments and tools.",
                    step_type=TourStepType.HIGHLIGHT,
                    target_widget="main_menu",
                    next_step="parameter_panel",
                    prev_step="welcome",
                ),
                TourStep(
                    id="parameter_panel",
                    title="Parameter Configuration",
                    content="Use this panel to configure experimental parameters like threshold values and trial counts.",
                    step_type=TourStepType.HIGHLIGHT,
                    target_widget="parameter_panel",
                    next_step="results_area",
                    prev_step="main_menu",
                ),
                TourStep(
                    id="results_area",
                    title="Results Display",
                    content="Experimental results and visualizations appear in this area.",
                    step_type=TourStepType.HIGHLIGHT,
                    target_widget="results_area",
                    next_step="complete",
                    prev_step="parameter_panel",
                ),
                TourStep(
                    id="complete",
                    title="Tour Complete",
                    content="You've completed the basic interface tour! You can now start exploring the framework.",
                    step_type=TourStepType.MODAL,
                    prev_step="results_area",
                ),
            ],
        )
        tours[basic_tour.id] = basic_tour

        # Experiment Setup Tour
        experiment_tour = FeatureTour(
            id="experiment_setup",
            name="Running Your First Experiment",
            description="Learn how to set up and run an APGI experiment",
            category="experiments",
            difficulty="beginner",
            estimated_time=5,
            steps=[
                TourStep(
                    id="select_experiment",
                    title="Select Experiment Type",
                    content="Choose from available experiment paradigms. We'll start with a basic threshold detection task.",
                    step_type=TourStepType.HIGHLIGHT,
                    target_widget="experiment_selector",
                    action="select_threshold_detection",
                    next_step="configure_params",
                ),
                TourStep(
                    id="configure_params",
                    title="Configure Parameters",
                    content="Set the number of participants, trials, and other experimental parameters.",
                    step_type=TourStepType.HIGHLIGHT,
                    target_widget="parameter_config",
                    next_step="run_experiment",
                    prev_step="select_experiment",
                ),
                TourStep(
                    id="run_experiment",
                    title="Run the Experiment",
                    content="Click the Run button to start the experiment. You can monitor progress in real-time.",
                    step_type=TourStepType.HIGHLIGHT,
                    target_widget="run_button",
                    action="click_run",
                    next_step="view_results",
                    prev_step="configure_params",
                ),
                TourStep(
                    id="view_results",
                    title="View Results",
                    content="Once complete, results will appear here including parameter estimates and statistical tests.",
                    step_type=TourStepType.HIGHLIGHT,
                    target_widget="results_display",
                    next_step="export_results",
                    prev_step="run_experiment",
                ),
                TourStep(
                    id="export_results",
                    title="Export Results",
                    content="You can export results to various formats including PDF reports and CSV data files.",
                    step_type=TourStepType.HIGHLIGHT,
                    target_widget="export_button",
                    prev_step="view_results",
                ),
            ],
        )
        tours[experiment_tour.id] = experiment_tour

        return tours

    def get_available_tours(self) -> List[FeatureTour]:
        """Get list of available tours."""
        return list(self.tours.values())

    def start_tour(self, tour_id: str, parent_widget) -> bool:
        """Start a feature tour."""
        if tour_id not in self.tours:
            return False

        self.current_tour = self.tours[tour_id]
        self.current_step = (
            self.current_tour.steps[0] if self.current_tour.steps else None
        )
        self.parent_widget = parent_widget

        if self.current_step:
            self._show_step(self.current_step)

        return True

    def next_step(self):
        """Move to the next step in the tour."""
        if not self.current_step or not self.current_step.next_step:
            self._end_tour()
            return

        next_step_id = self.current_step.next_step
        next_step = next(
            (s for s in self.current_tour.steps if s.id == next_step_id), None
        )

        if next_step:
            self._hide_current_step()
            self.current_step = next_step
            self._show_step(self.current_step)

    def prev_step(self):
        """Move to the previous step in the tour."""
        if not self.current_step or not self.current_step.prev_step:
            return

        prev_step_id = self.current_step.prev_step
        prev_step = next(
            (s for s in self.current_tour.steps if s.id == prev_step_id), None
        )

        if prev_step:
            self._hide_current_step()
            self.current_step = prev_step
            self._show_step(self.current_step)

    def _show_step(self, step: TourStep):
        """Show a tour step."""
        if step.step_type == TourStepType.MODAL:
            self._show_modal_step(step)
        elif step.step_type == TourStepType.HIGHLIGHT:
            self._show_highlight_step(step)
        elif step.step_type == TourStepType.TOOLTIP:
            self._show_tooltip_step(step)
        elif step.step_type == TourStepType.ACTION:
            self._perform_action_step(step)

    def _show_modal_step(self, step: TourStep):
        """Show a modal dialog step."""
        dialog = tk.Toplevel(self.parent_widget)
        dialog.title(step.title)
        dialog.geometry("400x300")
        dialog.resizable(False, False)

        # Make modal
        dialog.transient(self.parent_widget)
        dialog.grab_set()

        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - dialog.winfo_reqwidth()) // 2
        y = (dialog.winfo_screenheight() - dialog.winfo_reqheight()) // 2
        dialog.geometry(f"+{x}+{y}")

        # Content frame
        content_frame = ttk.Frame(dialog, padding=20)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(
            content_frame, text=step.title, font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(0, 10))

        # Content
        content_text = tk.Text(content_frame, wrap=tk.WORD, height=8, width=40)
        content_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        content_text.insert(tk.END, step.content)
        content_text.config(state=tk.DISABLED)

        # Buttons
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill=tk.X)

        if step.prev_step:
            ttk.Button(
                button_frame,
                text="Previous",
                command=lambda: [dialog.destroy(), self.prev_step()],
            ).pack(side=tk.LEFT)

        if step.next_step:
            ttk.Button(
                button_frame,
                text="Next",
                command=lambda: [dialog.destroy(), self.next_step()],
            ).pack(side=tk.RIGHT)
        else:
            ttk.Button(
                button_frame,
                text="Finish",
                command=lambda: [dialog.destroy(), self._end_tour()],
            ).pack(side=tk.RIGHT)

        ttk.Button(
            button_frame,
            text="Skip Tour",
            command=lambda: [dialog.destroy(), self._end_tour()],
        ).pack(side=tk.RIGHT, padx=(0, 10))

        self.tour_widgets["modal"] = dialog

    def _show_highlight_step(self, step: TourStep):
        """Show a highlight overlay step."""
        # This would create an overlay highlighting the target widget
        # For now, we'll show a simple tooltip-like popup
        self._show_tooltip_step(step)

    def _show_tooltip_step(self, step: TourStep):
        """Show a tooltip-style step."""
        tooltip = tk.Toplevel(self.parent_widget)
        tooltip.wm_overrideredirect(True)
        tooltip.configure(bg="lightyellow", relief="solid", borderwidth=1)

        # Content
        frame = ttk.Frame(tooltip, padding=10)
        frame.pack()

        title_label = ttk.Label(frame, text=step.title, font=("Arial", 10, "bold"))
        title_label.pack()

        content_label = ttk.Label(frame, text=step.content, wraplength=250)
        content_label.pack(pady=(5, 10))

        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack()

        if step.prev_step:
            ttk.Button(button_frame, text="◀", width=3, command=self.prev_step).pack(
                side=tk.LEFT, padx=2
            )

        if step.next_step:
            ttk.Button(button_frame, text="▶", width=3, command=self.next_step).pack(
                side=tk.LEFT, padx=2
            )
        else:
            ttk.Button(button_frame, text="✓", width=3, command=self._end_tour).pack(
                side=tk.LEFT, padx=2
            )

        ttk.Button(button_frame, text="✕", width=3, command=self._end_tour).pack(
            side=tk.LEFT, padx=2
        )

        # Position tooltip
        if step.position:
            x, y = step.position
        else:
            x = self.parent_widget.winfo_rootx() + 100
            y = self.parent_widget.winfo_rooty() + 100

        tooltip.geometry(f"+{x}+{y}")

        self.tour_widgets["tooltip"] = tooltip

    def _perform_action_step(self, step: TourStep):
        """Perform an action step."""
        # This would perform automated actions
        # For now, just move to next step
        if step.next_step:
            self.next_step()
        else:
            self._end_tour()

    def _hide_current_step(self):
        """Hide the current step UI elements."""
        for widget_type, widget in self.tour_widgets.items():
            if widget and widget.winfo_exists():
                widget.destroy()
        self.tour_widgets.clear()

    def _end_tour(self):
        """End the current tour."""
        self._hide_current_step()
        self.current_tour = None
        self.current_step = None


class HelpSystemUI:
    """Main help system UI component."""

    def __init__(self, parent):
        self.parent = parent
        self.help_content = HelpContent()
        self.tour_manager = FeatureTourManager()

        # Create help window
        self.help_window = None

    def show_help_window(self):
        """Show the main help window."""
        if self.help_window and self.help_window.winfo_exists():
            self.help_window.lift()
            return

        self.help_window = tk.Toplevel(self.parent)
        self.help_window.title("APGI Framework Help")
        self.help_window.geometry("800x600")

        # Create notebook for different help sections
        notebook = ttk.Notebook(self.help_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Help content tab
        self._create_help_content_tab(notebook)

        # Feature tours tab
        self._create_tours_tab(notebook)

        # Quick reference tab
        self._create_quick_reference_tab(notebook)

    def _create_help_content_tab(self, notebook):
        """Create the help content tab."""
        content_frame = ttk.Frame(notebook)
        notebook.add(content_frame, text="Help Topics")

        # Search frame
        search_frame = ttk.Frame(content_frame)
        search_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)

        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=(5, 0))
        search_entry.bind("<Return>", self._search_help)

        ttk.Button(search_frame, text="Search", command=self._search_help).pack(
            side=tk.LEFT, padx=5
        )

        # Content area
        content_paned = ttk.PanedWindow(content_frame, orient=tk.HORIZONTAL)
        content_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Topic list
        list_frame = ttk.Frame(content_paned)
        content_paned.add(list_frame, weight=1)

        ttk.Label(list_frame, text="Help Topics").pack()

        self.topic_listbox = tk.Listbox(list_frame)
        self.topic_listbox.pack(fill=tk.BOTH, expand=True)
        self.topic_listbox.bind("<<ListboxSelect>>", self._on_topic_select)

        # Populate topics
        for content_id, content_data in self.help_content.content.items():
            self.topic_listbox.insert(tk.END, content_data["title"])

        # Content display
        display_frame = ttk.Frame(content_paned)
        content_paned.add(display_frame, weight=2)

        ttk.Label(display_frame, text="Content").pack()

        # HTML-like text widget (simplified)
        self.content_text = tk.Text(display_frame, wrap=tk.WORD, state=tk.DISABLED)
        content_scrollbar = ttk.Scrollbar(
            display_frame, orient=tk.VERTICAL, command=self.content_text.yview
        )
        self.content_text.configure(yscrollcommand=content_scrollbar.set)

        self.content_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        content_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _create_tours_tab(self, notebook):
        """Create the feature tours tab."""
        tours_frame = ttk.Frame(notebook)
        notebook.add(tours_frame, text="Feature Tours")

        # Tours list
        tours_list_frame = ttk.LabelFrame(
            tours_frame, text="Available Tours", padding=10
        )
        tours_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Tour selection
        for tour in self.tour_manager.get_available_tours():
            tour_frame = ttk.Frame(tours_list_frame)
            tour_frame.pack(fill=tk.X, pady=5)

            # Tour info
            info_frame = ttk.Frame(tour_frame)
            info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

            title_label = ttk.Label(
                info_frame, text=tour.name, font=("Arial", 12, "bold")
            )
            title_label.pack(anchor=tk.W)

            desc_label = ttk.Label(info_frame, text=tour.description)
            desc_label.pack(anchor=tk.W)

            meta_label = ttk.Label(
                info_frame,
                text=f"Difficulty: {tour.difficulty.title()} | Time: ~{tour.estimated_time} min",
            )
            meta_label.pack(anchor=tk.W)

            # Start button
            ttk.Button(
                tour_frame,
                text="Start Tour",
                command=lambda t=tour: self._start_tour(t.id),
            ).pack(side=tk.RIGHT, padx=(10, 0))

    def _create_quick_reference_tab(self, notebook):
        """Create the quick reference tab."""
        ref_frame = ttk.Frame(notebook)
        notebook.add(ref_frame, text="Quick Reference")

        # Keyboard shortcuts
        shortcuts_frame = ttk.LabelFrame(
            ref_frame, text="Keyboard Shortcuts", padding=10
        )
        shortcuts_frame.pack(fill=tk.X, padx=10, pady=5)

        shortcuts = [
            ("Ctrl+N", "New Experiment"),
            ("Ctrl+O", "Open File"),
            ("Ctrl+S", "Save Results"),
            ("Ctrl+R", "Run Experiment"),
            ("F1", "Show Help"),
            ("F5", "Refresh Data"),
            ("Ctrl+Q", "Quit Application"),
        ]

        for shortcut, description in shortcuts:
            shortcut_frame = ttk.Frame(shortcuts_frame)
            shortcut_frame.pack(fill=tk.X, pady=2)

            ttk.Label(shortcut_frame, text=shortcut, font=("Courier", 10)).pack(
                side=tk.LEFT, width=15
            )
            ttk.Label(shortcut_frame, text=description).pack(side=tk.LEFT)

        # Parameter reference
        params_frame = ttk.LabelFrame(ref_frame, text="Key Parameters", padding=10)
        params_frame.pack(fill=tk.X, padx=10, pady=5)

        parameters = [
            ("θ₀", "Ignition threshold", "Controls conscious access threshold"),
            (
                "Πₑ",
                "Exteroceptive precision",
                "Reliability of external sensory information",
            ),
            ("Πᵢ", "Interoceptive precision", "Reliability of internal bodily signals"),
            ("β", "Somatic marker weight", "Influence of interoceptive signals"),
        ]

        for symbol, name, description in parameters:
            param_frame = ttk.Frame(params_frame)
            param_frame.pack(fill=tk.X, pady=2)

            ttk.Label(param_frame, text=symbol, font=("Arial", 12, "bold")).pack(
                side=tk.LEFT, width=5
            )
            ttk.Label(param_frame, text=f"{name}: {description}").pack(side=tk.LEFT)

    def _search_help(self, event=None):
        """Search help content."""
        query = self.search_var.get().strip()
        if not query:
            return

        results = self.help_content.search_content(query)

        # Clear and populate listbox with results
        self.topic_listbox.delete(0, tk.END)

        if results:
            for result in results:
                self.topic_listbox.insert(
                    tk.END, f"{result['title']} ({result['match_type']})"
                )
        else:
            self.topic_listbox.insert(tk.END, "No results found")

    def _on_topic_select(self, event):
        """Handle topic selection."""
        selection = self.topic_listbox.curselection()
        if not selection:
            return

        # Get selected topic (simplified - would need better mapping in real implementation)
        topic_text = self.topic_listbox.get(selection[0])

        # Find matching content
        for content_id, content_data in self.help_content.content.items():
            if content_data["title"] in topic_text:
                self._display_content(content_data["content"])
                break

    def _display_content(self, content: str):
        """Display help content (simplified HTML rendering)."""
        self.content_text.config(state=tk.NORMAL)
        self.content_text.delete(1.0, tk.END)

        # Simple HTML-to-text conversion
        import re

        # Remove HTML tags but keep structure
        content = re.sub(
            r"<h[1-6]>(.*?)</h[1-6]>", r"\n\1\n" + "=" * 50 + "\n", content
        )
        content = re.sub(r"<h3>(.*?)</h3>", r"\n\1\n" + "-" * 30 + "\n", content)
        content = re.sub(r"<li>(.*?)</li>", r"• \1\n", content)
        content = re.sub(r"<strong>(.*?)</strong>", r"\1", content)
        content = re.sub(r"<[^>]+>", "", content)  # Remove remaining tags

        self.content_text.insert(tk.END, content)
        self.content_text.config(state=tk.DISABLED)

    def _start_tour(self, tour_id: str):
        """Start a feature tour."""
        success = self.tour_manager.start_tour(tour_id, self.parent)
        if success:
            # Close help window during tour
            if self.help_window:
                self.help_window.withdraw()
        else:
            messagebox.showerror("Error", f"Could not start tour: {tour_id}")

    def show_context_help(self, widget_name: str):
        """Show context-sensitive help for a specific widget."""
        # This would show help specific to the current context
        help_text = f"Help for {widget_name}\n\nThis feature provides..."

        tooltip = tk.Toplevel(self.parent)
        tooltip.wm_overrideredirect(True)
        tooltip.configure(bg="lightyellow", relief="solid", borderwidth=1)

        label = ttk.Label(tooltip, text=help_text, background="lightyellow", padding=10)
        label.pack()

        # Position near mouse
        x = self.parent.winfo_pointerx() + 10
        y = self.parent.winfo_pointery() + 10
        tooltip.geometry(f"+{x}+{y}")

        # Auto-hide after 5 seconds
        tooltip.after(5000, tooltip.destroy)


# Convenience functions
def create_help_system(parent) -> HelpSystemUI:
    """Create a help system UI."""
    return HelpSystemUI(parent)


def show_quick_help(parent, topic: str = "getting_started"):
    """Show quick help for a specific topic."""
    help_system = HelpSystemUI(parent)
    help_system.show_help_window()
    # Would focus on specific topic
