"""
Simon Effect implementation.

The Simon effect is the finding that responses are typically faster and more accurate
when the stimulus occurs in the same relative location as the response, even if
the stimulus location is irrelevant to the task. This demonstrates spatial
stimulus-response compatibility effects.

APGI Integration:
- θₜ (threshold): Spatial response selection threshold
- π (precision): Spatial precision of stimulus-response mapping
- ε (prediction error): Spatial conflict prediction error
- β (inverse temperature): Consistency of spatial response mapping
"""

import random
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import time

from .. import TrialBasedTask, TrialBasedTaskConfig


@dataclass
class SimonConfig(TrialBasedTaskConfig):
    """Configuration for Simon experiment."""

    n_trials: int = 120
    stimulus_duration_ms: int = 200
    response_window_ms: int = 1500
    inter_trial_interval_ms: int = 1000

    # Stimulus parameters
    stimulus_colors: List[str] = None  # Colors for left/right responses
    response_keys: Dict[str, str] = None  # Mapping of colors to response keys
    positions: List[str] = None  # Left and right positions

    # Spatial parameters
    horizontal_distance: float = 5.0  # degrees of visual angle
    vertical_distance: float = 0.0  # degrees (0 for horizontal Simon)

    def __post_init__(self):
        if self.stimulus_colors is None:
            self.stimulus_colors = ["RED", "GREEN"]

        if self.response_keys is None:
            self.response_keys = {"RED": "left", "GREEN": "right"}

        if self.positions is None:
            self.positions = ["left", "right"]


class SimonStimulus:
    """Generate Simon task stimuli."""

    def __init__(self, config: SimonConfig):
        self.config = config
        self.positions = {
            "left": (
                -self.config.horizontal_distance / 2,
                self.config.vertical_distance,
            ),
            "right": (
                self.config.horizontal_distance / 2,
                self.config.vertical_distance,
            ),
        }

    def generate_stimulus(self) -> Dict[str, Any]:
        """Generate a single Simon stimulus."""
        # Select stimulus color (determines correct response)
        color = random.choice(self.config.stimulus_colors)
        correct_response = self.config.response_keys[color]

        # Select stimulus position (independent of color)
        position = random.choice(self.config.positions)
        position_coords = self.positions[position]

        # Determine congruence
        is_congruent = position == correct_response

        stimulus = {
            "color": color,
            "position": position,
            "position_coords": position_coords,
            "correct_response": correct_response,
            "is_congruent": is_congruent,
            "is_incongruent": not is_congruent,
        }

        return stimulus


class SimonTask(TrialBasedTask):
    """Simon task implementation."""

    def __init__(self, config: Optional[SimonConfig] = None):
        super().__init__(config)
        self.config = config or SimonConfig()
        self.stimulus_generator = SimonStimulus(self.config)
        self.spatial_effects = {}

    def setup(self, **kwargs):
        """Set up the Simon task."""
        super().setup(**kwargs)
        self.stimulus_generator = SimonStimulus(self.config)
        self.spatial_effects = {}

    def generate_trial_sequence(self) -> List[Dict[str, Any]]:
        """Generate balanced trial sequence."""
        trials = []

        # Create balanced design (congruent and incongruent trials)
        n_congruent = self.config.n_trials // 2
        n_incongruent = self.config.n_trials - n_congruent

        # Generate congruent trials
        for _ in range(n_congruent):
            trials.append({"trial_type": "congruent", "condition": "congruent"})

        # Generate incongruent trials
        for _ in range(n_incongruent):
            trials.append({"trial_type": "incongruent", "condition": "incongruent"})

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
            trial_config = {"trial_type": "congruent", "condition": "congruent"}

        # Generate stimulus until we get the desired congruence type
        max_attempts = 100
        stimulus = None

        for _ in range(max_attempts):
            stimulus = self.stimulus_generator.generate_stimulus()
            if trial_config["trial_type"] == "congruent" and stimulus["is_congruent"]:
                break
            elif (
                trial_config["trial_type"] == "incongruent"
                and stimulus["is_incongruent"]
            ):
                break

        if stimulus is None:
            # Fallback to any stimulus
            stimulus = self.stimulus_generator.generate_stimulus()

        base_params.update(
            {
                "stimulus": stimulus,
                "color": stimulus["color"],
                "position": stimulus["position"],
                "position_coords": stimulus["position_coords"],
                "correct_response": stimulus["correct_response"],
                "is_congruent": stimulus["is_congruent"],
                "is_incongruent": stimulus["is_incongruent"],
                "condition": trial_config["condition"],
                "stimulus_duration_ms": self.config.stimulus_duration_ms,
            }
        )

        return base_params

    def process_response(
        self, response: Any, correct_response: Any, trial_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Process Simon effect response."""
        # Response should be the side (left/right)
        if isinstance(response, str):
            response_side = response.lower()
        else:
            response_side = str(response).lower()

        correct_side = correct_response.lower()
        is_correct = response_side == correct_side

        # Get congruence from trial data or use default
        is_congruent = True  # Default
        if trial_data:
            is_congruent = trial_data.get("is_congruent", True)

        # Store spatial effects
        congruence = "congruent" if is_congruent else "incongruent"
        if congruence not in self.spatial_effects:
            self.spatial_effects[congruence] = {"rt": [], "accuracy": []}

        # Don't store RT here since it's not available yet
        self.spatial_effects[congruence]["accuracy"].append(1 if is_correct else 0)

        # Calculate confidence
        base_confidence = 0.8 if is_correct else 0.4
        if not is_congruent:
            base_confidence -= 0.1  # Lower confidence for incongruent trials

        return {
            "response": response_side,
            "accuracy": 1 if is_correct else 0,
            "reaction_time_ms": 0,  # Will be filled by simulate_response
            "confidence": base_confidence,
            "color": trial_data.get("color", "RED") if trial_data else "RED",
            "position": trial_data.get("position", "left") if trial_data else "left",
            "correct_response": correct_side,
            "is_congruent": is_congruent,
            "is_incongruent": not is_congruent,
            "condition": congruence,
        }

    def simulate_response(self, trial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate participant Simon task performance."""
        is_congruent = trial_data["is_congruent"]
        position = trial_data["position"]
        correct_response = trial_data["correct_response"]
        color = trial_data["color"]

        # Base reaction time and accuracy
        base_rt = 450  # Base RT in ms
        base_accuracy = 0.95

        # Simon interference effects
        if is_congruent:
            # Congruent trials: facilitation
            rt_effect = -30  # Faster RT
            accuracy_effect = 0.02
            interference_level = 0
        else:
            # Incongruent trials: interference
            rt_effect = 80  # Slower RT
            accuracy_effect = -0.08
            interference_level = 1

        # Calculate reaction time
        rt = base_rt + rt_effect

        # Add individual variation and noise
        rt = max(250, np.random.normal(rt, 100))

        # Calculate accuracy
        accuracy = base_accuracy + accuracy_effect
        accuracy = np.clip(accuracy, 0.7, 1.0)

        # Determine response
        if random.random() < accuracy:
            response = correct_response
        else:
            # Make error based on Simon effect
            if not is_congruent and random.random() < 0.6:
                # Most errors on incongruent trials are spatial responses
                response = position  # Respond to position instead of color
            else:
                # Random error
                other_response = "right" if correct_response == "left" else "left"
                response = other_response

        # Calculate confidence
        confidence = 0.8 if response == correct_response else 0.5
        if not is_congruent:
            confidence -= 0.1  # Lower confidence on incongruent trials

        return {
            "response": response,
            "reaction_time_ms": int(rt),
            "confidence": confidence,
            "timestamp": time.time(),
        }

    def compute_participant_summary(
        self, trials: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compute comprehensive summary for Simon task."""
        base_summary = super().compute_participant_summary(trials)

        if not trials:
            return base_summary

        df = pd.DataFrame(trials)

        # Simon specific metrics
        summary = {
            **base_summary,
            "overall_accuracy": 0,
            "mean_reaction_time": 0,
            "simon_effect": {},
            "condition_performance": {},
            "spatial_compatibility": {},
        }

        # Overall metrics
        if "accuracy" in df.columns:
            summary["overall_accuracy"] = df["accuracy"].mean()

        if "reaction_time_ms" in df.columns:
            summary["mean_reaction_time"] = df["reaction_time_ms"].mean()

        # Performance by condition
        for condition in ["congruent", "incongruent"]:
            condition_data = df[df["condition"] == condition]
            if len(condition_data) > 0:
                accuracy = (
                    condition_data["accuracy"].mean()
                    if "accuracy" in condition_data.columns
                    else 0
                )
                mean_rt = (
                    condition_data["reaction_time_ms"].mean()
                    if "reaction_time_ms" in condition_data.columns
                    else 0
                )

                summary["condition_performance"][condition] = {
                    "accuracy": accuracy,
                    "mean_rt": mean_rt,
                    "n_trials": len(condition_data),
                }

        # Calculate Simon effect
        congruent_data = df[df["is_congruent"] == True]
        incongruent_data = df[df["is_congruent"] == False]

        if len(congruent_data) > 0 and len(incongruent_data) > 0:
            # RT Simon effect (incongruent - congruent)
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

            summary["simon_effect"]["rt_effect_ms"] = incongruent_rt - congruent_rt

            # Accuracy Simon effect
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

            summary["simon_effect"]["accuracy_effect"] = congruent_acc - incongruent_acc

            # Effect sizes
            summary["simon_effect"]["rt_effect_size"] = (
                (incongruent_rt - congruent_rt) / congruent_rt
                if congruent_rt > 0
                else 0
            )
            summary["simon_effect"]["accuracy_effect_size"] = (
                congruent_acc - incongruent_acc
            )

        # Spatial compatibility analysis
        for position in ["left", "right"]:
            position_data = df[df["position"] == position]
            if len(position_data) > 0:
                accuracy = (
                    position_data["accuracy"].mean()
                    if "accuracy" in position_data.columns
                    else 0
                )
                mean_rt = (
                    position_data["reaction_time_ms"].mean()
                    if "reaction_time_ms" in position_data.columns
                    else 0
                )

                summary["spatial_compatibility"][f"position_{position}"] = {
                    "accuracy": accuracy,
                    "mean_rt": mean_rt,
                    "n_trials": len(position_data),
                }

        return summary


def run_simon_effect_experiment(**kwargs):
    """Run the Simon Effect experiment."""
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
        if hasattr(SimonConfig, config_key):
            config_params[config_key] = value

    # Create config and experiment
    config = SimonConfig(**config_params)
    experiment = SimonTask(config)

    # Set up and run experiment
    experiment.setup()
    results = experiment.run_experiment()

    # Save results if output file specified
    if kwargs.get("output_file"):
        experiment.save_data(kwargs["output_file"])

    return experiment


if __name__ == "__main__":
    # Example usage
    config = SimonConfig(
        n_trials=100, n_participants=5, stimulus_colors=["RED", "GREEN"]
    )

    experiment = SimonTask(config)
    experiment.setup()
    results = experiment.run_experiment()

    print("Simon Effect experiment completed!")
    print(f"Results shape: {results.shape}")

    # Print summary for first participant
    if experiment.participant_data:
        first_participant = list(experiment.participant_data.keys())[0]
        summary = experiment.participant_data[first_participant]["summary"]
        print(f"\nParticipant {first_participant} Summary:")
        print(f"Overall Accuracy: {summary.get('overall_accuracy', 0):.3f}")
        print(f"Mean Reaction Time: {summary.get('mean_reaction_time', 0):.1f} ms")
        print(
            f"Simon RT Effect: {summary.get('simon_effect', {}).get('rt_effect_ms', 0):.1f} ms"
        )
        print(f"Condition Performance: {summary.get('condition_performance', {})}")
