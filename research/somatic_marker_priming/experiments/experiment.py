import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from scipy.stats import norm, bernoulli
import random

from core.experiment import BaseExperiment
from apgi_framework.logging.standardized_logging import get_logger

logger = get_logger("somatic_marker_priming_experiment")

class SomaticMarkerPrimingExperiment(BaseExperiment):
    """
    Implements the Somatic Marker Priming experiment from the APGI framework.
    
    This experiment tests if unconsciously presented somatic markers can bias 
    subsequent conscious decisions by modulating precision.
    """
    
    def __init__(self, n_participants: int = 20, screen_size: Tuple[int, int] = (1920, 1080)):
        super().__init__(n_participants)
        self.screen_size = screen_size
        self.prime_duration = 0.033  # 33ms for backward masking
        self.mask_duration = 0.1     # 100ms mask
        self.decision_timeout = 2.0   # 2 seconds to respond
        
        # Stimulus parameters
        self.dot_speed = 5.0  # degrees per second
        self.dot_radius = 0.3  # degrees
        self.dot_lifetime = 10  # frames
        self.coherence_levels = [0.1, 0.2, 0.3, 0.4, 0.5]  # Motion coherence levels
        
        # Prime categories (using IAPS image IDs as placeholders)
        self.prime_categories = {
            'positive': [1010, 1440, 1463, 1710, 1750],  # Pleasant images (babies, happy faces)
            'negative': [1050, 1300, 1930, 2120, 2683],  # Unpleasant images (snakes, spiders)
            'neutral': [2190, 2210, 2383, 2480, 2514]    # Neutral objects
        }
        
        # Initialize trial structure
        self.prime_types = list(self.prime_categories.keys())
        self.directions = ['left', 'right']
        
    def setup(self, **kwargs):
        """Set up the experimental parameters."""
        # Update any parameters passed as kwargs
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        # Initialize trial parameters
        self.n_trials_per_condition = kwargs.get('n_trials_per_condition', 20)
        self.total_trials = len(self.prime_types) * len(self.coherence_levels) * self.n_trials_per_condition
        
        # Initialize data structures
        self.trial_sequence = []
        self._generate_trial_sequence()
        
    def run_block(self, participant_id: int, block_params: Dict) -> List[Dict]:
        """Run a block of trials. Expects block_params to contain 'trials' list."""
        trials: List[Dict] = block_params.get('trials', [])
        results: List[Dict] = []
        for tp in trials:
            results.append(self.run_trial(participant_id, tp))
        return results
    
    def _generate_trial_sequence(self):
        """Generate a randomized sequence of trials."""
        self.trial_sequence = []
        
        # Create all possible trial combinations
        for prime_type in self.prime_types:
            for coherence in self.coherence_levels:
                for _ in range(self.n_trials_per_condition):
                    direction = random.choice(self.directions)
                    prime_image = random.choice(self.prime_categories[prime_type])
                    
                    self.trial_sequence.append({
                        'prime_type': prime_type,
                        'prime_image': prime_image,
                        'coherence': coherence,
                        'direction': direction
                    })
        
        # Randomize trial order
        random.shuffle(self.trial_sequence)
    
    def _present_prime(self, prime_type: str, prime_image: int) -> Dict:
        """Present a masked prime stimulus."""
        # In a real experiment, this would present the actual image
        # For simulation, we'll just return the parameters
        return {
            'prime_type': prime_type,
            'prime_image': prime_image,
            'presented': True,
            'prime_duration': self.prime_duration,
            'mask_duration': self.mask_duration
        }
    
    def _generate_rdk_stimulus(self, coherence: float, direction: str, duration: float = 1.0) -> Dict:
        """Generate parameters for a random dot kinematogram."""
        n_dots = 100
        dot_positions = np.random.uniform(-5, 5, (n_dots, 2))  # Random positions in degrees
        dot_directions = np.random.uniform(0, 2*np.pi, n_dots)  # Random initial directions
        
        # Determine signal dots (move coherently)
        n_signal = int(n_dots * coherence)
        signal_idx = np.random.choice(n_dots, n_signal, replace=False)
        
        # Set signal direction
        target_angle = 0 if direction == 'right' else np.pi
        dot_directions[signal_idx] = target_angle
        
        # Calculate velocities
        velocities = np.column_stack([
            np.cos(dot_directions) * self.dot_speed,
            np.sin(dot_directions) * self.dot_speed
        ])
        
        return {
            'n_dots': n_dots,
            'coherence': coherence,
            'direction': direction,
            'dot_positions': dot_positions.tolist(),
            'velocities': velocities.tolist(),
            'duration': duration
        }
    
    def _simulate_physiological_response(self, prime_type: str) -> Dict:
        """Simulate physiological responses to primes."""
        # Baseline physiological measures
        baseline_scr = np.random.uniform(1, 3)  # Skin conductance response (microsiemens)
        baseline_pupil = np.random.uniform(3, 4)  # Pupil diameter (mm)
        
        # Modulate based on prime type
        if prime_type == 'positive':
            scr = baseline_scr * 1.2  # Moderate increase for positive
            pupil = baseline_pupil * 1.1
        elif prime_type == 'negative':
            scr = baseline_scr * 1.5  # Stronger response to negative
            pupil = baseline_pupil * 1.3
        else:  # neutral
            scr = baseline_scr
            pupil = baseline_pupil
            
        # Add some noise
        scr += np.random.normal(0, 0.1)
        pupil += np.random.normal(0, 0.05)
        
        return {
            'scr': max(0.5, scr),  # Ensure non-negative
            'pupil_size': max(2.0, pupil),  # Ensure reasonable pupil size
            'hrv': np.random.normal(50, 5)  # Heart rate variability
        }
    
    def run_trial(self, participant_id: int, trial_params: Dict) -> Dict:
        """Run a single trial of the experiment."""
        # Present prime (ensure prime_image exists, e.g., for practice trials)
        prime_type = trial_params['prime_type']
        prime_image = trial_params.get('prime_image', random.choice(self.prime_categories[prime_type]))
        prime_info = self._present_prime(prime_type, prime_image)
        
        # Simulate physiological response to prime
        phys_response = self._simulate_physiological_response(trial_params['prime_type'])
        
        # Generate RDK stimulus
        rdk_params = self._generate_rdk_stimulus(
            trial_params['coherence'],
            trial_params['direction']
        )
        
        # Simulate response based on coherence and prime type
        # Higher coherence = easier task = higher accuracy
        base_accuracy = 0.5 + (trial_params['coherence'] * 0.5)  # 0.5 to 1.0
        
        # Prime effect: negative primes increase precision (narrower decision bound)
        if trial_params['prime_type'] == 'negative':
            # Negative primes make responses more conservative
            accuracy = base_accuracy * 1.1  # Slightly better accuracy
            rt_factor = 0.9  # Faster RT due to increased precision
        elif trial_params['prime_type'] == 'positive':
            # Positive primes might make responses slightly more liberal
            accuracy = base_accuracy * 0.95  # Slightly worse accuracy
            rt_factor = 1.05  # Slightly slower RT
        else:  # neutral
            accuracy = base_accuracy
            rt_factor = 1.0
        
        # Cap accuracy at 0.95 to avoid ceiling effects
        accuracy = min(0.95, accuracy)
        
        # Determine if response was correct
        correct = bernoulli.rvs(accuracy) == 1
        
        # Simulate reaction time (inverse relationship with coherence)
        rt_base = 0.8 - (trial_params['coherence'] * 0.4)  # 0.4-0.8s range
        rt = np.random.normal(rt_base * rt_factor, 0.1)  # Add some noise
        
        # Create trial data
        trial_data = {
            'participant_id': participant_id,
            'trial_num': len([t for t in self.participant_data.get(participant_id, []) 
                            if t.get('prime_type') == trial_params['prime_type']]) + 1,
            **trial_params,
            **prime_info,
            **phys_response,
            'correct': correct,
            'rt': rt,
            'accuracy': accuracy
        }
        
        return trial_data
    
    def run_participant(self, participant_id: int):
        """Run the full experiment for a single participant."""
        logger.info(f"Running participant {participant_id}...")
        
        # Practice trials (not analyzed)
        practice_trials = [
            {'prime_type': 'neutral', 'coherence': 0.5, 'direction': d}
            for d in self.directions * 2
        ]
        
        # Run practice trials
        for trial_params in practice_trials:
            self.run_trial(participant_id, trial_params)
        
        # Run experimental trials
        trial_data = []
        for i, trial_params in enumerate(self.trial_sequence, 1):
            logger.debug(f"  Trial {i}/{len(self.trial_sequence)}")
            trial_result = self.run_trial(participant_id, trial_params)
            trial_data.append(trial_result)
        
        logger.info("Participant complete!")
        return trial_data
    
    def analyze_results(self):
        """Analyze the experimental results."""
        if self.data.empty:
            logger.warning("No data to analyze. Run the experiment first.")
            return None
            
        results = {}
        
        # Calculate accuracy by prime type and coherence
        for prime_type in self.prime_types:
            prime_data = self.data[self.data['prime_type'] == prime_type]
            
            for coherence in self.coherence_levels:
                coh_data = prime_data[np.isclose(prime_data['coherence'], coherence)]
                if len(coh_data) > 0:
                    acc = coh_data['correct'].mean()
                    mean_rt = coh_data[coh_data['correct']]['rt'].mean()
                    
                    results[f"{prime_type}_coh{coherence:.1f}_acc"] = acc
                    results[f"{prime_type}_coh{coherence:.1f}_rt"] = mean_rt
        
        # Print summary
        logger.info("\nResults by Prime Type and Coherence:")
        for prime in self.prime_types:
            logger.info(f"\n{prime.capitalize()} Primes:")
            for coh in self.coherence_levels:
                acc_key = f"{prime}_coh{coh:.1f}_acc"
                rt_key = f"{prime}_coh{coh:.1f}_rt"
                if acc_key in results and rt_key in results:
                    logger.info(f"  Coherence {coh:.1f}: Accuracy = {results[acc_key]:.2f}, RT = {results[rt_key]:.3f}s")
        
        return results
    
    def plot_results(self):
        """Plot the experimental results."""
        if self.data.empty:
            logger.warning("No data to plot. Run the experiment first.")
            return
        
        plt.figure(figsize=(15, 5))
        
        # Plot accuracy by coherence and prime type
        plt.subplot(1, 2, 1)
        for prime_type in self.prime_types:
            accs = []
            for coh in self.coherence_levels:
                subset = self.data[
                    (self.data['prime_type'] == prime_type) & 
                    (np.isclose(self.data['coherence'], coh))
                ]
                if len(subset) > 0:
                    accs.append(subset['correct'].mean())
                else:
                    accs.append(0)
            
            plt.plot(self.coherence_levels, accs, 'o-', label=prime_type)
        
        plt.xlabel('Coherence Level')
        plt.ylabel('Accuracy')
        plt.title('Accuracy by Coherence and Prime Type')
        plt.legend()
        plt.grid(True)
        
        # Plot RT by coherence and prime type
        plt.subplot(1, 2, 2)
        for prime_type in self.prime_types:
            rts = []
            for coh in self.coherence_levels:
                subset = self.data[
                    (self.data['prime_type'] == prime_type) & 
                    (np.isclose(self.data['coherence'], coh)) &
                    (self.data['correct'] == True)
                ]
                if len(subset) > 0:
                    rts.append(subset['rt'].mean())
                else:
                    rts.append(0.5)  # Default value if no data
            
            plt.plot(self.coherence_levels, rts, 'o-', label=prime_type)
        
        plt.xlabel('Coherence Level')
        plt.ylabel('Reaction Time (s)')
        plt.title('Reaction Time by Coherence and Prime Type')
        plt.legend()
        plt.grid(True)
        
        plt.tight_layout()
        # Save figure
        output_dir = Path("data/processed")
        output_dir.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_dir / "somatic_marker_priming_results.png", dpi=200)
        plt.close()


def run_somatic_marker_priming_experiment(n_participants=10, n_trials_per_condition=20):
    """Run the somatic marker priming experiment."""
    # Create and run the experiment
    experiment = SomaticMarkerPrimingExperiment(
        n_participants=n_participants
    )
    
    # Set up with custom parameters
    experiment.setup(
        n_trials_per_condition=n_trials_per_condition
    )
    
    # Run the experiment
    print("Running somatic marker priming experiment...")
    data = experiment.run_experiment()
    
    # Analyze and plot results
    results = experiment.analyze_results()
    experiment.plot_results()
    
    # Save the data
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "somatic_marker_priming_results.csv"
    data.to_csv(output_file, index=False)
    print(f"\nExperiment complete! Data saved to {output_file}")
    
    return experiment


if __name__ == "__main__":
    # Run with default parameters
    run_somatic_marker_priming_experiment(n_participants=1, n_trials_per_condition=10)
