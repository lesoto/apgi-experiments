"""
Attentional Blink implementation.

The attentional blink is a phenomenon where the detection of a second target stimulus
is impaired for a short period (200-500ms) after the first target has been detected.
This reveals temporal limitations in attentional processing.

APGI Integration:
- θₜ (threshold): Attentional resource allocation threshold
- π (precision): Temporal precision of attentional window
- ε (prediction error): Unexpected target timing
- β (inverse temperature): Determinism of target detection
"""

import random
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import time

from .. import TrialBasedTask, TrialBasedTaskConfig


@dataclass
class AttentionalBlinkConfig(TrialBasedTaskConfig):
    """Configuration for Attentional Blink experiment."""

    n_trials: int = 200
    stimulus_duration_ms: int = 50
    inter_stimulus_interval_ms: int = 100
    mask_duration_ms: int = 100
    response_window_ms: int = 2000

    # Target parameters
    target1_positions: List[int] = None  # Possible positions for T1
    target2_lags: List[int] = None  # Lags between T1 and T2 (in ISIs)
    n_distractors: int = 15  # Number of distractor items

    # Stimulus parameters
    stimulus_types: List[str] = None  # Types of stimuli (letters, digits, symbols)
    target1_type: str = "letter"  # What type of stimulus is T1
    target2_type: str = "digit"  # What type of stimulus is T2
    distractor_type: str = "symbol"  # What type of stimulus are distractors

    def __post_init__(self):
        if self.target1_positions is None:
            self.target1_positions = [4, 5, 6]  # T1 appears in positions 4-6

        if self.target2_lags is None:
            # Standard lags: 2, 3, 5, 7, 9 (representing attentional blink period)
            self.target2_lags = [2, 3, 5, 7, 9]

        if self.stimulus_types is None:
            self.stimulus_types = ["letter", "digit", "symbol"]


class StimulusStream:
    """Generate rapid serial visual presentation (RSVP) streams."""

    def __init__(self, config: AttentionalBlinkConfig):
        self.config = config
        self.stimulus_pool = self._create_stimulus_pool()

    def _create_stimulus_pool(self) -> Dict[str, List[str]]:
        """Create pools of different stimulus types."""
        return {
            "letter": list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
            "digit": list("0123456789"),
            "symbol": ["@", "#", "$", "%", "&", "*", "+", "=", "?", "!"],
        }

    def generate_stream(self, t1_position: int, t2_lag: int) -> List[Dict[str, Any]]:
        """Generate an RSVP stream with two targets."""
        stream = []
        stream_length = self.config.n_distractors + 2  # +2 for targets

        # Calculate T2 position
        t2_position = t1_position + t2_lag

        # Generate stream
        for position in range(stream_length):
            stimulus_info = {
                "position": position,
                "is_target1": position == t1_position,
                "is_target2": position == t2_position,
                "is_target": position in [t1_position, t2_position],
            }

            if position == t1_position:
                # Target 1
                stimulus = random.choice(self.stimulus_pool[self.config.target1_type])
                stimulus_info.update(
                    {
                        "stimulus": stimulus,
                        "type": self.config.target1_type,
                        "correct_response": stimulus,  # Report the stimulus
                    }
                )
            elif position == t2_position:
                # Target 2
                stimulus = random.choice(self.stimulus_pool[self.config.target2_type])
                stimulus_info.update(
                    {
                        "stimulus": stimulus,
                        "type": self.config.target2_type,
                        "correct_response": stimulus,  # Report the stimulus
                    }
                )
            else:
                # Distractor
                stimulus = random.choice(
                    self.stimulus_pool[self.config.distractor_type]
                )
                stimulus_info.update(
                    {
                        "stimulus": stimulus,
                        "type": self.config.distractor_type,
                        "correct_response": None,
                    }
                )

            stream.append(stimulus_info)

        return stream


class AttentionalBlinkTask(TrialBasedTask):
    """Attentional Blink task implementation."""

    def __init__(self, config: Optional[AttentionalBlinkConfig] = None):
        super().__init__(config)
        self.config = config or AttentionalBlinkConfig()
        self.stimulus_generator = StimulusStream(self.config)
        self.performance_by_lag = {lag: [] for lag in self.config.target2_lags}

    def setup(self, **kwargs):
        """Set up the attentional blink task."""
        super().setup(**kwargs)
        self.stimulus_generator = StimulusStream(self.config)
        self.performance_by_lag = {lag: [] for lag in self.config.target2_lags}

    def generate_trial_sequence(self) -> List[Dict[str, Any]]:
        """Generate trial sequence with balanced conditions."""
        trials = []

        # Create balanced design across all lags
        for lag in self.config.target2_lags:
            for _ in range(self.config.n_trials // len(self.config.target2_lags)):
                t1_position = random.choice(self.config.target1_positions)

                trials.append(
                    {
                        "t1_position": t1_position,
                        "t2_lag": lag,
                        "condition": f"lag_{lag}",
                    }
                )

        # Randomize trial order
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
            trial_config = {"t1_position": 5, "t2_lag": 3, "condition": "lag_3"}

        # Generate stimulus stream
        stream = self.stimulus_generator.generate_stream(
            trial_config["t1_position"], trial_config["t2_lag"]
        )

        base_params.update(
            {
                "stimulus_stream": stream,
                "t1_position": trial_config["t1_position"],
                "t2_position": trial_config["t1_position"] + trial_config["t2_lag"],
                "t2_lag": trial_config["t2_lag"],
                "condition": trial_config["condition"],
                "stream_length": len(stream),
                "stimulus_duration_ms": self.config.stimulus_duration_ms,
                "isi_ms": self.config.inter_stimulus_interval_ms,
            }
        )

        return base_params

    def process_response(
        self, response: Any, correct_response: Any, trial_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Process responses for both targets."""
        # Get actual correct responses from trial data if available
        if trial_data and "stimulus_stream" in trial_data:
            stream = trial_data["stimulus_stream"]
            t1_correct = None
            t2_correct = None

            for item in stream:
                if item.get("is_target1"):
                    t1_correct = item.get("stimulus")
                elif item.get("is_target2"):
                    t2_correct = item.get("stimulus")
        else:
            # Default correct responses for fallback
            t1_correct = "A"  # Default target 1
            t2_correct = "5"  # Default target 2

        # Response should be a tuple: (t1_response, t2_response)
        if isinstance(response, tuple) and len(response) == 2:
            t1_response, t2_response = response
        elif isinstance(response, dict):
            t1_response = response.get("t1_response")
            t2_response = response.get("t2_response")
        else:
            # Single response format
            t1_response = response
            t2_response = None

        # Calculate accuracy for each target
        t1_accuracy = (
            (t1_response == t1_correct)
            if t1_response is not None and t1_correct is not None
            else False
        )
        t2_accuracy = (
            (t2_response == t2_correct)
            if t2_response is not None and t2_correct is not None
            else False
        )

        # Overall accuracy (both targets correct)
        both_correct = t1_accuracy and t2_accuracy

        return {
            "response": str(response) if response is not None else None,
            "t1_response": str(t1_response) if t1_response is not None else None,
            "t2_response": str(t2_response) if t2_response is not None else None,
            "t1_correct": str(t1_correct) if t1_correct is not None else None,
            "t2_correct": str(t2_correct) if t2_correct is not None else None,
            "t1_accuracy": float(t1_accuracy),
            "t2_accuracy": float(t2_accuracy),
            "both_correct": float(both_correct),
            "accuracy": (
                1.0 if both_correct else 0.5 if (t1_accuracy or t2_accuracy) else 0.0
            ),
            "reaction_time_ms": 800,  # Default RT
            "confidence": 0.7,  # Default confidence
        }

    def simulate_response(self, trial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate participant responses with attentional blink effect."""
        # Handle different stream formats
        stream = trial_data.get("stimulus_stream", [])
        t2_lag = trial_data.get("t2_lag", 3)

        # Find targets in stream
        t1_stimulus = None
        t2_stimulus = None

        # Stream might be a list of dicts or other format
        if isinstance(stream, list):
            for item in stream:
                if isinstance(item, dict):
                    if item.get("is_target1"):
                        t1_stimulus = item.get("stimulus")
                    elif item.get("is_target2"):
                        t2_stimulus = item.get("stimulus")

        # Simulate attentional blink effect
        # T1 detection is generally good
        t1_detected = random.random() < 0.8

        # T2 detection depends on lag (attentional blink effect)
        if t2_lag in [2, 3]:  # Within attentional blink window
            t2_detection_prob = 0.3  # Poor detection
        elif t2_lag in [5, 7]:  # Partial recovery
            t2_detection_prob = 0.6
        else:  # lag 9 or more - full recovery
            t2_detection_prob = 0.75

        t2_detected = random.random() < t2_detection_prob

        # Generate responses
        t1_response = None
        t2_response = None

        if t1_detected:
            # Sometimes make errors even when detected
            if random.random() < 0.85:  # 85% correct when detected
                t1_response = t1_stimulus
            else:
                # Random error from same stimulus type
                pool = self.stimulus_generator.stimulus_pool[self.config.target1_type]
                t1_response = random.choice([s for s in pool if s != t1_stimulus])

        if t2_detected:
            if random.random() < 0.85:  # 85% correct when detected
                t2_response = t2_stimulus
            else:
                # Random error from same stimulus type
                pool = self.stimulus_generator.stimulus_pool[self.config.target2_type]
                t2_response = random.choice([s for s in pool if s != t2_stimulus])

        # Simulate reaction time (longer for more difficult lags)
        base_rt = 1200
        if t2_lag in [2, 3]:
            base_rt += 400  # Longer RT during attentional blink
        elif t2_lag in [5, 7]:
            base_rt += 200

        rt = max(500, np.random.normal(base_rt, 250))

        return {
            "response": (t1_response, t2_response),
            "reaction_time_ms": int(rt),
            "confidence": 0.6 if t1_detected and t2_detected else 0.4,
            "timestamp": time.time(),
        }

    def compute_participant_summary(
        self, trials: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compute comprehensive summary for attentional blink task."""
        base_summary = super().compute_participant_summary(trials)

        if not trials:
            return base_summary

        df = pd.DataFrame(trials)

        # Attentional blink specific metrics
        summary = {
            **base_summary,
            "t1_detection_rate": 0,
            "t2_detection_rate": 0,
            "both_targets_rate": 0,
            "performance_by_lag": {},
            "attentional_blink_depth": 0,
            "attentional_blink_duration": 0,
        }

        # Calculate detection rates
        if "t1_correct" in df.columns:
            # Convert string responses to boolean for accuracy calculation
            t1_correct_bool = df["t1_correct"].apply(
                lambda x: x is not None and str(x).strip() != ""
            )
            summary["t1_detection_rate"] = t1_correct_bool.mean()

        if "t2_correct" in df.columns:
            # Convert string responses to boolean for accuracy calculation
            t2_correct_bool = df["t2_correct"].apply(
                lambda x: x is not None and str(x).strip() != ""
            )
            summary["t2_detection_rate"] = t2_correct_bool.mean()

        if "both_correct" in df.columns:
            # Convert string responses to boolean for accuracy calculation
            both_correct_bool = df["both_correct"].apply(
                lambda x: float(x) if isinstance(x, (int, float)) else 0.0
            )
            summary["both_targets_rate"] = both_correct_bool.mean()

        # Calculate performance by lag
        if "t2_lag" in df.columns:
            for lag in sorted(df["t2_lag"].unique()):
                lag_trials = df[df["t2_lag"] == lag]
                if len(lag_trials) > 0:
                    # Convert string responses to boolean for accuracy calculation
                    t2_correct_bool = lag_trials["t2_correct"].apply(
                        lambda x: float(x) if isinstance(x, (int, float)) else 0.0
                    )
                    both_correct_bool = lag_trials["both_correct"].apply(
                        lambda x: float(x) if isinstance(x, (int, float)) else 0.0
                    )

                    t2_rate = (
                        t2_correct_bool.mean()
                        if "t2_correct" in lag_trials.columns
                        else 0
                    )
                    both_rate = (
                        both_correct_bool.mean()
                        if "both_correct" in lag_trials.columns
                        else 0
                    )

                    summary["performance_by_lag"][f"lag_{lag}"] = {
                        "t2_detection_rate": t2_rate,
                        "both_targets_rate": both_rate,
                        "n_trials": len(lag_trials),
                    }

        # Calculate attentional blink depth and duration
        lag_performance = []
        lags = []

        for lag_str, perf in summary["performance_by_lag"].items():
            lag_num = int(lag_str.split("_")[1])
            lags.append(lag_num)
            lag_performance.append(perf["t2_detection_rate"])

        if len(lag_performance) > 2:
            # Find minimum performance (blink depth)
            min_idx = np.argmin(lag_performance)
            summary["attentional_blink_depth"] = 1.0 - lag_performance[min_idx]
            summary["attentional_blink_duration"] = lags[min_idx]

        return summary


def run_attentional_blink_experiment(**kwargs):
    """Run the Attentional Blink experiment."""
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
        if hasattr(AttentionalBlinkConfig, config_key):
            config_params[config_key] = value

    # Create config and experiment
    config = AttentionalBlinkConfig(**config_params)
    experiment = AttentionalBlinkTask(config)

    # Set up and run experiment
    experiment.setup()
    results = experiment.run_experiment()

    # Save results if output file specified
    if kwargs.get("output_file"):
        experiment.save_data(kwargs["output_file"])

    return experiment


if __name__ == "__main__":
    # Example usage
    config = AttentionalBlinkConfig(
        n_trials=100, n_participants=5, target2_lags=[2, 3, 5, 7, 9]
    )

    experiment = AttentionalBlinkTask(config)
    experiment.setup()
    results = experiment.run_experiment()

    print("Attentional Blink experiment completed!")
    print(f"Results shape: {results.shape}")

    # Print summary for first participant
    if experiment.participant_data:
        first_participant = list(experiment.participant_data.keys())[0]
        summary = experiment.participant_data[first_participant]["summary"]
        print(f"\nParticipant {first_participant} Summary:")
        print(f"T1 Detection Rate: {summary.get('t1_detection_rate', 0):.3f}")
        print(f"T2 Detection Rate: {summary.get('t2_detection_rate', 0):.3f}")
        print(f"Both Targets Rate: {summary.get('both_targets_rate', 0):.3f}")
        print(
            f"Attentional Blink Depth: {summary.get('attentional_blink_depth', 0):.3f}"
        )
        print(f"Performance by Lag: {summary.get('performance_by_lag', {})}")
