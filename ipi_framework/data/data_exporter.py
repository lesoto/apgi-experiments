"""
Data Export and Visualization System for IPI Framework

This module provides multi-format data export capabilities and publication-quality
plotting and figure generation for falsification test results.
"""

import csv
import json
import h5py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any, Optional, Union, Tuple
from pathlib import Path
from datetime import datetime
import logging
from dataclasses import asdict

from ..core.data_models import (
    FalsificationResult, ExperimentalTrial, StatisticalSummary,
    IPIParameters, NeuralSignatures, ConsciousnessAssessment
)
from ..exceptions import DataExportError


class DataExporter:
    """
    Handles multi-format data export (CSV, JSON, HDF5) for experimental results.
    """
    
    def __init__(self, output_dir: str = "exports"):
        """
        Initialize the data exporter.
        
        Args:
            output_dir: Directory to save exported data
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)
    
    def export_falsification_results(
        self,
        results: List[FalsificationResult],
        format: str = "csv",
        filename: Optional[str] = None
    ) -> str:
        """
        Export falsification results to specified format.
        
        Args:
            results: List of falsification results
            format: Export format ("csv", "json", "hdf5")
            filename: Optional custom filename
            
        Returns:
            Path to exported file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"falsification_results_{timestamp}"
        
        try:
            if format == "csv":
                return self._export_results_csv(results, filename)
            elif format == "json":
                return self._export_results_json(results, filename)
            elif format == "hdf5":
                return self._export_results_hdf5(results, filename)
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            raise DataExportError(f"Failed to export falsification results: {str(e)}")
    
    def export_experimental_trials(
        self,
        trials: List[ExperimentalTrial],
        format: str = "csv",
        filename: Optional[str] = None
    ) -> str:
        """
        Export experimental trials to specified format.
        
        Args:
            trials: List of experimental trials
            format: Export format ("csv", "json", "hdf5")
            filename: Optional custom filename
            
        Returns:
            Path to exported file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"experimental_trials_{timestamp}"
        
        try:
            if format == "csv":
                return self._export_trials_csv(trials, filename)
            elif format == "json":
                return self._export_trials_json(trials, filename)
            elif format == "hdf5":
                return self._export_trials_hdf5(trials, filename)
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            raise DataExportError(f"Failed to export experimental trials: {str(e)}")
    
    def _export_results_csv(self, results: List[FalsificationResult], filename: str) -> str:
        """Export falsification results to CSV"""
        filepath = self.output_dir / f"{filename}.csv"
        
        # Convert results to flat dictionary format
        rows = []
        for result in results:
            row = {
                'test_type': result.test_type,
                'is_falsified': result.is_falsified,
                'confidence_level': result.confidence_level,
                'effect_size': result.effect_size,
                'p_value': result.p_value,
                'statistical_power': result.statistical_power,
                'replication_count': result.replication_count
            }
            
            # Add detailed results as separate columns
            if result.detailed_results:
                for key, value in result.detailed_results.items():
                    if isinstance(value, (int, float, str, bool)):
                        row[f'detail_{key}'] = value
            
            rows.append(row)
        
        # Write to CSV
        if rows:
            with open(filepath, 'w', newline='') as csvfile:
                fieldnames = rows[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
        
        self.logger.info(f"Exported {len(results)} falsification results to {filepath}")
        return str(filepath)
    
    def _export_results_json(self, results: List[FalsificationResult], filename: str) -> str:
        """Export falsification results to JSON"""
        filepath = self.output_dir / f"{filename}.json"
        
        # Convert to serializable format
        data = {
            'export_timestamp': datetime.now().isoformat(),
            'total_results': len(results),
            'results': [asdict(result) for result in results]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        self.logger.info(f"Exported {len(results)} falsification results to {filepath}")
        return str(filepath)
    
    def _export_results_hdf5(self, results: List[FalsificationResult], filename: str) -> str:
        """Export falsification results to HDF5"""
        filepath = self.output_dir / f"{filename}.h5"
        
        with h5py.File(filepath, 'w') as f:
            # Create groups for different data types
            results_group = f.create_group('falsification_results')
            
            # Store metadata
            results_group.attrs['export_timestamp'] = datetime.now().isoformat()
            results_group.attrs['total_results'] = len(results)
            
            if results:
                # Convert to arrays for efficient storage
                test_types = [r.test_type.encode('utf-8') for r in results]
                is_falsified = [r.is_falsified for r in results]
                confidence_levels = [r.confidence_level for r in results]
                effect_sizes = [r.effect_size for r in results]
                p_values = [r.p_value for r in results]
                statistical_powers = [r.statistical_power for r in results]
                replication_counts = [r.replication_count for r in results]
                
                # Store arrays
                results_group.create_dataset('test_types', data=test_types)
                results_group.create_dataset('is_falsified', data=is_falsified)
                results_group.create_dataset('confidence_levels', data=confidence_levels)
                results_group.create_dataset('effect_sizes', data=effect_sizes)
                results_group.create_dataset('p_values', data=p_values)
                results_group.create_dataset('statistical_powers', data=statistical_powers)
                results_group.create_dataset('replication_counts', data=replication_counts)
        
        self.logger.info(f"Exported {len(results)} falsification results to {filepath}")
        return str(filepath)
    
    def _export_trials_csv(self, trials: List[ExperimentalTrial], filename: str) -> str:
        """Export experimental trials to CSV"""
        filepath = self.output_dir / f"{filename}.csv"
        
        rows = []
        for trial in trials:
            row = {
                'trial_id': trial.trial_id,
                'participant_id': trial.participant_id,
                'condition': trial.condition,
                'timestamp': trial.timestamp.isoformat() if trial.timestamp else '',
                
                # IPI Parameters
                'extero_precision': trial.ipi_parameters.extero_precision,
                'intero_precision': trial.ipi_parameters.intero_precision,
                'extero_error': trial.ipi_parameters.extero_error,
                'intero_error': trial.ipi_parameters.intero_error,
                'somatic_gain': trial.ipi_parameters.somatic_gain,
                'threshold': trial.ipi_parameters.threshold,
                'steepness': trial.ipi_parameters.steepness,
                
                # Neural Signatures
                'p3b_amplitude': trial.neural_signatures.p3b_amplitude,
                'p3b_latency': trial.neural_signatures.p3b_latency,
                'gamma_plv': trial.neural_signatures.gamma_plv,
                'gamma_duration': trial.neural_signatures.gamma_duration,
                'pci_value': trial.neural_signatures.pci_value,
                
                # Consciousness Assessment
                'subjective_report': trial.consciousness_assessment.subjective_report,
                'forced_choice_accuracy': trial.consciousness_assessment.forced_choice_accuracy,
                'confidence_rating': trial.consciousness_assessment.confidence_rating,
                'wagering_behavior': trial.consciousness_assessment.wagering_behavior,
                'metacognitive_sensitivity': trial.consciousness_assessment.metacognitive_sensitivity
            }
            
            # Add BOLD activations as separate columns
            for region, activation in trial.neural_signatures.bold_activations.items():
                row[f'bold_{region}'] = activation
            
            rows.append(row)
        
        if rows:
            with open(filepath, 'w', newline='') as csvfile:
                fieldnames = rows[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
        
        self.logger.info(f"Exported {len(trials)} experimental trials to {filepath}")
        return str(filepath)
    
    def _export_trials_json(self, trials: List[ExperimentalTrial], filename: str) -> str:
        """Export experimental trials to JSON"""
        filepath = self.output_dir / f"{filename}.json"
        
        data = {
            'export_timestamp': datetime.now().isoformat(),
            'total_trials': len(trials),
            'trials': [asdict(trial) for trial in trials]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        self.logger.info(f"Exported {len(trials)} experimental trials to {filepath}")
        return str(filepath)
    
    def _export_trials_hdf5(self, trials: List[ExperimentalTrial], filename: str) -> str:
        """Export experimental trials to HDF5"""
        filepath = self.output_dir / f"{filename}.h5"
        
        with h5py.File(filepath, 'w') as f:
            trials_group = f.create_group('experimental_trials')
            trials_group.attrs['export_timestamp'] = datetime.now().isoformat()
            trials_group.attrs['total_trials'] = len(trials)
            
            if trials:
                # Create subgroups for different data types
                params_group = trials_group.create_group('ipi_parameters')
                neural_group = trials_group.create_group('neural_signatures')
                consciousness_group = trials_group.create_group('consciousness_assessment')
                
                # Extract and store parameter arrays
                extero_precisions = [t.ipi_parameters.extero_precision for t in trials]
                intero_precisions = [t.ipi_parameters.intero_precision for t in trials]
                extero_errors = [t.ipi_parameters.extero_error for t in trials]
                intero_errors = [t.ipi_parameters.intero_error for t in trials]
                somatic_gains = [t.ipi_parameters.somatic_gain for t in trials]
                thresholds = [t.ipi_parameters.threshold for t in trials]
                steepnesses = [t.ipi_parameters.steepness for t in trials]
                
                params_group.create_dataset('extero_precisions', data=extero_precisions)
                params_group.create_dataset('intero_precisions', data=intero_precisions)
                params_group.create_dataset('extero_errors', data=extero_errors)
                params_group.create_dataset('intero_errors', data=intero_errors)
                params_group.create_dataset('somatic_gains', data=somatic_gains)
                params_group.create_dataset('thresholds', data=thresholds)
                params_group.create_dataset('steepnesses', data=steepnesses)
                
                # Extract and store neural signature arrays
                p3b_amplitudes = [t.neural_signatures.p3b_amplitude for t in trials]
                p3b_latencies = [t.neural_signatures.p3b_latency for t in trials]
                gamma_plvs = [t.neural_signatures.gamma_plv for t in trials]
                gamma_durations = [t.neural_signatures.gamma_duration for t in trials]
                pci_values = [t.neural_signatures.pci_value for t in trials]
                
                neural_group.create_dataset('p3b_amplitudes', data=p3b_amplitudes)
                neural_group.create_dataset('p3b_latencies', data=p3b_latencies)
                neural_group.create_dataset('gamma_plvs', data=gamma_plvs)
                neural_group.create_dataset('gamma_durations', data=gamma_durations)
                neural_group.create_dataset('pci_values', data=pci_values)
        
        self.logger.info(f"Exported {len(trials)} experimental trials to {filepath}")
        return str(filepath)