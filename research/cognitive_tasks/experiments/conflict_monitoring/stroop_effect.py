"""
Stroop Effect implementation.

The Stroop effect demonstrates interference in task performance when participants
must name the ink color of a printed word while ignoring the word's meaning.
Response times are typically slower and error rates higher when the word meaning
and ink color are incongruent.

APGI Integration:
- θₜ (threshold): Cognitive control threshold for conflict resolution
- π (precision): Attentional precision for relevant vs. irrelevant dimensions
- ε (prediction error): Conflict-induced prediction error
- β (inverse temperature): Consistency of cognitive control
"""

import random
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import time

from .. import TrialBasedTask, TrialBasedTaskConfig


@dataclass
class StroopConfig(TrialBasedTaskConfig):
    """Configuration for Stroop experiment."""

    n_trials: int = 120
    stimulus_duration_ms: int = 2000
    response_window_ms: int = 3000
    inter_trial_interval_ms: int = 1000

    # Stimulus parameters
    colors: List[str] = None  # Color names
    color_codes: Dict[str, str] = None  # RGB values for colors
    font_size: int = 48
    stimulus_types: List[str] = None  # congruent, incongruent, neutral

    # Proportions of trial types
    congruent_ratio: float = 0.4
    incongruent_ratio: float = 0.4
    neutral_ratio: float = 0.2

    def __post_init__(self):
        if self.colors is None:
            self.colors = ["RED", "BLUE", "GREEN", "YELLOW"]

        if self.color_codes is None:
            self.color_codes = {
                "RED": "#FF0000",
                "BLUE": "#0000FF",
                "GREEN": "#00FF00",
                "YELLOW": "#FFFF00",
            }

        if self.stimulus_types is None:
            self.stimulus_types = ["congruent", "incongruent", "neutral"]


class StroopStimulus:
    """Generate Stroop stimuli."""

    def __init__(self, config: StroopConfig):
        self.config = config
        self.neutral_words = ["TABLE", "CHAIR", "PENCIL", "PAPER"]

    def generate_stimulus(self, stimulus_type: str) -> Dict[str, Any]:
        """Generate a single Stroop stimulus."""
        # Select ink color
        ink_color = random.choice(self.config.colors)

        if stimulus_type == "congruent":
            # Word meaning matches ink color
            word_text = ink_color
        elif stimulus_type == "incongruent":
            # Word meaning differs from ink color
            other_colors = [c for c in self.config.colors if c != ink_color]
            word_text = random.choice(other_colors)
        else:  # neutral
            # Neutral word with colored ink
            word_text = random.choice(self.neutral_words)

        stimulus = {
            "word_text": word_text,
            "ink_color": ink_color,
            "stimulus_type": stimulus_type,
            "correct_response": ink_color,
            "color_code": self.config.color_codes[ink_color],
            "is_congruent": stimulus_type == "congruent",
            "is_incongruent": stimulus_type == "incongruent",
            "is_neutral": stimulus_type == "neutral",
        }

        return stimulus


class StroopTask(TrialBasedTask):
    """Stroop task implementation."""

    def __init__(self, config: Optional[StroopConfig] = None):
        super().__init__(config)
        self.config = config or StroopConfig()
        self.stimulus_generator = StroopStimulus(self.config)
        self.conflict_effects = {}

    def setup(self, **kwargs):
        """Set up the Stroop task."""
        super().setup(**kwargs)
        self.stimulus_generator = StroopStimulus(self.config)
        self.conflict_effects = {}

    def generate_trial_sequence(self) -> List[Dict[str, Any]]:
        """Generate balanced trial sequence."""
        trials = []

        # Calculate number of trials for each condition
        n_congruent = int(self.config.n_trials * self.config.congruent_ratio)
        n_incongruent = int(self.config.n_trials * self.config.incongruent_ratio)
        n_neutral = self.config.n_trials - n_congruent - n_incongruent

        # Generate trials
        for _ in range(n_congruent):
            trials.append({"stimulus_type": "congruent", "condition": "congruent"})

        for _ in range(n_incongruent):
            trials.append({"stimulus_type": "incongruent", "condition": "incongruent"})

        for _ in range(n_neutral):
            trials.append({"stimulus_type": "neutral", "condition": "neutral"})

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
            trial_config = {"stimulus_type": "congruent", "condition": "congruent"}

        # Generate stimulus
        stimulus = self.stimulus_generator.generate_stimulus(
            trial_config["stimulus_type"]
        )

        base_params.update(
            {
                "stimulus": stimulus,
                "stimulus_type": trial_config["stimulus_type"],
                "condition": trial_config["condition"],
                "word_text": stimulus["word_text"],
                "ink_color": stimulus["ink_color"],
                "correct_response": stimulus["correct_response"],
                "stimulus_duration_ms": self.config.stimulus_duration_ms,
            }
        )

        return base_params

    def process_response(
        self, response: Any, correct_response: Any, trial_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Process Stroop response."""
        # Response should be the ink color
        if isinstance(response, str):
            response_color = response.upper()
        else:
            response_color = str(response).upper()

        correct_color = correct_response.upper()
        is_correct = response_color == correct_color

        # Get stimulus type from trial data or use default
        stimulus_type = "congruent"  # Default
        if trial_data:
            stimulus_type = trial_data.get("stimulus_type", "congruent")

        # Store conflict effects (simplified for now)
        if stimulus_type not in self.conflict_effects:
            self.conflict_effects[stimulus_type] = {"rt": [], "accuracy": []}

        # Don't store RT here since it's not available yet
        self.conflict_effects[stimulus_type]["accuracy"].append(1 if is_correct else 0)

        # Calculate confidence based on accuracy and stimulus type
        base_confidence = 0.8 if is_correct else 0.4
        if stimulus_type == "incongruent":
            base_confidence -= 0.1  # Lower confidence for incongruent trials
        elif stimulus_type == "congruent":
            base_confidence += 0.1  # Higher confidence for congruent trials

        return {
            "response": response_color,
            "accuracy": 1 if is_correct else 0,
            "reaction_time_ms": 0,  # Will be filled by simulate_response
            "confidence": base_confidence,
            "stimulus_type": stimulus_type,
            "word_text": trial_data.get("word_text", "RED") if trial_data else "RED",
            "ink_color": correct_color,
            "is_congruent": stimulus_type == "congruent",
            "is_incongruent": stimulus_type == "incongruent",
            "is_neutral": stimulus_type == "neutral",
        }

    def simulate_response(self, trial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate participant Stroop performance."""
        stimulus_type = trial_data["stimulus_type"]
        ink_color = trial_data["ink_color"]
        word_text = trial_data["word_text"]

        # Base reaction time and accuracy
        base_rt = 650  # Base RT in ms
        base_accuracy = 0.95

        # Stroop interference effects
        if stimulus_type == "congruent":
            # Congruent trials: facilitation
            rt_effect = -50  # Faster RT
            accuracy_effect = 0.02
            interference_level = 0
        elif stimulus_type == "incongruent":
            # Incongruent trials: interference
            rt_effect = 150  # Slower RT
            accuracy_effect = -0.15
            interference_level = 1
        else:  # neutral
            # Neutral trials: baseline
            rt_effect = 0
            accuracy_effect = 0
            interference_level = 0.5

        # Calculate reaction time
        rt = base_rt + rt_effect

        # Add individual variation and noise
        rt = max(300, np.random.normal(rt, 120))

        # Calculate accuracy
        accuracy = base_accuracy + accuracy_effect
        accuracy = np.clip(accuracy, 0.6, 1.0)

        # Determine response
        if random.random() < accuracy:
            response = ink_color
        else:
            # Make error based on stimulus type
            if stimulus_type == "incongruent" and random.random() < 0.7:
                # Most errors on incongruent trials are reading the word
                response = word_text
            else:
                # Random color error
                other_colors = [c for c in self.config.colors if c != ink_color]
                response = random.choice(other_colors)

        # Calculate confidence
        confidence = 0.8 if response == ink_color else 0.5
        if stimulus_type == "incongruent":
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
        """Compute comprehensive summary for Stroop task."""
        base_summary = super().compute_participant_summary(trials)

        if not trials:
            return base_summary

        df = pd.DataFrame(trials)

        # Stroop specific metrics
        summary = {
            **base_summary,
            "overall_accuracy": 0,
            "mean_reaction_time": 0,
            "stroop_interference": {},
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
            condition_data = df[df["stimulus_type"] == condition]
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

        # Calculate Stroop interference effects
        congruent_data = df[df["stimulus_type"] == "congruent"]
        incongruent_data = df[df["stimulus_type"] == "incongruent"]
        neutral_data = df[df["stimulus_type"] == "neutral"]

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

            summary["stroop_interference"]["rt_interference_ms"] = (
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

            summary["stroop_interference"]["accuracy_interference"] = (
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

            summary["stroop_interference"]["rt_interference_vs_neutral_ms"] = (
                incongruent_rt - neutral_rt
            )
            summary["stroop_interference"]["accuracy_interference_vs_neutral"] = (
                neutral_acc - incongruent_acc
            )

        # Conflict adaptation (performance improvement after incongruent trials)
        if "trial_number" in df.columns and "stimulus_type" in df.columns:
            df_sorted = df.sort_values("trial_number")

            post_incongruent_trials = []
            control_trials = []

            for i, trial in df_sorted.iterrows():
                if i > 0:  # Not first trial
                    prev_trial = df_sorted.iloc[i - 1]
                    if prev_trial["stimulus_type"] == "incongruent":
                        post_incongruent_trials.append(trial)
                    elif prev_trial["stimulus_type"] in ["congruent", "neutral"]:
                        control_trials.append(trial)

            if post_incongruent_trials and control_trials:
                post_df = pd.DataFrame(post_incongruent_trials)
                control_df = pd.DataFrame(control_trials)

                # Focus on incongruent trials following different contexts
                post_incongruent_incongruent = post_df[
                    post_df["stimulus_type"] == "incongruent"
                ]
                control_incongruent = control_df[
                    control_df["stimulus_type"] == "incongruent"
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


def run_stroop_effect_experiment(**kwargs):
    """Run the Stroop Effect experiment."""
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
        if hasattr(StroopConfig, config_key):
            config_params[config_key] = value

    # Create config and experiment
    config = StroopConfig(**config_params)
    experiment = StroopTask(config)

    # Set up and run experiment
    experiment.setup()
    results = experiment.run_experiment()

    # Save results if output file specified
    if kwargs.get("output_file"):
        experiment.save_data(kwargs["output_file"])

    return experiment


if __name__ == "__main__":
    # Example usage
    config = StroopConfig(
        n_trials=120,
        n_participants=5,
        congruent_ratio=0.4,
        incongruent_ratio=0.4,
        neutral_ratio=0.2,
    )

    experiment = StroopTask(config)
    experiment.setup()
    results = experiment.run_experiment()

    print("Stroop Effect experiment completed!")
    print(f"Results shape: {results.shape}")

    # Print summary for first participant
    if experiment.participant_data:
        first_participant = list(experiment.participant_data.keys())[0]
        summary = experiment.participant_data[first_participant]["summary"]
        print(f"\nParticipant {first_participant} Summary:")
        print(f"Overall Accuracy: {summary.get('overall_accuracy', 0):.3f}")
        print(f"Mean Reaction Time: {summary.get('mean_reaction_time', 0):.1f} ms")
        print(
            f"RT Interference: {summary.get('stroop_interference', {}).get('rt_interference_ms', 0):.1f} ms"
        )
        print(f"Condition Performance: {summary.get('condition_performance', {})}")
