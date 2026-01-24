"""
Dash/Streamlit integration for APGI Framework GUI applications.

Provides web-based dashboard capabilities with interactive visualizations,
real-time updates, and seamless integration with existing GUI components.
"""

import json
import threading
import time
import queue
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Check for optional dependencies
DASH_AVAILABLE = False
STREAMLIT_AVAILABLE = False

try:
    import dash
    from dash import dcc, html, Input, Output, State, callback
    import dash_bootstrap_components as dbc
    import plotly.graph_objs as go
    import plotly.express as px
    from dash.exceptions import PreventUpdate

    DASH_AVAILABLE = True
except ImportError:
    logger.warning(
        "Dash not available - install with: pip install dash dash-bootstrap-components plotly"
    )

try:
    import streamlit as st
    import pandas as pd

    STREAMLIT_AVAILABLE = True
except ImportError:
    logger.warning(
        "Streamlit not available - install with: pip install streamlit pandas"
    )


@dataclass
class DashboardConfig:
    """Configuration for web dashboard."""

    title: str = "APGI Framework Dashboard"
    port: int = 8050
    host: str = "127.0.0.1"
    debug: bool = False
    auto_open_browser: bool = True
    theme: str = "bootstrap"  # bootstrap, cyborg, darkly, etc.
    update_interval: int = 1000  # milliseconds


class DataProvider:
    """Base class for data providers for web dashboards."""

    def __init__(self):
        self.data_cache: Dict[str, Any] = {}
        self.last_update: Dict[str, datetime] = {}
        self.update_callbacks: List[Callable] = []

    def get_data(self, data_type: str, **kwargs) -> Any:
        """Get data of specified type."""
        raise NotImplementedError("Subclasses must implement get_data")

    def update_data(self, data_type: str, data: Any):
        """Update cached data."""
        self.data_cache[data_type] = data
        self.last_update[data_type] = datetime.now()

        # Notify callbacks
        for callback in self.update_callbacks:
            try:
                callback(data_type, data)
            except Exception as e:
                logger.error(f"Data provider callback error: {e}")

    def add_update_callback(self, callback: Callable):
        """Add callback for data updates."""
        self.update_callbacks.append(callback)


class APGIDataProvider(DataProvider):
    """Data provider for APGI Framework experiment data."""

    def __init__(self):
        super().__init__()
        self.experiment_results: List[Dict[str, Any]] = []
        self.real_time_data: Dict[str, Any] = {}
        self.system_status: Dict[str, Any] = {}

    def get_data(self, data_type: str, **kwargs) -> Any:
        """Get APGI-specific data."""
        if data_type == "experiments":
            return self.experiment_results
        elif data_type == "real_time":
            return self.real_time_data
        elif data_type == "system_status":
            return self.system_status
        elif data_type == "experiment_summary":
            return self._get_experiment_summary()
        elif data_type == "performance_metrics":
            return self._get_performance_metrics()
        else:
            return self.data_cache.get(data_type)

    def _get_experiment_summary(self) -> Dict[str, Any]:
        """Get experiment summary statistics."""
        if not self.experiment_results:
            return {"total": 0, "successful": 0, "failed": 0}

        total = len(self.experiment_results)
        successful = sum(
            1 for exp in self.experiment_results if exp.get("status") == "success"
        )
        failed = total - successful

        return {
            "total": total,
            "successful": successful,
            "failed": failed,
            "success_rate": successful / total if total > 0 else 0,
        }

    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        if not self.experiment_results:
            return {}

        # Extract performance data
        durations = [
            exp.get("duration", 0)
            for exp in self.experiment_results
            if exp.get("duration")
        ]

        if not durations:
            return {}

        return {
            "avg_duration": sum(durations) / len(durations),
            "min_duration": min(durations),
            "max_duration": max(durations),
            "total_experiments": len(durations),
        }

    def add_experiment_result(self, result: Dict[str, Any]):
        """Add a new experiment result."""
        self.experiment_results.append(result)
        self.update_data("experiments", self.experiment_results)

    def update_real_time_data(self, data: Dict[str, Any]):
        """Update real-time data."""
        self.real_time_data.update(data)
        self.update_data("real_time", self.real_time_data)

    def update_system_status(self, status: Dict[str, Any]):
        """Update system status."""
        self.system_status.update(status)
        self.update_data("system_status", self.system_status)


class DashDashboard:
    """
    Dash-based web dashboard for APGI Framework.

    Provides interactive visualizations, real-time updates, and
    comprehensive experiment monitoring.
    """

    def __init__(self, config: DashboardConfig, data_provider: DataProvider):
        if not DASH_AVAILABLE:
            raise ImportError(
                "Dash is not available. Install with: pip install dash dash-bootstrap-components plotly"
            )

        self.config = config
        self.data_provider = data_provider
        self.app = None
        self.server_thread: Optional[threading.Thread] = None
        self.is_running = False

        self._create_app()

    def _create_app(self):
        """Create the Dash application."""
        # Configure external stylesheets
        external_stylesheets = [dbc.themes.BOOTSTRAP]

        # Create Dash app
        self.app = dash.Dash(
            __name__, external_stylesheets=external_stylesheets, title=self.config.title
        )

        # Set layout
        self.app.layout = self._create_layout()

        # Setup callbacks
        self._setup_callbacks()

    def _create_layout(self) -> html.Div:
        """Create the dashboard layout."""
        return dbc.Container(
            [
                # Header
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.H1(
                                    self.config.title, className="text-primary mb-4"
                                ),
                                html.Hr(),
                            ]
                        )
                    ]
                ),
                # Control Panel
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardBody(
                                            [
                                                html.H5(
                                                    "Control Panel",
                                                    className="card-title",
                                                ),
                                                dbc.Row(
                                                    [
                                                        dbc.Col(
                                                            [
                                                                dbc.Button(
                                                                    "Refresh Data",
                                                                    id="refresh-btn",
                                                                    color="primary",
                                                                    className="me-2",
                                                                ),
                                                                dbc.Button(
                                                                    "Export Results",
                                                                    id="export-btn",
                                                                    color="secondary",
                                                                ),
                                                            ],
                                                            width=6,
                                                        ),
                                                        dbc.Col(
                                                            [
                                                                dcc.Interval(
                                                                    id="interval-component",
                                                                    interval=self.config.update_interval,
                                                                    n_intervals=0,
                                                                )
                                                            ],
                                                            width=6,
                                                        ),
                                                    ]
                                                ),
                                            ]
                                        )
                                    ],
                                    className="mb-4",
                                )
                            ],
                            width=12,
                        )
                    ]
                ),
                # Summary Cards
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardBody(
                                            [
                                                html.H4(
                                                    "Total Experiments",
                                                    className="card-title",
                                                ),
                                                html.H2(
                                                    id="total-experiments", children="0"
                                                ),
                                            ]
                                        )
                                    ]
                                )
                            ],
                            width=3,
                        ),
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardBody(
                                            [
                                                html.H4(
                                                    "Success Rate",
                                                    className="card-title",
                                                ),
                                                html.H2(
                                                    id="success-rate", children="0%"
                                                ),
                                            ]
                                        )
                                    ]
                                )
                            ],
                            width=3,
                        ),
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardBody(
                                            [
                                                html.H4(
                                                    "Avg Duration",
                                                    className="card-title",
                                                ),
                                                html.H2(
                                                    id="avg-duration", children="0s"
                                                ),
                                            ]
                                        )
                                    ]
                                )
                            ],
                            width=3,
                        ),
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardBody(
                                            [
                                                html.H4(
                                                    "System Status",
                                                    className="card-title",
                                                ),
                                                html.H2(
                                                    id="system-status",
                                                    children="🟢 Online",
                                                ),
                                            ]
                                        )
                                    ]
                                )
                            ],
                            width=3,
                        ),
                    ],
                    className="mb-4",
                ),
                # Charts Row
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardBody(
                                            [
                                                html.H5(
                                                    "Experiment Timeline",
                                                    className="card-title",
                                                ),
                                                dcc.Graph(id="timeline-chart"),
                                            ]
                                        )
                                    ]
                                )
                            ],
                            width=6,
                        ),
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardBody(
                                            [
                                                html.H5(
                                                    "Performance Metrics",
                                                    className="card-title",
                                                ),
                                                dcc.Graph(id="performance-chart"),
                                            ]
                                        )
                                    ]
                                )
                            ],
                            width=6,
                        ),
                    ],
                    className="mb-4",
                ),
                # Data Table
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardBody(
                                            [
                                                html.H5(
                                                    "Experiment Results",
                                                    className="card-title",
                                                ),
                                                html.Div(id="experiment-table"),
                                            ]
                                        )
                                    ]
                                )
                            ],
                            width=12,
                        )
                    ]
                ),
            ],
            fluid=True,
        )

    def _setup_callbacks(self):
        """Setup Dash callbacks."""

        @self.app.callback(
            [
                Output("total-experiments", "children"),
                Output("success-rate", "children"),
                Output("avg-duration", "children"),
                Output("system-status", "children"),
            ],
            [
                Input("interval-component", "n_intervals"),
                Input("refresh-btn", "n_clicks"),
            ],
        )
        def update_summary(n_intervals, n_clicks):
            """Update summary cards."""
            try:
                # Get experiment summary
                summary = self.data_provider.get_data("experiment_summary")

                total = summary.get("total", 0)
                success_rate = summary.get("success_rate", 0) * 100

                # Get performance metrics
                perf = self.data_provider.get_data("performance_metrics")
                avg_duration = perf.get("avg_duration", 0)

                # Get system status
                system_status = self.data_provider.get_data("system_status")
                status_text = (
                    "🟢 Online" if system_status.get("online", True) else "🔴 Offline"
                )

                return (
                    str(total),
                    f"{success_rate:.1f}%",
                    f"{avg_duration:.1f}s",
                    status_text,
                )

            except Exception as e:
                logger.error(f"Error updating summary: {e}")
                return "Error", "Error", "Error", "Error"

        @self.app.callback(
            Output("timeline-chart", "figure"),
            [
                Input("interval-component", "n_intervals"),
                Input("refresh-btn", "n_clicks"),
            ],
        )
        def update_timeline(n_intervals, n_clicks):
            """Update timeline chart."""
            try:
                experiments = self.data_provider.get_data("experiments")

                if not experiments:
                    return go.Figure()

                # Create timeline data
                timestamps = [exp.get("timestamp", "") for exp in experiments]
                statuses = [exp.get("status", "unknown") for exp in experiments]

                # Create scatter plot
                fig = go.Figure()

                for status in set(statuses):
                    status_data = [
                        (i, ts)
                        for i, (ts, s) in enumerate(zip(timestamps, statuses))
                        if s == status
                    ]
                    if status_data:
                        indices, times = zip(*status_data)
                        fig.add_trace(
                            go.Scatter(
                                x=times,
                                y=[status] * len(times),
                                mode="markers",
                                name=status.capitalize(),
                                marker=dict(size=8),
                            )
                        )

                fig.update_layout(
                    title="Experiment Timeline",
                    xaxis_title="Time",
                    yaxis_title="Status",
                    height=300,
                )

                return fig

            except Exception as e:
                logger.error(f"Error updating timeline: {e}")
                return go.Figure()

        @self.app.callback(
            Output("performance-chart", "figure"),
            [
                Input("interval-component", "n_intervals"),
                Input("refresh-btn", "n_clicks"),
            ],
        )
        def update_performance(n_intervals, n_clicks):
            """Update performance chart."""
            try:
                experiments = self.data_provider.get_data("experiments")

                if not experiments:
                    return go.Figure()

                # Extract performance data
                durations = [
                    exp.get("duration", 0) for exp in experiments if exp.get("duration")
                ]

                if not durations:
                    return go.Figure()

                # Create histogram
                fig = go.Figure(data=[go.Histogram(x=durations, nbinsx=20)])

                fig.update_layout(
                    title="Experiment Duration Distribution",
                    xaxis_title="Duration (seconds)",
                    yaxis_title="Count",
                    height=300,
                )

                return fig

            except Exception as e:
                logger.error(f"Error updating performance chart: {e}")
                return go.Figure()

        @self.app.callback(
            Output("experiment-table", "children"),
            [
                Input("interval-component", "n_intervals"),
                Input("refresh-btn", "n_clicks"),
            ],
        )
        def update_table(n_intervals, n_clicks):
            """Update experiment table."""
            try:
                experiments = self.data_provider.get_data("experiments")

                if not experiments:
                    return html.P("No experiments to display")

                # Create table data
                table_data = []
                for exp in experiments[-10:]:  # Show last 10 experiments
                    table_data.append(
                        html.Tr(
                            [
                                html.Td(exp.get("name", "Unknown")),
                                html.Td(exp.get("status", "Unknown")),
                                html.Td(f"{exp.get('duration', 0):.2f}s"),
                                html.Td(exp.get("timestamp", "")),
                            ]
                        )
                    )

                return dbc.Table(
                    [
                        html.Thead(
                            [
                                html.Tr(
                                    [
                                        html.Th("Name"),
                                        html.Th("Status"),
                                        html.Th("Duration"),
                                        html.Th("Timestamp"),
                                    ]
                                )
                            ]
                        ),
                        html.Tbody(table_data),
                    ],
                    striped=True,
                    bordered=True,
                    hover=True,
                    size="sm",
                )

            except Exception as e:
                logger.error(f"Error updating table: {e}")
                return html.P("Error loading data")

    def start_server(self):
        """Start the Dash server."""
        if self.is_running:
            logger.warning("Dash server is already running")
            return

        def run_server():
            try:
                self.app.run_server(
                    host=self.config.host,
                    port=self.config.port,
                    debug=self.config.debug,
                    use_reloader=False,
                )
            except Exception as e:
                logger.error(f"Dash server error: {e}")

        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        self.is_running = True

        logger.info(
            f"Dash dashboard started at http://{self.config.host}:{self.config.port}"
        )

        if self.config.auto_open_browser:
            import webbrowser

            webbrowser.open(f"http://{self.config.host}:{self.config.port}")

    def stop_server(self):
        """Stop the Dash server."""
        # Dash doesn't have a clean stop mechanism, but we can set the flag
        self.is_running = False
        logger.info("Dash server stopped")


class StreamlitDashboard:
    """
    Streamlit-based web dashboard for APGI Framework.

    Provides simple, fast web dashboard with minimal setup.
    """

    def __init__(self, data_provider: DataProvider):
        if not STREAMLIT_AVAILABLE:
            raise ImportError(
                "Streamlit is not available. Install with: pip install streamlit pandas"
            )

        self.data_provider = data_provider

    def run(self):
        """Run the Streamlit dashboard."""
        # This would typically be called from a separate streamlit script
        self._create_streamlit_app()

    def _create_streamlit_app(self):
        """Create the Streamlit application."""
        st.set_page_config(
            page_title="APGI Framework Dashboard", page_icon="🧪", layout="wide"
        )

        st.title("🧪 APGI Framework Dashboard")

        # Sidebar controls
        st.sidebar.header("Controls")

        if st.sidebar.button("Refresh Data"):
            st.rerun()

        if st.sidebar.button("Export Results"):
            st.info("Export functionality would be implemented here")

        # Main content
        self._show_summary_cards()

        st.markdown("---")

        # Charts
        col1, col2 = st.columns(2)

        with col1:
            self._show_timeline_chart()

        with col2:
            self._show_performance_chart()

        # Data table
        st.markdown("---")
        self._show_experiment_table()

    def _show_summary_cards(self):
        """Show summary cards."""
        summary = self.data_provider.get_data("experiment_summary")
        perf = self.data_provider.get_data("performance_metrics")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Experiments", summary.get("total", 0))

        with col2:
            success_rate = summary.get("success_rate", 0) * 100
            st.metric("Success Rate", f"{success_rate:.1f}%")

        with col3:
            avg_duration = perf.get("avg_duration", 0)
            st.metric("Avg Duration", f"{avg_duration:.1f}s")

        with col4:
            system_status = self.data_provider.get_data("system_status")
            status_text = (
                "🟢 Online" if system_status.get("online", True) else "🔴 Offline"
            )
            st.metric("System Status", status_text)

    def _show_timeline_chart(self):
        """Show timeline chart."""
        experiments = self.data_provider.get_data("experiments")

        if not experiments:
            st.info("No experiment data available")
            return

        # Create DataFrame
        df = pd.DataFrame(experiments)

        if "timestamp" in df.columns and "status" in df.columns:
            # Create timeline chart
            st.subheader("Experiment Timeline")

            # Simple scatter plot using matplotlib (Streamlit compatible)
            import matplotlib.pyplot as plt

            fig, ax = plt.subplots(figsize=(10, 4))

            for status in df["status"].unique():
                status_data = df[df["status"] == status]
                ax.scatter(
                    status_data.index,
                    [status] * len(status_data),
                    label=status.capitalize(),
                    alpha=0.7,
                )

            ax.set_xlabel("Experiment Index")
            ax.set_ylabel("Status")
            ax.set_title("Experiment Timeline")
            ax.legend()

            st.pyplot(fig)
            plt.close()

    def _show_performance_chart(self):
        """Show performance chart."""
        experiments = self.data_provider.get_data("experiments")

        if not experiments:
            st.info("No performance data available")
            return

        durations = [
            exp.get("duration", 0) for exp in experiments if exp.get("duration")
        ]

        if not durations:
            st.info("No duration data available")
            return

        st.subheader("Performance Distribution")

        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.hist(durations, bins=20, alpha=0.7, edgecolor="black")
        ax.set_xlabel("Duration (seconds)")
        ax.set_ylabel("Count")
        ax.set_title("Experiment Duration Distribution")

        st.pyplot(fig)
        plt.close()

    def _show_experiment_table(self):
        """Show experiment table."""
        experiments = self.data_provider.get_data("experiments")

        if not experiments:
            st.info("No experiments to display")
            return

        st.subheader("Recent Experiments")

        # Create DataFrame for display
        df_data = []
        for exp in experiments[-10:]:  # Show last 10
            df_data.append(
                {
                    "Name": exp.get("name", "Unknown"),
                    "Status": exp.get("status", "Unknown"),
                    "Duration": f"{exp.get('duration', 0):.2f}s",
                    "Timestamp": exp.get("timestamp", ""),
                }
            )

        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True)


class WebDashboardManager:
    """
    Manager for web dashboard integration.

    Provides unified interface for both Dash and Streamlit dashboards
    with automatic data synchronization.
    """

    def __init__(self):
        self.data_provider = APGIDataProvider()
        self.dash_dashboard: Optional[DashDashboard] = None
        self.streamlit_dashboard: Optional[StreamlitDashboard] = None
        self.active_dashboards: List[str] = []

    def create_dash_dashboard(
        self, config: Optional[DashboardConfig] = None
    ) -> DashDashboard:
        """Create a Dash dashboard."""
        if config is None:
            config = DashboardConfig()

        self.dash_dashboard = DashDashboard(config, self.data_provider)
        self.active_dashboards.append("dash")

        return self.dash_dashboard

    def create_streamlit_dashboard(self) -> StreamlitDashboard:
        """Create a Streamlit dashboard."""
        self.streamlit_dashboard = StreamlitDashboard(self.data_provider)
        self.active_dashboards.append("streamlit")

        return self.streamlit_dashboard

    def get_data_provider(self) -> APGIDataProvider:
        """Get the data provider for updating dashboard data."""
        return self.data_provider

    def start_all_dashboards(self):
        """Start all created dashboards."""
        if self.dash_dashboard:
            self.dash_dashboard.start_server()

        if self.streamlit_dashboard:
            # Streamlit runs in its own process
            logger.info(
                "Streamlit dashboard available - run with: streamlit run dashboard_script.py"
            )

    def stop_all_dashboards(self):
        """Stop all dashboards."""
        if self.dash_dashboard:
            self.dash_dashboard.stop_server()

        self.active_dashboards.clear()


def create_web_dashboard_manager() -> WebDashboardManager:
    """
    Convenience function to create a web dashboard manager.

    Returns:
        WebDashboardManager instance
    """
    return WebDashboardManager()
