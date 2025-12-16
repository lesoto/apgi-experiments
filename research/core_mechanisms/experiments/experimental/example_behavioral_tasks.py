"""
Example usage of the three core behavioral tasks for parameter estimation.

Demonstrates how to run the detection task, heartbeat detection task, and
dual-modality oddball task for extracting θ₀, Πᵢ, and β parameters.
"""

import logging
from pathlib import Path
import numpy as np

from .behavioral_tasks import (
    DetectionTask,
    HeartbeatDetectionTask,
    DualModalityOddballTask
)
from ..data.parameter_estimation_dao import ParameterEstimationDAO
from ..data.parameter_estimation_models import SessionData

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def example_detection_task():
    """
    Example: Run detection task for θ₀ estimation.
    
    This task presents Gabor patches or tones at varying intensities using
    an adaptive staircase procedure to estimate the baseline ignition threshold.
    """
    logger.info("=" * 60)
    logger.info("EXAMPLE: Detection Task for θ₀ Estimation")
    logger.info("=" * 60)
    
    # Create task
    task = DetectionTask(
        task_id="example_detection",
        modality="visual",  # or "auditory"
        n_trials=50,  # Reduced for example
        duration_minutes=5.0,
        participant_id="P001",
        session_id="S001"
    )
    
    # Initialize task
    if not task.initialize():
        logger.error("Failed to initialize detection task")
        return
    
    # Run task
    logger.info("Running detection task...")
    success = task.run()
    
    if success:
        # Get results
        results = task.get_results()
        logger.info("\nDetection Task Results:")
        logger.info(f"  Trials completed: {results['n_trials_completed']}")
        logger.info(f"  Threshold estimate (θ₀): {results['threshold_estimate']:.4f} ± {results['threshold_std']:.4f}")
        logger.info(f"  Hit rate: {results['hit_rate']:.3f}")
        logger.info(f"  Mean RT: {results['mean_reaction_time_ms']:.1f} ms")
        logger.info(f"  Staircase converged: {results['staircase_converged']}")
        
        # Simulate P3b validation
        logger.info("\nSimulating P3b validation...")
        simulated_p3b = [np.random.normal(5.0, 1.0) for _ in range(len(task.trials))]
        validation = task.validate_with_p3b(simulated_p3b)
        logger.info(f"  P3b correlation: r={validation.get('correlation', 0):.3f}")
        logger.info(f"  Validation passed: {validation.get('valid', False)}")
    
    # Cleanup
    task.cleanup()
    logger.info("Detection task completed\n")


def example_heartbeat_detection_task():
    """
    Example: Run heartbeat detection task for Πᵢ estimation.
    
    This task presents tones synchronized or asynchronized with heartbeat
    to measure interoceptive precision.
    """
    logger.info("=" * 60)
    logger.info("EXAMPLE: Heartbeat Detection Task for Πᵢ Estimation")
    logger.info("=" * 60)
    
    # Create task
    task = HeartbeatDetectionTask(
        task_id="example_heartbeat",
        n_trials=30,  # Reduced for example
        duration_minutes=4.0,
        participant_id="P001",
        session_id="S001"
    )
    
    # Initialize task
    if not task.initialize():
        logger.error("Failed to initialize heartbeat detection task")
        return
    
    # Run task
    logger.info("Running heartbeat detection task...")
    success = task.run()
    
    if success:
        # Get results
        results = task.get_results()
        logger.info("\nHeartbeat Detection Task Results:")
        logger.info(f"  Trials completed: {results['n_trials_completed']}")
        logger.info(f"  d' (sensitivity): {results['d_prime']:.3f}")
        logger.info(f"  Accuracy: {results['accuracy']:.3f}")
        logger.info(f"  Mean RT: {results['mean_reaction_time_ms']:.1f} ms")
        logger.info(f"  Final asynchrony: {results['final_asynchrony_ms']:.1f} ms")
        
        if results['confidence_analysis']:
            conf_analysis = results['confidence_analysis']
            logger.info(f"  Confidence-accuracy correlation: {conf_analysis['confidence_accuracy_correlation']:.3f}")
            logger.info(f"  Metacognitive sensitivity: {conf_analysis['metacognitive_sensitivity']:.3f}")
        
        # Simulate pupillometry integration
        logger.info("\nSimulating pupillometry integration...")
        simulated_pupil = [
            {
                'baseline': np.random.uniform(3.0, 4.0),
                'peak': np.random.uniform(3.5, 4.5),
                'time_to_peak': np.random.uniform(200, 500)
            }
            for _ in range(len(task.trials))
        ]
        task.integrate_pupillometry(simulated_pupil)
        logger.info("  Pupillometry data integrated")
        
        # Simulate HEP integration
        simulated_hep = [np.random.normal(2.0, 0.5) for _ in range(len(task.trials))]
        task.integrate_hep(simulated_hep)
        logger.info("  HEP data integrated")
    
    # Cleanup
    task.cleanup()
    logger.info("Heartbeat detection task completed\n")


def example_oddball_task():
    """
    Example: Run dual-modality oddball task for β estimation.
    
    This task presents precision-matched interoceptive and exteroceptive
    deviants to measure somatic bias.
    """
    logger.info("=" * 60)
    logger.info("EXAMPLE: Dual-Modality Oddball Task for β Estimation")
    logger.info("=" * 60)
    
    # Create task
    task = DualModalityOddballTask(
        task_id="example_oddball",
        n_trials=60,  # Reduced for example
        duration_minutes=6.0,
        deviant_probability=0.2,
        participant_id="P001",
        session_id="S001"
    )
    
    # Initialize task (includes calibration)
    logger.info("Initializing task (includes stimulus calibration)...")
    if not task.initialize():
        logger.error("Failed to initialize oddball task")
        return
    
    # Run task
    logger.info("Running oddball task...")
    success = task.run()
    
    if success:
        # Get results
        results = task.get_results()
        logger.info("\nOddball Task Results:")
        logger.info(f"  Trials completed: {results['n_trials_completed']}")
        logger.info(f"  Interoceptive deviants: {results['n_interoceptive_deviants']}")
        logger.info(f"  Exteroceptive deviants: {results['n_exteroceptive_deviants']}")
        logger.info(f"  Interoceptive detection rate: {results['interoceptive_detection_rate']:.3f}")
        logger.info(f"  Exteroceptive detection rate: {results['exteroceptive_detection_rate']:.3f}")
        logger.info(f"  Mean RT: {results['mean_reaction_time_ms']:.1f} ms")
        logger.info(f"  Interoceptive threshold: {results['intero_threshold']:.4f}")
        logger.info(f"  Exteroceptive threshold: {results['extero_threshold']:.4f}")
        
        # Simulate EEG P3b integration
        logger.info("\nSimulating EEG P3b integration...")
        simulated_p3b = []
        for trial in task.trials:
            if trial.deviant_type == 'interoceptive':
                p3b_amp = np.random.normal(6.0, 1.5)  # Higher for interoceptive
            elif trial.deviant_type == 'exteroceptive':
                p3b_amp = np.random.normal(4.0, 1.0)  # Lower for exteroceptive
            else:
                p3b_amp = np.random.normal(2.0, 0.5)  # Baseline for standards
            
            simulated_p3b.append({'amplitude': p3b_amp})
        
        task.integrate_eeg_p3b(simulated_p3b)
        
        # Get updated results with P3b ratio
        results = task.get_results()
        if results['p3b_ratio']:
            logger.info(f"  P3b ratio (β estimate): {results['p3b_ratio']:.3f}")
            
            if results['p3b_statistics']:
                stats = results['p3b_statistics']
                logger.info(f"  Interoceptive P3b: {stats['interoceptive_p3b_mean']:.2f} μV")
                logger.info(f"  Exteroceptive P3b: {stats['exteroceptive_p3b_mean']:.2f} μV")
    
    # Cleanup
    task.cleanup()
    logger.info("Oddball task completed\n")


def example_complete_session():
    """
    Example: Run complete parameter estimation session with all three tasks.
    
    This demonstrates a full session workflow for extracting all three
    APGI parameters: θ₀, Πᵢ, and β.
    """
    logger.info("=" * 60)
    logger.info("EXAMPLE: Complete Parameter Estimation Session")
    logger.info("=" * 60)
    
    participant_id = "P001"
    session_id = "S001_complete"
    
    # Create session data structure
    session = SessionData(
        session_id=session_id,
        participant_id=participant_id,
        protocol_version="1.0.0",
        researcher="Example Researcher"
    )
    
    logger.info(f"\nSession: {session_id}")
    logger.info(f"Participant: {participant_id}")
    logger.info(f"Protocol: {session.protocol_version}\n")
    
    # Task 1: Detection task for θ₀
    logger.info("Task 1/3: Detection Task (θ₀ estimation)")
    logger.info("-" * 60)
    detection_task = DetectionTask(
        task_id="session_detection",
        modality="visual",
        n_trials=50,
        participant_id=participant_id,
        session_id=session_id
    )
    
    if detection_task.initialize():
        detection_task.run()
        detection_results = detection_task.get_results()
        logger.info(f"✓ θ₀ estimate: {detection_results['threshold_estimate']:.4f}")
        detection_task.cleanup()
    
    logger.info("\nInter-task interval: 60 seconds\n")
    
    # Task 2: Heartbeat detection for Πᵢ
    logger.info("Task 2/3: Heartbeat Detection Task (Πᵢ estimation)")
    logger.info("-" * 60)
    heartbeat_task = HeartbeatDetectionTask(
        task_id="session_heartbeat",
        n_trials=30,
        participant_id=participant_id,
        session_id=session_id
    )
    
    if heartbeat_task.initialize():
        heartbeat_task.run()
        heartbeat_results = heartbeat_task.get_results()
        logger.info(f"✓ Πᵢ estimate (d'): {heartbeat_results['d_prime']:.3f}")
        heartbeat_task.cleanup()
    
    logger.info("\nInter-task interval: 60 seconds\n")
    
    # Task 3: Oddball task for β
    logger.info("Task 3/3: Dual-Modality Oddball Task (β estimation)")
    logger.info("-" * 60)
    oddball_task = DualModalityOddballTask(
        task_id="session_oddball",
        n_trials=60,
        participant_id=participant_id,
        session_id=session_id
    )
    
    if oddball_task.initialize():
        oddball_task.run()
        
        # Simulate P3b integration
        simulated_p3b = []
        for trial in oddball_task.trials:
            if trial.deviant_type == 'interoceptive':
                p3b_amp = np.random.normal(6.0, 1.5)
            elif trial.deviant_type == 'exteroceptive':
                p3b_amp = np.random.normal(4.0, 1.0)
            else:
                p3b_amp = np.random.normal(2.0, 0.5)
            simulated_p3b.append({'amplitude': p3b_amp})
        
        oddball_task.integrate_eeg_p3b(simulated_p3b)
        oddball_results = oddball_task.get_results()
        logger.info(f"✓ β estimate (P3b ratio): {oddball_results['p3b_ratio']:.3f}")
        oddball_task.cleanup()
    
    # Session summary
    logger.info("\n" + "=" * 60)
    logger.info("SESSION SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Participant: {participant_id}")
    logger.info(f"Session: {session_id}")
    logger.info("\nParameter Estimates:")
    logger.info(f"  θ₀ (Baseline Ignition Threshold): {detection_results['threshold_estimate']:.4f}")
    logger.info(f"  Πᵢ (Interoceptive Precision, d'): {heartbeat_results['d_prime']:.3f}")
    logger.info(f"  β (Somatic Bias, P3b ratio): {oddball_results['p3b_ratio']:.3f}")
    logger.info("\nSession completed successfully!")
    logger.info("=" * 60)


if __name__ == "__main__":
    """Run all examples."""
    
    print("\n" + "=" * 70)
    print("APGI FRAMEWORK - BEHAVIORAL TASKS EXAMPLES")
    print("=" * 70 + "\n")
    
    # Run individual task examples
    example_detection_task()
    example_heartbeat_detection_task()
    example_oddball_task()
    
    # Run complete session example
    example_complete_session()
    
    print("\n" + "=" * 70)
    print("ALL EXAMPLES COMPLETED")
    print("=" * 70 + "\n")
