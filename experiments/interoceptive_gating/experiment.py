import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import matplotlib.pyplot as plt
import mne
from mne import create_info
from mne.io import RawArray
from scipy import signal
from scipy.stats import norm, bernoulli

from core.experiment import BaseExperiment

class InteroceptiveGatingExperiment(BaseExperiment):
    """
    Implements the Interoceptive Gating Paradigm from the IPI framework.
    
    This experiment tests how interoceptive precision gates conscious access to
    exteroceptive stimuli using a cardiac discrimination task.
    """
    
    def __init__(self, n_participants: int = 20, sample_rate: int = 1000):
        super().__init__(n_participants)
        self.sample_rate = sample_rate
        self.conditions = ['interoceptive', 'exteroceptive', 'control']
        self.trial_duration = 2.0  # seconds
        self.isi = 1.0  # inter-stimulus interval in seconds
        
        # Stimulus parameters
        self.gabor_sf = 3.0  # spatial frequency (cycles/degree)
        self.gabor_size = 4.0  # degrees visual angle
        self.gabor_contrast = 0.5  # initial contrast (will be adjusted)
        
        # Threshold tracking parameters
        self.step_sizes = [0.1, 0.05, 0.02]  # contrast adjustment steps
        self.reversal_threshold = 6  # number of reversals before step size decreases
        
    def setup(self, **kwargs):
        """Set up the experimental parameters."""
        # Update any parameters passed as kwargs
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        # Initialize trial parameters
        self.n_trials_per_condition = kwargs.get('n_trials_per_condition', 50)
        self.total_trials = len(self.conditions) * self.n_trials_per_condition
        
        # Initialize threshold tracking for each condition
        self.thresholds = {cond: 0.5 for cond in self.conditions}  # Initial guess
        self.current_contrasts = {cond: 0.5 for cond in self.conditions}
        
    def _simulate_heartbeat(self, duration: float, hr_bpm: float = 70) -> np.ndarray:
        """Generate a simulated heartbeat signal."""
        t = np.linspace(0, duration, int(duration * self.sample_rate), endpoint=False)
        hr_hz = hr_bpm / 60.0
        
        # Create a basic ECG-like signal
        ecg = np.zeros_like(t)
        for i in range(1, 6):
            ecg += np.sin(2 * np.pi * hr_hz * i * t) / i
            
        # Add some noise
        ecg += np.random.normal(0, 0.1, len(ecg))
        return ecg
    
    def _generate_gabor(self, contrast: float, phase: float = 0) -> np.ndarray:
        """Generate a Gabor patch with the given contrast and phase."""
        # This would be implemented with a proper visual stimulus library
        # For now, we'll just return a placeholder
        return {
            'contrast': contrast,
            'phase': phase,
            'sf': self.gabor_sf,
            'size': self.gabor_size
        }
    
    def _present_stimulus(self, condition: str, contrast: float) -> Dict:
        """Present a single trial and collect responses."""
        # In a real experiment, this would present the stimulus and collect responses
        # For simulation, we'll generate synthetic data
        
        # Simulate stimulus presentation timing
        stimulus_onset = 0.5  # seconds after trial start
        
        # Generate heartbeat signal
        ecg = self._simulate_heartbeat(self.trial_duration)
        
        # Determine if this is a synchronous trial (50/50)
        is_synchronous = np.random.choice([True, False])
        
        # Generate Gabor patch
        gabor = self._generate_gabor(contrast)
        
        # Simulate response based on condition and contrast
        if condition == 'interoceptive':
            # Higher precision for interoceptive condition
            detection_prob = norm.cdf(contrast * 3 - 1.5)
        elif condition == 'exteroceptive':
            # Standard precision
            detection_prob = norm.cdf(contrast * 2 - 1.0)
        else:  # control
            # Lower precision
            detection_prob = norm.cdf(contrast * 1.5 - 0.75)
            
        # Add some noise to the detection probability
        detection_prob = np.clip(detection_prob + np.random.normal(0, 0.1), 0, 1)
        
        # Simulate response
        response = bernoulli.rvs(detection_prob) == 1
        rt = np.random.normal(0.5, 0.1)  # reaction time in seconds
        
        return {
            'condition': condition,
            'contrast': contrast,
            'is_synchronous': is_synchronous,
            'response': response,
            'rt': rt,
            'detection_prob': detection_prob
        }
    
    def _update_threshold(self, condition: str, response_was_correct: bool):
        """Update the contrast threshold using a staircase procedure."""
        # Simplified staircase procedure
        if response_was_correct:
            # Make it harder (lower contrast)
            self.current_contrasts[condition] *= 0.9
        else:
            # Make it easier (higher contrast)
            self.current_contrasts[condition] *= 1.1
            
        # Keep contrast in reasonable bounds
        self.current_contrasts[condition] = np.clip(self.current_contrasts[condition], 0.01, 1.0)
        
        # Update threshold estimate (simple moving average)
        self.thresholds[condition] = 0.9 * self.thresholds[condition] + 0.1 * self.current_contrasts[condition]
        
        return self.current_contrasts[condition]
    
    def run_trial(self, participant_id: int, condition: str) -> Dict:
        """Run a single trial of the experiment."""
        # Get current contrast for this condition
        contrast = self.current_contrasts[condition]
        
        # Present stimulus and get response
        trial_data = self._present_stimulus(condition, contrast)
        trial_data['participant_id'] = participant_id
        trial_data['trial_num'] = len([d for d in self.participant_data.get(participant_id, []) 
                                     if d.get('condition') == condition]) + 1
        
        # Update threshold based on response
        self._update_threshold(condition, trial_data['response'])
        
        return trial_data
    
    def run_block(self, participant_id: int, condition: str, n_trials: Optional[int] = None):
        """Run a block of trials for a single condition."""
        if n_trials is None:
            n_trials = self.n_trials_per_condition
            
        block_data = []
        for _ in range(n_trials):
            trial_data = self.run_trial(participant_id, condition)
            block_data.append(trial_data)
            
        return block_data
    
    def run_participant(self, participant_id: int):
        """Run the full experiment for a single participant."""
        print(f"Running participant {participant_id}...")
        
        # Randomize condition order
        conditions = np.random.permutation(self.conditions)
        
        all_trials = []
        
        # Run blocks for each condition
        for condition in conditions:
            print(f"  Running {condition} condition...")
            block_data = self.run_block(participant_id, condition)
            all_trials.extend(block_data)
            
        return all_trials
    
    def analyze_results(self):
        """Analyze the experimental results."""
        if self.data.empty:
            print("No data to analyze. Run the experiment first.")
            return None
            
        results = {}
        
        # Calculate detection rates by condition
        for condition in self.conditions:
            cond_data = self.data[self.data['condition'] == condition]
            detection_rate = cond_data['response'].mean()
            mean_rt = cond_data[cond_data['response']]['rt'].mean()
            
            results[f"{condition}_detection_rate"] = detection_rate
            results[f"{condition}_mean_rt"] = mean_rt
            
            print(f"{condition.capitalize()} condition:")
            print(f"  Detection rate: {detection_rate:.2f}")
            print(f"  Mean RT: {mean_rt:.3f} s")
        
        return results
    
    def plot_results(self):
        """Plot the experimental results."""
        if self.data.empty:
            print("No data to plot. Run the experiment first.")
            return
            
        # Plot detection rates by condition
        plt.figure(figsize=(10, 5))
        
        detection_rates = []
        for condition in self.conditions:
            cond_data = self.data[self.data['condition'] == condition]
            detection_rates.append(cond_data['response'].mean())
            
        plt.bar(self.conditions, detection_rates)
        plt.ylim(0, 1.1)
        plt.ylabel('Detection Rate')
        plt.title('Detection Rate by Condition')
        plt.tight_layout()
        # Save figure
        output_dir = Path("data/processed")
        output_dir.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_dir / "interoceptive_gating_detection_rate.png", dpi=200)
        plt.close()
        
        # Plot contrast thresholds
        plt.figure(figsize=(10, 5))
        thresholds = [self.thresholds[cond] for cond in self.conditions]
        plt.bar(self.conditions, thresholds)
        plt.ylim(0, 1.1)
        plt.ylabel('Contrast Threshold')
        plt.title('Contrast Threshold by Condition')
        plt.tight_layout()
        # Save figure
        output_dir = Path("data/processed")
        output_dir.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_dir / "interoceptive_gating_thresholds.png", dpi=200)
        plt.close()


def run_interoceptive_gating_experiment(n_participants=10, n_trials_per_condition=50):
    """Run the interoceptive gating experiment."""
    # Create and run the experiment
    experiment = InteroceptiveGatingExperiment(
        n_participants=n_participants
    )
    
    # Set up with custom parameters
    experiment.setup(
        n_trials_per_condition=n_trials_per_condition
    )
    
    # Run the experiment
    print("Running interoceptive gating experiment...")
    data = experiment.run_experiment()
    
    # Analyze and plot results
    results = experiment.analyze_results()
    experiment.plot_results()
    
    # Save the data
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "interoceptive_gating_results.csv"
    data.to_csv(output_file, index=False)
    print(f"\nExperiment complete! Data saved to {output_file}")
    
    return experiment


if __name__ == "__main__":
    # Run with default parameters
    run_interoceptive_gating_experiment(n_participants=1, n_trials_per_condition=20)
