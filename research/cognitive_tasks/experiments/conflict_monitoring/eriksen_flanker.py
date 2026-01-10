"""
Eriksen Flanker Task implementation.

The Eriksen flanker task measures attention and cognitive control. Participants respond
to a central target stimulus while ignoring surrounding flanker stimuli. Response times
are slower and error rates higher when flankers are incompatible with the target.

APGI Integration:
- θₜ (threshold): Attentional filtering threshold
- π (precision): Spatial precision of attentional focus
- ε (prediction error): Flanker conflict prediction error
- β (inverse temperature): Consistency of response selection
"""

import random
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import time

from .. import TrialBasedTask, TrialBasedTaskConfig


@dataclass
class EriksenFlankerConfig(TrialBasedTaskConfig):
    """Configuration for Eriksen Flanker experiment."""

    n_trials: int = 120
    stimulus_duration_ms: int = 200
    response_window_ms: int = 1500
    inter_trial_interval_ms: int = 1000

    # Stimulus parameters
    target_stimuli: List[str] = None  # Central target stimuli
    flanker_stimuli: List[str] = None  # Flanker stimuli
    n_flankers: int = 2  # Number of flankers on each side

    # Flanker compatibility conditions
    compatibility_types: List[str] = None  # congruent, incongruent, neutral

    # Proportions of trial types
    congruent_ratio: float = 0.4
    incongruent_ratio: float = 0.4
    neutral_ratio: float = 0.2

    def __post_init__(self):
        if self.target_stimuli is None:
            self.target_stimuli = ["<", ">"]  # Left and right arrows

        if self.flanker_stimuli is None:
            self.flanker_stimuli = ["<", ">", "="]  # Left, right, neutral

        if self.compatibility_types is None:
            self.compatibility_types = ["congruent", "incongruent", "neutral"]


class FlankerStimulus:
    """Generate Eriksen flanker stimuli."""

    def __init__(self, config: EriksenFlankerConfig):
        self.config = config
        self.response_mapping = {"<": "left", ">": "right", "=": "neutral"}

    def generate_stimulus(self, compatibility_type: str) -> Dict[str, Any]:
        """Generate a single flanker stimulus."""
        # Select target stimulus
        target = random.choice(["<", ">"])
        correct_response = self.response_mapping[target]

        # Generate flankers based on compatibility type
        if compatibility_type == "congruent":
            # Flankers point same direction as target
            flankers = [target] * (self.config.n_flankers * 2)
        elif compatibility_type == "incongruent":
            # Flankers point opposite direction to target
            opposite = ">" if target == "<" else "<"
            flankers = [opposite] * (self.config.n_flankers * 2)
        else:  # neutral
            # Flankers are neutral symbols
            flankers = ["="] * (self.config.n_flankers * 2)

        # Create stimulus display
        left_flankers = "".join(flankers[: self.config.n_flankers])
        right_flankers = "".join(flankers[self.config.n_flankers :])
        stimulus_display = f"{left_flankers}{target}{right_flankers}"

        stimulus = {
            "target": target,
            "flankers": flankers,
            "stimulus_display": stimulus_display,
            "correct_response": correct_response,
            "compatibility_type": compatibility_type,
            "is_congruent": compatibility_type == "congruent",
            "is_incongruent": compatibility_type == "incongruent",
            "is_neutral": compatibility_type == "neutral",
        }

        return stimulus


class EriksenFlankerTask(TrialBasedTask):
    """Eriksen Flanker task implementation."""

    def __init__(self, config: Optional[EriksenFlankerConfig] = None):
        super().__init__(config)
        self.config = config or EriksenFlankerConfig()
        self.stimulus_generator = FlankerStimulus(self.config)
        self.flanker_effects = {}

    def setup(self, **kwargs):
        """Set up the Eriksen Flanker task."""
        super().setup(**kwargs)
        self.stimulus_generator = FlankerStimulus(self.config)
        self.flanker_effects = {}

    def generate_trial_sequence(self) -> List[Dict[str, Any]]:
        """Generate balanced trial sequence."""
        trials = []

        # Calculate number of trials for each condition
        n_congruent = int(self.config.n_trials * self.config.congruent_ratio)
        n_incongruent = int(self.config.n_trials * self.config.incongruent_ratio)
        n_neutral = self.config.n_trials - n_congruent - n_incongruent

        # Generate trials
        for _ in range(n_congruent):
            trials.append({"compatibility_type": "congruent", "condition": "congruent"})

        for _ in range(n_incongruent):
            trials.append(
                {"compatibility_type": "incongruent", "condition": "incongruent"}
            )

        for _ in range(n_neutral):
            trials.append({"compatibility_type": "neutral", "condition": "neutral"})

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
            trial_config = {"compatibility_type": "congruent", "condition": "congruent"}

        # Generate stimulus
        stimulus = self.stimulus_generator.generate_stimulus(
            trial_config["compatibility_type"]
        )

        base_params.update(
            {
                "stimulus": stimulus,
                "target": stimulus["target"],
                "flankers": stimulus["flankers"],
                "stimulus_display": stimulus["stimulus_display"],
                "correct_response": stimulus["correct_response"],
                "compatibility_type": trial_config["compatibility_type"],
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
        """Process Eriksen Flanker response."""
        # Response should be the direction (left/right)
        if isinstance(response, str):
            response_side = response.lower()
        else:
            response_side = str(response).lower()

        correct_side = correct_response.lower()
        is_correct = response_side == correct_side

        # Get compatibility type from trial data or use default
        compatibility_type = "congruent"  # Default
        if trial_data:
            compatibility_type = trial_data.get("compatibility_type", "congruent")

        # Store flanker effects
        if compatibility_type not in self.flanker_effects:
            self.flanker_effects[compatibility_type] = {"rt": [], "accuracy": []}

        # Don't store RT here since it's not available yet
        self.flanker_effects[compatibility_type]["accuracy"].append(
            1 if is_correct else 0
        )

        # Calculate confidence based on accuracy and compatibility
        base_confidence = 0.8 if is_correct else 0.4
        if compatibility_type == "incongruent":
            base_confidence -= 0.1  # Lower confidence for incongruent trials

        return {
            "response": response_side,
            "accuracy": 1 if is_correct else 0,
            "reaction_time_ms": 0,  # Will be filled by simulate_response
            "confidence": base_confidence,
            "target": trial_data.get("target", "←") if trial_data else "←",
            "stimulus_display": (
                trial_data.get("stimulus_display", "←←←←←") if trial_data else "←←←←←"
            ),
            "correct_response": correct_side,
            "compatibility_type": compatibility_type,
            "is_congruent": compatibility_type == "congruent",
            "is_incongruent": compatibility_type == "incongruent",
            "is_neutral": compatibility_type == "neutral",
        }

    def simulate_response(self, trial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate participant Eriksen Flanker performance."""
        compatibility_type = trial_data["compatibility_type"]
        target = trial_data["target"]
        correct_response = trial_data["correct_response"]
        flankers = trial_data["flankers"]

        # Base reaction time and accuracy
        base_rt = 500  # Base RT in ms
        base_accuracy = 0.95

        # Flanker interference effects
        if compatibility_type == "congruent":
            # Congruent trials: facilitation
            rt_effect = -40  # Faster RT
            accuracy_effect = 0.02
            interference_level = 0
        elif compatibility_type == "incongruent":
            # Incongruent trials: interference
            rt_effect = 120  # Slower RT
            accuracy_effect = -0.12
            interference_level = 1
        else:  # neutral
            # Neutral trials: baseline
            rt_effect = 0
            accuracy_effect = 0
            interference_level = 0.5

        # Calculate reaction time
        rt = base_rt + rt_effect

        # Add individual variation and noise
        rt = max(300, np.random.normal(rt, 110))

        # Calculate accuracy
        accuracy = base_accuracy + accuracy_effect
        accuracy = np.clip(accuracy, 0.6, 1.0)

        # Determine response
        if random.random() < accuracy:
            response = correct_response
        else:
            # Make error based on flanker influence
            if compatibility_type == "incongruent" and random.random() < 0.7:
                # Most errors on incongruent trials are influenced by flankers
                flanker_direction = self.stimulus_generator.response_mapping[
                    flankers[0]
                ]
                if flanker_direction in ["left", "right"]:
                    response = flanker_direction
                else:
                    # Random error if neutral flankers
                    response = "right" if correct_response == "left" else "left"
            else:
                # Random error
                response = "right" if correct_response == "left" else "left"

        # Calculate confidence
        confidence = 0.8 if response == correct_response else 0.5
        if compatibility_type == "incongruent":
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
        """Compute comprehensive summary for Eriksen Flanker task."""
        base_summary = super().compute_participant_summary(trials)

        if not trials:
            return base_summary

        df = pd.DataFrame(trials)

        # Flanker specific metrics
        summary = {
            **base_summary,
            "overall_accuracy": 0,
            "mean_reaction_time": 0,
            "flanker_interference": {},
            "condition_performance": {},
            "conflict_adaptation": {},
        }

        # Overall metrics
        if "accuracy" in df.columns:
            summary["overall_accuracy"] = df["accuracy"].mean()

        if "reaction_time_ms" in df.columns:
            summary["mean_reaction_time"] = df["reaction_time_ms"].mean()

        # Performance by condition
        for condition in ["congruent", "incongruent", "neutral"]:
            condition_data = df[df["compatibility_type"] == condition]
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

        # Calculate Flanker interference effects
        congruent_data = df[df["is_congruent"] == True]
        incongruent_data = df[df["is_incongruent"] == True]
        neutral_data = df[df["is_neutral"] == True]

        if len(congruent_data) > 0 and len(incongruent_data) > 0:
            # RT interference (incongruent - congruent)
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

            summary["flanker_interference"]["rt_interference_ms"] = (
                incongruent_rt - congruent_rt
            )

            # Accuracy interference
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

            summary["flanker_interference"]["accuracy_interference"] = (
                congruent_acc - incongruent_acc
            )

        if len(neutral_data) > 0 and len(incongruent_data) > 0:
            # Relative to neutral baseline
            neutral_rt = (
                neutral_data["reaction_time_ms"].mean()
                if "reaction_time_ms" in neutral_data.columns
                else 0
            )
            neutral_acc = (
                neutral_data["accuracy"].mean()
                if "accuracy" in neutral_data.columns
                else 0
            )

            incongruent_rt = (
                incongruent_data["reaction_time_ms"].mean()
                if "reaction_time_ms" in incongruent_data.columns
                else 0
            )
            incongruent_acc = (
                incongruent_data["accuracy"].mean()
                if "accuracy" in incongruent_data.columns
                else 0
            )

            summary["flanker_interference"]["rt_interference_vs_neutral_ms"] = (
                incongruent_rt - neutral_rt
            )
            summary["flanker_interference"]["accuracy_interference_vs_neutral"] = (
                neutral_acc - incongruent_acc
            )

        # Conflict adaptation (performance improvement after incongruent trials)
        if "trial_number" in df.columns and "compatibility_type" in df.columns:
            df_sorted = df.sort_values("trial_number")

            post_incongruent_trials = []
            control_trials = []

            for i, trial in df_sorted.iterrows():
                if i > 0:  # Not first trial
                    prev_trial = df_sorted.iloc[i - 1]
                    if prev_trial["compatibility_type"] == "incongruent":
                        post_incongruent_trials.append(trial)
                    elif prev_trial["compatibility_type"] in ["congruent", "neutral"]:
                        control_trials.append(trial)

            if post_incongruent_trials and control_trials:
                post_df = pd.DataFrame(post_incongruent_trials)
                control_df = pd.DataFrame(control_trials)

                # Focus on incongruent trials following different contexts
                post_incongruent_incongruent = post_df[
                    post_df["compatibility_type"] == "incongruent"
                ]
                control_incongruent = control_df[
                    control_df["compatibility_type"] == "incongruent"
                ]

                if (
                    len(post_incongruent_incongruent) > 0
                    and len(control_incongruent) > 0
                ):
                    post_rt = (
                        post_incongruent_incongruent["reaction_time_ms"].mean()
                        if "reaction_time_ms" in post_incongruent_incongruent.columns
                        else 0
                    )
                    control_rt = (
                        control_incongruent["reaction_time_ms"].mean()
                        if "reaction_time_ms" in control_incongruent.columns
                        else 0
                    )

                    summary["conflict_adaptation"] = {
                        "rt_adaptation_ms": control_rt
                        - post_rt,  # Positive = adaptation (faster after conflict)
                        "post_conflict_incongruent_rt": post_rt,
                        "control_incongruent_rt": control_rt,
                        "n_post_conflict_trials": len(post_incongruent_incongruent),
                        "n_control_trials": len(control_incongruent),
                    }

        return summary


def run_eriksen_flanker_experiment(**kwargs):
    """Run the Eriksen Flanker experiment."""
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
        if hasattr(EriksenFlankerConfig, config_key):
            config_params[config_key] = value

    # Create config and experiment
    config = EriksenFlankerConfig(**config_params)
    experiment = EriksenFlankerTask(config)

    # Set up and run experiment
    experiment.setup()
    results = experiment.run_experiment()

    # Save results if output file specified
    if kwargs.get("output_file"):
        experiment.save_data(kwargs["output_file"])

    return experiment


if __name__ == "__main__":
    # Example usage
    config = EriksenFlankerConfig(
        n_trials=120,
        n_participants=5,
        congruent_ratio=0.4,
        incongruent_ratio=0.4,
        neutral_ratio=0.2,
    )

    experiment = EriksenFlankerTask(config)
    experiment.setup()
    results = experiment.run_experiment()

    print("Eriksen Flanker experiment completed!")
    print(f"Results shape: {results.shape}")

    # Print summary for first participant
    if experiment.participant_data:
        first_participant = list(experiment.participant_data.keys())[0]
        summary = experiment.participant_data[first_participant]["summary"]
        print(f"\nParticipant {first_participant} Summary:")
        print(f"Overall Accuracy: {summary.get('overall_accuracy', 0):.3f}")
        print(f"Mean Reaction Time: {summary.get('mean_reaction_time', 0):.1f} ms")
        print(
            f"Flanker RT Interference: {summary.get('flanker_interference', {}).get('rt_interference_ms', 0):.1f} ms"
        )
        print(f"Condition Performance: {summary.get('condition_performance', {})}")
