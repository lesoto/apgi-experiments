"""
Test script for ClinicalParameterExtraction module.

Demonstrates the 30-minute assessment battery and parameter extraction.
"""

import numpy as np
from datetime import datetime, timedelta
from ipi_framework.clinical.parameter_extraction import (
    ClinicalParameterExtractor,
    ClinicalParameters,
    AssessmentBattery,
    ReliabilityMetrics,
    extract_parameters_quick
)


def test_standard_battery_creation():
    """Test creation of standard 30-minute assessment battery."""
    print("=" * 60)
    print("TEST 1: Standard Battery Creation")
    print("=" * 60)
    
    extractor = ClinicalParameterExtractor(participant_id="P001")
    battery = extractor.create_standard_battery()
    
    print(f"\nBattery ID: {battery.battery_id}")
    print(f"Participant ID: {battery.participant_id}")
    print(f"Number of tasks: {len(battery.tasks)}")
    print(f"Total planned duration: {battery.get_total_planned_duration():.1f} minutes")
    
    print("\nTasks:")
    for i, task in enumerate(battery.tasks, 1):
        print(f"  {i}. {task.task_type.value} ({task.modality.value}) - "
              f"{task.duration:.1f} min, {task.n_trials} trials")
    
    assert len(battery.tasks) == 6, "Should have 6 tasks"
    assert battery.get_total_planned_duration() == 30.0, "Should be 30 minutes"
    
    print("\n✓ Standard battery creation successful")
    return battery


def test_parameter_extraction():
    """Test parameter extraction from simulated data."""
    print("\n" + "=" * 60)
    print("TEST 2: Parameter Extraction")
    print("=" * 60)
    
    extractor = ClinicalParameterExtractor(participant_id="P001")
    battery = extractor.create_standard_battery()
    
    # Mark tasks as completed
    for task in battery.tasks:
        task.completed = True
        task.completion_time = task.duration
        task.data_quality = 0.85
    
    battery.completed = True
    battery.start_time = datetime.now()
    battery.end_time = battery.start_time + timedelta(minutes=30)
    
    # Simulate behavioral data
    behavioral_data = {
        'visual_threshold': 0.45,
        'auditory_threshold': 0.50,
        'interoceptive_threshold': 0.55,
        'visual_accuracy': 0.80,
        'auditory_accuracy': 0.75,
        'rt_variability': 95.0,
        'heartbeat_accuracy': 0.65,
        'breath_awareness': 0.60,
        'emotional_stroop_interference': 60.0,
        'psychometric_slope': 1.2,
        'recovery_trials': 4
    }
    
    # Simulate neural data
    neural_data = {
        'p3b_amplitude': 6.5,
        'gamma_power': 0.6,
        'p3b_amplitude_emotional': 7.0,
        'p3b_amplitude_neutral': 5.5
    }
    
    # Simulate physiological data
    physiological_data = {
        'pupil_dilation_intero': 0.6,
        'hrv': 55.0,
        'scr_emotional': 0.6
    }
    
    # Extract parameters
    params = extractor.extract_parameters_from_battery(
        battery, behavioral_data, neural_data, physiological_data
    )
    
    print(f"\nExtracted Parameters:")
    print(f"  Ignition Threshold (θₜ): {params.theta_t:.2f} "
          f"[{params.theta_t_ci[0]:.2f}-{params.theta_t_ci[1]:.2f}]")
    print(f"  Exteroceptive Precision (Πₑ): {params.pi_e:.2f} "
          f"[{params.pi_e_ci[0]:.2f}-{params.pi_e_ci[1]:.2f}]")
    print(f"  Interoceptive Precision (Πᵢ): {params.pi_i:.2f} "
          f"[{params.pi_i_ci[0]:.2f}-{params.pi_i_ci[1]:.2f}]")
    print(f"  Somatic Bias (β): {params.beta:.2f} "
          f"[{params.beta_ci[0]:.2f}-{params.beta_ci[1]:.2f}]")
    print(f"  Sigmoid Steepness (α): {params.alpha:.2f}")
    print(f"  Recovery Rate (γ): {params.gamma:.3f}")
    
    print(f"\nQuality Metrics:")
    print(f"  Data Quality: {params.data_quality:.2f}")
    print(f"  Completion Rate: {params.completion_rate:.1%}")
    
    # Validate parameters are in reasonable ranges
    assert 1.0 <= params.theta_t <= 6.0, "Threshold out of range"
    assert 0.5 <= params.pi_e <= 4.0, "Exteroceptive precision out of range"
    assert 0.3 <= params.pi_i <= 3.5, "Interoceptive precision out of range"
    assert 0.5 <= params.beta <= 3.0, "Somatic bias out of range"
    
    print("\n✓ Parameter extraction successful")
    return params


def test_reliability_metrics():
    """Test reliability metrics calculation."""
    print("\n" + "=" * 60)
    print("TEST 3: Reliability Metrics")
    print("=" * 60)
    
    extractor = ClinicalParameterExtractor(participant_id="P001")
    
    # Create two sets of parameters (simulating test-retest)
    params1 = ClinicalParameters(
        theta_t=3.2,
        pi_e=2.1,
        pi_i=1.8,
        beta=1.3,
        participant_id="P001",
        assessment_date=datetime.now()
    )
    
    params2 = ClinicalParameters(
        theta_t=3.3,
        pi_e=2.0,
        pi_i=1.9,
        beta=1.4,
        participant_id="P001",
        assessment_date=datetime.now() + timedelta(days=7)
    )
    
    # Calculate reliability metrics
    reliability = extractor.calculate_reliability_metrics(
        params1, params2, timedelta(days=7)
    )
    
    print(f"\nTest-Retest ICC (1-week interval):")
    for param, icc in reliability.test_retest_icc.items():
        print(f"  {param}: {icc:.3f}")
    
    print(f"\nStandard Error of Measurement:")
    for param, sem in reliability.sem.items():
        print(f"  {param}: {sem:.3f}")
    
    print("\n✓ Reliability metrics calculation successful")
    return reliability


def test_internal_consistency():
    """Test internal consistency calculation."""
    print("\n" + "=" * 60)
    print("TEST 4: Internal Consistency")
    print("=" * 60)
    
    extractor = ClinicalParameterExtractor(participant_id="P001")
    battery = extractor.create_standard_battery()
    
    # Simulate trial-level data
    trial_data = {
        'visual_detection': np.random.normal(0.75, 0.1, 40).tolist(),
        'auditory_detection': np.random.normal(0.70, 0.12, 40).tolist(),
        'heartbeat_detection': np.random.normal(0.65, 0.15, 30).tolist()
    }
    
    # Calculate internal consistency
    alpha = extractor.calculate_internal_consistency(battery, trial_data)
    
    print(f"\nCronbach's Alpha: {alpha:.3f}")
    
    if alpha >= 0.7:
        print("  → Good internal consistency")
    elif alpha >= 0.6:
        print("  → Acceptable internal consistency")
    else:
        print("  → Poor internal consistency")
    
    # Calculate split-half reliability
    split_half = extractor.calculate_split_half_reliability(battery, trial_data)
    
    print(f"\nSplit-Half Reliability: {split_half:.3f}")
    
    print("\n✓ Internal consistency calculation successful")


def test_criterion_validation():
    """Test criterion validation."""
    print("\n" + "=" * 60)
    print("TEST 5: Criterion Validation")
    print("=" * 60)
    
    extractor = ClinicalParameterExtractor(participant_id="P001")
    
    # Create parameters for anxious individual
    params = ClinicalParameters(
        theta_t=2.5,  # Low threshold
        pi_e=2.2,
        pi_i=2.5,  # High interoceptive precision
        beta=1.8,  # High somatic bias
        participant_id="P001"
    )
    
    # Simulate criterion measures
    criterion_measures = {
        'anxiety_scale': 65.0,  # High anxiety
        'depression_scale': 30.0,  # Moderate depression
        'interoceptive_awareness': 75.0  # High awareness
    }
    
    # Validate against criteria
    correlations = extractor.validate_against_criterion(params, criterion_measures)
    
    print(f"\nCriterion Correlations:")
    for criterion, corr in correlations.items():
        print(f"  {criterion}: {corr:.3f}")
    
    print("\n✓ Criterion validation successful")


def test_clinical_report():
    """Test clinical report generation."""
    print("\n" + "=" * 60)
    print("TEST 6: Clinical Report Generation")
    print("=" * 60)
    
    extractor = ClinicalParameterExtractor(participant_id="P001")
    
    # Create parameters
    params = ClinicalParameters(
        theta_t=2.8,
        pi_e=2.1,
        pi_i=2.3,
        beta=1.6,
        alpha=1.2,
        gamma=0.12,
        theta_t_ci=(2.5, 3.1),
        pi_e_ci=(1.9, 2.3),
        pi_i_ci=(2.0, 2.6),
        beta_ci=(1.4, 1.8),
        participant_id="P001",
        assessment_date=datetime.now(),
        assessment_duration=30.0,
        data_quality=0.85,
        completion_rate=1.0
    )
    
    # Create reliability metrics
    reliability = ReliabilityMetrics(
        test_retest_icc={'theta_t': 0.82, 'pi_e': 0.78, 'pi_i': 0.85, 'beta': 0.75},
        cronbach_alpha=0.81,
        split_half_reliability=0.79,
        classification_accuracy=0.78
    )
    
    # Generate report
    report = extractor.generate_clinical_report(params, reliability)
    
    print("\n" + report)
    
    print("\n✓ Clinical report generation successful")


def test_quick_extraction():
    """Test quick parameter extraction function."""
    print("\n" + "=" * 60)
    print("TEST 7: Quick Parameter Extraction")
    print("=" * 60)
    
    # Simulate data
    behavioral_data = {
        'visual_threshold': 0.48,
        'auditory_threshold': 0.52,
        'interoceptive_threshold': 0.50,
        'visual_accuracy': 0.78,
        'auditory_accuracy': 0.76,
        'rt_variability': 100.0,
        'heartbeat_accuracy': 0.62,
        'breath_awareness': 0.58,
        'emotional_stroop_interference': 55.0
    }
    
    # Quick extraction
    params = extract_parameters_quick("P002", behavioral_data)
    
    print(f"\nQuick Extraction Results:")
    print(f"  Participant: {params.participant_id}")
    print(f"  θₜ: {params.theta_t:.2f}")
    print(f"  Πₑ: {params.pi_e:.2f}")
    print(f"  Πᵢ: {params.pi_i:.2f}")
    print(f"  β: {params.beta:.2f}")
    
    print("\n✓ Quick extraction successful")


def test_longitudinal_tracking():
    """Test longitudinal parameter tracking."""
    print("\n" + "=" * 60)
    print("TEST 8: Longitudinal Tracking")
    print("=" * 60)
    
    extractor = ClinicalParameterExtractor(participant_id="P001")
    
    # Create parameter history (simulating treatment response)
    base_date = datetime.now()
    parameter_history = [
        ClinicalParameters(
            theta_t=2.5, pi_e=2.0, pi_i=2.5, beta=1.8,
            assessment_date=base_date
        ),
        ClinicalParameters(
            theta_t=2.8, pi_e=2.1, pi_i=2.3, beta=1.6,
            assessment_date=base_date + timedelta(weeks=4)
        ),
        ClinicalParameters(
            theta_t=3.1, pi_e=2.0, pi_i=2.0, beta=1.4,
            assessment_date=base_date + timedelta(weeks=8)
        ),
        ClinicalParameters(
            theta_t=3.3, pi_e=2.0, pi_i=1.8, beta=1.3,
            assessment_date=base_date + timedelta(weeks=12)
        )
    ]
    
    # Track changes
    trends = extractor.track_longitudinal_changes(parameter_history)
    
    print(f"\nLongitudinal Trends:")
    for param, stats in trends.items():
        print(f"\n  {param}:")
        print(f"    Mean: {stats['mean']:.2f}")
        print(f"    Change: {stats['change']:.2f} ({stats['percent_change']:.1f}%)")
        if 'slope_per_week' in stats:
            print(f"    Trend: {stats['slope_per_week']:.3f} per week")
    
    print("\n✓ Longitudinal tracking successful")


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("CLINICAL PARAMETER EXTRACTION - COMPREHENSIVE TEST")
    print("=" * 60)
    
    try:
        test_standard_battery_creation()
        test_parameter_extraction()
        test_reliability_metrics()
        test_internal_consistency()
        test_criterion_validation()
        test_clinical_report()
        test_quick_extraction()
        test_longitudinal_tracking()
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)
        print("\nClinicalParameterExtraction module is working correctly!")
        print("The 30-minute assessment battery successfully extracts:")
        print("  • Ignition threshold (θₜ)")
        print("  • Exteroceptive precision (Πₑ)")
        print("  • Interoceptive precision (Πᵢ)")
        print("  • Somatic bias weight (β)")
        print("\nWith comprehensive reliability and validity metrics.")
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
