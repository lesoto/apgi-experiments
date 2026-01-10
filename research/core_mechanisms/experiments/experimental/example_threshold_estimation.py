"""
Example usage of Priority 1 Direct Threshold Estimation System

Demonstrates how to use the threshold estimation protocols and neural validation
pipeline for APGI framework validation.
"""

import numpy as np
import logging
from pathlib import Path

# Import threshold estimation components
from threshold_estimation_system import (
    ThresholdEstimationProtocol,
    ModalityThresholdConfig,
    ThresholdType,
    create_default_visual_config,
    create_default_auditory_config,
    create_default_interoceptive_config,
)

# Import neural validation
from neural_threshold_validation import (
    NeuralThresholdValidationPipeline,
    validate_neural_predictions,
)

from multi_modal_task_manager import ModalityType

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def example_basic_threshold_estimation():
    """
    Example 1: Basic threshold estimation without neural recording.

    Demonstrates psychophysical threshold estimation across multiple modalities
    with cross-modal normalization.
    """
    logger.info("=" * 60)
    logger.info("Example 1: Basic Threshold Estimation")
    logger.info("=" * 60)

    # Initialize protocol
    participant_id = "P001"
    session_id = "session_001"

    protocol = ThresholdEstimationProtocol(
        participant_id=participant_id, session_id=session_id
    )

    # Initialize (would connect to actual hardware in real implementation)
    if not protocol.initialize():
        logger.error("Failed to initialize protocol")
        return

    # Run threshold estimation for visual modality
    logger.info("\n--- Visual Threshold Estimation ---")
    visual_config = create_default_visual_config()
    visual_result = protocol.run_threshold_estimation(visual_config)

    if visual_result:
        logger.info(
            f"Visual threshold: {visual_result.conscious_threshold.threshold:.4f}"
        )
        logger.info(f"Normalized threshold: {visual_result.normalized_threshold:.4f}")
        logger.info(f"Trials completed: {visual_result.n_trials_completed}")
        logger.info(f"Data quality: {visual_result.data_quality_score:.2f}")

    # Run threshold estimation for auditory modality
    logger.info("\n--- Auditory Threshold Estimation ---")
    auditory_config = create_default_auditory_config()
    auditory_result = protocol.run_threshold_estimation(auditory_config)

    if auditory_result:
        logger.info(
            f"Auditory threshold: {auditory_result.conscious_threshold.threshold:.4f}"
        )
        logger.info(f"Normalized threshold: {auditory_result.normalized_threshold:.4f}")
        logger.info(f"Trials completed: {auditory_result.n_trials_completed}")

    # Calculate cross-modal consistency
    logger.info("\n--- Cross-Modal Analysis ---")
    consistency = protocol.calculate_cross_modal_consistency()
    if consistency:
        logger.info(f"Cross-modal consistency: {consistency:.3f}")
        logger.info(f"Requirement (r > 0.5): {'PASS' if consistency > 0.5 else 'FAIL'}")

    # Save results
    output_dir = "threshold_results"
    protocol.save_results(output_dir)
    logger.info(f"\nResults saved to {output_dir}/")

    # Cleanup
    protocol.cleanup()
    logger.info("\nExample 1 completed successfully!")


def example_neural_validation():
    """
    Example 2: Threshold estimation with neural validation.

    Demonstrates integrated psychophysical and neural recording to validate
    P3b stochastic appearance and gamma-band activity correlation.
    """
    logger.info("\n" + "=" * 60)
    logger.info("Example 2: Neural Validation Pipeline")
    logger.info("=" * 60)

    # Initialize pipeline
    participant_id = "P002"
    session_id = "session_001"

    pipeline = NeuralThresholdValidationPipeline(
        participant_id=participant_id, session_id=session_id
    )

    # Initialize (would connect to EEG hardware in real implementation)
    if not pipeline.initialize():
        logger.error("Failed to initialize pipeline")
        return

    # Run neural threshold estimation for visual modality
    logger.info("\n--- Visual Threshold with Neural Recording ---")
    visual_config = create_default_visual_config()
    validation_result = pipeline.run_neural_threshold_estimation(visual_config)

    if validation_result:
        logger.info(
            f"\nBehavioral threshold: {validation_result.behavioral_threshold:.4f}"
        )
        logger.info(f"Trials analyzed: {validation_result.n_trials_analyzed}")
        logger.info(
            f"Trials rejected (artifacts): {validation_result.n_trials_rejected}"
        )

        logger.info("\n--- Neural Signatures ---")
        logger.info(
            f"P3b-threshold correlation: {validation_result.p3b_amplitude_threshold_correlation:.3f}"
        )
        logger.info(
            f"Gamma-threshold correlation: {validation_result.gamma_power_threshold_correlation:.3f}"
        )
        logger.info(
            f"P3b stochastic appearance: {validation_result.p3b_stochastic_appearance_detected}"
        )
        logger.info(
            f"P3b detection rate near threshold: {validation_result.p3b_detection_rate_near_threshold:.2f}"
        )

        logger.info("\n--- Neural-Behavioral Correspondence ---")
        logger.info(
            f"P3b predicts detection: {validation_result.p3b_predicts_detection:.3f}"
        )
        logger.info(
            f"Gamma predicts detection: {validation_result.gamma_predicts_detection:.3f}"
        )

        logger.info("\n--- Quality Metrics ---")
        logger.info(f"Signal quality: {validation_result.overall_signal_quality:.2f}")
        logger.info(
            f"Validation confidence: {validation_result.validation_confidence:.2f}"
        )

        # Validate against APGI predictions
        logger.info("\n--- APGI Framework Validation ---")
        validations = validate_neural_predictions(validation_result)
        for check, passed in validations.items():
            status = "✓ PASS" if passed else "✗ FAIL"
            logger.info(f"{check}: {status}")

    # Save results
    output_dir = "neural_validation_results"
    pipeline.save_results(output_dir)
    logger.info(f"\nResults saved to {output_dir}/")

    # Cleanup
    pipeline.cleanup()
    logger.info("\nExample 2 completed successfully!")


def example_test_retest_reliability():
    """
    Example 3: Test-retest reliability assessment.

    Demonstrates calculation of test-retest reliability (ICC) across sessions.
    """
    logger.info("\n" + "=" * 60)
    logger.info("Example 3: Test-Retest Reliability")
    logger.info("=" * 60)

    participant_id = "P003"

    # Session 1
    logger.info("\n--- Session 1 ---")
    protocol_s1 = ThresholdEstimationProtocol(
        participant_id=participant_id, session_id="session_001"
    )
    protocol_s1.initialize()

    visual_config = create_default_visual_config()
    result_s1 = protocol_s1.run_threshold_estimation(visual_config)
    protocol_s1.cleanup()

    if result_s1:
        logger.info(
            f"Session 1 threshold: {result_s1.conscious_threshold.threshold:.4f}"
        )

    # Session 2 (simulated 1 week later)
    logger.info("\n--- Session 2 (1 week later) ---")
    protocol_s2 = ThresholdEstimationProtocol(
        participant_id=participant_id, session_id="session_002"
    )
    protocol_s2.initialize()

    result_s2 = protocol_s2.run_threshold_estimation(visual_config)
    protocol_s2.cleanup()

    if result_s2:
        logger.info(
            f"Session 2 threshold: {result_s2.conscious_threshold.threshold:.4f}"
        )

    # Calculate test-retest reliability
    if result_s1 and result_s2:
        logger.info("\n--- Reliability Analysis ---")
        icc = protocol_s2.calculate_test_retest_reliability(result_s1, result_s2)

        if icc:
            logger.info(f"Test-retest ICC: {icc:.3f}")
            logger.info(f"Requirement (ICC > 0.70): {'PASS' if icc > 0.70 else 'FAIL'}")

    logger.info("\nExample 3 completed successfully!")


def example_complete_validation_battery():
    """
    Example 4: Complete validation battery across all modalities.

    Demonstrates comprehensive threshold estimation and neural validation
    across visual, auditory, and interoceptive modalities.
    """
    logger.info("\n" + "=" * 60)
    logger.info("Example 4: Complete Validation Battery")
    logger.info("=" * 60)

    participant_id = "P004"
    session_id = "session_001"

    # Initialize neural validation pipeline
    pipeline = NeuralThresholdValidationPipeline(
        participant_id=participant_id, session_id=session_id
    )

    if not pipeline.initialize():
        logger.error("Failed to initialize pipeline")
        return

    # Test all modalities
    modalities = [
        ("Visual", create_default_visual_config()),
        ("Auditory", create_default_auditory_config()),
        ("Interoceptive", create_default_interoceptive_config()),
    ]

    results_summary = []

    for modality_name, config in modalities:
        logger.info(f"\n{'=' * 40}")
        logger.info(f"Testing {modality_name} Modality")
        logger.info(f"{'=' * 40}")

        result = pipeline.run_neural_threshold_estimation(config)

        if result:
            results_summary.append(
                {
                    "modality": modality_name,
                    "threshold": result.behavioral_threshold,
                    "p3b_correlation": result.p3b_amplitude_threshold_correlation,
                    "gamma_correlation": result.gamma_power_threshold_correlation,
                    "validation_confidence": result.validation_confidence,
                }
            )

            logger.info(f"Threshold: {result.behavioral_threshold:.4f}")
            logger.info(
                f"P3b correlation: {result.p3b_amplitude_threshold_correlation:.3f}"
            )
            logger.info(
                f"Gamma correlation: {result.gamma_power_threshold_correlation:.3f}"
            )

    # Summary report
    logger.info("\n" + "=" * 60)
    logger.info("VALIDATION BATTERY SUMMARY")
    logger.info("=" * 60)

    for summary in results_summary:
        logger.info(f"\n{summary['modality']}:")
        logger.info(f"  Threshold: {summary['threshold']:.4f}")
        logger.info(f"  P3b-threshold r: {summary['p3b_correlation']:.3f}")
        logger.info(f"  Gamma-threshold r: {summary['gamma_correlation']:.3f}")
        logger.info(f"  Confidence: {summary['validation_confidence']:.2f}")

    # Save comprehensive results
    output_dir = "complete_validation_results"
    pipeline.save_results(output_dir)
    logger.info(f"\nComplete results saved to {output_dir}/")

    # Cleanup
    pipeline.cleanup()
    logger.info("\nExample 4 completed successfully!")


if __name__ == "__main__":
    """
    Run all examples.

    Note: These examples use simulated data. In a real implementation,
    they would connect to actual stimulus presentation hardware and
    EEG recording equipment.
    """

    logger.info("APGI Framework - Priority 1 Threshold Estimation Examples")
    logger.info("=" * 60)
    logger.info("Note: Using simulated data for demonstration")
    logger.info("=" * 60)

    try:
        # Run examples
        example_basic_threshold_estimation()
        example_neural_validation()
        example_test_retest_reliability()
        example_complete_validation_battery()

        logger.info("\n" + "=" * 60)
        logger.info("All examples completed successfully!")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Error running examples: {e}", exc_info=True)
