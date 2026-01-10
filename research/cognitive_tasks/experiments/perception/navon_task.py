"""
Navon Task implementation.

The Navon task measures global vs. local processing bias. Participants view
large letters made of smaller letters and must identify either the global letter
or the local letters. This reveals attentional processing style and hierarchical
perception preferences.

APGI Integration:
- θₜ (threshold): Global/local processing threshold
- π (precision): Spatial attention precision
- ε (prediction error): Global-local conflict prediction error
- β (inverse temperature): Processing consistency
"""

import random
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import time

from .. import TrialBasedTask, TrialBasedTaskConfig


@dataclass
class NavonConfig(TrialBasedTaskConfig):
    """Configuration for Navon experiment."""

    n_trials: int = 120
    stimulus_duration_ms: int = 2000
    response_window_ms: int = 3000
    inter_trial_interval_ms: int = 1000

    # Navon parameters
    global_letters: List[str] = None  # Large letters
    local_letters: List[str] = None  # Small letters
    grid_size: int = 5  # Size of grid for local letters
    congruency_types: List[str] = None  # congruent, incongruent, neutral

    # Task parameters
    target_levels: List[str] = None  # global, local, both
    response_mapping: Dict[str, str] = None  # Key mappings for responses

    def __post_init__(self):
        if self.global_letters is None:
            self.global_letters = ["H", "S", "E", "T", "F"]

        if self.local_letters is None:
            self.local_letters = ["X", "O", "A", "L", "I"]

        if self.congruency_types is None:
            self.congruency_types = ["congruent", "incongruent", "neutral"]

        if self.target_levels is None:
            self.target_levels = ["global", "local"]

        if self.response_mapping is None:
            self.response_mapping = {
                "H": "h",
                "S": "s",
                "E": "e",
                "T": "t",
                "F": "f",
                "X": "x",
                "O": "o",
                "A": "a",
                "L": "l",
                "I": "i",
            }


class NavonStimulus:
    """Generate Navon hierarchical stimuli."""

    def __init__(self, config: NavonConfig):
        self.config = config

    def generate_stimulus(
        self, global_letter: str, local_letter: str, congruency: str
    ) -> Dict[str, Any]:
        """Generate a Navon stimulus."""
        # Create grid of local letters
        grid = [
            [local_letter for _ in range(self.config.grid_size)]
            for _ in range(self.config.grid_size)
        ]

        # Determine congruency
        if congruency == "congruent":
            # Global and local letters are the same
            global_letter = local_letter
        elif congruency == "incongruent":
            # Global and local letters are different
            # Ensure they're different
            if global_letter == local_letter:
                available_globals = [
                    l for l in self.config.global_letters if l != local_letter
                ]
                global_letter = (
                    random.choice(available_globals)
                    if available_globals
                    else global_letter
                )
        else:  # neutral
            # Use neutral configuration (e.g., global letter not in local set)
            pass

        stimulus = {
            "global_letter": global_letter,
            "local_letter": local_letter,
            "grid": grid,
            "congruency": congruency,
            "is_congruent": global_letter == local_letter,
            "is_incongruent": congruency == "incongruent"
            and global_letter != local_letter,
            "is_neutral": congruency == "neutral",
        }

        return stimulus

    def generate_random_stimulus(self) -> Dict[str, Any]:
        """Generate a random Navon stimulus."""
        congruency = random.choice(self.config.congruency_types)
        local_letter = random.choice(self.config.local_letters)

        stimulus = self.generate_stimulus("", local_letter, congruency)

        return stimulus


class NavonTask(TrialBasedTask):
    """Navon task implementation."""

    def __init__(self, config: Optional[NavonConfig] = None):
        super().__init__(config)
        self.config = config or NavonConfig()
        self.stimulus_generator = NavonStimulus(self.config)
        self.processing_bias = {}

    def setup(self, **kwargs):
        """Set up the Navon task."""
        super().setup(**kwargs)
        self.stimulus_generator = NavonStimulus(self.config)
        self.processing_bias = {}

    def generate_trial_sequence(self) -> List[Dict[str, Any]]:
        """Generate balanced trial sequence."""
        trials = []

        # Create balanced design across congruency and target levels
        for congruency in self.config.congruency_types:
            for target_level in self.config.target_levels:
                n_trials_condition = self.config.n_trials // (
                    len(self.config.congruency_types) * len(self.config.target_levels)
                )

                for _ in range(n_trials_condition):
                    trials.append(
                        {
                            "congruency": congruency,
                            "target_level": target_level,
                            "condition": f"{congruency}_{target_level}",
                        }
                    )

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
            trial_config = {
                "congruency": "congruent",
                "target_level": "global",
                "condition": "congruent_global",
            }

        # Generate stimulus
        stimulus = self.stimulus_generator.generate_random_stimulus()

        # Override congruency if specified
        if trial_config["congruency"] != stimulus["congruency"]:
            local_letter = stimulus["local_letter"]
            stimulus = self.stimulus_generator.generate_stimulus(
                "", local_letter, trial_config["congruency"]
            )

        # Determine correct response based on target level
        if trial_config["target_level"] == "global":
            correct_response = self.config.response_mapping.get(
                stimulus["global_letter"], stimulus["global_letter"].lower()
            )
        elif trial_config["target_level"] == "local":
            correct_response = self.config.response_mapping.get(
                stimulus["local_letter"], stimulus["local_letter"].lower()
            )
        else:  # both - respond with global letter
            correct_response = self.config.response_mapping.get(
                stimulus["global_letter"], stimulus["global_letter"].lower()
            )

        base_params.update(
            {
                "stimulus": stimulus,
                "global_letter": stimulus["global_letter"],
                "local_letter": stimulus["local_letter"],
                "grid": stimulus["grid"],
                "congruency": stimulus["congruency"],
                "target_level": trial_config["target_level"],
                "correct_response": correct_response,
                "is_congruent": stimulus["is_congruent"],
                "is_incongruent": stimulus["is_incongruent"],
                "is_neutral": stimulus["is_neutral"],
                "condition": trial_config["condition"],
                "stimulus_duration_ms": self.config.stimulus_duration_ms,
            }
        )

        return base_params

    def process_response(
        self, response: Any, correct_response: Any, trial_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Process Navon task response."""
        # Handle different response formats
        if isinstance(response, str):
            response_str = response.lower()
        else:
            response_str = str(response).lower()

        correct_str = correct_response.lower()
        is_correct = response_str == correct_str

        # Get trial data from parameters if available
        if trial_data:
            congruency = trial_data.get("congruency", "congruent")
            target_level = trial_data.get("target_level", "global")
            global_letter = trial_data.get("global_letter", "unknown")
            local_letter = trial_data.get("local_letter", "unknown")
            is_congruent = trial_data.get("is_congruent", False)
            is_incongruent = trial_data.get("is_incongruent", False)
            is_neutral = trial_data.get("is_neutral", False)
            condition = trial_data.get("condition", "default")
            reaction_time_ms = trial_data.get("reaction_time_ms", 800)
        else:
            # Default values
            congruency = "congruent"
            target_level = "global"
            global_letter = "unknown"
            local_letter = "unknown"
            is_congruent = False
            is_incongruent = False
            is_neutral = False
            condition = "default"
            reaction_time_ms = 800

        # Store processing bias data
        key = f"{congruency}_{target_level}"
        if key not in self.processing_bias:
            self.processing_bias[key] = {
                "accuracy": [],
                "reaction_times": [],
                "responses": [],
            }

        self.processing_bias[key]["accuracy"].append(1 if is_correct else 0)
        self.processing_bias[key]["responses"].append(response_str)

        if reaction_time_ms > 0:
            self.processing_bias[key]["reaction_times"].append(reaction_time_ms)

        # Calculate confidence based on accuracy and congruency
        base_confidence = 0.8 if is_correct else 0.4

        # Adjust confidence based on congruency
        if congruency == "congruent":
            base_confidence += 0.1
        elif congruency == "incongruent":
            base_confidence -= 0.1

        return {
            "response": response_str,
            "accuracy": 1 if is_correct else 0,
            "reaction_time_ms": reaction_time_ms,
            "confidence": base_confidence,
            "global_letter": global_letter,
            "local_letter": local_letter,
            "congruency": congruency,
            "target_level": target_level,
            "is_congruent": is_congruent,
            "is_incongruent": is_incongruent,
            "is_neutral": is_neutral,
            "correct_response": correct_str,
            "condition": condition,
        }

    def simulate_response(self, trial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate participant Navon task performance."""
        congruency = trial_data["congruency"]
        target_level = trial_data["target_level"]
        global_letter = trial_data["global_letter"]
        local_letter = trial_data["local_letter"]
        correct_response = trial_data["correct_response"]

        # Base accuracy depends on congruency and target level
        base_accuracy = 0.85

        # Congruency effects
        if congruency == "congruent":
            base_accuracy += 0.1  # Easier when global and local match
        elif congruency == "incongruent":
            base_accuracy -= 0.15  # Harder when they conflict
        else:  # neutral
            base_accuracy -= 0.05

        # Target level effects (global vs. local bias)
        # Simulate individual bias (some people prefer global, some local)
        global_bias = 0.1  # Slight global bias (typical)

        if target_level == "global":
            base_accuracy += global_bias
        else:  # local
            base_accuracy -= global_bias

        base_accuracy = np.clip(base_accuracy, 0.3, 0.95)

        # Generate response
        if random.random() < base_accuracy:
            response = correct_response
        else:
            # Generate incorrect response
            if target_level == "global":
                # Wrong global letter
                other_globals = [
                    l for l in self.config.global_letters if l != global_letter
                ]
                response = self.config.response_mapping.get(
                    random.choice(other_globals), "x"
                )
            else:
                # Wrong local letter
                other_locals = [
                    l for l in self.config.local_letters if l != local_letter
                ]
                response = self.config.response_mapping.get(
                    random.choice(other_locals), "x"
                )

        # Calculate reaction time
        base_rt = 800

        # Slower for incongruent trials
        if congruency == "incongruent":
            base_rt += 200
        elif congruency == "congruent":
            base_rt -= 100

        # Slower for local processing (typically harder)
        if target_level == "local":
            base_rt += 100

        rt = max(400, np.random.normal(base_rt, 150))

        # Calculate confidence
        actual_correct = response == correct_response
        confidence = 0.8 if actual_correct else 0.4

        if congruency == "congruent" and actual_correct:
            confidence += 0.1
        elif congruency == "incongruent" and not actual_correct:
            confidence -= 0.1

        return {
            "response": response,
            "reaction_time_ms": int(rt),
            "confidence": confidence,
            "timestamp": time.time(),
        }

    def compute_participant_summary(
        self, trials: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compute comprehensive summary for Navon task."""
        base_summary = super().compute_participant_summary(trials)

        if not trials:
            return base_summary

        df = pd.DataFrame(trials)

        # Navon specific metrics
        summary = {
            **base_summary,
            "overall_accuracy": 0,
            "mean_reaction_time": 0,
            "global_local_bias": {},
            "congruency_effects": {},
            "processing_style": {},
        }

        # Overall metrics
        if "accuracy" in df.columns:
            summary["overall_accuracy"] = df["accuracy"].mean()

        if "reaction_time_ms" in df.columns:
            summary["mean_reaction_time"] = df["reaction_time_ms"].mean()

        # Performance by target level (global vs. local bias)
        for target_level in df["target_level"].unique():
            level_data = df[df["target_level"] == target_level]
            if len(level_data) > 0:
                accuracy = (
                    level_data["accuracy"].mean()
                    if "accuracy" in level_data.columns
                    else 0
                )
                mean_rt = (
                    level_data["reaction_time_ms"].mean()
                    if "reaction_time_ms" in level_data.columns
                    else 0
                )

                summary["global_local_bias"][target_level] = {
                    "accuracy": accuracy,
                    "mean_rt": mean_rt,
                    "n_trials": len(level_data),
                }

        # Calculate global vs. local processing bias
        global_data = df[df["target_level"] == "global"]
        local_data = df[df["target_level"] == "local"]

        if len(global_data) > 0 and len(local_data) > 0:
            global_acc = (
                global_data["accuracy"].mean()
                if "accuracy" in global_data.columns
                else 0
            )
            local_acc = (
                local_data["accuracy"].mean() if "accuracy" in local_data.columns else 0
            )

            summary["processing_style"] = {
                "global_accuracy": global_acc,
                "local_accuracy": local_acc,
                "global_local_difference": global_acc - local_acc,
                "bias": (
                    "global"
                    if global_acc > local_acc
                    else "local" if local_acc > global_acc else "neutral"
                ),
            }

        # Performance by congruency
        for congruency in df["congruency"].unique():
            congruency_data = df[df["congruency"] == congruency]
            if len(congruency_data) > 0:
                accuracy = (
                    congruency_data["accuracy"].mean()
                    if "accuracy" in congruency_data.columns
                    else 0
                )
                mean_rt = (
                    congruency_data["reaction_time_ms"].mean()
                    if "reaction_time_ms" in congruency_data.columns
                    else 0
                )

                summary["congruency_effects"][congruency] = {
                    "accuracy": accuracy,
                    "mean_rt": mean_rt,
                    "n_trials": len(congruency_data),
                }

        # Calculate Navon effect (interference in incongruent trials)
        congruent_data = df[df["congruency"] == "congruent"]
        incongruent_data = df[df["congruency"] == "incongruent"]

        if len(congruent_data) > 0 and len(incongruent_data) > 0:
            congruent_acc = (
                congruent_data["accuracy"].mean()
                if "accuracy" in congruent_data.columns
                else 0
            )
            incongruent_acc = (
                incongruent_data["accuracy"].mean()
                if "accuracy" in incongruent_data.columns
                else 0
            )
            congruent_rt = (
                congruent_data["reaction_time_ms"].mean()
                if "reaction_time_ms" in congruent_data.columns
                else 0
            )
            incongruent_rt = (
                incongruent_data["reaction_time_ms"].mean()
                if "reaction_time_ms" in incongruent_data.columns
                else 0
            )

            summary["congruency_effects"]["navon_effect"] = {
                "accuracy_interference": congruent_acc - incongruent_acc,
                "rt_interference": incongruent_rt - congruent_rt,
                "congruent_accuracy": congruent_acc,
                "incongruent_accuracy": incongruent_acc,
                "congruent_rt": congruent_rt,
                "incongruent_rt": incongruent_rt,
            }

        return summary


def run_navon_task_experiment(**kwargs):
    """Run the Navon Task experiment."""
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
        if hasattr(NavonConfig, config_key):
            config_params[config_key] = value

    # Create config and experiment
    config = NavonConfig(**config_params)
    experiment = NavonTask(config)

    # Set up and run experiment
    experiment.setup()
    results = experiment.run_experiment()

    # Save results if output file specified
    if kwargs.get("output_file"):
        experiment.save_data(kwargs["output_file"])

    return experiment


if __name__ == "__main__":
    # Example usage
    config = NavonConfig(
        n_trials=120,
        n_participants=5,
        congruency_types=["congruent", "incongruent", "neutral"],
        target_levels=["global", "local"],
    )

    experiment = NavonTask(config)
    experiment.setup()
    results = experiment.run_experiment()

    print("Navon Task experiment completed!")
    print(f"Results shape: {results.shape}")

    # Print summary for first participant
    if experiment.participant_data:
        first_participant = list(experiment.participant_data.keys())[0]
        summary = experiment.participant_data[first_participant]["summary"]
        print(f"\nParticipant {first_participant} Summary:")
        print(f"Overall Accuracy: {summary.get('overall_accuracy', 0):.3f}")
        print(f"Mean Reaction Time: {summary.get('mean_reaction_time', 0):.1f} ms")
        print(
            f"Processing Bias: {summary.get('processing_style', {}).get('bias', 'neutral')}"
        )
        print(f"Global vs Local Accuracy: {summary.get('global_local_bias', {})}")
        print(
            f"Navon Effect: {summary.get('congruency_effects', {}).get('navon_effect', {})}"
        )
