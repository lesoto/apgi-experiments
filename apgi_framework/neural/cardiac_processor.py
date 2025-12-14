"""
Cardiac signal processing pipeline for parameter estimation.

Provides R-peak detection, HRV analysis, HEP extraction, and quality assessment
for interoceptive precision estimation in APGI experiments.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import numpy as np
from scipy import signal
from scipy.stats import zscore
import time


class RPeakAlgorithm(Enum):
    """R-peak detection algorithms."""
    SIMPLE_THRESHOLD = "simple_threshold"
    PAN_TOMPKINS = "pan_tompkins"
    WAVELET = "wavelet"
    ADAPTIVE = "adaptive"


@dataclass
class HRVMetrics:
    """Heart rate variability metrics."""
    # Time domain metrics
    mean_hr: float  # Mean heart rate (bpm)
    sdnn: float  # Standard deviation of NN intervals (ms)
    rmssd: float  # Root mean square of successive differences (ms)
    pnn50: float  # Percentage of successive differences > 50ms
    
    # Frequency domain metrics
    lf_power: Optional[float] = None  # Low frequency power (0.04-0.15 Hz)
    hf_power: Optional[float] = None  # High frequency power (0.15-0.4 Hz)
    lf_hf_ratio: Optional[float] = None  # LF/HF ratio
    total_power: Optional[float] = None  # Total spectral power
    
    # Additional metrics
    n_beats: int = 0  # Number of beats analyzed
    recording_duration: float = 0.0  # Duration in seconds


@dataclass
class CardiacQualityMetrics:
    """Quality assessment for cardiac signals."""
    overall_quality: float  # Overall quality score (0-1)
    signal_quality_index: float  # SQI based on template matching
    ectopic_beat_percentage: float  # Percentage of ectopic beats
    missed_beat_percentage: float  # Estimated missed beats
    noise_level: float  # Estimated noise level
    recommendation: str  # Quality recommendation


class CardiacProcessor:
    """
    Cardiac signal processor with multiple R-peak detection algorithms.
    
    Integrates existing R-peak detection with additional algorithms
    for robust heartbeat detection in various signal conditions.
    """
    
    def __init__(self, sampling_rate: float = 1000.0,
                 algorithm: RPeakAlgorithm = RPeakAlgorithm.ADAPTIVE,
                 heart_rate_monitor: Optional[Any] = None):
        """
        Initialize cardiac processor.
        
        Args:
            sampling_rate: ECG/PPG sampling rate in Hz
            algorithm: R-peak detection algorithm to use
            heart_rate_monitor: HeartRateMonitor instance (from physiological_monitoring)
        """
        self.sampling_rate = sampling_rate
        self.algorithm = algorithm
        self.heart_rate_monitor = heart_rate_monitor
        
    def preprocess_ecg(self, ecg_signal: np.ndarray) -> np.ndarray:
        """
        Preprocess ECG signal with filtering.
        
        Args:
            ecg_signal: Raw ECG signal
            
        Returns:
            Preprocessed ECG signal
        """
        # Bandpass filter (0.5-40 Hz for ECG)
        nyquist = self.sampling_rate / 2.0
        b, a = signal.butter(4, [0.5 / nyquist, 40.0 / nyquist], btype='bandpass')
        filtered = signal.filtfilt(b, a, ecg_signal)
        
        # Remove baseline wander with high-pass filter
        b_hp, a_hp = signal.butter(2, 0.5 / nyquist, btype='highpass')
        filtered = signal.filtfilt(b_hp, a_hp, filtered)
        
        return filtered
    
    def detect_r_peaks_pan_tompkins(self, ecg_signal: np.ndarray,
                                    timestamps: np.ndarray) -> np.ndarray:
        """
        Detect R-peaks using Pan-Tompkins algorithm.
        
        Args:
            ecg_signal: Preprocessed ECG signal
            timestamps: Timestamp array
            
        Returns:
            Array of R-peak timestamps
        """
        # Derivative (emphasizes QRS slope)
        derivative = np.diff(ecg_signal)
        derivative = np.pad(derivative, (0, 1), mode='edge')
        
        # Squaring (emphasizes higher frequencies)
        squared = derivative ** 2
        
        # Moving window integration
        window_size = int(0.15 * self.sampling_rate)  # 150ms window
        integrated = np.convolve(squared, np.ones(window_size) / window_size, mode='same')
        
        # Adaptive thresholding
        threshold = np.mean(integrated) + 0.5 * np.std(integrated)
        
        # Find peaks above threshold
        peaks = []
        above_threshold = integrated > threshold
        
        in_peak = False
        peak_start = 0
        
        for i in range(len(above_threshold)):
            if above_threshold[i] and not in_peak:
                in_peak = True
                peak_start = i
            elif not above_threshold[i] and in_peak:
                # Find maximum in original signal within this region
                peak_region = ecg_signal[peak_start:i]
                if len(peak_region) > 0:
                    peak_idx = peak_start + np.argmax(peak_region)
                    peaks.append(timestamps[peak_idx])
                in_peak = False
        
        # Filter by physiological constraints (40-200 bpm)
        if len(peaks) > 1:
            min_rr_interval = 60.0 / 200.0  # 200 bpm max
            filtered_peaks = [peaks[0]]
            
            for peak in peaks[1:]:
                if peak - filtered_peaks[-1] >= min_rr_interval:
                    filtered_peaks.append(peak)
            
            peaks = filtered_peaks
        
        return np.array(peaks)
    
    def detect_r_peaks_adaptive(self, ecg_signal: np.ndarray,
                               timestamps: np.ndarray) -> np.ndarray:
        """
        Detect R-peaks using adaptive threshold method.
        
        Args:
            ecg_signal: Preprocessed ECG signal
            timestamps: Timestamp array
            
        Returns:
            Array of R-peak timestamps
        """
        # Compute adaptive threshold using moving statistics
        window_size = int(0.5 * self.sampling_rate)  # 500ms window
        
        peaks = []
        threshold_history = []
        
        for i in range(window_size, len(ecg_signal) - window_size, window_size // 4):
            window = ecg_signal[i - window_size:i + window_size]
            
            # Adaptive threshold: mean + k * std
            threshold = np.mean(window) + 0.6 * np.std(window)
            threshold_history.append(threshold)
            
            # Find peaks in window
            window_peaks = signal.find_peaks(
                ecg_signal[i:i + window_size],
                height=threshold,
                distance=int(0.3 * self.sampling_rate)  # Min 300ms between peaks
            )[0]
            
            # Convert to timestamps
            for peak_idx in window_peaks:
                peaks.append(timestamps[i + peak_idx])
        
        return np.array(peaks)
    
    def detect_r_peaks(self, ecg_signal: np.ndarray,
                      timestamps: np.ndarray) -> np.ndarray:
        """
        Detect R-peaks using configured algorithm.
        
        Args:
            ecg_signal: ECG signal (raw or preprocessed)
            timestamps: Timestamp array
            
        Returns:
            Array of R-peak timestamps
        """
        # Preprocess signal
        preprocessed = self.preprocess_ecg(ecg_signal)
        
        # Use configured algorithm
        if self.algorithm == RPeakAlgorithm.PAN_TOMPKINS:
            r_peaks = self.detect_r_peaks_pan_tompkins(preprocessed, timestamps)
        
        elif self.algorithm == RPeakAlgorithm.ADAPTIVE:
            r_peaks = self.detect_r_peaks_adaptive(preprocessed, timestamps)
        
        elif self.algorithm == RPeakAlgorithm.SIMPLE_THRESHOLD:
            # Use existing heart rate monitor if available
            if self.heart_rate_monitor:
                r_peaks = self.heart_rate_monitor.detect_r_peaks(preprocessed, timestamps)
            else:
                # Fallback to adaptive
                r_peaks = self.detect_r_peaks_adaptive(preprocessed, timestamps)
        
        else:
            # Default to adaptive
            r_peaks = self.detect_r_peaks_adaptive(preprocessed, timestamps)
        
        return r_peaks
    
    def correct_ectopic_beats(self, rr_intervals: np.ndarray,
                             threshold: float = 0.2) -> Tuple[np.ndarray, np.ndarray]:
        """
        Detect and correct ectopic beats (abnormal heartbeats).
        
        Args:
            rr_intervals: RR interval array (ms)
            threshold: Threshold for detecting ectopic beats (relative change)
            
        Returns:
            Tuple of (corrected RR intervals, ectopic beat mask)
        """
        if len(rr_intervals) < 3:
            return rr_intervals, np.zeros(len(rr_intervals), dtype=bool)
        
        # Compute successive differences
        successive_diffs = np.abs(np.diff(rr_intervals))
        relative_diffs = successive_diffs / rr_intervals[:-1]
        
        # Detect ectopic beats (large relative changes)
        ectopic = np.zeros(len(rr_intervals), dtype=bool)
        ectopic[1:] = relative_diffs > threshold
        
        # Correct ectopic beats by interpolation
        corrected = rr_intervals.copy()
        for i in np.where(ectopic)[0]:
            if i > 0 and i < len(corrected) - 1:
                # Interpolate from neighbors
                corrected[i] = (corrected[i-1] + corrected[i+1]) / 2
        
        return corrected, ectopic


class HRVAnalyzer:
    """
    Heart rate variability analyzer with time and frequency domain metrics.
    
    Extends existing HRV metrics with frequency domain analysis
    for comprehensive autonomic assessment.
    """
    
    def __init__(self, sampling_rate: float = 1000.0):
        """
        Initialize HRV analyzer.
        
        Args:
            sampling_rate: Sampling rate for interpolation
        """
        self.sampling_rate = sampling_rate
    
    def compute_time_domain_metrics(self, rr_intervals: np.ndarray) -> Dict[str, float]:
        """
        Compute time domain HRV metrics.
        
        Args:
            rr_intervals: RR interval array (ms)
            
        Returns:
            Dictionary with time domain metrics
        """
        if len(rr_intervals) < 2:
            return {
                'mean_hr': 0.0,
                'sdnn': 0.0,
                'rmssd': 0.0,
                'pnn50': 0.0
            }
        
        # Mean heart rate
        mean_rr = np.mean(rr_intervals)
        mean_hr = 60000.0 / mean_rr if mean_rr > 0 else 0.0
        
        # SDNN: Standard deviation of NN intervals
        sdnn = np.std(rr_intervals)
        
        # RMSSD: Root mean square of successive differences
        successive_diffs = np.diff(rr_intervals)
        rmssd = np.sqrt(np.mean(successive_diffs ** 2))
        
        # pNN50: Percentage of successive differences > 50ms
        pnn50 = np.sum(np.abs(successive_diffs) > 50) / len(successive_diffs) * 100
        
        return {
            'mean_hr': float(mean_hr),
            'sdnn': float(sdnn),
            'rmssd': float(rmssd),
            'pnn50': float(pnn50)
        }
    
    def compute_frequency_domain_metrics(self, rr_intervals: np.ndarray,
                                        r_peak_times: np.ndarray) -> Dict[str, float]:
        """
        Compute frequency domain HRV metrics using Welch's method.
        
        Args:
            rr_intervals: RR interval array (ms)
            r_peak_times: R-peak timestamps (seconds)
            
        Returns:
            Dictionary with frequency domain metrics
        """
        if len(rr_intervals) < 10:
            return {
                'lf_power': 0.0,
                'hf_power': 0.0,
                'lf_hf_ratio': 0.0,
                'total_power': 0.0
            }
        
        # Interpolate RR intervals to uniform sampling
        # Create uniform time base
        duration = r_peak_times[-1] - r_peak_times[0]
        uniform_time = np.arange(0, duration, 1.0 / 4.0)  # 4 Hz sampling
        
        # Interpolate RR intervals
        interp_rr = np.interp(uniform_time, r_peak_times[1:], rr_intervals)
        
        # Compute power spectral density using Welch's method
        freqs, psd = signal.welch(
            interp_rr,
            fs=4.0,  # 4 Hz sampling
            nperseg=min(256, len(interp_rr)),
            scaling='density'
        )
        
        # Define frequency bands
        vlf_band = (0.0, 0.04)  # Very low frequency
        lf_band = (0.04, 0.15)  # Low frequency
        hf_band = (0.15, 0.4)   # High frequency
        
        # Compute band powers
        lf_indices = np.where((freqs >= lf_band[0]) & (freqs < lf_band[1]))[0]
        hf_indices = np.where((freqs >= hf_band[0]) & (freqs < hf_band[1]))[0]
        
        lf_power = np.trapz(psd[lf_indices], freqs[lf_indices]) if len(lf_indices) > 0 else 0.0
        hf_power = np.trapz(psd[hf_indices], freqs[hf_indices]) if len(hf_indices) > 0 else 0.0
        total_power = np.trapz(psd, freqs)
        
        # LF/HF ratio
        lf_hf_ratio = lf_power / hf_power if hf_power > 0 else 0.0
        
        return {
            'lf_power': float(lf_power),
            'hf_power': float(hf_power),
            'lf_hf_ratio': float(lf_hf_ratio),
            'total_power': float(total_power)
        }
    
    def compute_comprehensive_hrv(self, rr_intervals: np.ndarray,
                                 r_peak_times: np.ndarray) -> HRVMetrics:
        """
        Compute comprehensive HRV metrics (time and frequency domain).
        
        Args:
            rr_intervals: RR interval array (ms)
            r_peak_times: R-peak timestamps (seconds)
            
        Returns:
            HRVMetrics object with all metrics
        """
        # Time domain metrics
        time_metrics = self.compute_time_domain_metrics(rr_intervals)
        
        # Frequency domain metrics
        freq_metrics = self.compute_frequency_domain_metrics(rr_intervals, r_peak_times)
        
        # Recording duration
        duration = r_peak_times[-1] - r_peak_times[0] if len(r_peak_times) > 1 else 0.0
        
        return HRVMetrics(
            mean_hr=time_metrics['mean_hr'],
            sdnn=time_metrics['sdnn'],
            rmssd=time_metrics['rmssd'],
            pnn50=time_metrics['pnn50'],
            lf_power=freq_metrics['lf_power'],
            hf_power=freq_metrics['hf_power'],
            lf_hf_ratio=freq_metrics['lf_hf_ratio'],
            total_power=freq_metrics['total_power'],
            n_beats=len(rr_intervals) + 1,
            recording_duration=duration
        )


class HEPExtractor:
    """
    Heartbeat-evoked potential (HEP) extractor.
    
    Extracts EEG epochs time-locked to R-peaks for interoceptive
    neural processing analysis.
    """
    
    def __init__(self, sampling_rate: float = 1000.0):
        """
        Initialize HEP extractor.
        
        Args:
            sampling_rate: EEG sampling rate in Hz
        """
        self.sampling_rate = sampling_rate
    
    def extract_hep_epochs(self, eeg_data: np.ndarray,
                          r_peak_times: np.ndarray,
                          eeg_timestamps: np.ndarray,
                          tmin: float = -0.2,
                          tmax: float = 0.8) -> np.ndarray:
        """
        Extract HEP epochs around R-peaks.
        
        Args:
            eeg_data: EEG data (channels x samples)
            r_peak_times: R-peak timestamps
            eeg_timestamps: EEG timestamps
            tmin: Start time relative to R-peak (seconds)
            tmax: End time relative to R-peak (seconds)
            
        Returns:
            HEP epochs (epochs x channels x samples)
        """
        n_channels = eeg_data.shape[0]
        
        # Convert time to samples
        samples_before = int(abs(tmin) * self.sampling_rate)
        samples_after = int(tmax * self.sampling_rate)
        epoch_length = samples_before + samples_after
        
        epochs = []
        
        for r_peak_time in r_peak_times:
            # Find closest EEG timestamp
            time_diffs = np.abs(eeg_timestamps - r_peak_time)
            r_peak_idx = np.argmin(time_diffs)
            
            # Extract epoch
            start_idx = r_peak_idx - samples_before
            end_idx = r_peak_idx + samples_after
            
            # Check bounds
            if start_idx >= 0 and end_idx <= eeg_data.shape[1]:
                epoch = eeg_data[:, start_idx:end_idx]
                
                # Ensure correct length
                if epoch.shape[1] == epoch_length:
                    epochs.append(epoch)
        
        if not epochs:
            return np.array([]).reshape(0, n_channels, epoch_length)
        
        return np.array(epochs)
    
    def compute_hep_amplitude(self, hep_epochs: np.ndarray,
                             time_window: Tuple[float, float] = (0.25, 0.4),
                             tmin: float = -0.2) -> np.ndarray:
        """
        Compute HEP amplitude in specified time window.
        
        Args:
            hep_epochs: HEP epochs (epochs x channels x samples)
            time_window: Time window for HEP (start, end) in seconds post R-peak
            tmin: Start time of epoch relative to R-peak
            
        Returns:
            HEP amplitudes (epochs x channels)
        """
        if hep_epochs.size == 0:
            return np.array([])
        
        # Convert time window to sample indices
        window_start_sample = int((time_window[0] - tmin) * self.sampling_rate)
        window_end_sample = int((time_window[1] - tmin) * self.sampling_rate)
        
        # Ensure valid indices
        window_start_sample = max(0, window_start_sample)
        window_end_sample = min(hep_epochs.shape[2], window_end_sample)
        
        # Extract HEP window and compute mean amplitude
        hep_window = hep_epochs[:, :, window_start_sample:window_end_sample]
        hep_amplitudes = np.mean(hep_window, axis=2)
        
        return hep_amplitudes
    
    def apply_baseline_correction(self, hep_epochs: np.ndarray,
                                  baseline_window: Tuple[float, float] = (-0.2, 0.0),
                                  tmin: float = -0.2) -> np.ndarray:
        """
        Apply baseline correction to HEP epochs.
        
        Args:
            hep_epochs: HEP epochs (epochs x channels x samples)
            baseline_window: Baseline time window (start, end) in seconds
            tmin: Start time of epoch relative to R-peak
            
        Returns:
            Baseline-corrected HEP epochs
        """
        if hep_epochs.size == 0:
            return hep_epochs
        
        # Convert baseline window to sample indices
        baseline_start_sample = int((baseline_window[0] - tmin) * self.sampling_rate)
        baseline_end_sample = int((baseline_window[1] - tmin) * self.sampling_rate)
        
        # Ensure valid indices
        baseline_start_sample = max(0, baseline_start_sample)
        baseline_end_sample = min(hep_epochs.shape[2], baseline_end_sample)
        
        # Compute baseline
        baseline = np.mean(
            hep_epochs[:, :, baseline_start_sample:baseline_end_sample],
            axis=2,
            keepdims=True
        )
        
        # Subtract baseline
        corrected = hep_epochs - baseline
        
        return corrected


class CardiacQualityAssessor:
    """
    Cardiac signal quality assessment.
    
    Evaluates signal quality, detects artifacts, and validates beat detection
    for reliable HRV and HEP analysis.
    """
    
    def __init__(self, sampling_rate: float = 1000.0):
        """
        Initialize cardiac quality assessor.
        
        Args:
            sampling_rate: Cardiac signal sampling rate in Hz
        """
        self.sampling_rate = sampling_rate
    
    def compute_signal_quality_index(self, ecg_signal: np.ndarray,
                                     r_peaks: np.ndarray,
                                     timestamps: np.ndarray) -> float:
        """
        Compute signal quality index based on template matching.
        
        Args:
            ecg_signal: ECG signal
            r_peaks: Detected R-peak timestamps
            timestamps: Signal timestamps
            
        Returns:
            Signal quality index (0-1)
        """
        if len(r_peaks) < 3:
            return 0.0
        
        # Extract beat templates
        templates = []
        window_size = int(0.3 * self.sampling_rate)  # 300ms window
        
        for r_peak in r_peaks:
            # Find R-peak index
            peak_idx = np.argmin(np.abs(timestamps - r_peak))
            
            # Extract template
            start_idx = max(0, peak_idx - window_size // 2)
            end_idx = min(len(ecg_signal), peak_idx + window_size // 2)
            
            if end_idx - start_idx == window_size:
                template = ecg_signal[start_idx:end_idx]
                templates.append(template)
        
        if len(templates) < 3:
            return 0.0
        
        # Compute mean template
        mean_template = np.mean(templates, axis=0)
        
        # Compute correlation of each beat with mean template
        correlations = []
        for template in templates:
            corr = np.corrcoef(template, mean_template)[0, 1]
            if not np.isnan(corr):
                correlations.append(corr)
        
        # SQI is mean correlation
        sqi = np.mean(correlations) if correlations else 0.0
        
        return float(max(0.0, min(1.0, sqi)))
    
    def detect_ectopic_beats(self, rr_intervals: np.ndarray) -> Tuple[float, np.ndarray]:
        """
        Detect ectopic beats in RR interval series.
        
        Args:
            rr_intervals: RR interval array (ms)
            
        Returns:
            Tuple of (ectopic percentage, ectopic mask)
        """
        if len(rr_intervals) < 3:
            return 0.0, np.zeros(len(rr_intervals), dtype=bool)
        
        # Compute z-scores of RR intervals
        rr_z = np.abs(zscore(rr_intervals))
        
        # Detect outliers (z-score > 3)
        ectopic = rr_z > 3.0
        
        ectopic_percentage = np.sum(ectopic) / len(ectopic) * 100
        
        return float(ectopic_percentage), ectopic
    
    def estimate_missed_beats(self, rr_intervals: np.ndarray) -> float:
        """
        Estimate percentage of missed beats.
        
        Args:
            rr_intervals: RR interval array (ms)
            
        Returns:
            Estimated missed beat percentage
        """
        if len(rr_intervals) < 2:
            return 0.0
        
        # Expected RR interval (median)
        expected_rr = np.median(rr_intervals)
        
        # Count intervals that are approximately double the expected
        # (indicating a missed beat)
        missed = np.sum(rr_intervals > 1.5 * expected_rr)
        
        missed_percentage = missed / len(rr_intervals) * 100
        
        return float(missed_percentage)
    
    def assess_quality(self, ecg_signal: np.ndarray,
                      r_peaks: np.ndarray,
                      rr_intervals: np.ndarray,
                      timestamps: np.ndarray) -> CardiacQualityMetrics:
        """
        Comprehensive cardiac signal quality assessment.
        
        Args:
            ecg_signal: ECG signal
            r_peaks: Detected R-peak timestamps
            rr_intervals: RR interval array (ms)
            timestamps: Signal timestamps
            
        Returns:
            CardiacQualityMetrics object
        """
        # Signal quality index
        sqi = self.compute_signal_quality_index(ecg_signal, r_peaks, timestamps)
        
        # Ectopic beats
        ectopic_percentage, _ = self.detect_ectopic_beats(rr_intervals)
        
        # Missed beats
        missed_percentage = self.estimate_missed_beats(rr_intervals)
        
        # Noise level (estimated from high-frequency content)
        noise_level = np.std(np.diff(ecg_signal)) / np.std(ecg_signal)
        
        # Overall quality score
        quality_components = [
            sqi * 0.4,  # 40% weight
            (1 - ectopic_percentage / 100) * 0.3,  # 30% weight
            (1 - missed_percentage / 100) * 0.2,  # 20% weight
            (1 - min(noise_level, 1.0)) * 0.1  # 10% weight
        ]
        overall_quality = sum(quality_components)
        
        # Recommendation
        if overall_quality >= 0.8:
            recommendation = "excellent"
        elif overall_quality >= 0.6:
            recommendation = "good"
        elif overall_quality >= 0.4:
            recommendation = "acceptable"
        else:
            recommendation = "poor"
        
        return CardiacQualityMetrics(
            overall_quality=float(overall_quality),
            signal_quality_index=float(sqi),
            ectopic_beat_percentage=float(ectopic_percentage),
            missed_beat_percentage=float(missed_percentage),
            noise_level=float(noise_level),
            recommendation=recommendation
        )
