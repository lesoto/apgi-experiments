"""
APGI Framework Experiments

This script demonstrates the APGI model through several experiments that explore different aspects of the ignition threshold mechanism.
"""

import ast
import matplotlib.pyplot as plt
import numpy as np
import argparse
import importlib
import sys
from pathlib import Path

# Add project root to Python path first
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Now import modules
try:
    from models.apgi_model import APGIModel, APGIParams
except ImportError:
    # Try alternative import paths
    try:
        from apgi_framework.core.equation import APGIEquation

        # Create compatibility wrappers
        class APGIParams:
            def __init__(self, **kwargs):
                self.theta_base = kwargs.get("theta_base", 5.0)
                self.n_steps = kwargs.get("n_steps", 1000)
                self.sigma_pe = kwargs.get("sigma_pe", 0.5)
                self.sigma_pi = kwargs.get("sigma_pi", 0.5)

        class APGIModel:
            def __init__(self, params):
                self.params = params
                self.equation = APGIEquation()

            def generate_prediction_errors(self, n_steps):
                np.random.seed(42)
                return np.random.randn(n_steps), np.random.randn(n_steps)

            def compute_precision(self, variance):
                return 1.0 / variance if variance > 0 else 1.0

            def compute_somatic_marker(self, context, arousal):
                return 1.0

            def sigmoid(self, x):
                return 1.0 / (1.0 + np.exp(-np.clip(x, -500, 500)))

            def simulate(self, mc_a=None):
                n_steps = self.params.n_steps
                epsilon_e, epsilon_i = self.generate_prediction_errors(n_steps)

                Pi_e = self.compute_precision(self.params.sigma_pe**2)
                Pi_i = self.compute_precision(self.params.sigma_pi**2)
                mc_a = mc_a or self.compute_somatic_marker(0, 0)

                S_t = Pi_e * np.abs(epsilon_e) + (Pi_i * mc_a) * np.abs(epsilon_i)
                B_t = self.sigmoid(S_t - self.params.theta_base)
                theta_t = np.full(n_steps, self.params.theta_base)

                return S_t, B_t, theta_t

    except Exception as e:
        logger.warning(f"Could not import APGI model: {e}, using mock implementation")

        class APGIParams:
            def __init__(self, **kwargs):
                self.theta_base = kwargs.get("theta_base", 5.0)
                self.n_steps = kwargs.get("n_steps", 1000)
                self.sigma_pe = kwargs.get("sigma_pe", 0.5)
                self.sigma_pi = kwargs.get("sigma_pi", 0.5)

        class APGIModel:
            def __init__(self, params):
                self.params = params

            def generate_prediction_errors(self, n_steps):
                np.random.seed(42)
                return np.random.randn(n_steps), np.random.randn(n_steps)

            def compute_precision(self, variance):
                return 1.0 / variance if variance > 0 else 1.0

            def compute_somatic_marker(self, context, arousal):
                return 1.0

            def sigmoid(self, x):
                return 1.0 / (1.0 + np.exp(-np.clip(x, -500, 500)))

            def simulate(self, mc_a=None):
                n_steps = self.params.n_steps
                epsilon_e, epsilon_i = self.generate_prediction_errors(n_steps)

                Pi_e = self.compute_precision(self.params.sigma_pe**2)
                Pi_i = self.compute_precision(self.params.sigma_pi**2)
                mc_a = mc_a or self.compute_somatic_marker(0, 0)

                S_t = Pi_e * np.abs(epsilon_e) + (Pi_i * mc_a) * np.abs(epsilon_i)
                B_t = self.sigmoid(S_t - self.params.theta_base)
                theta_t = np.full(n_steps, self.params.theta_base)

                return S_t, B_t, theta_t


from apgi_framework.logging.standardized_logging import get_logger

plt.style.use("ggplot")
plt.rcParams["figure.facecolor"] = "white"

# Initialize logger
logger = get_logger("run_experiments")

EXPERIMENTS = {
    "interoceptive_gating": "examples.01_run_primary_falsification_test",
    "somatic_marker_priming": "examples.02_batch_processing_configurations",
    "metabolic_cost": "examples.03_custom_analysis_saved_results",
    "ai_benchmarking": "examples.04_extending_falsification_criteria",
    # Fallback to examples for other experiments
    "iowa_gambling_task": "examples.01_run_primary_falsification_test",
    "probabilistic_category_learning": "examples.02_batch_processing_configurations",
    "attentional_blink": "examples.03_custom_analysis_saved_results",
    "change_blindness": "examples.04_extending_falsification_criteria",
    "visual_search": "examples.01_run_primary_falsification_test",
    "posner_cueing": "examples.02_batch_processing_configurations",
    "stroop_effect": "examples.03_custom_analysis_saved_results",
    "simon_effect": "examples.04_extending_falsification_criteria",
    "eriksen_flanker": "examples.01_run_primary_falsification_test",
    "masking": "examples.02_batch_processing_configurations",
    "binocular_rivalry": "examples.03_custom_analysis_saved_results",
    "inattentional_blindness": "examples.04_extending_falsification_criteria",
    "dual_n_back": "examples.01_run_primary_falsification_test",
    "sternberg_memory": "examples.02_batch_processing_configurations",
    "working_memory_span": "examples.03_custom_analysis_saved_results",
    "drm_false_memory": "examples.04_extending_falsification_criteria",
    "go_no_go": "examples.01_run_primary_falsification_test",
    "stop_signal": "examples.02_batch_processing_configurations",
    "navon_task": "examples.03_custom_analysis_saved_results",
    "multisensory_integration": "examples.04_extending_falsification_criteria",
    "serial_reaction_time": "examples.01_run_primary_falsification_test",
    "artificial_grammar_learning": "examples.02_batch_processing_configurations",
    "time_estimation": "examples.03_custom_analysis_saved_results",
    "virtual_navigation": "examples.04_extending_falsification_criteria",
}


def _is_safe_data_structure(data) -> bool:
    """
    Validate that nested data structures don't contain dangerous elements.

    Args:
        data: Data structure to validate (list, dict, or tuple)

    Returns:
        True if safe, False if potentially dangerous
    """
    dangerous_patterns = [
        "__import__",
        "eval(",
        "exec(",
        "compile(",
        "subprocess",
        "os.system",
        "os.popen",
        "open(",
        "socket",
        "urllib",
        "http",
        "ftplib",
        "pickle.loads",
        "pickle.load",
        "pickle.dump",
    ]

    def check_string_safety(safety_string):
        if not isinstance(safety_string, str):
            return True
        return not any(
            pattern in safety_string.lower() for pattern in dangerous_patterns
        )

    if isinstance(data, (list, tuple)):
        return all(_is_safe_data_structure(item) for item in data)
    elif isinstance(data, dict):
        return all(
            check_string_safety(k) and _is_safe_data_structure(v)
            for k, v in data.items()
        )
    elif isinstance(data, str):
        return check_string_safety(data)
    else:
        return True


def get_available_experiments() -> Dict[str, str]:
    """Return a dictionary of available experiments."""
    return EXPERIMENTS


def run_experiment(experiment_name: str, **kwargs):
    """Run the specified experiment with the given parameters."""
    if experiment_name not in EXPERIMENTS:
        raise ValueError(
            f"Unknown experiment: {experiment_name}. "
            f"Available experiments: {', '.join(EXPERIMENTS.keys())}"
        )

    try:
        module_path = EXPERIMENTS[experiment_name]
        module = importlib.import_module(module_path)

        # Get the run function (should be named run_{experiment_name}_experiment)
        run_func_name = f"run_{experiment_name}_experiment"
        if not hasattr(module, run_func_name):
            raise AttributeError(
                f"Module {module_path} does not contain function {run_func_name}"
            )

        run_func = getattr(module, run_func_name)

        # Handle parameter name mapping for compatibility
        mapped_kwargs = kwargs.copy()
        if (
            "n_trials" in mapped_kwargs
            and "n_trials_per_condition" not in mapped_kwargs
        ):
            mapped_kwargs["n_trials_per_condition"] = mapped_kwargs.pop("n_trials")

        # Run the experiment with the provided kwargs
        logger.info(
            f"Running {experiment_name} experiment with parameters: {mapped_kwargs}"
        )
        return run_func(**mapped_kwargs)

    except ImportError as e:
        logger.error(f"Error importing experiment module: {e}")
        raise
    except Exception as e:
        logger.error(f"Error running experiment: {e}")
        raise


def experiment_threshold_effects():
    """Experiment 1: How does the threshold θₜ affect ignition probability?"""
    logger.info("Running Experiment 1: Threshold Effects")

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

        plt.plot(mean_B, label=f"θₜ = {theta}")
        plt.fill_between(range(len(mean_B)), mean_B - std_B, mean_B + std_B, alpha=0.2)

    plt.title("Effect of Threshold (θₜ) on Ignition Probability")
    plt.xlabel("Time Step")
    plt.ylabel("Mean Ignition Probability (Bₜ)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("threshold_effects.png")
    plt.show()


def experiment_somatic_markers():
    """Experiment 2: How do somatic markers (M_{c,a}) influence ignition?"""
    logger.info("Running Experiment 2: Somatic Marker Effects")

    # Test different somatic marker values
    mc_a_values = [0.1, 0.5, 1.0, 2.0]
    params = APGIParams(n_steps=1000)
    model = APGIModel(params)

    plt.figure(figsize=(12, 8))

    for i, mc_a in enumerate(mc_a_values, 1):
        S_t, B_t, theta_t = model.simulate(mc_a=mc_a)

        plt.subplot(2, 2, i)
        plt.plot(S_t, "b-", alpha=0.7, label="Sₜ (Surprise)")
        plt.axhline(y=theta_t[0], color="r", linestyle="--", label="θₜ (Threshold)")
        plt.plot(
            np.where(B_t > 0.5, S_t, np.nan),
            "go",
            markersize=3,
            alpha=0.5,
            label="Ignition (Bₜ > 0.5)",
        )

        plt.title(f"Somatic Marker M_{{c,a}} = {mc_a}")
        plt.xlabel("Time Step")
        plt.ylabel("Value")
        plt.legend()
        plt.grid(True)

    plt.tight_layout()
    plt.savefig("somatic_marker_effects.png")
    plt.show()


def experiment_precision_effects():
    """Experiment 3: How do precision parameters affect ignition?"""
    logger.info("Running Experiment 3: Precision Effects")

    # Test different precision values
    precision_combinations = [
        (0.5, 0.5),  # Low extero, low intero
        (2.0, 0.5),  # High extero, low intero
        (0.5, 2.0),  # Low extero, high intero
        (2.0, 2.0),  # High extero, high intero
    ]

    n_steps = 500
    n_simulations = 10

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    for idx, (sigma_pe, sigma_pi) in enumerate(precision_combinations):
        params = APGIParams(
            n_steps=n_steps, sigma_pe=sigma_pe, sigma_pi=sigma_pi, theta_base=5.0
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
        axes[idx].plot(ignition_prob, "b-", alpha=0.7)
        axes[idx].set_title(f"Πₑ={1/sigma_pe**2:.1f}, Πᵢ={1/sigma_pi**2:.1f}")
        axes[idx].set_xlabel("Time Step")
        axes[idx].set_ylabel("Ignition Probability")
        axes[idx].grid(True)
        axes[idx].set_ylim(-0.05, 1.05)

    plt.suptitle("Effects of Precision Parameters on Ignition Probability")
    plt.tight_layout()
    plt.savefig("precision_effects.png")
    plt.show()


def experiment_dynamic_threshold():
    """Experiment 4: Dynamic threshold based on context."""
    logger.info("Running Experiment 4: Dynamic Threshold")

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
    plt.plot(S_static, "b-", alpha=0.7, label="Surprise (Sₜ)")
    plt.plot(theta_static, "r--", label="Threshold (θₜ)")
    plt.plot(
        np.where(B_static > 0.5, S_static, np.nan),
        "go",
        markersize=3,
        alpha=0.5,
        label="Ignition (Bₜ > 0.5)",
    )
    plt.title("Static Threshold Model")
    plt.legend()
    plt.grid(True)

    # Dynamic threshold results
    plt.subplot(2, 1, 2)
    plt.plot(S_dynamic, "b-", alpha=0.7, label="Surprise (Sₜ)")
    plt.plot(theta_dynamic, "r-", label="Dynamic Threshold (θₜ)")
    plt.plot(
        np.where(B_dynamic > 0.5, S_dynamic, np.nan),
        "go",
        markersize=3,
        alpha=0.5,
        label="Ignition (Bₜ > 0.5)",
    )
    plt.title("Dynamic Threshold Model")
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.savefig("dynamic_threshold.png")
    plt.show()


def main_demo():
    """Run all experiments."""
    logger.info("Starting APGI Framework Experiments")
    logger.info("-" * 50)

    # Run experiments
    experiment_threshold_effects()
    experiment_somatic_markers()
    experiment_precision_effects()
    experiment_dynamic_threshold()

    logger.info("\nAll experiments completed!")


def main():
    """If no CLI args are provided, run all demos; otherwise run a specific experiment module."""
    if len(sys.argv) == 1:
        # No arguments: run the demo suite
        return main_demo()

    parser = argparse.ArgumentParser(description="Run APGI consciousness experiments")

    # Add common arguments
    parser.add_argument(
        "experiment", choices=EXPERIMENTS.keys(), help="Name of the experiment to run"
    )

    # Add experiment-specific arguments
    parser.add_argument(
        "--n_participants",
        type=int,
        default=10,
        help="Number of participants to simulate",
    )
    parser.add_argument(
        "--n_trials", type=int, default=50, help="Number of trials per condition"
    )
    parser.add_argument(
        "--output", type=str, default=None, help="Output file path for results (CSV)"
    )

    # Parse known arguments first
    args, remaining_args = parser.parse_known_args()

    # Convert remaining args to dict of key-value pairs
    experiment_kwargs = {}
    i = 0
    while i < len(remaining_args):
        if remaining_args[i].startswith("--"):
            key = remaining_args[i][2:]
            if i + 1 < len(remaining_args) and not remaining_args[i + 1].startswith(
                "--"
            ):
                # Try to parse the value safely with strict validation
                try:
                    # Only allow specific safe types: numbers, strings, booleans, lists, dicts
                    parsed_value = ast.literal_eval(remaining_args[i + 1])
                    # Additional validation to prevent code execution
                    if isinstance(
                        parsed_value, (int, float, str, bool, list, dict, tuple)
                    ):
                        # Validate nested structures don't contain dangerous elements
                        if isinstance(parsed_value, (list, dict, tuple)):
                            if _is_safe_data_structure(parsed_value):
                                experiment_kwargs[key] = parsed_value
                            else:
                                logger.warning(
                                    f"Unsafe data structure in parameter {key}, skipping"
                                )
                        else:
                            experiment_kwargs[key] = parsed_value
                    else:
                        logger.warning(
                            f"Unsupported type {type(parsed_value)} for parameter {key}, skipping"
                        )
                except (ValueError, SyntaxError):
                    experiment_kwargs[key] = remaining_args[i + 1]
                i += 2
            else:
                # Flag without value, assume boolean True
                experiment_kwargs[key] = True
                i += 1
        else:
            i += 1

    # Add common arguments to experiment kwargs
    experiment_kwargs.update(
        {"n_participants": args.n_participants, "n_trials_per_condition": args.n_trials}
    )

    if args.output:
        experiment_kwargs["output_file"] = args.output

    # Run the experiment
    try:
        run_experiment(args.experiment, **experiment_kwargs)
        logger.info("\nExperiment completed successfully!")
        return 0
    except Exception as e:
        logger.error(f"\nError running experiment: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
