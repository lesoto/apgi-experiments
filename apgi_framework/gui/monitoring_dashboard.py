"""
Real-time multi-modal monitoring dashboard.

Provides live monitoring of EEG, pupillometry, cardiac signals, and parameter estimates.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional, List
from datetime import datetime
import numpy as np
import logging

logger = logging.getLogger(__name__)


class LiveEEGMonitor:
    """
    Real-time EEG signal quality and P3b/HEP display.
    
    Monitors EEG data quality, artifact rates, and neural signatures.
    """
    
    def __init__(self, parent_frame: tk.Frame):
        """
        Initialize EEG monitor.
        
        Args:
            parent_frame: Parent tkinter frame
        """
        self.frame = ttk.LabelFrame(parent_frame, text="EEG Monitoring", padding=10)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Signal quality indicators
        quality_frame = ttk.Frame(self.frame)
        quality_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(quality_frame, text="Signal Quality:").pack(side=tk.LEFT, padx=5)
        self.quality_label = ttk.Label(quality_frame, text="N/A", foreground="gray")
        self.quality_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(quality_frame, text="Artifact Rate:").pack(side=tk.LEFT, padx=5)
        self.artifact_label = ttk.Label(quality_frame, text="N/A", foreground="gray")
        self.artifact_label.pack(side=tk.LEFT, padx=5)
        
        # Neural signatures
        signature_frame = ttk.LabelFrame(self.frame, text="Neural Signatures", padding=5)
        signature_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        ttk.Label(signature_frame, text="P3b Amplitude (μV):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.p3b_label = ttk.Label(signature_frame, text="N/A")
        self.p3b_label.grid(row=0, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(signature_frame, text="HEP Amplitude (μV):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.hep_label = ttk.Label(signature_frame, text="N/A")
        self.hep_label.grid(row=1, column=1, sticky=tk.W, pady=2)
        
        # Bad channels display
        ttk.Label(signature_frame, text="Bad Channels:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.bad_channels_label = ttk.Label(signature_frame, text="None")
        self.bad_channels_label.grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # Current state
        self.current_quality = 0.0
        self.artifact_rate = 0.0
        self.p3b_amplitude = None
        self.hep_amplitude = None
        self.bad_channels: List[str] = []
        
        logger.info("LiveEEGMonitor initialized")
    
    def update_signal_quality(self, quality_score: float, artifact_rate: float) -> None:
        """
        Update EEG signal quality display.
        
        Args:
            quality_score: Signal quality score (0-1)
            artifact_rate: Artifact rate (0-1)
        """
        self.current_quality = quality_score
        self.artifact_rate = artifact_rate
        
        # Update quality label with color coding
        quality_text = f"{quality_score:.2f}"
        if quality_score >= 0.8:
            color = "green"
        elif quality_score >= 0.6:
            color = "orange"
        else:
            color = "red"
        
        self.quality_label.config(text=quality_text, foreground=color)
        
        # Update artifact rate
        artifact_text = f"{artifact_rate*100:.1f}%"
        artifact_color = "green" if artifact_rate < 0.2 else "orange" if artifact_rate < 0.4 else "red"
        self.artifact_label.config(text=artifact_text, foreground=artifact_color)
    
    def update_p3b(self, amplitude: float, latency: Optional[float] = None) -> None:
        """
        Update P3b amplitude display.
        
        Args:
            amplitude: P3b amplitude in μV
            latency: Optional P3b latency in ms
        """
        self.p3b_amplitude = amplitude
        
        if latency:
            text = f"{amplitude:.2f} μV ({latency:.0f} ms)"
        else:
            text = f"{amplitude:.2f} μV"
        
        self.p3b_label.config(text=text)
    
    def update_hep(self, amplitude: float) -> None:
        """
        Update HEP amplitude display.
        
        Args:
            amplitude: HEP amplitude in μV
        """
        self.hep_amplitude = amplitude
        self.hep_label.config(text=f"{amplitude:.2f} μV")
    
    def update_bad_channels(self, bad_channels: List[str]) -> None:
        """
        Update bad channels display.
        
        Args:
            bad_channels: List of bad channel names
        """
        self.bad_channels = bad_channels
        
        if bad_channels:
            text = ", ".join(bad_channels[:5])  # Show first 5
            if len(bad_channels) > 5:
                text += f" (+{len(bad_channels)-5} more)"
            self.bad_channels_label.config(text=text, foreground="red")
        else:
            self.bad_channels_label.config(text="None", foreground="green")
    
    def reset(self) -> None:
        """Reset monitor display."""
        self.quality_label.config(text="N/A", foreground="gray")
        self.artifact_label.config(text="N/A", foreground="gray")
        self.p3b_label.config(text="N/A")
        self.hep_label.config(text="N/A")
        self.bad_channels_label.config(text="None", foreground="gray")


class PupillometryMonitor:
    """
    Live pupillometry signal monitoring.
    
    Displays pupil diameter, blink rate, and data quality.
    """
    
    def __init__(self, parent_frame: tk.Frame):
        """
        Initialize pupillometry monitor.
        
        Args:
            parent_frame: Parent tkinter frame
        """
        self.frame = ttk.LabelFrame(parent_frame, text="Pupillometry Monitoring", padding=10)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Signal quality
        quality_frame = ttk.Frame(self.frame)
        quality_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(quality_frame, text="Data Quality:").pack(side=tk.LEFT, padx=5)
        self.quality_label = ttk.Label(quality_frame, text="N/A", foreground="gray")
        self.quality_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(quality_frame, text="Data Loss:").pack(side=tk.LEFT, padx=5)
        self.data_loss_label = ttk.Label(quality_frame, text="N/A", foreground="gray")
        self.data_loss_label.pack(side=tk.LEFT, padx=5)
        
        # Pupil measurements
        measurements_frame = ttk.LabelFrame(self.frame, text="Measurements", padding=5)
        measurements_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        ttk.Label(measurements_frame, text="Pupil Diameter (mm):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.diameter_label = ttk.Label(measurements_frame, text="N/A")
        self.diameter_label.grid(row=0, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(measurements_frame, text="Blink Rate (bpm):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.blink_rate_label = ttk.Label(measurements_frame, text="N/A")
        self.blink_rate_label.grid(row=1, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(measurements_frame, text="Tracking Loss:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.tracking_loss_label = ttk.Label(measurements_frame, text="N/A")
        self.tracking_loss_label.grid(row=2, column=1, sticky=tk.W, pady=2)
        
        logger.info("PupillometryMonitor initialized")
    
    def update_quality(self, quality_score: float, data_loss: float) -> None:
        """
        Update pupillometry data quality.
        
        Args:
            quality_score: Quality score (0-1)
            data_loss: Data loss proportion (0-1)
        """
        # Update quality
        quality_text = f"{quality_score:.2f}"
        quality_color = "green" if quality_score >= 0.8 else "orange" if quality_score >= 0.6 else "red"
        self.quality_label.config(text=quality_text, foreground=quality_color)
        
        # Update data loss
        loss_text = f"{data_loss*100:.1f}%"
        loss_color = "green" if data_loss < 0.1 else "orange" if data_loss < 0.3 else "red"
        self.data_loss_label.config(text=loss_text, foreground=loss_color)
    
    def update_measurements(self, diameter: float, blink_rate: float, tracking_loss: int) -> None:
        """
        Update pupil measurements.
        
        Args:
            diameter: Pupil diameter in mm
            blink_rate: Blink rate in blinks per minute
            tracking_loss: Number of tracking loss episodes
        """
        self.diameter_label.config(text=f"{diameter:.2f} mm")
        self.blink_rate_label.config(text=f"{blink_rate:.1f} bpm")
        self.tracking_loss_label.config(text=str(tracking_loss))
    
    def reset(self) -> None:
        """Reset monitor display."""
        self.quality_label.config(text="N/A", foreground="gray")
        self.data_loss_label.config(text="N/A", foreground="gray")
        self.diameter_label.config(text="N/A")
        self.blink_rate_label.config(text="N/A")
        self.tracking_loss_label.config(text="N/A")


class CardiacMonitor:
    """
    Live cardiac signal monitoring.
    
    Displays heart rate, HRV, and R-peak detection quality.
    """
    
    def __init__(self, parent_frame: tk.Frame):
        """
        Initialize cardiac monitor.
        
        Args:
            parent_frame: Parent tkinter frame
        """
        self.frame = ttk.LabelFrame(parent_frame, text="Cardiac Monitoring", padding=10)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Signal quality
        quality_frame = ttk.Frame(self.frame)
        quality_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(quality_frame, text="Signal Quality:").pack(side=tk.LEFT, padx=5)
        self.quality_label = ttk.Label(quality_frame, text="N/A", foreground="gray")
        self.quality_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(quality_frame, text="R-peak Confidence:").pack(side=tk.LEFT, padx=5)
        self.rpeak_label = ttk.Label(quality_frame, text="N/A", foreground="gray")
        self.rpeak_label.pack(side=tk.LEFT, padx=5)
        
        # Cardiac measurements
        measurements_frame = ttk.LabelFrame(self.frame, text="Measurements", padding=5)
        measurements_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        ttk.Label(measurements_frame, text="Heart Rate (BPM):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.hr_label = ttk.Label(measurements_frame, text="N/A")
        self.hr_label.grid(row=0, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(measurements_frame, text="HRV (RMSSD ms):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.hrv_label = ttk.Label(measurements_frame, text="N/A")
        self.hrv_label.grid(row=1, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(measurements_frame, text="RR Interval (ms):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.rr_label = ttk.Label(measurements_frame, text="N/A")
        self.rr_label.grid(row=2, column=1, sticky=tk.W, pady=2)
        
        logger.info("CardiacMonitor initialized")
    
    def update_quality(self, quality_score: float, rpeak_confidence: float) -> None:
        """
        Update cardiac signal quality.
        
        Args:
            quality_score: Signal quality score (0-1)
            rpeak_confidence: R-peak detection confidence (0-1)
        """
        # Update quality
        quality_text = f"{quality_score:.2f}"
        quality_color = "green" if quality_score >= 0.8 else "orange" if quality_score >= 0.6 else "red"
        self.quality_label.config(text=quality_text, foreground=quality_color)
        
        # Update R-peak confidence
        rpeak_text = f"{rpeak_confidence:.2f}"
        rpeak_color = "green" if rpeak_confidence >= 0.9 else "orange" if rpeak_confidence >= 0.7 else "red"
        self.rpeak_label.config(text=rpeak_text, foreground=rpeak_color)
    
    def update_measurements(self, heart_rate: float, hrv: float, rr_interval: float) -> None:
        """
        Update cardiac measurements.
        
        Args:
            heart_rate: Heart rate in BPM
            hrv: Heart rate variability (RMSSD) in ms
            rr_interval: RR interval in ms
        """
        self.hr_label.config(text=f"{heart_rate:.1f} BPM")
        self.hrv_label.config(text=f"{hrv:.1f} ms")
        self.rr_label.config(text=f"{rr_interval:.1f} ms")
    
    def reset(self) -> None:
        """Reset monitor display."""
        self.quality_label.config(text="N/A", foreground="gray")
        self.rpeak_label.config(text="N/A", foreground="gray")
        self.hr_label.config(text="N/A")
        self.hrv_label.config(text="N/A")
        self.rr_label.config(text="N/A")


class RealTimeParameterEstimateUpdater:
    """
    Real-time parameter estimate updates.
    
    Displays ongoing Bayesian parameter estimates as data accumulates.
    """
    
    def __init__(self, parent_frame: tk.Frame):
        """
        Initialize parameter estimate updater.
        
        Args:
            parent_frame: Parent tkinter frame
        """
        self.frame = ttk.LabelFrame(parent_frame, text="Parameter Estimates", padding=10)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Parameter displays
        params_frame = ttk.Frame(self.frame)
        params_frame.pack(fill=tk.BOTH, expand=True)
        
        # θ₀ (theta0)
        ttk.Label(params_frame, text="θ₀ (Ignition Threshold):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.theta0_label = ttk.Label(params_frame, text="N/A")
        self.theta0_label.grid(row=0, column=1, sticky=tk.W, pady=2)
        
        # Πᵢ (pi_i)
        ttk.Label(params_frame, text="Πᵢ (Interoceptive Precision):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.pi_i_label = ttk.Label(params_frame, text="N/A")
        self.pi_i_label.grid(row=1, column=1, sticky=tk.W, pady=2)
        
        # β (beta)
        ttk.Label(params_frame, text="β (Somatic Bias):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.beta_label = ttk.Label(params_frame, text="N/A")
        self.beta_label.grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # Convergence status
        ttk.Label(params_frame, text="Convergence:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.convergence_label = ttk.Label(params_frame, text="N/A")
        self.convergence_label.grid(row=3, column=1, sticky=tk.W, pady=2)
        
        logger.info("RealTimeParameterEstimateUpdater initialized")
    
    def update_theta0(self, mean: float, std: float, ci_lower: float, ci_upper: float) -> None:
        """
        Update θ₀ estimate.
        
        Args:
            mean: Mean estimate
            std: Standard deviation
            ci_lower: Lower 95% credible interval
            ci_upper: Upper 95% credible interval
        """
        text = f"{mean:.3f} ± {std:.3f} [{ci_lower:.3f}, {ci_upper:.3f}]"
        self.theta0_label.config(text=text)
    
    def update_pi_i(self, mean: float, std: float, ci_lower: float, ci_upper: float) -> None:
        """
        Update Πᵢ estimate.
        
        Args:
            mean: Mean estimate
            std: Standard deviation
            ci_lower: Lower 95% credible interval
            ci_upper: Upper 95% credible interval
        """
        text = f"{mean:.3f} ± {std:.3f} [{ci_lower:.3f}, {ci_upper:.3f}]"
        self.pi_i_label.config(text=text)
    
    def update_beta(self, mean: float, std: float, ci_lower: float, ci_upper: float) -> None:
        """
        Update β estimate.
        
        Args:
            mean: Mean estimate
            std: Standard deviation
            ci_lower: Lower 95% credible interval
            ci_upper: Upper 95% credible interval
        """
        text = f"{mean:.3f} ± {std:.3f} [{ci_lower:.3f}, {ci_upper:.3f}]"
        self.beta_label.config(text=text)
    
    def update_convergence(self, converged: bool, r_hat: float) -> None:
        """
        Update convergence status.
        
        Args:
            converged: Whether chains have converged
            r_hat: Gelman-Rubin statistic
        """
        if converged:
            text = f"Converged (R̂={r_hat:.3f})"
            color = "green"
        else:
            text = f"Not converged (R̂={r_hat:.3f})"
            color = "orange"
        
        self.convergence_label.config(text=text, foreground=color)
    
    def reset(self) -> None:
        """Reset parameter displays."""
        self.theta0_label.config(text="N/A")
        self.pi_i_label.config(text="N/A")
        self.beta_label.config(text="N/A")
        self.convergence_label.config(text="N/A", foreground="gray")


class QualityAlertSystem:
    """
    Automated data quality issue detection and notifications.
    
    Monitors all data streams and generates alerts for quality issues.
    """
    
    def __init__(self, parent_frame: tk.Frame):
        """
        Initialize quality alert system.
        
        Args:
            parent_frame: Parent tkinter frame
        """
        self.frame = ttk.LabelFrame(parent_frame, text="Quality Alerts", padding=10)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Alert display
        self.alert_text = tk.Text(self.frame, height=10, state=tk.DISABLED, wrap=tk.WORD)
        self.alert_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags for different alert levels
        self.alert_text.tag_config("info", foreground="blue")
        self.alert_text.tag_config("warning", foreground="orange")
        self.alert_text.tag_config("error", foreground="red")
        
        self.alerts: List[Dict[str, Any]] = []
        
        logger.info("QualityAlertSystem initialized")
    
    def add_alert(self, level: str, message: str, source: str = "") -> None:
        """
        Add a quality alert.
        
        Args:
            level: Alert level ('info', 'warning', or 'error')
            message: Alert message
            source: Source of alert (e.g., 'EEG', 'Pupillometry')
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        alert = {
            'timestamp': timestamp,
            'level': level,
            'message': message,
            'source': source
        }
        
        self.alerts.append(alert)
        
        # Update display
        self.alert_text.config(state=tk.NORMAL)
        
        alert_line = f"[{timestamp}] "
        if source:
            alert_line += f"[{source}] "
        alert_line += f"{message}\n"
        
        self.alert_text.insert(tk.END, alert_line, level)
        self.alert_text.see(tk.END)
        self.alert_text.config(state=tk.DISABLED)
        
        logger.log(
            logging.WARNING if level == "warning" else logging.ERROR if level == "error" else logging.INFO,
            f"Quality alert: {source} - {message}"
        )
    
    def check_eeg_quality(self, quality_score: float, artifact_rate: float) -> None:
        """
        Check EEG quality and generate alerts if needed.
        
        Args:
            quality_score: EEG quality score (0-1)
            artifact_rate: Artifact rate (0-1)
        """
        if quality_score < 0.5:
            self.add_alert("error", f"Poor EEG quality: {quality_score:.2f}", "EEG")
        elif quality_score < 0.7:
            self.add_alert("warning", f"Moderate EEG quality: {quality_score:.2f}", "EEG")
        
        if artifact_rate > 0.5:
            self.add_alert("error", f"High artifact rate: {artifact_rate*100:.1f}%", "EEG")
        elif artifact_rate > 0.3:
            self.add_alert("warning", f"Elevated artifact rate: {artifact_rate*100:.1f}%", "EEG")
    
    def check_pupil_quality(self, data_loss: float, tracking_loss: int) -> None:
        """
        Check pupillometry quality and generate alerts if needed.
        
        Args:
            data_loss: Data loss proportion (0-1)
            tracking_loss: Number of tracking loss episodes
        """
        if data_loss > 0.4:
            self.add_alert("error", f"High pupil data loss: {data_loss*100:.1f}%", "Pupillometry")
        elif data_loss > 0.2:
            self.add_alert("warning", f"Moderate pupil data loss: {data_loss*100:.1f}%", "Pupillometry")
        
        if tracking_loss > 10:
            self.add_alert("warning", f"Frequent tracking loss: {tracking_loss} episodes", "Pupillometry")
    
    def check_cardiac_quality(self, quality_score: float, rpeak_confidence: float) -> None:
        """
        Check cardiac signal quality and generate alerts if needed.
        
        Args:
            quality_score: Cardiac quality score (0-1)
            rpeak_confidence: R-peak detection confidence (0-1)
        """
        if quality_score < 0.6:
            self.add_alert("error", f"Poor cardiac quality: {quality_score:.2f}", "Cardiac")
        elif quality_score < 0.8:
            self.add_alert("warning", f"Moderate cardiac quality: {quality_score:.2f}", "Cardiac")
        
        if rpeak_confidence < 0.7:
            self.add_alert("warning", f"Low R-peak confidence: {rpeak_confidence:.2f}", "Cardiac")
    
    def clear_alerts(self) -> None:
        """Clear all alerts."""
        self.alerts.clear()
        self.alert_text.config(state=tk.NORMAL)
        self.alert_text.delete(1.0, tk.END)
        self.alert_text.config(state=tk.DISABLED)
    
    def get_alert_summary(self) -> Dict[str, int]:
        """
        Get summary of alerts by level.
        
        Returns:
            Dictionary with counts by alert level
        """
        summary = {'info': 0, 'warning': 0, 'error': 0}
        
        for alert in self.alerts:
            level = alert['level']
            if level in summary:
                summary[level] += 1
        
        return summary
