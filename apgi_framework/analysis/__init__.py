"""
Analysis components for the APGI Framework.

This module contains statistical analysis tools, validation frameworks,
and reporting capabilities for comprehensive APGI falsification testing.
"""

from .statistical_tester import (
    StatisticalTester,
    StatisticalResult,
    TestType,
    CorrectionMethod,
    ClusterCorrectionResult
)

from .effect_size_calculator import (
    EffectSizeCalculator,
    EffectSizeResult,
    BootstrapResult,
    EffectSizeType,
    ConfidenceIntervalMethod,
    get_effect_size_guidelines
)

from .replication_tracker import (
    ReplicationTracker,
    PowerAnalyzer,
    ExperimentResult,
    ReplicationSummary,
    PowerAnalysisResult,
    ReplicationStatus,
    PowerAnalysisMethod
)

from .sample_size_validator import (
    SampleSizeValidator,
    ValidationResult,
    PowerReport,
    ValidationStatus,
    TestRequirement,
    SampleSizeRequirement
)

from .statistical_report_generator import (
    StatisticalReportGenerator,
    StatisticalSummary,
    PublicationReport,
    FalsificationAssessment,
    FalsificationConclusion,
    ReportFormat
)

from .bayesian_models import (
    HierarchicalBayesianModel,
    SurpriseAccumulator,
    IgnitionProbabilityCalculator,
    StanModelCompiler,
    ParameterDistribution,
    ParameterEstimates
)

from .parameter_estimation import (
    JointParameterFitter,
    ParameterExtractor,
    ConvergenceDiagnosticsCalculator,
    IndividualParameterEstimator,
    ConvergenceDiagnostics,
    FitResults
)

from .parameter_recovery import (
    SyntheticDataGenerator,
    ParameterRecoveryValidator,
    RecoveryAnalyzer,
    ValidationReportGenerator,
    GroundTruthParameters,
    RecoveryMetrics,
    RecoveryResults
)

from .predictive_validity import (
    EmotionalInterferenceTask,
    ContinuousPerformanceTask,
    BodyVigilanceScaleAnalyzer,
    PredictivePowerComparator,
    PredictiveValidityFramework,
    TaskPerformance,
    ValidityResult,
    ComparativeValidityResult
)

__all__ = [
    # Statistical Testing
    'StatisticalTester',
    'StatisticalResult',
    'TestType',
    'CorrectionMethod',
    'ClusterCorrectionResult',
    
    # Effect Size Calculation
    'EffectSizeCalculator',
    'EffectSizeResult',
    'BootstrapResult',
    'EffectSizeType',
    'ConfidenceIntervalMethod',
    'get_effect_size_guidelines',
    
    # Replication and Power Analysis
    'ReplicationTracker',
    'PowerAnalyzer',
    'ExperimentResult',
    'ReplicationSummary',
    'PowerAnalysisResult',
    'ReplicationStatus',
    'PowerAnalysisMethod',
    
    # Sample Size Validation
    'SampleSizeValidator',
    'ValidationResult',
    'PowerReport',
    'ValidationStatus',
    'TestRequirement',
    'SampleSizeRequirement',
    
    # Report Generation
    'StatisticalReportGenerator',
    'StatisticalSummary',
    'PublicationReport',
    'FalsificationAssessment',
    'FalsificationConclusion',
    'ReportFormat',
    
    # Bayesian Modeling
    'HierarchicalBayesianModel',
    'SurpriseAccumulator',
    'IgnitionProbabilityCalculator',
    'StanModelCompiler',
    'ParameterDistribution',
    'ParameterEstimates',
    
    # Parameter Estimation Pipeline
    'JointParameterFitter',
    'ParameterExtractor',
    'ConvergenceDiagnosticsCalculator',
    'IndividualParameterEstimator',
    'ConvergenceDiagnostics',
    'FitResults',
    
    # Parameter Recovery Validation
    'SyntheticDataGenerator',
    'ParameterRecoveryValidator',
    'RecoveryAnalyzer',
    'ValidationReportGenerator',
    'GroundTruthParameters',
    'RecoveryMetrics',
    'RecoveryResults',
    
    # Predictive Validity Testing
    'EmotionalInterferenceTask',
    'ContinuousPerformanceTask',
    'BodyVigilanceScaleAnalyzer',
    'PredictivePowerComparator',
    'PredictiveValidityFramework',
    'TaskPerformance',
    'ValidityResult',
    'ComparativeValidityResult'
]