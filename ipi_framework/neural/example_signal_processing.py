"""
Example usage of the real-time signal processing pipeline.

Demonstrates integration of EEG, pupillometry, and cardiac processing
with quality control for parameter estimation experiments.
"""

import numpy as np
from ipi_framework.neural import (
    # Signal processors
    EEGProcessor,
    PupillometryProcessor,
    CardiacProcessor,
    
    # Feature extractors
    ERPExtractor,
    PupilFeatureExtractor,
    HRVAnalyzer,
    HEPExtractor,
    
    # Quality control
    SignalQualityMonitor,
    OperatorNotificationSystem,
    
    # Data acquisition interfaces
    EEGInterface,
    EEGConfig,
    PupillometryInterface,
    PupillometryConfig,
    PhysiologicalMonitoring,
    PhysiologicalConfig
)


def example_eeg_processing():
    """Example: EEG signal processing with artifact detection and ERP extraction."""
    print("=== EEG Signal Processing Example ===\n")
    
    # Initialize EEG processor
    eeg_processor = EEGProcessor(
        sampling_rate=1000.0,
        highpass=0.1,
        lowpass=30.0,
        notch_freq=60.0
    )
    
    # Simulate EEG data (10 channels, 5 seconds)
    n_channels = 10
    n_samples = 5000
    sampling_rate = 1000.0
    
    # Generate synthetic EEG with some noise
    t = np.arange(n_samples) / sampling_rate
    eeg_data = np.random.randn(n_channels, n_samples) * 10.0
    
    # Add some alpha oscillations (10 Hz)
    for ch in range(n_channels):
        eeg_data[ch, :] += 20 * np.sin(2 * np.pi * 10 * t)
    
    timestamps = t
    channels = [f'Ch{i+1}' for i in range(n_channels)]
    
    # Process EEG data
    print("Processing EEG data...")
    processed = eeg_processor.process_realtime(eeg_data, timestamps, channels)
    print(f"Processed {processed.data.shape[1]} samples from {processed.data.shape[0]} channels")
    
    # Detect artifacts
    print("\nDetecting artifacts...")
    artifact_detector = eeg_processor.FASTERArtifactDetector(z_threshold=3.0)
    cleaned_data, artifact_report = artifact_detector.clean(processed.data)
    print(f"Artifact report: {artifact_report}")
    
    # Extract ERPs
    print("\nExtracting ERPs...")
    erp_extractor = ERPExtractor(sampling_rate=sampling_rate)
    
    # Simulate event times
    event_times = np.array([1.0, 2.0, 3.0, 4.0])
    
    # Extract P3b features (assuming Pz is channel 5)
    pz_channel_idx = 5
    features = erp_extractor.extract_features(
        cleaned_data,
        event_times,
        timestamps,
        pz_channel_idx
    )
    
    print(f"P3b amplitude: {features.p3b_amplitude:.2f} µV" if features.p3b_amplitude else "P3b: Not detected")
    print(f"P3b latency: {features.p3b_latency:.3f} s" if features.p3b_latency else "")
    
    print("\n✓ EEG processing complete\n")


def example_pupillometry_processing():
    """Example: Pupillometry signal processing with feature extraction."""
    print("=== Pupillometry Signal Processing Example ===\n")
    
    # Initialize pupillometry processor
    pupil_processor = PupillometryProcessor(sampling_rate=1000.0)
    
    # Simulate pupil data (5 seconds)
    n_samples = 5000
    sampling_rate = 1000.0
    t = np.arange(n_samples) / sampling_rate
    
    # Generate synthetic pupil diameter with dilation response
    baseline_diameter = 4.0  # mm
    pupil_data = baseline_diameter + 0.3 * np.random.randn(n_samples)
    
    # Add dilation response at t=1s
    stimulus_time = 1.0
    response_window = (t > stimulus_time) & (t < stimulus_time + 1.0)
    pupil_data[response_window] += 0.5 * np.exp(-(t[response_window] - stimulus_time) / 0.3)
    
    # Add some blinks
    blink_times = [0.5, 2.5, 4.0]
    for blink_time in blink_times:
        blink_window = (t > blink_time) & (t < blink_time + 0.15)
        pupil_data[blink_window] = 0  # Simulate blink
    
    timestamps = t
    confidence = np.ones(n_samples) * 0.95
    confidence[pupil_data == 0] = 0.0  # Low confidence during blinks
    
    # Process trial
    print("Processing pupil data...")
    processed = pupil_processor.process_trial(
        pupil_data,
        timestamps,
        confidence,
        baseline_window=(-0.5, 0.0),
        stimulus_time=stimulus_time
    )
    
    print(f"Baseline diameter: {processed['baseline']:.2f} mm")
    print(f"Detected {np.sum(processed['blinks'])} blink samples")
    
    # Extract features
    print("\nExtracting pupil features...")
    feature_extractor = PupilFeatureExtractor(sampling_rate=sampling_rate)
    
    features = feature_extractor.extract_window_features(
        processed['clean_data'],
        timestamps,
        stimulus_time,
        window=(0.2, 0.5),
        baseline=processed['baseline']
    )
    
    print(f"Peak dilation: {features.peak_dilation:.2f} mm")
    print(f"Time to peak: {features.time_to_peak:.0f} ms")
    print(f"Percent change: {features.percent_change:.1f}%")
    print(f"Quality score: {features.quality_score:.2f}")
    
    print("\n✓ Pupillometry processing complete\n")


def example_cardiac_processing():
    """Example: Cardiac signal processing with HRV analysis."""
    print("=== Cardiac Signal Processing Example ===\n")
    
    # Initialize cardiac processor
    cardiac_processor = CardiacProcessor(sampling_rate=1000.0)
    
    # Simulate ECG data (10 seconds)
    n_samples = 10000
    sampling_rate = 1000.0
    t = np.arange(n_samples) / sampling_rate
    
    # Generate synthetic ECG with R-peaks
    heart_rate = 70  # bpm
    rr_interval = 60.0 / heart_rate  # seconds
    
    ecg_signal = np.random.randn(n_samples) * 0.1
    
    # Add R-peaks
    r_peak_times = []
    current_time = 1.0
    while current_time < t[-1] - 1.0:
        peak_idx = int(current_time * sampling_rate)
        # Add QRS complex
        ecg_signal[peak_idx-10:peak_idx+20] += np.concatenate([
            np.linspace(0, -0.5, 10),
            np.linspace(-0.5, 2.0, 15),
            np.linspace(2.0, 0, 15)
        ])
        r_peak_times.append(current_time)
        current_time += rr_interval + np.random.randn() * 0.05  # Add variability
    
    timestamps = t
    
    # Detect R-peaks
    print("Detecting R-peaks...")
    detected_r_peaks = cardiac_processor.detect_r_peaks(ecg_signal, timestamps)
    print(f"Detected {len(detected_r_peaks)} R-peaks")
    
    # Compute HRV metrics
    print("\nComputing HRV metrics...")
    hrv_analyzer = HRVAnalyzer(sampling_rate=sampling_rate)
    
    # Compute RR intervals
    if len(detected_r_peaks) > 1:
        rr_intervals = np.diff(detected_r_peaks) * 1000  # Convert to ms
        
        hrv_metrics = hrv_analyzer.compute_comprehensive_hrv(
            rr_intervals,
            detected_r_peaks
        )
        
        print(f"Mean HR: {hrv_metrics.mean_hr:.1f} bpm")
        print(f"SDNN: {hrv_metrics.sdnn:.1f} ms")
        print(f"RMSSD: {hrv_metrics.rmssd:.1f} ms")
        print(f"pNN50: {hrv_metrics.pnn50:.1f}%")
        
        if hrv_metrics.lf_power:
            print(f"LF/HF ratio: {hrv_metrics.lf_hf_ratio:.2f}")
    
    print("\n✓ Cardiac processing complete\n")


def example_integrated_quality_control():
    """Example: Integrated quality control across all modalities."""
    print("=== Integrated Quality Control Example ===\n")
    
    # Initialize quality monitor
    quality_monitor = SignalQualityMonitor(update_interval=1.0)
    
    # Initialize notification system
    notification_system = OperatorNotificationSystem()
    
    # Register notification callback
    def print_notification(notification):
        print(f"[{notification['type'].upper()}] {notification.get('message', 'Quality update')}")
    
    notification_system.register_callback(print_notification)
    
    # Simulate quality metrics from different modalities
    print("Simulating quality monitoring...\n")
    
    # Good quality scenario
    print("Scenario 1: Good quality data")
    eeg_metrics = {
        'overall_quality': 0.85,
        'artifact_rate': 0.08,
        'bad_channels_count': 1
    }
    pupil_metrics = {
        'overall_quality': 0.90,
        'data_loss_percentage': 5.0,
        'tracking_confidence': 0.92
    }
    cardiac_metrics = {
        'overall_quality': 0.88,
        'signal_quality_index': 0.85,
        'ectopic_beat_percentage': 2.0
    }
    
    quality_metrics = quality_monitor.update_quality_metrics(
        eeg_metrics, pupil_metrics, cardiac_metrics
    )
    
    print(f"Overall quality: {quality_metrics.overall_quality:.2f}")
    print(f"Quality level: {quality_metrics.quality_level.value}")
    print(f"Continue recording: {quality_metrics.continue_recording}")
    print(f"Suggestions: {quality_metrics.suggested_actions[0]}")
    
    notification_system.send_quality_update(quality_metrics)
    
    # Poor quality scenario
    print("\nScenario 2: Poor quality data")
    eeg_metrics = {
        'overall_quality': 0.45,
        'artifact_rate': 0.25,
        'bad_channels_count': 8
    }
    pupil_metrics = {
        'overall_quality': 0.40,
        'data_loss_percentage': 30.0,
        'tracking_confidence': 0.55
    }
    cardiac_metrics = {
        'overall_quality': 0.50,
        'signal_quality_index': 0.60,
        'ectopic_beat_percentage': 8.0
    }
    
    quality_metrics = quality_monitor.update_quality_metrics(
        eeg_metrics, pupil_metrics, cardiac_metrics
    )
    
    print(f"Overall quality: {quality_metrics.overall_quality:.2f}")
    print(f"Quality level: {quality_metrics.quality_level.value}")
    print(f"Continue recording: {quality_metrics.continue_recording}")
    print(f"Active alerts: {quality_metrics.active_alerts}")
    print(f"Suggestions:")
    for suggestion in quality_metrics.suggested_actions[:3]:
        print(f"  - {suggestion}")
    
    notification_system.send_quality_update(quality_metrics)
    
    # Get quality summary
    print("\nQuality summary:")
    summary = quality_monitor.get_quality_summary(window_seconds=60.0)
    if summary['status'] == 'ok':
        print(f"Mean overall quality: {summary['overall_quality_mean']:.2f}")
        print(f"Current quality level: {summary['current_quality_level']}")
    
    print("\n✓ Quality control demonstration complete\n")


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("Real-Time Signal Processing Pipeline Examples")
    print("="*60 + "\n")
    
    # Run examples
    example_eeg_processing()
    example_pupillometry_processing()
    example_cardiac_processing()
    example_integrated_quality_control()
    
    print("="*60)
    print("All examples completed successfully!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
