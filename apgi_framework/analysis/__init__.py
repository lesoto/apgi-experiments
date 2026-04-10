"""
Analysis components for the APGI Framework.

This module contains statistical analysis tools, validation frameworks,
and reporting capabilities for comprehensive APGI falsification testing.
"""

from .analysis_engine import (
    AnalysisEngine,
    AnalysisResult,
)
from .bayesian_models import (
    HierarchicalBayesianModel,
    IgnitionProbabilityCalculator,
    ParameterDistribution,
    ParameterEstimates,
    StanModelCompiler,
    SurpriseAccumulator,
)
from .effect_size_calculator import (
    BootstrapResult,
    ConfidenceIntervalMethod,
    EffectSizeCalculator,
    EffectSizeResult,
    EffectSizeType,
    get_effect_size_guidelines,
)
from .parameter_estimation import (
    ConvergenceDiagnostics,
    ConvergenceDiagnosticsCalculator,
    FitResults,
    IndividualParameterEstimator,
    JointParameterFitter,
    ParameterExtractor,
)
from .parameter_recovery import (
    GroundTruthParameters,
    ParameterRecoveryValidator,
    RecoveryAnalyzer,
    RecoveryMetrics,
    RecoveryResults,
    SyntheticDataGenerator,
    ValidationReportGenerator,
)
from .predictive_validity import (
    BodyVigilanceScaleAnalyzer,
    ComparativeValidityResult,
    ContinuousPerformanceTask,
    EmotionalInterferenceTask,
    PredictivePowerComparator,
    PredictiveValidityFramework,
    TaskPerformance,
    ValidityResult,
)
from .replication_tracker import (
    ExperimentResult,
    PowerAnalysisMethod,
    PowerAnalysisResult,
    PowerAnalyzer,
    ReplicationStatus,
    ReplicationSummary,
    ReplicationTracker,
)
from .sample_size_validator import (
    PowerReport,
    SampleSizeRequirement,
    SampleSizeValidator,
    TestRequirement,
    ValidationResult,
    ValidationStatus,
)
from .statistical_report_generator import (
    FalsificationAssessment,
    FalsificationConclusion,
    PublicationReport,
    ReportFormat,
    StatisticalReportGenerator,
    StatisticalSummary,
)
from .statistical_tester import (
    ClusterCorrectionResult,
    CorrectionMethod,
    StatisticalResult,
    StatisticalTester,
    TestType,
)


# Mock classes for testing
class StatisticalAnalyzer:
    """Mock statistical analyzer for testing purposes."""

    def __init__(self):
        self.analysis_results = {}

    def analyze_results(self, data):
        """Analyze experimental results."""
        analysis_id = f"analysis_{hash(str(data)) % 10000:04d}"
        result = {
            "analysis_id": analysis_id,
            "statistical_significance": True,
            "confidence_interval": [0.01, 0.05],
            "recommendation": "reject_null_hypothesis",
            "p_value": 0.03,
            "effect_size": "medium",
            "data": data,
            "timestamp": "2024-01-01T00:00:00Z",
        }
        self.analysis_results[analysis_id] = result
        return result

    def get_analysis(self, analysis_id):
        """Get analysis result by ID."""
        return self.analysis_results.get(analysis_id)


class ProgressiveAnalyzer:
    """Mock progressive analyzer for testing purposes."""

    def __init__(self):
        self.analysis_steps = []
        self.current_step = 0

    def add_analysis_step(self, step_data):
        """Add an analysis step."""
        step_id = f"step_{len(self.analysis_steps)}"
        step = {
            "step_id": step_id,
            "step_data": step_data,
            "completed": False,
            "timestamp": "2024-01-01T00:00:00Z",
        }
        self.analysis_steps.append(step)
        return step

    def complete_step(self, step_id):
        """Mark an analysis step as completed."""
        for step in self.analysis_steps:
            if step["step_id"] == step_id:
                step["completed"] = True
                break

    def get_progress(self):
        """Get analysis progress."""
        completed = sum(1 for step in self.analysis_steps if step["completed"])
        return {
            "total_steps": len(self.analysis_steps),
            "completed_steps": completed,
            "progress_percentage": (
                (completed / len(self.analysis_steps) * 100)
                if self.analysis_steps
                else 0
            ),
        }


class ReplicationChecker:
    """Mock replication checker for testing purposes."""

    def __init__(self):
        self.replication_results = {}

    def check_replication(self, original_result, replication_result):
        """Check if results replicate successfully."""
        replication_id = (
            f"rep_{hash(str(original_result) + str(replication_result)) % 10000:04d}"
        )
        result = {
            "replication_id": replication_id,
            "original_result": original_result,
            "replication_result": replication_result,
            "replication_successful": True,
            "effect_size_similarity": 0.95,
            "p_value_consistency": 0.88,
            "timestamp": "2024-01-01T00:00:00Z",
        }
        self.replication_results[replication_id] = result
        return result


class CrossModalAnalyzer:
    """Mock cross-modal analyzer for testing purposes."""

    def __init__(self):
        self.modal_analyses = {}

    def analyze_cross_modal(self, modality1_data, modality2_data):
        """Analyze cross-modal relationships."""
        analysis_id = (
            f"cross_{hash(str(modality1_data) + str(modality2_data)) % 10000:04d}"
        )
        result = {
            "analysis_id": analysis_id,
            "modality1": modality1_data,
            "modality2": modality2_data,
            "correlation": 0.75,
            "cross_modal_consistency": 0.82,
            "integration_score": 0.79,
            "timestamp": "2024-01-01T00:00:00Z",
        }
        self.modal_analyses[analysis_id] = result
        return result


__all__ = [
    # Statistical Testing
    "StatisticalTester",
    "StatisticalResult",
    "TestType",
    "CorrectionMethod",
    "ClusterCorrectionResult",
    # Effect Size Calculation
    "EffectSizeCalculator",
    "EffectSizeResult",
    "BootstrapResult",
    "EffectSizeType",
    "ConfidenceIntervalMethod",
    "get_effect_size_guidelines",
    # Replication and Power Analysis
    "ReplicationTracker",
    "PowerAnalyzer",
    "ExperimentResult",
    "ReplicationSummary",
    "PowerAnalysisResult",
    "ReplicationStatus",
    "PowerAnalysisMethod",
    # Sample Size Validation
    "SampleSizeValidator",
    "ValidationResult",
    "PowerReport",
    "ValidationStatus",
    "TestRequirement",
    "SampleSizeRequirement",
    # Report Generation
    "StatisticalReportGenerator",
    "StatisticalSummary",
    "PublicationReport",
    "FalsificationAssessment",
    "FalsificationConclusion",
    "ReportFormat",
    # Bayesian Modeling
    "HierarchicalBayesianModel",
    "SurpriseAccumulator",
    "IgnitionProbabilityCalculator",
    "StanModelCompiler",
    "ParameterDistribution",
    "ParameterEstimates",
    # Parameter Estimation Pipeline
    "JointParameterFitter",
    "ParameterExtractor",
    "ConvergenceDiagnosticsCalculator",
    "IndividualParameterEstimator",
    "ConvergenceDiagnostics",
    "FitResults",
    # Parameter Recovery Validation
    "SyntheticDataGenerator",
    "ParameterRecoveryValidator",
    "RecoveryAnalyzer",
    "ValidationReportGenerator",
    "GroundTruthParameters",
    "RecoveryMetrics",
    "RecoveryResults",
    # Predictive Validity Testing
    "EmotionalInterferenceTask",
    "ContinuousPerformanceTask",
    "BodyVigilanceScaleAnalyzer",
    "PredictivePowerComparator",
    "PredictiveValidityFramework",
    "TaskPerformance",
    "ValidityResult",
    "ComparativeValidityResult",
    # Analysis Engine
    "AnalysisEngine",
    "AnalysisResult",
    # Mock classes for testing
    "StatisticalAnalyzer",
    "ProgressiveAnalyzer",
    "ReplicationChecker",
    "CrossModalAnalyzer",
]
