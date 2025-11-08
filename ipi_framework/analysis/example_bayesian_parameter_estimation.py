"""
Example usage of hierarchical Bayesian parameter estimation pipeline.

This script demonstrates how to:
1. Fit hierarchical Bayesian models to estimate θ₀, Πᵢ, and β
2. Extract parameter estimates with uncertainty quantification
3. Validate parameter recovery with synthetic data
4. Test predictive validity on independent tasks
"""

import numpy as np
from ipi_framework.analysis import (
    # Bayesian modeling
    HierarchicalBayesianModel,
    SurpriseAccumulator,
    IgnitionProbabilityCalculator,
    
    # Parameter estimation
    JointParameterFitter,
    IndividualParameterEstimator,
    
    # Parameter recovery
    SyntheticDataGenerator,
    ParameterRecoveryValidator,
    GroundTruthParameters,
    
    # Predictive validity
    PredictiveValidityFramework,
    EmotionalInterferenceTask,
    ContinuousPerformanceTask,
    BodyVigilanceScaleAnalyzer
)


def example_surprise_accumulation():
    """Example: Simulate surprise accumulation dynamics."""
    print("=" * 70)
    print("Example 1: Surprise Accumulation")
    print("=" * 70)
    
    # Initialize surprise accumulator
    accumulator = SurpriseAccumulator(tau=1.0, dt=0.001)
    
    # Simulate prediction errors over time
    duration = 2.0  # seconds
    n_steps = int(duration / 0.001)
    
    # Create time-varying prediction errors
    pi_e = np.ones(n_steps) * 1.0  # Exteroceptive precision
    epsilon_e = np.sin(np.linspace(0, 4*np.pi, n_steps)) * 0.5  # Oscillating PE
    pi_i = np.ones(n_steps) * 0.8  # Interoceptive precision
    epsilon_i = np.random.randn(n_steps) * 0.3  # Noisy interoceptive PE
    beta = 1.2  # Somatic bias
    
    # Integrate surprise
    surprise_trace = accumulator.integrate(
        pi_e, epsilon_e, pi_i, epsilon_i, beta, duration
    )
    
    print(f"Surprise accumulated over {duration}s")
    print(f"Final surprise level: {surprise_trace[-1]:.4f}")
    print(f"Peak surprise: {np.max(surprise_trace):.4f}")
    print()


def example_ignition_probability():
    """Example: Calculate ignition probability from surprise."""
    print("=" * 70)
    print("Example 2: Ignition Probability")
    print("=" * 70)
    
    # Initialize calculator
    calculator = IgnitionProbabilityCalculator(alpha=10.0)
    
    # Test different surprise levels
    threshold = 0.5
    surprise_levels = np.linspace(0, 1.5, 10)
    
    print(f"Threshold: {threshold}")
    print("\nSurprise → Ignition Probability:")
    for surprise in surprise_levels:
        prob = calculator.compute_probability(surprise, threshold)
        print(f"  {surprise:.2f} → {prob:.4f}")
    
    # Find ignition time
    surprise_trace = np.linspace(0, 1.0, 1000)
    ignition_time = calculator.find_ignition_time(
        surprise_trace, threshold, probability_threshold=0.9
    )
    print(f"\nIgnition time (P > 0.9): {ignition_time:.3f}s")
    print()


def example_parameter_estimation():
    """Example: Fit hierarchical Bayesian model to estimate parameters."""
    print("=" * 70)
    print("Example 3: Parameter Estimation")
    print("=" * 70)
    
    # Generate synthetic data for demonstration
    generator = SyntheticDataGenerator(random_seed=42)
    
    ground_truth = GroundTruthParameters(
        theta0=0.5,
        pi_i=1.2,
        beta=1.1
    )
    
    print(f"Ground truth parameters:")
    print(f"  θ₀ = {ground_truth.theta0}")
    print(f"  Πᵢ = {ground_truth.pi_i}")
    print(f"  β = {ground_truth.beta}")
    print()
    
    # Generate data
    detection_data, heartbeat_data, oddball_data = \
        generator.generate_complete_dataset(ground_truth)
    
    print("Generated synthetic data:")
    print(f"  Detection trials: {len(detection_data['detected'])}")
    print(f"  Heartbeat trials: {len(heartbeat_data['synchronous'])}")
    print(f"  Oddball trials: {len(oddball_data['trial_type'])}")
    print()
    
    # Fit model (using fewer iterations for demo)
    print("Fitting hierarchical Bayesian model...")
    print("(This may take a few minutes...)")
    
    # Note: Actual fitting requires PyStan installation
    # fitter = JointParameterFitter()
    # results = fitter.fit_all_subjects(
    #     detection_data, heartbeat_data, oddball_data,
    #     participant_ids=['demo_participant'],
    #     session_ids=['demo_session'],
    #     chains=2,
    #     iter=500
    # )
    # 
    # estimates = results.parameter_estimates[0]
    # print(f"\nRecovered parameters:")
    # print(f"  θ₀ = {estimates.theta0.mean:.3f} "
    #       f"[{estimates.theta0.credible_interval_95[0]:.3f}, "
    #       f"{estimates.theta0.credible_interval_95[1]:.3f}]")
    # print(f"  Πᵢ = {estimates.pi_i.mean:.3f} "
    #       f"[{estimates.pi_i.credible_interval_95[0]:.3f}, "
    #       f"{estimates.pi_i.credible_interval_95[1]:.3f}]")
    # print(f"  β = {estimates.beta.mean:.3f} "
    #       f"[{estimates.beta.credible_interval_95[0]:.3f}, "
    #       f"{estimates.beta.credible_interval_95[1]:.3f}]")
    
    print("(Skipping actual fitting - requires PyStan)")
    print()


def example_parameter_recovery():
    """Example: Validate parameter recovery with synthetic data."""
    print("=" * 70)
    print("Example 4: Parameter Recovery Validation")
    print("=" * 70)
    
    # Initialize validator
    validator = ParameterRecoveryValidator(random_seed=42)
    
    print("Running parameter recovery validation...")
    print("(This would generate 100 synthetic datasets and fit models)")
    print()
    
    # Note: Actual validation requires PyStan and takes significant time
    # results = validator.run_validation(
    #     n_datasets=100,
    #     noise_level=0.1,
    #     chains=4,
    #     iter=1000,
    #     verbose=True
    # )
    # 
    # print(results.summary())
    # 
    # # Check if validation passed
    # if results.passed:
    #     print("✓ Parameter recovery validation PASSED")
    #     print("  Pipeline can accurately recover ground-truth parameters")
    # else:
    #     print("✗ Parameter recovery validation FAILED")
    #     print("  Consider refining model or increasing data quality")
    
    print("(Skipping actual validation - requires PyStan)")
    print()


def example_predictive_validity():
    """Example: Test predictive validity on independent tasks."""
    print("=" * 70)
    print("Example 5: Predictive Validity Testing")
    print("=" * 70)
    
    # Initialize framework
    framework = PredictiveValidityFramework()
    
    # Test Πᵢ with emotional interference task
    print("Testing Πᵢ with emotional interference task...")
    emotional_task = EmotionalInterferenceTask(task_type='stroop')
    
    # Simulate running task
    performance = emotional_task.run_task('demo_participant')
    print(f"  Interference effect: {performance.interference_effect:.1f} ms")
    
    # Predict from Πᵢ
    pi_i = 1.2
    predicted_interference = emotional_task.predict_from_pi_i(pi_i)
    print(f"  Predicted from Πᵢ={pi_i}: {predicted_interference:.1f} ms")
    print()
    
    # Test θ₀ with continuous performance task
    print("Testing θ₀ with continuous performance task...")
    cpt_task = ContinuousPerformanceTask()
    
    performance = cpt_task.run_task('demo_participant')
    print(f"  Lapse rate: {performance.lapse_rate:.3f}")
    
    # Predict from θ₀
    theta0 = 0.5
    predicted_lapses = cpt_task.predict_from_theta0(theta0)
    print(f"  Predicted from θ₀={theta0}: {predicted_lapses:.3f}")
    print()
    
    # Test β with Body Vigilance Scale
    print("Testing β with Body Vigilance Scale...")
    bvs_analyzer = BodyVigilanceScaleAnalyzer()
    
    responses = bvs_analyzer.collect_questionnaire('demo_participant')
    print(f"  BVS score: {responses['total_score']:.2f}")
    
    # Predict from β
    beta = 1.1
    predicted_bvs = bvs_analyzer.predict_from_beta(beta)
    print(f"  Predicted from β={beta}: {predicted_bvs:.2f}")
    print()


def main():
    """Run all examples."""
    print("\n")
    print("*" * 70)
    print("HIERARCHICAL BAYESIAN PARAMETER ESTIMATION EXAMPLES")
    print("*" * 70)
    print("\n")
    
    # Run examples
    example_surprise_accumulation()
    example_ignition_probability()
    example_parameter_estimation()
    example_parameter_recovery()
    example_predictive_validity()
    
    print("=" * 70)
    print("Examples completed!")
    print("=" * 70)
    print()
    print("Note: Full parameter estimation requires PyStan installation:")
    print("  pip install pystan")
    print()
    print("For production use:")
    print("  1. Install PyStan")
    print("  2. Collect real behavioral and neural data")
    print("  3. Run parameter recovery validation")
    print("  4. Fit models to empirical data")
    print("  5. Test predictive validity")
    print()


if __name__ == '__main__':
    main()
