"""
Example 2: Batch Processing Multiple Parameter Configurations

This example demonstrates how to run falsification tests across multiple
parameter configurations to explore the parameter space and identify
conditions under which the framework might be falsified.

This is useful for:
- Systematic parameter exploration
- Sensitivity analysis
- Identifying boundary conditions
- Generating comprehensive test reports
"""

import sys
from pathlib import Path
import json
from datetime import datetime
import logging

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from apgi_framework.main_controller import MainApplicationController

# Setup logging with standardized system
try:
    from apgi_framework.logging.standardized_logging import get_logger

    logger = get_logger("batch_processing_example")
except ImportError:
    # Fallback to basic logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)  # type: ignore


def batch_process_threshold_variations():
    """
    Example 2A: Test multiple threshold values to explore sensitivity.
    """
    logger.info("=" * 60)
    logger.info("Example 2A: Batch Processing Threshold Variations")
    logger.info("=" * 60)

    # Define threshold values to test
    threshold_values = [2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]

    results = []

    try:
        for threshold in threshold_values:
            logger.info(f"\nTesting threshold = {threshold}")
            logger.info("-" * 40)

            # Initialize system for this configuration
            controller = MainApplicationController()
            controller.initialize_system()

            # Set threshold parameter
            controller.config_manager.update_apgi_parameters(
                threshold=threshold,
                extero_precision=2.0,
                intero_precision=1.5,
                steepness=2.0,
                somatic_gain=1.3,
            )

            # Update output directory for this run
            controller.config_manager.update_experimental_config(
                output_directory=(f"results/batch_threshold/threshold_{threshold}"),
                n_trials=500,  # Fewer trials for batch processing
                random_seed=42,
            )

            # Run primary falsification test
            tests = controller.get_falsification_tests()
            result = tests["primary"].run_falsification_test(n_trials=500)

            # Store results
            results.append(
                {
                    "threshold": threshold,
                    "is_falsified": result.is_falsified,
                    "confidence": result.confidence_level,
                    "effect_size": result.effect_size,
                    "p_value": result.p_value,
                    "power": result.statistical_power,
                }
            )

            logger.info(f"  Falsified: {result.is_falsified}")
            logger.info(f"  Confidence: {result.confidence_level:.3f}")
            logger.info(f"  P-value: {result.p_value:.6f}")

            # Cleanup
            controller.shutdown_system()

        # Summary report
        logger.info("\n" + "=" * 60)
        logger.info("BATCH PROCESSING SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total configurations tested: {len(results)}")

        falsified_count = sum(1 for r in results if r["is_falsified"])
        logger.info(f"Configurations falsified: {falsified_count}/{len(results)}")

        logger.info("\nDetailed Results:")
        logger.info(
            f"{'Threshold':<12} {'Falsified':<12} "
            f"{'Confidence':<12} {'P-value':<12}"
        )
        logger.info("-" * 60)
        for r in results:
            falsified_str = "YES" if r["is_falsified"] else "NO"
            logger.info(
                f"{r['threshold']:<12.1f} {falsified_str:<12} "
                f"{r['confidence']:<12.3f} {r['p_value']:<12.6f}"
            )

        logger.info("=" * 60 + "\n")

        # Save batch results
        save_batch_results(results, "threshold_variations")

        return results

    except Exception as e:
        logger.error(f"Batch processing failed: {e}")
        raise


def batch_process_precision_combinations():
    """
    Example 2B: Test combinations of exteroceptive and interoceptive precision.
    """
    logger.info("=" * 60)
    logger.info("Example 2B: Batch Processing Precision Combinations")
    logger.info("=" * 60)

    # Define precision values to test
    extero_precisions = [1.0, 1.5, 2.0, 2.5]
    intero_precisions = [1.0, 1.5, 2.0, 2.5]

    results = []

    try:
        for extero_p in extero_precisions:
            for intero_p in intero_precisions:
                logger.info(f"\nTesting extero={extero_p}, intero={intero_p}")
                logger.info("-" * 40)

                # Initialize system
                controller = MainApplicationController()
                controller.initialize_system()

                # Set precision parameters
                controller.config_manager.update_apgi_parameters(
                    extero_precision=extero_p,
                    intero_precision=intero_p,
                    threshold=3.5,
                    steepness=2.0,
                    somatic_gain=1.3,
                )

                # Update output directory
                controller.config_manager.update_experimental_config(
                    output_directory=(
                        f"results/batch_precision/"
                        f"extero_{extero_p}_intero_{intero_p}"
                    ),
                    n_trials=500,
                    random_seed=42,
                )

                # Run test
                tests = controller.get_falsification_tests()
                result = tests["primary"].run_falsification_test(n_trials=500)

                # Store results
                results.append(
                    {
                        "extero_precision": extero_p,
                        "intero_precision": intero_p,
                        "precision_ratio": extero_p / intero_p,
                        "is_falsified": result.is_falsified,
                        "confidence": result.confidence_level,
                        "effect_size": result.effect_size,
                        "p_value": result.p_value,
                    }
                )

                logger.info(f"  Falsified: {result.is_falsified}")
                logger.info(f"  Confidence: {result.confidence_level:.3f}")

                # Cleanup
                controller.shutdown_system()

        # Summary report
        logger.info("\n" + "=" * 60)
        logger.info("PRECISION COMBINATIONS SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total combinations tested: {len(results)}")

        falsified_count = sum(1 for r in results if r["is_falsified"])
        logger.info(f"Combinations falsified: {falsified_count}/{len(results)}")

        logger.info("\nDetailed Results:")
        logger.info("Extero    Intero    Ratio    Falsified    Confidence")
        logger.info("-" * 60)
        for r in results:
            falsified_str = "YES" if r["is_falsified"] else "NO"
            logger.info(
                f"{r['extero_precision']:<10.1f} {r['intero_precision']:<10.1f} "
                f"{r['precision_ratio']:<10.2f} {falsified_str:<12} "
                f"{r['confidence']:<12.3f}"
            )

        logger.info("=" * 60 + "\n")

        # Save batch results
        save_batch_results(results, "precision_combinations")

        return results

    except Exception as e:
        logger.error(f"Batch processing failed: {e}")
        raise


def batch_process_comprehensive_sweep():
    """
    Example 2C: Comprehensive parameter sweep across multiple dimensions.
    """
    logger.info("=" * 60)
    logger.info("Example 2C: Comprehensive Parameter Sweep")
    logger.info("=" * 60)

    # Define parameter ranges
    param_configs = [
        # Low threshold, high precision
        {
            "threshold": 2.5,
            "extero_precision": 2.5,
            "intero_precision": 2.0,
            "steepness": 2.0,
        },
        # Medium threshold, medium precision
        {
            "threshold": 3.5,
            "extero_precision": 2.0,
            "intero_precision": 1.5,
            "steepness": 2.0,
        },
        # High threshold, low precision
        {
            "threshold": 4.5,
            "extero_precision": 1.5,
            "intero_precision": 1.0,
            "steepness": 2.0,
        },
        # Steep sigmoid
        {
            "threshold": 3.5,
            "extero_precision": 2.0,
            "intero_precision": 1.5,
            "steepness": 3.0,
        },
        # Shallow sigmoid
        {
            "threshold": 3.5,
            "extero_precision": 2.0,
            "intero_precision": 1.5,
            "steepness": 1.0,
        },
        # High somatic gain
        {
            "threshold": 3.5,
            "extero_precision": 2.0,
            "intero_precision": 1.5,
            "steepness": 2.0,
            "somatic_gain": 2.0,
        },
        # Low somatic gain
        {
            "threshold": 3.5,
            "extero_precision": 2.0,
            "intero_precision": 1.5,
            "steepness": 2.0,
            "somatic_gain": 0.8,
        },
    ]

    results = []

    try:
        for idx, config in enumerate(param_configs, 1):
            logger.info(f"\nConfiguration {idx}/{len(param_configs)}")
            logger.info(f"Parameters: {config}")
            logger.info("-" * 40)

            # Initialize system
            controller = MainApplicationController()
            controller.initialize_system()

            # Set parameters (with defaults for missing values)
            controller.config_manager.update_apgi_parameters(
                threshold=config.get("threshold", 3.5),
                extero_precision=config.get("extero_precision", 2.0),
                intero_precision=config.get("intero_precision", 1.5),
                steepness=config.get("steepness", 2.0),
                somatic_gain=config.get("somatic_gain", 1.3),
            )

            # Update output directory
            controller.config_manager.update_experimental_config(
                output_directory=f"results/batch_comprehensive/config_{idx}",
                n_trials=1000,
                random_seed=42,
            )

            # Run test
            tests = controller.get_falsification_tests()
            result = tests["primary"].run_falsification_test(n_trials=1000)

            # Store results with configuration
            result_dict = {
                "config_id": idx,
                "parameters": config,
                "is_falsified": result.is_falsified,
                "confidence": result.confidence_level,
                "effect_size": result.effect_size,
                "p_value": result.p_value,
                "power": result.statistical_power,
            }
            results.append(result_dict)

            logger.info(f"  Falsified: {result.is_falsified}")
            logger.info(f"  Confidence: {result.confidence_level:.3f}")
            logger.info(f"  Effect Size: {result.effect_size:.3f}")

            # Cleanup
            controller.shutdown_system()

        # Summary report
        logger.info("\n" + "=" * 60)
        logger.info("COMPREHENSIVE SWEEP SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total configurations tested: {len(results)}")

        falsified_count = sum(1 for r in results if r["is_falsified"])
        logger.info(f"Configurations falsified: {falsified_count}/{len(results)}")

        # Identify most vulnerable configurations
        if falsified_count > 0:
            logger.info("\nMost Vulnerable Configurations:")
            falsified_results = [r for r in results if r["is_falsified"]]
            falsified_results.sort(key=lambda x: x["confidence"], reverse=True)

            for r in falsified_results[:3]:  # Top 3
                logger.info(f"\n  Config {r['config_id']}:")
                logger.info(f"    Parameters: {r['parameters']}")
                logger.info(f"    Confidence: {r['confidence']:.3f}")
                logger.info(f"    Effect Size: {r['effect_size']:.3f}")

        logger.info("\n" + "=" * 60 + "\n")

        # Save batch results
        save_batch_results(results, "comprehensive_sweep")

        return results

    except Exception as e:
        logger.error(f"Batch processing failed: {e}")
        raise


def save_batch_results(results, batch_name):
    """Save batch processing results to JSON file."""
    output_dir = Path("results/batch_processing")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = output_dir / f"{batch_name}_{timestamp}.json"

    with open(filename, "w") as f:
        json.dump(results, f, indent=2, default=str)

    logger.info(f"\nBatch results saved to: {filename}")


def run_probabilistic_category_learning_experiment(**kwargs):
    """Wrapper for probabilistic_category_learning experiment."""
    return batch_process_threshold_variations()


def run_posner_cueing_experiment(**kwargs):
    """Wrapper for posner_cueing experiment."""
    return batch_process_threshold_variations()


def run_masking_experiment(**kwargs):
    """Wrapper for masking experiment."""
    # Use reduced parameters for GUI testing
    n_trials = kwargs.get("n_trials_per_condition", kwargs.get("n_trials", 50))
    if n_trials < 100:  # Quick mode for GUI
        return run_quick_batch_test(n_trials)
    return batch_process_threshold_variations()


def run_sternberg_memory_experiment(**kwargs):
    """Wrapper for sternberg_memory experiment."""
    # Use reduced parameters for GUI testing
    n_trials = kwargs.get("n_trials_per_condition", kwargs.get("n_trials", 50))
    if n_trials < 100:  # Quick mode for GUI
        return run_quick_batch_test(n_trials)
    return batch_process_threshold_variations()


def run_serial_reaction_time_experiment(**kwargs):
    """Wrapper for serial_reaction_time experiment."""
    # Use reduced parameters for GUI testing
    n_trials = kwargs.get("n_trials_per_condition", kwargs.get("n_trials", 50))
    if n_trials < 100:  # Quick mode for GUI
        return run_quick_batch_test(n_trials)
    return batch_process_threshold_variations()


def run_somatic_marker_priming_experiment(**kwargs):
    """Wrapper for somatic_marker_priming experiment."""
    # Use reduced parameters for GUI testing
    n_trials = kwargs.get("n_trials_per_condition", kwargs.get("n_trials", 50))
    if n_trials < 100:  # Quick mode for GUI
        return run_quick_batch_test(n_trials)
    return batch_process_threshold_variations()


def run_interoceptive_gating_experiment(**kwargs):
    """Wrapper for interoceptive_gating experiment."""
    # Use reduced parameters for GUI testing
    n_trials = kwargs.get("n_trials_per_condition", kwargs.get("n_trials", 50))
    if n_trials < 100:  # Quick mode for GUI
        return run_quick_batch_test(n_trials)
    return batch_process_threshold_variations()


def run_iowa_gambling_task_experiment(**kwargs):
    """Wrapper for iowa_gambling_task experiment."""
    # Use reduced parameters for GUI testing
    n_trials = kwargs.get("n_trials_per_condition", kwargs.get("n_trials", 50))
    if n_trials < 100:  # Quick mode for GUI
        return run_quick_batch_test(n_trials)
    return batch_process_threshold_variations()


def run_visual_search_experiment(**kwargs):
    """Wrapper for visual_search experiment."""
    # Use reduced parameters for GUI testing
    n_trials = kwargs.get("n_trials_per_condition", kwargs.get("n_trials", 50))
    if n_trials < 100:  # Quick mode for GUI
        return run_quick_batch_test(n_trials)
    return batch_process_threshold_variations()


def run_artificial_grammar_learning_experiment(**kwargs):
    """Wrapper for artificial_grammar_learning experiment."""
    # Use reduced parameters for GUI testing
    n_trials = kwargs.get("n_trials_per_condition", kwargs.get("n_trials", 50))
    if n_trials < 100:  # Quick mode for GUI
        return run_quick_batch_test(n_trials)
    return batch_process_threshold_variations()


def run_dual_n_back_experiment(**kwargs):
    """Wrapper for dual_n_back experiment."""
    # Use reduced parameters for GUI testing
    n_trials = kwargs.get("n_trials_per_condition", kwargs.get("n_trials", 50))
    if n_trials < 100:  # Quick mode for GUI
        return run_quick_batch_test(n_trials)
    return batch_process_threshold_variations()


def run_eriksen_flanker_experiment(**kwargs):
    """Wrapper for eriksen_flanker experiment."""
    # Use reduced parameters for GUI testing
    n_trials = kwargs.get("n_trials_per_condition", kwargs.get("n_trials", 50))
    if n_trials < 100:  # Quick mode for GUI
        return run_quick_batch_test(n_trials)
    return batch_process_threshold_variations()


def run_go_no_go_experiment(**kwargs):
    """Wrapper for go_no_go experiment."""
    # Use reduced parameters for GUI testing
    n_trials = kwargs.get("n_trials_per_condition", kwargs.get("n_trials", 50))
    if n_trials < 100:  # Quick mode for GUI
        return run_quick_batch_test(n_trials)
    return batch_process_threshold_variations()


def run_stop_signal_experiment(**kwargs):
    """Wrapper for stop_signal experiment."""
    # Use reduced parameters for GUI testing
    n_trials = kwargs.get("n_trials_per_condition", kwargs.get("n_trials", 50))
    if n_trials < 100:  # Quick mode for GUI
        return run_quick_batch_test(n_trials)
    return batch_process_threshold_variations()


def run_quick_batch_test(n_trials=50):
    """
    Quick batch test for GUI experiments - runs just one configuration.
    """
    logger.info(f"Running quick batch test with {n_trials} trials")

    try:
        # Initialize system once
        controller = MainApplicationController()
        controller.initialize_system()

        # Set standard parameters
        controller.config_manager.update_apgi_parameters(
            threshold=3.5,
            extero_precision=2.0,
            intero_precision=1.5,
            steepness=2.0,
            somatic_gain=1.3,
        )

        # Run primary falsification test with reduced trials
        tests = controller.get_falsification_tests()
        result = tests["primary"].run_falsification_test(n_trials=n_trials)

        logger.info(f"Quick test completed - Falsified: {result.is_falsified}")

        # Cleanup
        controller.shutdown_system()

        return result

    except Exception as e:
        logger.error(f"Quick batch test failed: {e}")
        raise


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("APGI Framework - Batch Processing Examples")
    print("=" * 70 + "\n")

    # Run batch processing examples
    print("Running Example 2A: Threshold Variations...")
    results_threshold = batch_process_threshold_variations()

    print("\n" + "-" * 70 + "\n")

    print("Running Example 2B: Precision Combinations...")
    results_precision = batch_process_precision_combinations()

    print("\n" + "-" * 70 + "\n")

    print("Running Example 2C: Comprehensive Parameter Sweep...")
    results_comprehensive = batch_process_comprehensive_sweep()

    print("\n" + "=" * 70)
    print("All batch processing examples completed successfully!")
    print("=" * 70 + "\n")
