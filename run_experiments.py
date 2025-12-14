"""
APGI Framework Experiments

This script demonstrates the APGI model through several experiments that explore different aspects of the ignition threshold mechanism.
"""

import numpy as np
import matplotlib.pyplot as plt
from apgi_model import APGIModel, APGIParams, plot_simulation
from typing import List, Dict, Any, Tuple
import argparse
import importlib
import sys
from pathlib import Path
import seaborn as sns

plt.style.use('ggplot')
plt.rcParams['figure.facecolor'] = 'white'
 
sys.path.append(str(Path(__file__).parent))

EXPERIMENTS = {
    "interoceptive_gating": "experiments.interoceptive_gating.experiment",
    "somatic_marker_priming": "experiments.somatic_marker_priming.experiment",
    "metabolic_cost": "experiments.metabolic_cost.experiment",
    "ai_benchmarking": "experiments.ai_benchmarking.experiment",
}

def get_available_experiments() -> Dict[str, str]:
    """Return a dictionary of available experiments."""
    return EXPERIMENTS

def run_experiment(experiment_name: str, **kwargs):
    """Run the specified experiment with the given parameters."""
    if experiment_name not in EXPERIMENTS:
        raise ValueError(f"Unknown experiment: {experiment_name}. "
                         f"Available experiments: {', '.join(EXPERIMENTS.keys())}")
    
    try:
        module_path = EXPERIMENTS[experiment_name]
        module = importlib.import_module(module_path)
        
        # Get the run function (should be named run_{experiment_name}_experiment)
        run_func_name = f"run_{experiment_name}_experiment"
        if not hasattr(module, run_func_name):
            raise AttributeError(f"Module {module_path} does not contain function {run_func_name}")
        
        run_func = getattr(module, run_func_name)
        
        # Run the experiment with the provided kwargs
        print(f"Running {experiment_name} experiment with parameters: {kwargs}")
        return run_func(**kwargs)
        
    except ImportError as e:
        print(f"Error importing experiment module: {e}")
        raise
    except Exception as e:
        print(f"Error running experiment: {e}")
        raise

def experiment_threshold_effects():
    """Experiment 1: How does the threshold θₜ affect ignition probability?"""
    print("Running Experiment 1: Threshold Effects")
    
    # Test different threshold values
    thresholds = [3.0, 5.0, 7.0]
    n_simulations = 5
    
    plt.figure(figsize=(12, 6))
    
    for theta in thresholds:
        params = APGIParams(theta_base=theta, n_steps=500)
        model = APGIModel(params)
        
        # Run multiple simulations for each threshold
        all_B = []
        for _ in range(n_simulations):
            _, B_t, _ = model.simulate()
            all_B.append(B_t)
        
        # Plot mean and std across simulations
        mean_B = np.mean(all_B, axis=0)
        std_B = np.std(all_B, axis=0)
        
        plt.plot(mean_B, label=f'θₜ = {theta}')
        plt.fill_between(range(len(mean_B)), 
                        mean_B - std_B, 
                        mean_B + std_B, 
                        alpha=0.2)
    
    plt.title('Effect of Threshold (θₜ) on Ignition Probability')
    plt.xlabel('Time Step')
    plt.ylabel('Mean Ignition Probability (Bₜ)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('threshold_effects.png')
    plt.show()

def experiment_somatic_markers():
    """Experiment 2: How do somatic markers (M_{c,a}) influence ignition?"""
    print("Running Experiment 2: Somatic Marker Effects")
    
    # Test different somatic marker values
    mc_a_values = [0.1, 0.5, 1.0, 2.0]
    params = APGIParams(n_steps=1000)
    model = APGIModel(params)
    
    plt.figure(figsize=(12, 8))
    
    for i, mc_a in enumerate(mc_a_values, 1):
        S_t, B_t, theta_t = model.simulate(mc_a=mc_a)
        
        plt.subplot(2, 2, i)
        plt.plot(S_t, 'b-', alpha=0.7, label='Sₜ (Surprise)')
        plt.axhline(y=theta_t[0], color='r', linestyle='--', label='θₜ (Threshold)')
        plt.plot(np.where(B_t > 0.5, S_t, np.nan), 'go', 
                markersize=3, alpha=0.5, label='Ignition (Bₜ > 0.5)')
        
        plt.title(f'Somatic Marker M_{{c,a}} = {mc_a}')
        plt.xlabel('Time Step')
        plt.ylabel('Value')
        plt.legend()
        plt.grid(True)
    
    plt.tight_layout()
    plt.savefig('somatic_marker_effects.png')
    plt.show()

def experiment_precision_effects():
    """Experiment 3: How do precision parameters affect ignition?"""
    print("Running Experiment 3: Precision Effects")
    
    # Test different precision values
    precision_combinations = [
        (0.5, 0.5),  # Low extero, low intero
        (2.0, 0.5),  # High extero, low intero
        (0.5, 2.0),  # Low extero, high intero
        (2.0, 2.0)   # High extero, high intero
    ]
    
    n_steps = 500
    n_simulations = 10
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()
    
    for idx, (sigma_pe, sigma_pi) in enumerate(precision_combinations):
        params = APGIParams(
            n_steps=n_steps,
            sigma_pe=sigma_pe,
            sigma_pi=sigma_pi,
            theta_base=5.0
        )
        model = APGIModel(params)
        
        # Run multiple simulations
        ignition_counts = np.zeros(n_steps)
        
        for _ in range(n_simulations):
            S_t, B_t, _ = model.simulate()
            ignition_counts += (B_t > 0.5).astype(int)
        
        # Convert to probability
        ignition_prob = ignition_counts / n_simulations
        
        # Plot
        axes[idx].plot(ignition_prob, 'b-', alpha=0.7)
        axes[idx].set_title(f'Πₑ={1/sigma_pe**2:.1f}, Πᵢ={1/sigma_pi**2:.1f}')
        axes[idx].set_xlabel('Time Step')
        axes[idx].set_ylabel('Ignition Probability')
        axes[idx].grid(True)
        axes[idx].set_ylim(-0.05, 1.05)
    
    plt.suptitle('Effects of Precision Parameters on Ignition Probability')
    plt.tight_layout()
    plt.savefig('precision_effects.png')
    plt.show()

def experiment_dynamic_threshold():
    """Experiment 4: Dynamic threshold based on context."""
    print("Running Experiment 4: Dynamic Threshold")
    
    class DynamicThresholdModel(APGIModel):
        """Extends APGIModel with dynamic threshold based on surprise history."""
        def __init__(self, params: APGIParams):
            super().__init__(params)
            self.theta = params.theta_base
            self.adaptation_rate = 0.01
            
        def update_threshold(self, surprise: float) -> float:
            """Dynamically adjust threshold based on recent surprise."""
            # Adjust threshold based on whether surprise is increasing or decreasing
            self.theta += self.adaptation_rate * (surprise - self.theta)
            return self.theta
    
    # Create models
    static_model = APGIModel(APGIParams(n_steps=1000, theta_base=5.0))
    dynamic_model = DynamicThresholdModel(APGIParams(n_steps=1000, theta_base=5.0))
    
    # Run simulations
    S_static, B_static, theta_static = static_model.simulate()
    
    # For dynamic model, we need to run step by step
    n_steps = 1000
    S_dynamic = np.zeros(n_steps)
    B_dynamic = np.zeros(n_steps)
    theta_dynamic = np.zeros(n_steps)
    
    # Generate prediction errors
    epsilon_e, epsilon_i = dynamic_model.generate_prediction_errors(n_steps)
    
    # Compute precisions
    Pi_e = dynamic_model.compute_precision(dynamic_model.params.sigma_pe**2)
    Pi_i = dynamic_model.compute_precision(dynamic_model.params.sigma_pi**2)
    mc_a = dynamic_model.compute_somatic_marker(0, 0)
    
    # Run simulation with dynamic threshold
    for t in range(n_steps):
        # Compute surprise
        S_t = Pi_e * np.abs(epsilon_e[t]) + (Pi_i * mc_a) * np.abs(epsilon_i[t])
        S_dynamic[t] = S_t
        
        # Get current threshold and compute ignition probability
        theta_t = dynamic_model.theta
        theta_dynamic[t] = theta_t
        B_dynamic[t] = dynamic_model.sigmoid(S_t - theta_t)
        
        # Update threshold for next step
        dynamic_model.update_threshold(S_t)
    
    # Plot results
    plt.figure(figsize=(14, 8))
    
    # Static threshold results
    plt.subplot(2, 1, 1)
    plt.plot(S_static, 'b-', alpha=0.7, label='Surprise (Sₜ)')
    plt.plot(theta_static, 'r--', label='Threshold (θₜ)')
    plt.plot(np.where(B_static > 0.5, S_static, np.nan), 'go', 
             markersize=3, alpha=0.5, label='Ignition (Bₜ > 0.5)')
    plt.title('Static Threshold Model')
    plt.legend()
    plt.grid(True)
    
    # Dynamic threshold results
    plt.subplot(2, 1, 2)
    plt.plot(S_dynamic, 'b-', alpha=0.7, label='Surprise (Sₜ)')
    plt.plot(theta_dynamic, 'r-', label='Dynamic Threshold (θₜ)')
    plt.plot(np.where(B_dynamic > 0.5, S_dynamic, np.nan), 'go', 
             markersize=3, alpha=0.5, label='Ignition (Bₜ > 0.5)')
    plt.title('Dynamic Threshold Model')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig('dynamic_threshold.png')
    plt.show()

def main_demo():
    """Run all experiments."""
    print("Starting APGI Framework Experiments")
    print("-" * 50)
    
    # Run experiments
    experiment_threshold_effects()
    experiment_somatic_markers()
    experiment_precision_effects()
    experiment_dynamic_threshold()
    
    print("\nAll experiments completed!")

def main():
    """If no CLI args are provided, run all demos; otherwise run a specific experiment module."""
    if len(sys.argv) == 1:
        # No arguments: run the demo suite
        return main_demo()

    parser = argparse.ArgumentParser(description='Run APGI consciousness experiments')
    
    # Add common arguments
    parser.add_argument('experiment', 
                       choices=EXPERIMENTS.keys(),
                       help='Name of the experiment to run')
    
    # Add experiment-specific arguments
    parser.add_argument('--n_participants', type=int, default=10,
                       help='Number of participants to simulate')
    parser.add_argument('--n_trials', type=int, default=50,
                       help='Number of trials per condition')
    parser.add_argument('--output', type=str, default=None,
                       help='Output file path for results (CSV)')
    
    # Parse known arguments first
    args, remaining_args = parser.parse_known_args()
    
    # Convert remaining args to dict of key-value pairs
    experiment_kwargs = {}
    i = 0
    while i < len(remaining_args):
        if remaining_args[i].startswith('--'):
            key = remaining_args[i][2:]
            if i + 1 < len(remaining_args) and not remaining_args[i+1].startswith('--'):
                # Try to evaluate the value (to handle numbers, lists, etc.)
                try:
                    experiment_kwargs[key] = eval(remaining_args[i+1])
                except (NameError, SyntaxError):
                    experiment_kwargs[key] = remaining_args[i+1]
                i += 2
            else:
                # Flag without value, assume boolean True
                experiment_kwargs[key] = True
                i += 1
        else:
            i += 1
    
    # Add common arguments to experiment kwargs
    experiment_kwargs.update({
        'n_participants': args.n_participants,
        'n_trials_per_condition': args.n_trials
    })
    
    if args.output:
        experiment_kwargs['output_file'] = args.output
    
    # Run the experiment
    try:
        result = run_experiment(args.experiment, **experiment_kwargs)
        print("\nExperiment completed successfully!")
        return 0
    except Exception as e:
        print(f"\nError running experiment: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
