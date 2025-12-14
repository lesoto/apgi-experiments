"""
Example usage of the experimental control and stimulus presentation system.

Demonstrates how to use the MultiModalTaskManager, AdaptiveStaircase,
and TimingController for a complete experimental paradigm.
"""

import logging
from typing import List

from .multi_modal_task_manager import (
    MultiModalTaskManager,
    ModalityType,
    TaskParadigm
)
from .adaptive_staircase import (
    StaircaseParameters,
    StaircaseType,
    create_staircase
)
from .precision_timing import (
    TimingController,
    TimingMode
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_detection_threshold_experiment():
    """
    Example: Run a visual detection threshold estimation experiment.
    
    This demonstrates:
    - Multi-modal task management
    - Adaptive staircase for threshold estimation
    - Precision timing and synchronization
    """
    logger.info("=== Starting Detection Threshold Experiment ===")
    
    # Initialize components
    task_manager = MultiModalTaskManager(
        manager_id="detection_exp",
        enable_visual=True,
        enable_auditory=False,
        enable_interoceptive=False
    )
    
    # Initialize task manager
    if not task_manager.initialize():
        logger.error("Failed to initialize task manager")
        return
    
    # Create adaptive staircase for threshold estimation
    staircase_params = StaircaseParameters(
        staircase_type=StaircaseType.QUEST_PLUS,
        min_intensity=0.01,
        max_intensity=1.0,
        initial_intensity=0.5,
        min_trials=20,
        max_trials=50,
        min_reversals=6
    )
    
    staircase = create_staircase(
        staircase_type=StaircaseType.QUEST_PLUS,
        parameters=staircase_params,
        staircase_id="visual_detection"
    )
    
    # Initialize timing controller
    timing_controller = TimingController(
        controller_id="detection_timing",
        timing_mode=TimingMode.HIGH_PRECISION,
        enable_hardware_sync=False
    )
    
    timing_controller.start_session()
    
    # Run trials
    trial_number = 0
    while staircase.should_continue():
        trial_number += 1
        
        # Get next intensity from staircase
        intensity = staircase.get_next_intensity()
        
        # Create trial configuration
        trial_config = task_manager.create_detection_trial(
            trial_number=trial_number,
            modality=ModalityType.VISUAL,
            intensity=intensity,
            is_target=True
        )
        
        # Mark trial start
        timing_controller.start_trial(trial_number)
        
        # Present trial
        result = task_manager.present_trial(trial_config)
        
        if result:
            # Update staircase with response
            staircase.update(intensity, result.response_detected)
            
            # Log trial result
            logger.info(f"Trial {trial_number}: intensity={intensity:.3f}, "
                       f"detected={result.response_detected}, "
                       f"RT={result.reaction_time_ms:.1f}ms" if result.reaction_time_ms else "no response")
        
        # Mark trial end
        timing_controller.end_trial(trial_number)
    
    # Get threshold estimate
    threshold_estimate = staircase.get_threshold_estimate()
    
    logger.info("\n=== Experiment Complete ===")
    logger.info(f"Threshold estimate: {threshold_estimate.threshold:.4f} ± {threshold_estimate.std_error:.4f}")
    logger.info(f"Converged: {threshold_estimate.converged} after {threshold_estimate.n_trials} trials")
    logger.info(f"Confidence interval: [{threshold_estimate.confidence_interval[0]:.4f}, "
               f"{threshold_estimate.confidence_interval[1]:.4f}]")
    
    # Get performance summary
    performance = task_manager.get_performance_summary()
    logger.info(f"\nPerformance summary:")
    logger.info(f"  Response rate: {performance['response_rate']:.2%}")
    logger.info(f"  Mean RT: {performance['mean_reaction_time_ms']:.1f}ms")
    logger.info(f"  Timing quality: {performance['timing_quality']}")
    
    # Get timing statistics
    timing_stats = timing_controller.get_comprehensive_summary()
    logger.info(f"\nTiming statistics:")
    logger.info(f"  Mean timing error: {timing_stats['timing_statistics']['mean_abs_error_ms']:.3f}ms")
    logger.info(f"  Timing quality: {timing_stats['timing_statistics']['timing_quality']}")
    
    # Cleanup
    task_manager.cleanup()
    
    return threshold_estimate, performance, timing_stats


def run_oddball_paradigm():
    """
    Example: Run a multi-modal oddball paradigm.
    
    This demonstrates:
    - Multi-modal stimulus presentation
    - Trial sequencing and randomization
    - Synchronization markers for neural data
    """
    logger.info("=== Starting Oddball Paradigm ===")
    
    # Initialize task manager with multiple modalities
    task_manager = MultiModalTaskManager(
        manager_id="oddball_exp",
        enable_visual=True,
        enable_auditory=True,
        enable_interoceptive=False
    )
    
    if not task_manager.initialize():
        logger.error("Failed to initialize task manager")
        return
    
    # Initialize timing controller with hardware sync
    timing_controller = TimingController(
        controller_id="oddball_timing",
        timing_mode=TimingMode.HIGH_PRECISION,
        enable_hardware_sync=True  # Enable for EEG synchronization
    )
    
    timing_controller.start_session()
    
    # Create trial sequence (80% standard, 20% oddball)
    trial_types = ['standard'] * 80 + ['oddball'] * 20
    
    sequence = timing_controller.sequencer.create_sequence(
        trial_types=trial_types,
        n_repetitions=1,
        randomize=True,
        random_seed=42
    )
    
    logger.info(f"Created sequence with {len(sequence)} trials")
    
    # Run trials
    trial_number = 0
    while timing_controller.sequencer.has_more_trials():
        trial_spec = timing_controller.sequencer.get_next_trial()
        trial_number += 1
        
        is_oddball = trial_spec['trial_type'] == 'oddball'
        
        # Alternate between visual and auditory modalities
        modality = ModalityType.VISUAL if trial_number % 2 == 0 else ModalityType.AUDITORY
        
        # Create trial configuration
        trial_config = task_manager.create_oddball_trial(
            trial_number=trial_number,
            modality=modality,
            is_oddball=is_oddball
        )
        
        # Mark trial start with sync marker
        timing_controller.start_trial(trial_number)
        
        # Present trial
        result = task_manager.present_trial(trial_config)
        
        if result:
            logger.info(f"Trial {trial_number} ({trial_spec['trial_type']}): "
                       f"modality={modality.value}, "
                       f"detected={result.response_detected}, "
                       f"correct={result.correct}")
        
        # Mark trial end
        timing_controller.end_trial(trial_number)
    
    # Get results
    performance = task_manager.get_performance_summary()
    timing_summary = timing_controller.get_comprehensive_summary()
    
    logger.info("\n=== Oddball Paradigm Complete ===")
    logger.info(f"Accuracy: {performance['accuracy']:.2%}")
    logger.info(f"Mean RT: {performance['mean_reaction_time_ms']:.1f}ms")
    logger.info(f"Synchronization markers sent: {timing_summary['synchronization_summary']['total_markers']}")
    
    # Cleanup
    task_manager.cleanup()
    
    return performance, timing_summary


def run_cross_modal_threshold_comparison():
    """
    Example: Compare thresholds across visual, auditory, and interoceptive modalities.
    
    This demonstrates:
    - Cross-modal threshold estimation
    - Threshold normalization
    - Multi-modal task management
    """
    logger.info("=== Starting Cross-Modal Threshold Comparison ===")
    
    from .adaptive_staircase import CrossModalThresholdNormalizer
    
    # Initialize task manager with all modalities
    task_manager = MultiModalTaskManager(
        manager_id="crossmodal_exp",
        enable_visual=True,
        enable_auditory=True,
        enable_interoceptive=True
    )
    
    if not task_manager.initialize():
        logger.error("Failed to initialize task manager")
        return
    
    # Initialize threshold normalizer
    normalizer = CrossModalThresholdNormalizer()
    
    # Test each modality
    modalities = [
        (ModalityType.VISUAL, "visual"),
        (ModalityType.AUDITORY, "auditory"),
        (ModalityType.INTEROCEPTIVE, "interoceptive")
    ]
    
    threshold_estimates = {}
    
    for modality, modality_name in modalities:
        logger.info(f"\n--- Testing {modality_name} modality ---")
        
        # Create staircase
        staircase_params = StaircaseParameters(
            staircase_type=StaircaseType.QUEST_PLUS,
            min_intensity=0.01,
            max_intensity=1.0,
            min_trials=15,
            max_trials=30
        )
        
        staircase = create_staircase(
            staircase_type=StaircaseType.QUEST_PLUS,
            parameters=staircase_params,
            staircase_id=f"{modality_name}_threshold"
        )
        
        # Run threshold estimation
        trial_number = 0
        while staircase.should_continue():
            trial_number += 1
            intensity = staircase.get_next_intensity()
            
            trial_config = task_manager.create_detection_trial(
                trial_number=trial_number,
                modality=modality,
                intensity=intensity,
                is_target=True
            )
            
            result = task_manager.present_trial(trial_config)
            
            if result:
                staircase.update(intensity, result.response_detected)
        
        # Get threshold estimate
        threshold = staircase.get_threshold_estimate()
        threshold_estimates[modality_name] = threshold
        
        # Set detection threshold for normalization
        normalizer.set_detection_threshold(modality_name, threshold.threshold)
        
        logger.info(f"{modality_name} threshold: {threshold.threshold:.4f} ± {threshold.std_error:.4f}")
    
    # Compare thresholds
    logger.info("\n=== Cross-Modal Comparison ===")
    
    # Compare visual to auditory
    ratio_va = normalizer.compare_thresholds(
        "visual", threshold_estimates["visual"].threshold,
        "auditory", threshold_estimates["auditory"].threshold
    )
    if ratio_va:
        logger.info(f"Visual/Auditory threshold ratio: {ratio_va:.3f}")
    
    # Compare visual to interoceptive
    ratio_vi = normalizer.compare_thresholds(
        "visual", threshold_estimates["visual"].threshold,
        "interoceptive", threshold_estimates["interoceptive"].threshold
    )
    if ratio_vi:
        logger.info(f"Visual/Interoceptive threshold ratio: {ratio_vi:.3f}")
    
    # Get normalizer summary
    summary = normalizer.get_summary()
    logger.info(f"\nNormalized thresholds: {summary['normalized_thresholds']}")
    
    # Cleanup
    task_manager.cleanup()
    
    return threshold_estimates, summary


if __name__ == "__main__":
    # Run example experiments
    
    # Example 1: Simple detection threshold estimation
    print("\n" + "="*60)
    print("EXAMPLE 1: Detection Threshold Estimation")
    print("="*60)
    threshold, perf, timing = run_detection_threshold_experiment()
    
    # Example 2: Oddball paradigm with synchronization
    print("\n" + "="*60)
    print("EXAMPLE 2: Oddball Paradigm")
    print("="*60)
    oddball_perf, oddball_timing = run_oddball_paradigm()
    
    # Example 3: Cross-modal threshold comparison
    print("\n" + "="*60)
    print("EXAMPLE 3: Cross-Modal Threshold Comparison")
    print("="*60)
    thresholds, norm_summary = run_cross_modal_threshold_comparison()
    
    print("\n" + "="*60)
    print("All examples completed successfully!")
    print("="*60)
