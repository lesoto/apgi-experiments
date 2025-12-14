"""
Example usage of the neural data acquisition and processing pipeline.

Demonstrates integration of EEG interface, ERP analysis, microstate analysis,
and gamma synchrony detection for APGI framework validation.
"""

import numpy as np
from apgi_framework.neural import (
    EEGInterface, EEGConfig, ChannelInfo, ChannelType,
    ERPAnalysis, MicrostateAnalysis, GammaSynchronyAnalysis
)


def example_eeg_acquisition():
    """Example: Real-time EEG data acquisition."""
    print("=== EEG Data Acquisition Example ===\n")
    
    # Configure channels
    channels = [
        ChannelInfo("Fz", ChannelType.EEG, position=(0, 0.5, 0.8)),
        ChannelInfo("Cz", ChannelType.EEG, position=(0, 0, 1.0)),
        ChannelInfo("Pz", ChannelType.EEG, position=(0, -0.5, 0.8)),
        ChannelInfo("Oz", ChannelType.EEG, position=(0, -0.8, 0.5)),
    ]
    
    # Create configuration
    config = EEGConfig(
        sampling_rate=1000.0,
        buffer_size=10000,
        channels=channels,
        reference_type="average",
        artifact_threshold=100.0
    )
    
    # Initialize interface
    eeg = EEGInterface(config)
    
    # Register callback for real-time processing
    artifact_count = [0]
    
    def process_callback(data, timestamp, artifacts):
        if artifacts['any'].any():
            artifact_count[0] += 1
    
    eeg.register_callback(process_callback)
    
    # Simulate streaming for 2 seconds
    print("Starting data acquisition...")
    eeg.start_streaming()
    
    import time
    time.sleep(2.0)
    
    eeg.stop_streaming()
    
    # Check signal quality
    quality = eeg.check_signal_quality()
    print(f"Signal quality: {quality['status']}")
    print(f"Samples acquired: {quality['samples_acquired']}")
    print(f"Artifact rate: {quality['artifact_rate']:.3f}")
    print(f"Duration: {quality['duration_seconds']:.1f} seconds\n")
    
    return eeg


def example_erp_analysis():
    """Example: ERP component extraction."""
    print("=== ERP Analysis Example ===\n")
    
    # Simulate ERP data (4 channels x 1000 samples = 1 second at 1000 Hz)
    sampling_rate = 1000.0
    n_channels = 4
    n_samples = 1000
    
    # Create synthetic P3b-like waveform
    time = np.arange(n_samples) / sampling_rate * 1000  # ms
    
    # P3b: Gaussian centered at 400ms
    p3b = 10 * np.exp(-0.5 * ((time - 400) / 80) ** 2)
    
    # N1: Negative peak at 150ms
    n1 = -5 * np.exp(-0.5 * ((time - 150) / 30) ** 2)
    
    # P1: Positive peak at 100ms
    p1 = 3 * np.exp(-0.5 * ((time - 100) / 20) ** 2)
    
    # Combine components and add noise
    erp_signal = p3b + n1 + p1 + np.random.randn(n_samples) * 2
    
    # Replicate across channels
    erp_data = np.tile(erp_signal, (n_channels, 1))
    
    # Initialize analyzer
    erp = ERPAnalysis(sampling_rate=sampling_rate)
    
    # Extract all components
    components = erp.extract_all_components(
        data=erp_data[2],  # Use Pz channel
        time_zero_idx=200,  # Stimulus at 200ms
        channel="Pz"
    )
    
    print(f"P3b amplitude: {components.p3b_amplitude:.2f} µV")
    print(f"P3b latency: {components.p3b_latency:.2f} ms")
    print(f"P3b area: {components.p3b_area:.2f} µV·ms")
    print(f"P1 amplitude: {components.p1_amplitude:.2f} µV")
    print(f"N1 amplitude: {components.n1_amplitude:.2f} µV")
    print(f"Signal-to-noise ratio: {components.snr:.2f}\n")
    
    return erp, erp_data


def example_microstate_analysis():
    """Example: Microstate clustering and temporal dynamics."""
    print("=== Microstate Analysis Example ===\n")
    
    # Simulate EEG data (32 channels x 10000 samples = 10 seconds)
    n_channels = 32
    n_samples = 10000
    sampling_rate = 1000.0
    
    # Create synthetic data with 4 distinct topographies
    np.random.seed(42)
    
    # Define 4 template topographies
    templates = np.random.randn(n_channels, 4)
    for i in range(4):
        templates[:, i] = templates[:, i] / np.linalg.norm(templates[:, i])
    
    # Create sequence by randomly switching between templates
    data = np.zeros((n_channels, n_samples))
    current_state = 0
    
    for i in range(n_samples):
        # Switch state occasionally
        if i % 100 == 0:
            current_state = np.random.randint(0, 4)
        
        # Add template with noise
        data[:, i] = templates[:, current_state] * 10 + np.random.randn(n_channels) * 2
    
    # Initialize analyzer
    ms = MicrostateAnalysis(n_states=4, sampling_rate=sampling_rate)
    
    # Fit templates
    print("Fitting microstate templates...")
    fitted_templates = ms.fit_microstates(data, use_gfp_peaks=True)
    print(f"Fitted {fitted_templates.shape[1]} microstate templates\n")
    
    # Analyze sequence
    sequence = ms.analyze_sequence(data, smooth=True)
    
    print("Temporal metrics:")
    print(f"  Total segments: {len(sequence.durations)}")
    print(f"  State occurrences: {sequence.occurrences}")
    print(f"  State coverage (%): {sequence.coverage}")
    print(f"\nTransition matrix:")
    print(sequence.transition_matrix)
    print()
    
    return ms, sequence


def example_gamma_synchrony():
    """Example: Gamma-band coherence and network analysis."""
    print("=== Gamma Synchrony Analysis Example ===\n")
    
    # Simulate EEG data with gamma oscillations
    sampling_rate = 1000.0
    duration = 5.0  # seconds
    n_samples = int(duration * sampling_rate)
    
    # Create two signals with gamma-band coherence
    time = np.arange(n_samples) / sampling_rate
    
    # Gamma oscillation at 40 Hz
    gamma_freq = 40.0
    phase_offset = np.pi / 4  # 45 degree phase lag
    
    signal1 = np.sin(2 * np.pi * gamma_freq * time) + np.random.randn(n_samples) * 0.5
    signal2 = np.sin(2 * np.pi * gamma_freq * time + phase_offset) + np.random.randn(n_samples) * 0.5
    
    # Initialize analyzer
    gamma = GammaSynchronyAnalysis(sampling_rate=sampling_rate)
    
    # Compute coherence
    metrics = gamma.compute_gamma_coherence(
        signal1=signal1,
        signal2=signal2,
        channel_pair=("Frontal", "Posterior")
    )
    
    print(f"Gamma coherence: {metrics.gamma_coherence:.3f}")
    print(f"Peak frequency: {metrics.gamma_peak_freq:.1f} Hz")
    print(f"Peak coherence: {metrics.gamma_peak_coherence:.3f}")
    print(f"Phase locking value: {metrics.phase_locking_value:.3f}\n")
    
    # Compute phase-amplitude coupling
    # Create signal with theta-gamma PAC
    theta_freq = 6.0
    theta_phase = 2 * np.pi * theta_freq * time
    gamma_amp = 1 + 0.5 * np.sin(theta_phase)  # Gamma amplitude modulated by theta
    pac_signal = gamma_amp * np.sin(2 * np.pi * gamma_freq * time)
    
    pac = gamma.compute_phase_amplitude_coupling(
        low_freq_signal=pac_signal,
        high_freq_signal=pac_signal,
        phase_band=(4, 8),
        amp_band=(30, 80)
    )
    
    print(f"Theta-gamma PAC strength: {pac:.3f}\n")
    
    # Detect gamma bursts
    bursts = gamma.detect_gamma_bursts(
        data=signal1,
        threshold=2.0,
        min_duration=50.0
    )
    
    print(f"Detected {len(bursts)} gamma bursts")
    if bursts:
        print(f"  First burst: {bursts[0]['start_time']:.1f} - {bursts[0]['end_time']:.1f} ms")
        print(f"  Duration: {bursts[0]['duration']:.1f} ms")
        print(f"  Peak amplitude: {bursts[0]['peak_amplitude']:.2f}\n")
    
    return gamma, metrics


def example_integrated_pipeline():
    """Example: Integrated neural processing pipeline."""
    print("=== Integrated Pipeline Example ===\n")
    
    # Simulate complete experiment data
    n_channels = 32
    n_trials = 50
    n_samples_per_trial = 1000
    sampling_rate = 1000.0
    
    print(f"Processing {n_trials} trials with {n_channels} channels...")
    
    # Initialize all analyzers
    erp = ERPAnalysis(sampling_rate=sampling_rate)
    ms = MicrostateAnalysis(n_states=4, sampling_rate=sampling_rate)
    gamma = GammaSynchronyAnalysis(sampling_rate=sampling_rate)
    
    # Simulate trials
    all_p3b_amplitudes = []
    all_gamma_coherences = []
    
    for trial in range(n_trials):
        # Generate synthetic trial data
        trial_data = np.random.randn(n_channels, n_samples_per_trial) * 5
        
        # Add P3b to posterior channels
        time = np.arange(n_samples_per_trial)
        p3b = 8 * np.exp(-0.5 * ((time - 400) / 80) ** 2)
        trial_data[20:24, :] += p3b  # Add to posterior channels
        
        # Extract P3b
        components = erp.extract_all_components(
            data=trial_data[22],
            time_zero_idx=200,
            channel="Pz"
        )
        all_p3b_amplitudes.append(components.p3b_amplitude)
        
        # Compute frontal-posterior coherence
        fp_coherence = gamma.compute_frontal_posterior_coherence(
            data=trial_data,
            frontal_channels=[0, 1, 2],
            posterior_channels=[20, 21, 22]
        )
        all_gamma_coherences.append(fp_coherence)
    
    # Summary statistics
    print(f"\nResults across {n_trials} trials:")
    print(f"  Mean P3b amplitude: {np.mean(all_p3b_amplitudes):.2f} ± {np.std(all_p3b_amplitudes):.2f} µV")
    print(f"  Mean gamma coherence: {np.mean(all_gamma_coherences):.3f} ± {np.std(all_gamma_coherences):.3f}")
    
    # Test APGI prediction: P3b amplitude should correlate with gamma coherence
    correlation = np.corrcoef(all_p3b_amplitudes, all_gamma_coherences)[0, 1]
    print(f"  P3b-gamma correlation: r = {correlation:.3f}")
    print("\nIntegrated pipeline complete!\n")


if __name__ == "__main__":
    print("Neural Data Processing Pipeline Examples")
    print("=" * 50)
    print()
    
    # Run examples
    example_eeg_acquisition()
    example_erp_analysis()
    example_microstate_analysis()
    example_gamma_synchrony()
    example_integrated_pipeline()
    
    print("All examples completed successfully!")
