import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Literal
from scipy.signal import convolve
from scipy.stats import norm, ttest_rel
import mne

from core.experiment import BaseExperiment

class MetabolicCostExperiment(BaseExperiment):
    """
    Implements the Metabolic Cost of Ignition experiment from the IPI framework.
    
    This experiment measures the metabolic expenditure associated with different
    levels of conscious processing using simulated fMRI/fNIRS data.
    """
    
    def __init__(self, n_participants: int = 15, sample_rate: int = 100):
        super().__init__(n_participants)
        self.sample_rate = sample_rate  # Hz
        self.conditions = ['subliminal', 'conscious', 'deliberation']
        
        # Task parameters (in seconds)
        self.trial_duration = 4.0
        self.isi = 2.0  # inter-stimulus interval
        self.block_duration = 30.0  # duration of each condition block
        
        # Metabolic parameters
        self.baseline_metabolic_rate = 1.0  # arbitrary units
        self.neural_efficiency = 0.7  # baseline efficiency
        
        # HRF parameters for convolution
        self.hrf_params = {
            'peak_delay': 6.0,    # seconds to peak
            'peak_disp': 0.9,     # dispersion of peak
            'undershoot': 0.1,    # undershoot as fraction of peak
            'p_u_ratio': 6.0,     # peak to undershoot ratio
            'onset': 0.0,         # onset of HRF
        }
    
    def setup(self, **kwargs):
        """Set up the experimental parameters."""
        # Update any parameters passed as kwargs
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        # Calculate number of trials per block
        self.n_trials_per_block = int(self.block_duration / (self.trial_duration + self.isi))
        self.total_trials = len(self.conditions) * self.n_trials_per_block
        
        # Initialize data structures
        self.trial_sequence = []
        self._generate_trial_sequence()
    
    def _generate_trial_sequence(self):
        """Generate a randomized sequence of trials in blocks."""
        self.trial_sequence = []
        
        # Create blocks for each condition
        for block_num, condition in enumerate(self.conditions):
            for trial_in_block in range(self.n_trials_per_block):
                self.trial_sequence.append({
                    'condition': condition,
                    'block_num': block_num,
                    'trial_in_block': trial_in_block,
                    'onset_time': block_num * self.block_duration + trial_in_block * (self.trial_duration + self.isi)
                })
    
    def _generate_hrf(self, duration: float) -> np.ndarray:
        """Generate a hemodynamic response function."""
        # Time vector
        t = np.linspace(0, duration, int(duration * self.sample_rate), endpoint=False)
        
        # Gamma functions for HRF
        peak = (t / self.hrf_params['peak_delay']) ** 6 * np.exp(-t / self.hrf_params['peak_disp'])
        undershoot = (t / (self.hrf_params['peak_delay'] * 2)) * np.exp(-t / (self.hrf_params['peak_disp'] * 2))
        
        # Combine and normalize
        hrf = peak - self.hrf_params['undershoot'] * undershoot
        return hrf / hrf.max()
    
    def _simulate_neural_activity(self, condition: str, duration: float) -> Dict[str, np.ndarray]:
        """Simulate neural activity for different conditions."""
        n_samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, n_samples, endpoint=False)
        
        # Base activity (random fluctuations)
        base_activity = np.random.normal(0, 0.1, n_samples)
        
        # Condition-specific activity
        if condition == 'subliminal':
            # Minimal sustained activity, mostly noise
            signal = 0.2 * np.sin(2 * np.pi * 0.5 * t)  # Very low frequency
            network_activity = 0.1 * np.random.normal(0, 1, n_samples)
            
        elif condition == 'conscious':
            # Moderate activity in sensory and frontoparietal networks
            signal = 0.8 * np.sin(2 * np.pi * 0.8 * t)
            network_activity = 0.5 * np.sin(2 * np.pi * 0.4 * t + 1)
            
        else:  # deliberation
            # High, sustained activity in frontoparietal network
            signal = 1.2 * np.sin(2 * np.pi * 0.6 * t)
            network_activity = 1.0 * np.sin(2 * np.pi * 0.3 * t + 0.5)
        
        # Add some noise
        noise = 0.2 * np.random.normal(0, 1, n_samples)
        
        # Combine signals
        total_activity = base_activity + signal + network_activity + noise
        
        return {
            'time': t,
            'sensory_activity': base_activity + signal,
            'network_activity': network_activity,
            'total_activity': total_activity,
            'metabolic_demand': np.abs(total_activity)  # Absolute value to represent energy cost
        }
    
    def _simulate_metabolic_response(self, neural_activity: np.ndarray) -> Dict[str, np.ndarray]:
        """Convert neural activity to metabolic response using Balloon model."""
        # Simple Balloon model parameters
        tau = 1.25  # time constant for flow-inducing signal
        alpha = 0.4  # stiffness parameter
        E0 = 0.4     # resting oxygen extraction fraction
        
        # Time parameters
        dt = 1.0 / self.sample_rate
        n_samples = len(neural_activity)
        
        # Initialize state variables
        f = np.ones(n_samples)  # blood flow
        v = np.ones(n_samples)  # blood volume
        q = np.ones(n_samples)  # deoxyhemoglobin content
        y = np.zeros(n_samples)  # BOLD signal
        
        # Constants for BOLD signal model (placed before use)
        k1 = 7 * E0
        k2 = 2.0
        k3 = 2 * E0 - 0.2

        # Neural activity drives flow
        for t in range(1, n_samples):
            # Flow-inducing signal (low-pass filtered neural activity)
            df = (neural_activity[t-1] - f[t-1]) / tau
            f[t] = np.clip(f[t-1] + df * dt, 0.1, 3.0)
            
            # Blood volume (balloon model)
            dv = (f[t] - v[t-1] ** (1/alpha)) / tau
            v[t] = np.clip(v[t-1] + dv * dt, 0.5, 2.0)
            
            # Oxygen extraction
            q[t] = q[t-1] + dt * ((f[t] * (1 - (1 - E0) ** (1/f[t])) / E0) - (q[t-1] * v[t-1] ** (1/alpha - 1))) / tau
            
            # BOLD signal (simplified)
            y[t] = 100 * E0 * (k1 * (1 - q[t]) + k2 * (1 - q[t]/v[t]) + k3 * (1 - v[t]))
        
        # Convolve with HRF
        hrf = self._generate_hrf(30.0)  # 30s HRF
        bold_response = convolve(neural_activity, hrf, mode='same')[:n_samples]
        
        return {
            'blood_flow': f,
            'blood_volume': v,
            'deoxyhemoglobin': q,
            'bold_signal': bold_response,
            'metabolic_rate': f * (1 - (1 - E0) ** (1/f))  # metabolic rate ~ flow * oxygen extraction
        }
    
    def run_block(self, participant_id: int, block_params: Dict) -> List[Dict]:
        """Run a block of trials. Expects block_params to contain 'trials' list."""
        trials: List[Dict] = block_params.get('trials', [])
        results: List[Dict] = []
        for tp in trials:
            results.append(self.run_trial(participant_id, tp))
        return results
    
    def run_trial(self, participant_id: int, trial_params: Dict) -> Dict:
        """Run a single trial of the experiment."""
        # Simulate neural activity for this condition
        neural_data = self._simulate_neural_activity(
            trial_params['condition'], 
            self.trial_duration
        )
        
        # Simulate metabolic response
        metabolic_data = self._simulate_metabolic_response(neural_data['total_activity'])
        
        # Calculate summary statistics
        mean_neural_activity = np.mean(neural_data['total_activity'])
        mean_metabolic_rate = np.mean(metabolic_data['metabolic_rate'])
        bold_response = np.mean(metabolic_data['bold_signal'])
        
        # Create trial data
        trial_data = {
            'participant_id': participant_id,
            'condition': trial_params['condition'],
            'block_num': trial_params['block_num'],
            'trial_in_block': trial_params['trial_in_block'],
            'onset_time': trial_params['onset_time'],
            'mean_neural_activity': mean_neural_activity,
            'mean_metabolic_rate': mean_metabolic_rate,
            'bold_response': bold_response,
            'efficiency': mean_neural_activity / (mean_metabolic_rate + 1e-6)  # avoid division by zero
        }
        
        return {**trial_data, **neural_data, **metabolic_data}
    
    def run_participant(self, participant_id: int):
        """Run the full experiment for a single participant."""
        print(f"Running participant {participant_id}...")
        
        # Run all trials
        trial_data = []
        for i, trial_params in enumerate(self.trial_sequence, 1):
            print(f"  Trial {i}/{len(self.trial_sequence)} ({trial_params['condition']})", end='\r')
            trial_result = self.run_trial(participant_id, trial_params)
            trial_data.append(trial_result)
        
        print("\nParticipant complete!")
        return trial_data
    
    def analyze_results(self):
        """Analyze the experimental results."""
        if self.data.empty:
            print("No data to analyze. Run the experiment first.")
            return None
            
        results = {}
        
        # Calculate mean values by condition
        for condition in self.conditions:
            cond_data = self.data[self.data['condition'] == condition]
            
            results[f"{condition}_neural_activity"] = cond_data['mean_neural_activity'].mean()
            results[f"{condition}_metabolic_rate"] = cond_data['mean_metabolic_rate'].mean()
            results[f"{condition}_bold_response"] = cond_data['bold_response'].mean()
            results[f"{condition}_efficiency"] = cond_data['efficiency'].mean()
        
        # Perform statistical tests
        conditions = ['subliminal', 'conscious', 'deliberation']
        for i in range(len(conditions)):
            for j in range(i+1, len(conditions)):
                c1, c2 = conditions[i], conditions[j]
                
                # Neural activity comparison
                t_stat, p_val = ttest_rel(
                    self.data[self.data['condition'] == c1]['mean_neural_activity'],
                    self.data[self.data['condition'] == c2]['mean_neural_activity']
                )
                results[f"{c1}_vs_{c2}_neural_p"] = p_val
                
                # Metabolic rate comparison
                t_stat, p_val = ttest_rel(
                    self.data[self.data['condition'] == c1]['mean_metabolic_rate'],
                    self.data[self.data['condition'] == c2]['mean_metabolic_rate']
                )
                results[f"{c1}_vs_{c2}_metabolic_p"] = p_val
        
        # Print summary
        print("\nResults by Condition:")
        for condition in self.conditions:
            print(f"\n{condition.capitalize()}:")
            print(f"  Mean Neural Activity: {results[f'{condition}_neural_activity']:.3f}")
            print(f"  Mean Metabolic Rate: {results[f'{condition}_metabolic_rate']:.3f}")
            print(f"  Mean BOLD Response: {results[f'{condition}_bold_response']:.3f}")
            print(f"  Neural Efficiency: {results[f'{condition}_efficiency']:.3f}")
        
        # Print statistical comparisons
        print("\nStatistical Comparisons:")
        comparisons = [('subliminal', 'conscious'), 
                      ('conscious', 'deliberation'),
                      ('subliminal', 'deliberation')]
        
        for c1, c2 in comparisons:
            print(f"\n{c1.capitalize()} vs {c2.capitalize()}:")
            print(f"  Neural Activity: p = {results[f'{c1}_vs_{c2}_neural_p']:.4f}")
            print(f"  Metabolic Rate: p = {results[f'{c1}_vs_{c2}_metabolic_p']:.4f}")
        
        return results
    
    def plot_results(self):
        """Plot the experimental results."""
        if self.data.empty:
            print("No data to plot. Run the experiment first.")
            return
        
        plt.figure(figsize=(15, 10))
        
        # Plot 1: Neural activity and metabolic rate by condition
        plt.subplot(2, 2, 1)
        conditions = ['subliminal', 'conscious', 'deliberation']
        neural_means = [self.data[self.data['condition'] == c]['mean_neural_activity'].mean() for c in conditions]
        metabolic_means = [self.data[self.data['condition'] == c]['mean_metabolic_rate'].mean() for c in conditions]
        
        x = np.arange(len(conditions))
        width = 0.35
        
        plt.bar(x - width/2, neural_means, width, label='Neural Activity')
        plt.bar(x + width/2, metabolic_means, width, label='Metabolic Rate')
        
        plt.xlabel('Condition')
        plt.ylabel('Activity/Rate (a.u.)')
        plt.title('Neural Activity and Metabolic Rate by Condition')
        plt.xticks(x, [c.capitalize() for c in conditions])
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Plot 2: BOLD response over time
        plt.subplot(2, 2, 2)
        for condition in conditions:
            cond_data = self.data[self.data['condition'] == condition]
            plt.plot(cond_data['onset_time'], cond_data['bold_response'], 'o-', 
                    label=condition.capitalize())
        
        plt.xlabel('Time (s)')
        plt.ylabel('BOLD Response (a.u.)')
        plt.title('BOLD Response Over Time')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Plot 3: Neural efficiency by condition
        plt.subplot(2, 2, 3)
        efficiency_means = [self.data[self.data['condition'] == c]['efficiency'].mean() for c in conditions]
        efficiency_sems = [self.data[self.data['condition'] == c]['efficiency'].sem() for c in conditions]
        
        plt.bar(conditions, efficiency_means, yerr=efficiency_sems, capsize=5)
        plt.xlabel('Condition')
        plt.ylabel('Neural Efficiency (Activity/Rate)')
        plt.title('Neural Efficiency by Condition')
        plt.grid(True, alpha=0.3)
        
        # Plot 4: Time series of neural and metabolic activity for one trial of each condition
        plt.subplot(2, 2, 4)
        for condition in conditions:
            # Get the first trial of this condition
            trial = self.data[self.data['condition'] == condition].iloc[0]
            time = trial['time']
            
            # Normalize for comparison
            neural = (trial['total_activity'] - np.min(trial['total_activity'])) / \
                    (np.max(trial['total_activity']) - np.min(trial['total_activity']) + 1e-6)
            metabolic = (trial['metabolic_rate'] - np.min(trial['metabolic_rate'])) / \
                       (np.max(trial['metabolic_rate']) - np.min(trial['metabolic_rate']) + 1e-6)
            
            plt.plot(time, neural, '--', label=f"{condition.capitalize()} Neural")
            plt.plot(time, metabolic, '-', label=f"{condition.capitalize()} Metabolic")
        
        plt.xlabel('Time (s)')
        plt.ylabel('Normalized Activity')
        plt.title('Neural vs. Metabolic Activity')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        # Save combined figure
        output_dir = Path("data/processed")
        output_dir.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_dir / "metabolic_cost_results.png", dpi=200)
        plt.close()


def run_metabolic_cost_experiment(n_participants=10, n_trials_per_condition=15):
    """Run the metabolic cost experiment."""
    # Create and run the experiment
    experiment = MetabolicCostExperiment(
        n_participants=n_participants
    )
    
    # Set up with custom parameters
    experiment.setup(
        n_trials_per_condition=n_trials_per_condition
    )
    
    # Run the experiment
    print("Running metabolic cost experiment...")
    data = experiment.run_experiment()
    
    # Analyze and plot results
    results = experiment.analyze_results()
    experiment.plot_results()
    
    # Save the data
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "metabolic_cost_results.csv"
    data.to_csv(output_file, index=False)
    print(f"\nExperiment complete! Data saved to {output_file}")
    
    return experiment


if __name__ == "__main__":
    # Run with default parameters
    run_metabolic_cost_experiment(n_participants=1, n_trials_per_condition=5)
