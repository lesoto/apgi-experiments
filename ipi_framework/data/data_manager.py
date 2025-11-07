"""
Integrated Data Management System for IPI Framework

This module provides a unified interface for all data management, reporting,
and visualization capabilities.
"""

from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import logging
from datetime import datetime

from ..core.data_models import (
    FalsificationResult, ExperimentalTrial, StatisticalSummary,
    IPIParameters, NeuralSignatures, ConsciousnessAssessment
)
from ..exceptions import DataManagementError

from .report_generator import ReportGenerator, FalsificationReport
from .data_exporter import DataExporter
from .visualizer import IPIVisualizer, InteractiveVisualizer
from .dashboard import DashboardServer, ExperimentMonitor


class IntegratedDataManager:
    """
    Unified data management system that coordinates all data operations.
    """
    
    def __init__(
        self,
        base_output_dir: str = "ipi_outputs",
        enable_dashboard: bool = True,
        dashboard_port: int = 8080
    ):
        """
        Initialize the integrated data manager.
        
        Args:
            base_output_dir: Base directory for all outputs
            enable_dashboard: Whether to enable the web dashboard
            dashboard_port: Port for the dashboard server
        """
        self.base_output_dir = Path(base_output_dir)
        self.base_output_dir.mkdir(exist_ok=True)
        
        # Initialize components
        self.report_generator = ReportGenerator(str(self.base_output_dir / "reports"))
        self.data_exporter = DataExporter(str(self.base_output_dir / "exports"))
        self.visualizer = IPIVisualizer(str(self.base_output_dir / "figures"))
        self.interactive_visualizer = InteractiveVisualizer()
        
        # Dashboard setup
        self.enable_dashboard = enable_dashboard
        if enable_dashboard:
            self.dashboard = DashboardServer(
                port=dashboard_port,
                data_dir=str(self.base_output_dir / "dashboard")
            )
            self.experiment_monitor = self.dashboard.monitor
        else:
            self.dashboard = None
            self.experiment_monitor = ExperimentMonitor()
        
        self.logger = logging.getLogger(__name__)
        
        # Active experiments tracking
        self.active_experiments = {}
    
    def start_system(self):
        """Start the data management system"""
        try:
            if self.enable_dashboard:
                self.dashboard.start_dashboard()
            else:
                self.experiment_monitor.start_monitoring()
            
            self.logger.info("Data management system started successfully")
            
        except Exception as e:
            raise DataManagementError(f"Failed to start data management system: {str(e)}")
    
    def stop_system(self):
        """Stop the data management system"""
        try:
            if self.enable_dashboard:
                self.dashboard.stop_dashboard()
            else:
                self.experiment_monitor.stop_monitoring()
            
            self.logger.info("Data management system stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping data management system: {str(e)}")
    
    def register_experiment(
        self,
        experiment_id: str,
        metadata: Dict[str, Any]
    ) -> str:
        """
        Register a new experiment for tracking and management.
        
        Args:
            experiment_id: Unique experiment identifier
            metadata: Experiment metadata
            
        Returns:
            Experiment ID
        """
        try:
            # Register with monitor
            self.experiment_monitor.register_experiment(experiment_id, metadata)
            
            # Track locally
            self.active_experiments[experiment_id] = {
                'metadata': metadata,
                'start_time': datetime.now(),
                'results': [],
                'trials': [],
                'reports': [],
                'exports': [],
                'figures': []
            }
            
            self.logger.info(f"Registered experiment {experiment_id}")
            return experiment_id
            
        except Exception as e:
            raise DataManagementError(f"Failed to register experiment: {str(e)}")
    
    def update_experiment_data(
        self,
        experiment_id: str,
        results: Optional[List[FalsificationResult]] = None,
        trials: Optional[List[ExperimentalTrial]] = None,
        current_trial: Optional[int] = None
    ):
        """
        Update experiment data and notify monitoring systems.
        
        Args:
            experiment_id: Experiment identifier
            results: New falsification results
            trials: New experimental trials
            current_trial: Current trial number
        """
        try:
            if experiment_id not in self.active_experiments:
                raise ValueError(f"Experiment {experiment_id} not registered")
            
            exp_data = self.active_experiments[experiment_id]
            
            # Update local data
            if results:
                exp_data['results'].extend(results)
            
            if trials:
                exp_data['trials'].extend(trials)
            
            # Update monitor
            if current_trial is not None:
                self.experiment_monitor.update_experiment_progress(
                    experiment_id, current_trial, results, trials
                )
            
            self.logger.debug(f"Updated data for experiment {experiment_id}")
            
        except Exception as e:
            raise DataManagementError(f"Failed to update experiment data: {str(e)}")
    
    def complete_experiment(self, experiment_id: str):
        """Mark experiment as completed"""
        try:
            if experiment_id in self.active_experiments:
                self.experiment_monitor.complete_experiment(experiment_id)
                self.logger.info(f"Completed experiment {experiment_id}")
            
        except Exception as e:
            raise DataManagementError(f"Failed to complete experiment: {str(e)}")
    
    def generate_comprehensive_report(
        self,
        experiment_id: str,
        statistical_summary: StatisticalSummary,
        formats: List[str] = None
    ) -> Dict[str, str]:
        """
        Generate comprehensive report for an experiment.
        
        Args:
            experiment_id: Experiment identifier
            statistical_summary: Statistical analysis summary
            formats: Report formats to generate
            
        Returns:
            Dictionary mapping format to file path
        """
        try:
            if experiment_id not in self.active_experiments:
                raise ValueError(f"Experiment {experiment_id} not registered")
            
            exp_data = self.active_experiments[experiment_id]
            results = exp_data['results']
            trials = exp_data['trials']
            
            if not results:
                raise ValueError(f"No results available for experiment {experiment_id}")
            
            # Generate report
            report = self.report_generator.generate_falsification_report(
                experiment_id, results, trials, statistical_summary
            )
            
            # Save in multiple formats
            if formats is None:
                formats = ["json", "txt", "html"]
            
            report_paths = {}
            for format in formats:
                path = self.report_generator.save_report(report, format)
                report_paths[format] = path
                exp_data['reports'].append(path)
            
            self.logger.info(f"Generated comprehensive report for experiment {experiment_id}")
            return report_paths
            
        except Exception as e:
            raise DataManagementError(f"Failed to generate comprehensive report: {str(e)}")
    
    def export_experiment_data(
        self,
        experiment_id: str,
        formats: List[str] = None
    ) -> Dict[str, Dict[str, str]]:
        """
        Export experiment data in multiple formats.
        
        Args:
            experiment_id: Experiment identifier
            formats: Export formats
            
        Returns:
            Dictionary mapping data type and format to file path
        """
        try:
            if experiment_id not in self.active_experiments:
                raise ValueError(f"Experiment {experiment_id} not registered")
            
            exp_data = self.active_experiments[experiment_id]
            results = exp_data['results']
            trials = exp_data['trials']
            
            if formats is None:
                formats = ["csv", "json", "hdf5"]
            
            export_paths = {
                'results': {},
                'trials': {}
            }
            
            # Export results
            if results:
                for format in formats:
                    path = self.data_exporter.export_falsification_results(
                        results, format, f"{experiment_id}_results"
                    )
                    export_paths['results'][format] = path
                    exp_data['exports'].append(path)
            
            # Export trials
            if trials:
                for format in formats:
                    path = self.data_exporter.export_experimental_trials(
                        trials, format, f"{experiment_id}_trials"
                    )
                    export_paths['trials'][format] = path
                    exp_data['exports'].append(path)
            
            self.logger.info(f"Exported data for experiment {experiment_id}")
            return export_paths
            
        except Exception as e:
            raise DataManagementError(f"Failed to export experiment data: {str(e)}")
    
    def generate_visualizations(
        self,
        experiment_id: str,
        statistical_summary: StatisticalSummary,
        create_publication_set: bool = True
    ) -> List[str]:
        """
        Generate visualizations for an experiment.
        
        Args:
            experiment_id: Experiment identifier
            statistical_summary: Statistical analysis summary
            create_publication_set: Whether to create publication-ready figure set
            
        Returns:
            List of paths to generated figures
        """
        try:
            if experiment_id not in self.active_experiments:
                raise ValueError(f"Experiment {experiment_id} not registered")
            
            exp_data = self.active_experiments[experiment_id]
            results = exp_data['results']
            trials = exp_data['trials']
            
            if not results or not trials:
                raise ValueError(f"Insufficient data for visualization in experiment {experiment_id}")
            
            figure_paths = []
            
            if create_publication_set:
                # Generate complete publication figure set
                pub_figures = self.visualizer.create_publication_figure_set(
                    results, trials, statistical_summary, experiment_id
                )
                figure_paths.extend(pub_figures)
            else:
                # Generate individual figures
                figures = [
                    self.visualizer.plot_falsification_summary(results),
                    self.visualizer.plot_neural_signatures(trials),
                    self.visualizer.plot_ipi_parameter_space(trials),
                    self.visualizer.plot_statistical_summary(statistical_summary)
                ]
                figure_paths.extend(figures)
            
            # Update experiment data
            exp_data['figures'].extend(figure_paths)
            
            self.logger.info(f"Generated {len(figure_paths)} visualizations for experiment {experiment_id}")
            return figure_paths
            
        except Exception as e:
            raise DataManagementError(f"Failed to generate visualizations: {str(e)}")
    
    def get_experiment_summary(self, experiment_id: str) -> Dict[str, Any]:
        """Get comprehensive experiment summary"""
        try:
            if experiment_id not in self.active_experiments:
                return {}
            
            exp_data = self.active_experiments[experiment_id]
            monitor_data = self.experiment_monitor.get_experiment_status(experiment_id)
            
            summary = {
                'experiment_id': experiment_id,
                'metadata': exp_data['metadata'],
                'start_time': exp_data['start_time'].isoformat(),
                'status': monitor_data.get('status', 'unknown'),
                'progress': monitor_data.get('progress', 0.0),
                'statistics': monitor_data.get('statistics', {}),
                'data_counts': {
                    'results': len(exp_data['results']),
                    'trials': len(exp_data['trials']),
                    'reports': len(exp_data['reports']),
                    'exports': len(exp_data['exports']),
                    'figures': len(exp_data['figures'])
                },
                'files': {
                    'reports': exp_data['reports'],
                    'exports': exp_data['exports'],
                    'figures': exp_data['figures']
                }
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting experiment summary: {str(e)}")
            return {}
    
    def get_all_experiments_summary(self) -> Dict[str, Dict[str, Any]]:
        """Get summary of all experiments"""
        return {
            exp_id: self.get_experiment_summary(exp_id)
            for exp_id in self.active_experiments.keys()
        }
    
    def cleanup_experiment(self, experiment_id: str, keep_files: bool = True):
        """
        Clean up experiment data and resources.
        
        Args:
            experiment_id: Experiment identifier
            keep_files: Whether to keep generated files
        """
        try:
            if experiment_id in self.active_experiments:
                exp_data = self.active_experiments[experiment_id]
                
                if not keep_files:
                    # Delete generated files
                    all_files = exp_data['reports'] + exp_data['exports'] + exp_data['figures']
                    
                    for file_path in all_files:
                        try:
                            Path(file_path).unlink(missing_ok=True)
                        except Exception as e:
                            self.logger.warning(f"Could not delete file {file_path}: {str(e)}")
                
                # Remove from tracking
                del self.active_experiments[experiment_id]
                
                self.logger.info(f"Cleaned up experiment {experiment_id}")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up experiment {experiment_id}: {str(e)}")
    
    def get_dashboard_url(self) -> Optional[str]:
        """Get dashboard URL if enabled"""
        if self.enable_dashboard and self.dashboard:
            return f"http://localhost:{self.dashboard.port}"
        return None


# Convenience function for easy setup
def create_data_manager(
    output_dir: str = "ipi_outputs",
    enable_dashboard: bool = True,
    dashboard_port: int = 8080
) -> IntegratedDataManager:
    """
    Create and configure an integrated data manager.
    
    Args:
        output_dir: Base output directory
        enable_dashboard: Whether to enable dashboard
        dashboard_port: Dashboard port
        
    Returns:
        Configured data manager
    """
    return IntegratedDataManager(
        base_output_dir=output_dir,
        enable_dashboard=enable_dashboard,
        dashboard_port=dashboard_port
    )