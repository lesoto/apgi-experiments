"""
Sternberg Memory implementation.

The Sternberg memory task assesses recognition memory and retrieval speed.
Participants memorize a set of items (positive set) and then indicate whether
probe items were in the memorized set. Reaction times typically increase
with set size, revealing serial vs. parallel search processes.

APGI Integration:
- θₜ (threshold): Memory retrieval threshold
- π (precision): Memory precision/confidence
- ε (prediction error): Recognition prediction error
- β (inverse temperature): Response consistency
"""

import random
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import time

from .. import TrialBasedTask, TrialBasedTaskConfig


@dataclass
class SternbergConfig(TrialBasedTaskConfig):
    """Configuration for Sternberg Memory experiment."""

    n_trials: int = 120
    study_duration_ms: int = 2000  # Time to study positive set
    retention_interval_ms: int = 1000  # Delay between study and test
    probe_duration_ms: int = 1500
    response_window_ms: int = 2000

    # Memory parameters
    set_sizes: List[int] = None  # Different positive set sizes
    stimulus_types: List[str] = None  # Types of stimuli to use

    # Stimulus parameters
    stimuli_pool: List[str] = None  # Pool of possible stimuli
    positive_set_ratio: float = 0.5  # Proportion of positive probes

    def __post_init__(self):
        if self.set_sizes is None:
            self.set_sizes = [2, 4, 6]

        if self.stimulus_types is None:
            self.stimulus_types = ["letters", "digits", "words"]

        if self.stimuli_pool is None:
            # Create a diverse stimulus pool
            letters = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
            digits = list("0123456789")
            words = [
                "APPLE",
                "CHAIR",
                "HOUSE",
                "MOUSE",
                "PAPER",
                "STONE",
                "WATER",
                "LIGHT",
            ]
            self.stimuli_pool = letters + digits + words


class SternbergStimulus:
    """Generate Sternberg memory stimuli."""

    def __init__(self, config: SternbergConfig):
        self.config = config

    def generate_trial(self, set_size: int) -> Dict[str, Any]:
        """Generate a single Sternberg trial."""
        # Select positive set (items to memorize)
        positive_set = random.sample(self.config.stimuli_pool, set_size)

        # Determine probe type
        is_positive = random.random() < self.config.positive_set_ratio

        if is_positive:
            # Probe is from positive set
            probe = random.choice(positive_set)
        else:
            # Probe is not from positive set
            available_probes = [
                s for s in self.config.stimuli_pool if s not in positive_set
            ]
            probe = random.choice(available_probes)

        trial = {
            "positive_set": positive_set,
            "set_size": set_size,
            "probe": probe,
            "is_positive": is_positive,
            "correct_response": "yes" if is_positive else "no",
        }

        return trial


class SternbergTask(TrialBasedTask):
    """Sternberg memory task implementation."""

    def __init__(self, config: Optional[SternbergConfig] = None):
        super().__init__(config)
        self.config = config or SternbergConfig()
        self.stimulus_generator = SternbergStimulus(self.config)
        self.memory_performance = {}

    def setup(self, **kwargs):
        """Set up the Sternberg memory task."""
        super().setup(**kwargs)
        self.stimulus_generator = SternbergStimulus(self.config)
        self.memory_performance = {}

    def generate_trial_sequence(self) -> List[Dict[str, Any]]:
        """Generate balanced trial sequence."""
        trials = []

        # Create balanced design across set sizes
        for set_size in self.config.set_sizes:
            n_trials_per_size = self.config.n_trials // len(self.config.set_sizes)

            for _ in range(n_trials_per_size):
                trials.append({"set_size": set_size, "condition": f"size_{set_size}"})

        # Randomize order
        random.shuffle(trials)

        # Add trial numbers
        for i, trial in enumerate(trials):
            trial["trial_number"] = i

        return trials

    def generate_trial_parameters(
        self, participant_id: int, trial_number: int
    ) -> Dict[str, Any]:
        """Generate parameters for a specific trial."""
        base_params = super().generate_trial_parameters(participant_id, trial_number)

        # Get trial configuration
        if trial_number < len(self.trial_sequence):
            trial_config = self.trial_sequence[trial_number]
        else:
            # Default configuration
            trial_config = {"set_size": 4, "condition": "size_4"}

        # Generate stimulus
        stimulus = self.stimulus_generator.generate_trial(trial_config["set_size"])

        base_params.update(
            {
                "positive_set": stimulus["positive_set"],
                "set_size": stimulus["set_size"],
                "probe": stimulus["probe"],
                "is_positive": stimulus["is_positive"],
                "correct_response": stimulus["correct_response"],
                "condition": trial_config["condition"],
                "study_duration_ms": self.config.study_duration_ms,
                "retention_interval_ms": self.config.retention_interval_ms,
                "probe_duration_ms": self.config.probe_duration_ms,
            }
        )

        return base_params

    def process_response(
        self, response: Any, correct_response: Any, trial_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Process Sternberg memory response."""
        # Response should be 'yes' or 'no'
        if isinstance(response, str):
            response_str = response.lower()
        else:
            response_str = str(response).lower()

        correct_str = correct_response.lower()
        is_correct = response_str == correct_str

        # Get memory set parameters from trial data or use defaults
        memory_set_size = 4  # Default
        probe_type = "positive"  # Default

        if trial_data:
            memory_set_size = trial_data.get("set_size", 4)
            probe_type = (
                "positive" if trial_data.get("is_positive", False) else "negative"
            )

        # Store performance by set size
        if memory_set_size not in self.memory_performance:
            self.memory_performance[memory_set_size] = {
                "accuracy": [],
                "reaction_times": [],
                "positive_accuracy": [],
                "negative_accuracy": [],
            }

        self.memory_performance[memory_set_size]["accuracy"].append(
            1 if is_correct else 0
        )
        self.memory_performance[memory_set_size]["reaction_times"].append(
            0
        )  # Will be updated later

        # Store by probe type
        if probe_type == "positive":
            self.memory_performance[memory_set_size]["positive_accuracy"].append(
                1 if is_correct else 0
            )
        else:
            self.memory_performance[memory_set_size]["negative_accuracy"].append(
                1 if is_correct else 0
            )

        # Calculate confidence based on accuracy and set size
        base_confidence = 0.8 if is_correct else 0.4
        base_confidence *= (
            1.0 - memory_set_size * 0.05
        )  # Lower confidence for larger sets

        return {
            "response": response_str,
            "accuracy": 1 if is_correct else 0,
            "reaction_time_ms": 0,  # Will be filled by simulate_response
            "confidence": base_confidence,
            "probe": trial_data.get("probe", "A") if trial_data else "A",
            "memory_set_size": memory_set_size,
            "probe_type": probe_type,
            "probe_item": trial_data.get("probe_item", "A") if trial_data else "A",
            "condition": (
                trial_data.get("condition", "unknown") if trial_data else "unknown"
            ),
        }

    def simulate_response(self, trial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate participant Sternberg memory performance."""
        set_size = trial_data["set_size"]
        probe = trial_data["probe"]
        is_positive = trial_data["is_positive"]
        positive_set = trial_data["positive_set"]

        # Base accuracy decreases with set size
        base_accuracy = 0.95 - (set_size * 0.05)
        base_accuracy = max(0.6, base_accuracy)

        # Positive trials (probe in set) are typically harder than negative trials
        if is_positive:
            base_accuracy -= 0.05

        # Calculate response probability
        response_prob = base_accuracy

        # Generate response
        if random.random() < response_prob:
            response = trial_data["correct_response"]
        else:
            # Incorrect response
            response = "no" if trial_data["correct_response"] == "yes" else "yes"

        # Calculate reaction time (increases with set size)
        # Classic Sternberg effect: ~38ms per item
        base_rt = 600 + (set_size * 38)

        # Positive trials are typically slower
        if is_positive:
            base_rt += 50

        rt = max(300, np.random.normal(base_rt, 120))

        # Calculate confidence
        actual_correct = response == trial_data["correct_response"]
        confidence = 0.8 if actual_correct else 0.4
        confidence *= 1.0 - set_size * 0.05

        return {
            "response": response,
            "reaction_time_ms": int(rt),
            "confidence": confidence,
            "timestamp": time.time(),
        }

    def compute_participant_summary(
        self, trials: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compute comprehensive summary for Sternberg memory task."""
        base_summary = super().compute_participant_summary(trials)

        if not trials:
            return base_summary

        df = pd.DataFrame(trials)

        # Sternberg specific metrics
        summary = {
            **base_summary,
            "overall_accuracy": 0,
            "mean_reaction_time": 0,
            "set_size_effects": {},
            "memory_search_slope": 0,
            "probe_type_effects": {},
        }

        # Overall metrics
        if "accuracy" in df.columns:
            summary["overall_accuracy"] = df["accuracy"].mean()

        if "reaction_time_ms" in df.columns:
            summary["mean_reaction_time"] = df["reaction_time_ms"].mean()

        # Performance by set size
        set_sizes = []
        mean_rts = []
        accuracies = []

        for set_size in sorted(df["set_size"].unique()):
            size_data = df[df["set_size"] == set_size]
            if len(size_data) > 0:
                accuracy = (
                    size_data["accuracy"].mean()
                    if "accuracy" in size_data.columns
                    else 0
                )
                mean_rt = (
                    size_data["reaction_time_ms"].mean()
                    if "reaction_time_ms" in size_data.columns
                    else 0
                )
                positive_acc = (
                    size_data[size_data["is_positive"] == True]["accuracy"].mean()
                    if "accuracy" in size_data.columns
                    else 0
                )
                negative_acc = (
                    size_data[size_data["is_positive"] == False]["accuracy"].mean()
                    if "accuracy" in size_data.columns
                    else 0
                )

                summary["set_size_effects"][f"size_{set_size}"] = {
                    "accuracy": accuracy,
                    "mean_rt": mean_rt,
                    "positive_accuracy": positive_acc,
                    "negative_accuracy": negative_acc,
                    "n_trials": len(size_data),
                }

                set_sizes.append(set_size)
                mean_rts.append(mean_rt)
                accuracies.append(accuracy)

        # Calculate memory search slope (RT slope as function of set size)
        if len(set_sizes) > 1:
            slope, intercept = np.polyfit(set_sizes, mean_rts, 1)
            summary["memory_search_slope"] = {
                "slope_ms_per_item": slope,
                "intercept_ms": intercept,
                "r_squared": (
                    np.corrcoef(set_sizes, mean_rts)[0, 1] ** 2
                    if len(set_sizes) > 1
                    else 0
                ),
            }

            # Interpret slope
            if abs(slope) < 10:
                search_type = "parallel"
            elif abs(slope) > 30:
                search_type = "serial"
            else:
                search_type = "mixed"

            summary["memory_search_slope"]["search_type"] = search_type

        # Probe type effects
        positive_trials = df[df["is_positive"] == True]
        negative_trials = df[df["is_positive"] == False]

        if len(positive_trials) > 0:
            summary["probe_type_effects"]["positive"] = {
                "accuracy": (
                    positive_trials["accuracy"].mean()
                    if "accuracy" in positive_trials.columns
                    else 0
                ),
                "mean_rt": (
                    positive_trials["reaction_time_ms"].mean()
                    if "reaction_time_ms" in positive_trials.columns
                    else 0
                ),
                "n_trials": len(positive_trials),
            }

        if len(negative_trials) > 0:
            summary["probe_type_effects"]["negative"] = {
                "accuracy": (
                    negative_trials["accuracy"].mean()
                    if "accuracy" in negative_trials.columns
                    else 0
                ),
                "mean_rt": (
                    negative_trials["reaction_time_ms"].mean()
                    if "reaction_time_ms" in negative_trials.columns
                    else 0
                ),
                "n_trials": len(negative_trials),
            }

        # Calculate d' (signal detection measure)
        if len(positive_trials) > 0 and len(negative_trials) > 0:
            hit_rate = (
                positive_trials["accuracy"].mean()
                if "accuracy" in positive_trials.columns
                else 0
            )
            false_alarm_rate = (
                1 - negative_trials["accuracy"].mean()
                if "accuracy" in negative_trials.columns
                else 0
            )

            # Avoid extreme values
            hit_rate = np.clip(hit_rate, 0.01, 0.99)
            false_alarm_rate = np.clip(false_alarm_rate, 0.01, 0.99)

            # Calculate d' and criterion
            from scipy import stats

            d_prime = stats.norm.ppf(hit_rate) - stats.norm.ppf(false_alarm_rate)
            criterion = (
                -(stats.norm.ppf(hit_rate) + stats.norm.ppf(false_alarm_rate)) / 2
            )

            summary["signal_detection"] = {
                "d_prime": d_prime,
                "criterion": criterion,
                "hit_rate": hit_rate,
                "false_alarm_rate": false_alarm_rate,
            }

        return summary


def run_sternberg_memory_experiment(**kwargs):
    """Run the Sternberg Memory experiment."""
    # Create config with provided parameters
    config_params = {}

    # Map common parameters
    param_mapping = {
        "n_participants": "n_participants",
        "n_trials": "n_trials",
        "n_trials_per_condition": "n_trials",
    }

    for key, value in kwargs.items():
        config_key = param_mapping.get(key, key)
        if hasattr(SternbergConfig, config_key):
            config_params[config_key] = value

    # Create config and experiment
    config = SternbergConfig(**config_params)
    experiment = SternbergTask(config)

    # Set up and run experiment
    experiment.setup()
    results = experiment.run_experiment()

    # Save results if output file specified
    if kwargs.get("output_file"):
        experiment.save_data(kwargs["output_file"])

    return experiment


if __name__ == "__main__":
    # Example usage
    config = SternbergConfig(
        n_trials=120, n_participants=5, set_sizes=[2, 4, 6], positive_set_ratio=0.5
    )

    experiment = SternbergTask(config)
    experiment.setup()
    results = experiment.run_experiment()

    print("Sternberg Memory experiment completed!")
    print(f"Results shape: {results.shape}")

    # Print summary for first participant
    if experiment.participant_data:
        first_participant = list(experiment.participant_data.keys())[0]
        summary = experiment.participant_data[first_participant]["summary"]
        print(f"\nParticipant {first_participant} Summary:")
        print(f"Overall Accuracy: {summary.get('overall_accuracy', 0):.3f}")
        print(f"Mean Reaction Time: {summary.get('mean_reaction_time', 0):.1f} ms")
        print(
            f"Memory Search Slope: {summary.get('memory_search_slope', {}).get('slope_ms_per_item', 0):.1f} ms/item"
        )
        print(f"Set Size Effects: {summary.get('set_size_effects', {})}")
