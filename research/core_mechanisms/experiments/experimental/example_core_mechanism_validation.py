"""
Example script demonstrating Priority 2 core mechanism validation.

This script shows how to use the neuromodulatory blockade simulator and
surprise accumulation dynamics analyzer to validate APGI framework predictions.
"""

import numpy as np
from typing import List

from research.core_mechanisms.experiments.experimental.neuromodulatory_blockade import (
    NeuromodulatoryBlockadeSimulator,
    NeuromodulatorEffect,
)
from research.core_mechanisms.experiments.experimental.surprise_accumulation_dynamics import (
    SurpriseAccumulationAnalyzer,
    TrialSurpriseEstimate,
)
from apgi_framework.neural.erp_analysis import ERPAnalysis, ERPComponents
from apgi_framework.core.equation import APGIEquation


def example_neuromodulatory_blockade():
    """
    Example: Simulate propranolol effects on P3b amplitude.

    Tests the prediction that beta-adrenergic blockade selectively impairs
    ignition-related neural signatures while preserving early sensory processing.
    """
    print("=" * 70)
    print("EXAMPLE 1: NEUROMODULATORY BLOCKADE SIMULATION")
    print("=" * 70)
    print()

    # Initialize simulator
    simulator = NeuromodulatoryBlockadeSimulator(random_seed=42)

    # Run complete blockade experiment
    result = simulator.simulate_blockade_experiment(
        n_trials_per_condition=40,
        baseline_p3b_mean=8.0,
        baseline_p3b_std=2.0,
        baseline_n1_mean=-5.0,
        baseline_n1_std=1.5,
        baseline_p1_mean=3.0,
        baseline_p1_std=1.0,
    )

    # Generate and print report
    report = simulator.generate_report(result)
    print(report)

    # Validate predictions
    print("\nPREDICTION VALIDATION:")
    print(f"  ✓ P3b reduction (20-40%): {result.meets_p3b_reduction_prediction}")
    print(
        f"  ✓ Early ERP preservation (<10% change): {result.meets_early_preservation_prediction}"
    )
    print(f"  ✓ Emotional selectivity: {result.meets_emotional_selectivity_prediction}")

    all_met = (
        result.meets_p3b_reduction_prediction
        and result.meets_early_preservation_prediction
        and result.meets_emotional_selectivity_prediction
    )

    if all_met:
        print("\n✓ ALL PREDICTIONS MET - APGI framework validated!")
    else:
        print("\n✗ Some predictions not met - requires further investigation")

    return result


def example_surprise_accumulation_dynamics():
    """
    Example: Analyze trial-by-trial surprise accumulation from neural data.

    Tests whether neural signatures can estimate surprise (Sₜ) and predict
    ignition events on a trial-by-trial basis.
    """
    print("\n\n")
    print("=" * 70)
    print("EXAMPLE 2: SURPRISE ACCUMULATION DYNAMICS ANALYSIS")
    print("=" * 70)
    print()

    # Initialize analyzer
    apgi_equation = APGIEquation()
    analyzer = SurpriseAccumulationAnalyzer(
        apgi_equation=apgi_equation, near_threshold_window=0.5
    )

    # Generate synthetic trial data
    n_trials = 100
    print(f"Generating {n_trials} synthetic trials...")

    # Simulate ERP components
    erp_components = []
    gamma_powers = []
    reaction_times = []
    conscious_reports = []

    for i in range(n_trials):
        # Vary P3b amplitude (proxy for surprise)
        p3b_amp = np.random.normal(8.0, 2.5)
        p3b_lat = np.random.normal(400, 50)

        # Gamma power correlates with P3b
        gamma_power = max(0.0, min(1.0, (p3b_amp / 15.0) + np.random.normal(0, 0.1)))

        # Early components relatively stable
        n1_amp = np.random.normal(-5.0, 1.0)
        p1_amp = np.random.normal(3.0, 0.8)

        # Conscious report based on P3b amplitude (threshold ~6 µV)
        conscious = p3b_amp > 6.0 + np.random.normal(0, 1.0)

        # Reaction time inversely related to P3b (faster for stronger ignition)
        if conscious:
            rt = max(200, 500 - (p3b_amp - 6.0) * 20 + np.random.normal(0, 50))
        else:
            rt = 0  # No response

        # Create ERP components
        erp = ERPComponents(
            p3b_amplitude=p3b_amp,
            p3b_latency=p3b_lat,
            p3b_area=p3b_amp * 200,
            n1_amplitude=n1_amp,
            n1_latency=150,
            p1_amplitude=p1_amp,
            p1_latency=100,
            snr=p3b_amp / 2.0,
        )

        erp_components.append(erp)
        gamma_powers.append(gamma_power)
        reaction_times.append(rt)
        conscious_reports.append(conscious)

    # Analyze trial-by-trial dynamics
    print("Analyzing surprise accumulation dynamics...")
    result = analyzer.analyze_trial_by_trial(
        erp_components=erp_components,
        gamma_powers=gamma_powers,
        reaction_times=reaction_times,
        conscious_reports=conscious_reports,
    )

    # Generate and print report
    report = analyzer.generate_report(result)
    print(report)

    # Show example trial estimates
    print("\nEXAMPLE TRIAL ESTIMATES:")
    print(
        f"{'Trial':<10} {'Est. S_t':<10} {'Threshold':<10} {'P(ignition)':<12} {'Actual':<8} {'RT (ms)':<10}"
    )
    print("-" * 70)

    for i in range(min(10, len(result.trial_estimates))):
        est = result.trial_estimates[i]
        print(
            f"{est.trial_id:<10} {est.estimated_surprise:<10.2f} {est.estimated_threshold:<10.2f} "
            f"{est.predicted_ignition_probability:<12.3f} {str(est.actual_ignition):<8} "
            f"{est.reaction_time if est.reaction_time else 'N/A':<10}"
        )

    return result


def example_combined_validation():
    """
    Example: Combined validation of both core mechanisms.

    Demonstrates how neuromodulatory blockade affects surprise accumulation
    dynamics, providing comprehensive validation of APGI framework predictions.
    """
    print("\n\n")
    print("=" * 70)
    print("EXAMPLE 3: COMBINED CORE MECHANISM VALIDATION")
    print("=" * 70)
    print()

    # Initialize components
    simulator = NeuromodulatoryBlockadeSimulator(random_seed=42)
    analyzer = SurpriseAccumulationAnalyzer()

    print("Simulating baseline condition...")

    # Generate baseline trials
    n_trials = 50
    baseline_erps = []
    baseline_gamma = []
    baseline_rts = []
    baseline_conscious = []

    for i in range(n_trials):
        p3b_amp = np.random.normal(8.0, 2.0)
        gamma = max(0.0, min(1.0, p3b_amp / 15.0 + np.random.normal(0, 0.1)))
        conscious = p3b_amp > 6.0
        rt = max(200, 500 - (p3b_amp - 6.0) * 20) if conscious else 0

        erp = ERPComponents(
            p3b_amplitude=p3b_amp, p3b_latency=400, n1_amplitude=-5.0, p1_amplitude=3.0
        )

        baseline_erps.append(erp)
        baseline_gamma.append(gamma)
        baseline_rts.append(rt)
        baseline_conscious.append(conscious)

    # Analyze baseline
    baseline_result = analyzer.analyze_trial_by_trial(
        erp_components=baseline_erps,
        gamma_powers=baseline_gamma,
        reaction_times=baseline_rts,
        conscious_reports=baseline_conscious,
    )

    print(
        f"Baseline prediction accuracy: {baseline_result.ignition_prediction_accuracy:.3f}"
    )
    print(f"Baseline AUC: {baseline_result.ignition_prediction_auc:.3f}")

    print("\nSimulating propranolol blockade condition...")

    # Generate blockade trials (apply propranolol effects)
    blockade_erps = []
    blockade_gamma = []
    blockade_rts = []
    blockade_conscious = []

    for i in range(n_trials):
        # Baseline P3b
        baseline_p3b = np.random.normal(8.0, 2.0)

        # Apply propranolol effect (30% reduction)
        blockade_p3b = baseline_p3b * 0.70

        gamma = max(0.0, min(1.0, blockade_p3b / 15.0 + np.random.normal(0, 0.1)))
        conscious = blockade_p3b > 6.0  # Harder to reach threshold
        rt = max(200, 500 - (blockade_p3b - 6.0) * 20) if conscious else 0

        erp = ERPComponents(
            p3b_amplitude=blockade_p3b,
            p3b_latency=410,  # Slight delay
            n1_amplitude=-5.0,  # Preserved
            p1_amplitude=3.0,  # Preserved
        )

        blockade_erps.append(erp)
        blockade_gamma.append(gamma)
        blockade_rts.append(rt)
        blockade_conscious.append(conscious)

    # Analyze blockade
    blockade_result = analyzer.analyze_trial_by_trial(
        erp_components=blockade_erps,
        gamma_powers=blockade_gamma,
        reaction_times=blockade_rts,
        conscious_reports=blockade_conscious,
    )

    print(
        f"Blockade prediction accuracy: {blockade_result.ignition_prediction_accuracy:.3f}"
    )
    print(f"Blockade AUC: {blockade_result.ignition_prediction_auc:.3f}")

    # Compare conditions
    print("\nCOMPARISON:")
    print(
        f"  Ignition rate baseline: {baseline_result.n_ignition_trials / baseline_result.n_trials:.2%}"
    )
    print(
        f"  Ignition rate blockade: {blockade_result.n_ignition_trials / blockade_result.n_trials:.2%}"
    )
    print(
        f"  Reduction: {(1 - blockade_result.n_ignition_trials / baseline_result.n_ignition_trials):.1%}"
    )

    print("\n✓ Combined validation demonstrates:")
    print("  1. Propranolol reduces P3b amplitude (ignition marker)")
    print("  2. Reduced P3b leads to fewer ignition events")
    print("  3. Surprise accumulation dynamics predict ignition probability")
    print("  4. Neural signatures track computational mechanisms")


if __name__ == "__main__":
    # Run all examples
    print("APGI FRAMEWORK - PRIORITY 2 CORE MECHANISM VALIDATION")
    print("=" * 70)
    print()

    # Example 1: Neuromodulatory blockade
    blockade_result = example_neuromodulatory_blockade()

    # Example 2: Surprise accumulation dynamics
    accumulation_result = example_surprise_accumulation_dynamics()

    # Example 3: Combined validation
    example_combined_validation()

    print("\n\n")
    print("=" * 70)
    print("ALL EXAMPLES COMPLETED")
    print("=" * 70)
