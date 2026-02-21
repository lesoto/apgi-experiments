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
]
