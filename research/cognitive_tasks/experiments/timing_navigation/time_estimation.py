"""
Time Estimation implementation.

Time estimation measures the subjective perception of time intervals.
Participants estimate the duration of visual or auditory stimuli, revealing
temporal perception biases and the scalar property of time perception.

APGI Integration:
- θₜ (threshold): Temporal discrimination threshold
- π (precision): Time estimation precision
- ε (prediction error): Temporal prediction error
- β (inverse temperature): Estimation consistency
"""

import random
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import time

from .. import TrialBasedTask, TrialBasedTaskConfig


@dataclass
class TimeEstimationConfig(TrialBasedTaskConfig):
    """Configuration for Time Estimation experiment."""

    n_trials: int = 120
    stimulus_duration_ms: int = 1000  # Duration of stimulus to be estimated
    response_window_ms: int = 5000
    inter_trial_interval_ms: int = 2000

    # Time estimation parameters
    target_durations: List[int] = None  # Different durations to estimate
    duration_range: Tuple[int, int] = (200, 3000)  # Min and max durations
    n_duration_levels: int = 5  # Number of different durations

    # Modality parameters
    modalities: List[str] = None  # visual, auditory, tactile
    stimulus_types: List[str] = None  # simple, complex

    # Response parameters
    response_method: str = "numeric"  # numeric, verbal, visual
    estimation_units: str = "milliseconds"  # milliseconds, seconds

    def __post_init__(self):
        if self.target_durations is None:
            # Create logarithmic spacing of durations
            min_d, max_d = self.duration_range
            self.target_durations = (
                np.logspace(np.log10(min_d), np.log10(max_d), self.n_duration_levels)
                .astype(int)
                .tolist()
            )

        if self.modalities is None:
            self.modalities = ["visual", "auditory"]

        if self.stimulus_types is None:
            self.stimulus_types = ["simple"]


class TimeEstimationStimulus:
    """Generate time estimation stimuli."""

    def __init__(self, config: TimeEstimationConfig):
        self.config = config

    def generate_stimulus(self, duration: int, modality: str) -> Dict[str, Any]:
        """Generate a stimulus for time estimation."""
        stimulus = {
            "duration": duration,
            "modality": modality,
            "stimulus_type": "simple",
        }

        if modality == "visual":
            # Visual stimulus (e.g., circle)
            stimulus["visual_stimulus"] = "●"
            stimulus["auditory_stimulus"] = None
            stimulus["tactile_stimulus"] = None
        elif modality == "auditory":
            # Auditory stimulus (tone)
            stimulus["visual_stimulus"] = None
            stimulus["auditory_stimulus"] = f"{duration}Hz tone"
            stimulus["tactile_stimulus"] = None
        elif modality == "tactile":
            # Tactile stimulus (vibration)
            stimulus["visual_stimulus"] = None
            stimulus["auditory_stimulus"] = None
            stimulus["tactile_stimulus"] = f"vibration_{duration}ms"

        return stimulus


class TimeEstimationTask(TrialBasedTask):
    """Time Estimation task implementation."""

    def __init__(self, config: Optional[TimeEstimationConfig] = None):
        super().__init__(config)
        self.config = config or TimeEstimationConfig()
        self.stimulus_generator = TimeEstimationStimulus(self.config)
        self.time_perception_data = {}

    def setup(self, **kwargs):
        """Set up the Time Estimation task."""
        super().setup(**kwargs)
        self.stimulus_generator = TimeEstimationStimulus(self.config)
        self.time_perception_data = {}

    def generate_trial_sequence(self) -> List[Dict[str, Any]]:
        """Generate balanced trial sequence."""
        trials = []

        # Create balanced design across modalities and durations
        for modality in self.config.modalities:
            for duration in self.config.target_durations:
                n_trials_condition = self.config.n_trials // (
                    len(self.config.modalities) * len(self.config.target_durations)
                )

                for _ in range(n_trials_condition):
                    trials.append(
                        {
                            "modality": modality,
                            "duration": duration,
                            "condition": f"{modality}_{duration}ms",
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
                "modality": "visual",
                "duration": 1000,
                "condition": "visual_1000ms",
            }

        # Generate stimulus
        stimulus = self.stimulus_generator.generate_stimulus(
            trial_config["duration"], trial_config["modality"]
        )

        base_params.update(
            {
                "stimulus": stimulus,
                "modality": trial_config["modality"],
                "duration": trial_config["duration"],
                "condition": trial_config["condition"],
                "stimulus_duration_ms": trial_config["duration"],
                "response_window_ms": self.config.response_window_ms,
            }
        )

        return base_params

    def process_response(
        self, response: Any, correct_response: Any, trial_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Process time estimation response."""
        # Handle different response formats
        if isinstance(response, (int, float)):
            estimated_duration = float(response)
        elif isinstance(response, str):
            # Parse numeric response from string
            try:
                estimated_duration = float(response)
            except ValueError:
                # Invalid response
                estimated_duration = 0.0
        else:
            estimated_duration = 0.0

        # Get trial data from parameters if available
        if trial_data:
            actual_duration = trial_data.get("duration", 1000)
            modality = trial_data.get("modality", "visual")
            condition = trial_data.get("condition", "default")
        else:
            # Default values
            actual_duration = 1000
            modality = "visual"
            condition = "default"

        # Calculate accuracy (within acceptable range)
        tolerance = actual_duration * 0.15  # 15% tolerance
        is_accurate = abs(estimated_duration - actual_duration) <= tolerance

        # Store time perception data
        duration = actual_duration

        key = f"{modality}_{duration}ms"
        if key not in self.time_perception_data:
            self.time_perception_data[key] = {
                "estimates": [],
                "errors": [],
                "accuracies": [],
            }

        self.time_perception_data[key]["estimates"].append(estimated_duration)

        # Calculate relative error
        relative_error = (estimated_duration - actual_duration) / actual_duration
        absolute_error = abs(estimated_duration - actual_duration)

        self.time_perception_data[key]["errors"].append(relative_error)
        self.time_perception_data[key]["accuracies"].append(1 if is_accurate else 0)

        # Calculate confidence based on accuracy
        base_confidence = 0.7 if is_accurate else 0.3

        # Higher confidence for shorter durations (easier to estimate)
        if duration < 1000:
            base_confidence += 0.1
        elif duration > 2000:
            base_confidence -= 0.1

        return {
            "response": estimated_duration,
            "accuracy": 1 if is_accurate else 0,
            "reaction_time_ms": (
                trial_data.get("reaction_time_ms", 800) if trial_data else 800
            ),
            "confidence": base_confidence,
            "estimated_duration": estimated_duration,
            "actual_duration": actual_duration,
            "absolute_error": absolute_error,
            "relative_error": relative_error,
            "modality": modality,
            "condition": condition,
        }

    def simulate_response(self, trial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate participant time estimation performance."""
        actual_duration = trial_data["duration"]
        modality = trial_data["modality"]

        # Base estimation accuracy depends on duration and modality
        # Weber's law: just noticeable difference increases with duration
        weber_fraction = 0.1  # Weber fraction for time perception
        standard_deviation = actual_duration * weber_fraction

        # Generate estimate with systematic bias
        # People typically underestimate longer durations
        systematic_bias = (
            -actual_duration * 0.05
            if actual_duration > 1500
            else actual_duration * 0.02
        )

        # Add individual variation
        estimate = (
            actual_duration + systematic_bias + np.random.normal(0, standard_deviation)
        )

        # Ensure positive estimate
        estimate = max(50, estimate)

        # Calculate reaction time (longer for difficult estimations)
        base_rt = 1500

        # Longer RTs for longer durations
        if actual_duration > 1500:
            base_rt += 300
        elif actual_duration > 2000:
            base_rt += 500

        # Modality effects
        if modality == "auditory":
            base_rt -= 100  # Auditory time estimation is typically more accurate
        elif modality == "tactile":
            base_rt += 200  # Tactile is harder

        rt = max(600, np.random.normal(base_rt, 300))

        # Calculate confidence
        absolute_error = abs(estimate - actual_duration)
        tolerance = actual_duration * 0.15
        is_accurate = absolute_error <= tolerance

        confidence = 0.7 if is_accurate else 0.3
        if is_accurate:
            confidence += 0.1  # Higher confidence for accurate estimates

        return {
            "response": estimate,
            "reaction_time_ms": int(rt),
            "confidence": confidence,
            "timestamp": time.time(),
        }

    def compute_participant_summary(
        self, trials: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compute comprehensive summary for time estimation task."""
        base_summary = super().compute_participant_summary(trials)

        if not trials:
            return base_summary

        df = pd.DataFrame(trials)

        # Time estimation specific metrics
        summary = {
            **base_summary,
            "overall_accuracy": 0,
            "mean_reaction_time": 0,
            "time_perception": {},
            "modality_performance": {},
            "duration_effects": {},
            "scalar_timing": {},
        }

        # Overall metrics
        if "accuracy" in df.columns:
            summary["overall_accuracy"] = df["accuracy"].mean()

        if "reaction_time_ms" in df.columns:
            summary["mean_reaction_time"] = df["reaction_time_ms"].mean()

        # Performance by modality
        for modality in df["modality"].unique():
            modality_data = df[df["modality"] == modality]
            if len(modality_data) > 0:
                accuracy = (
                    modality_data["accuracy"].mean()
                    if "accuracy" in modality_data.columns
                    else 0
                )
                mean_rt = (
                    modality_data["reaction_time_ms"].mean()
                    if "reaction_time_ms" in modality_data.columns
                    else 0
                )
                mean_absolute_error = (
                    modality_data["absolute_error"].mean()
                    if "absolute_error" in modality_data.columns
                    else 0
                )

                summary["modality_performance"][modality] = {
                    "accuracy": accuracy,
                    "mean_rt": mean_rt,
                    "mean_absolute_error": mean_absolute_error,
                    "n_trials": len(modality_data),
                }

        # Performance by duration
        for duration in sorted(df["actual_duration"].unique()):
            duration_data = df[df["actual_duration"] == duration]
            if len(duration_data) > 0:
                accuracy = (
                    duration_data["accuracy"].mean()
                    if "accuracy" in duration_data.columns
                    else 0
                )
                mean_absolute_error = (
                    duration_data["absolute_error"].mean()
                    if "absolute_error" in duration_data.columns
                    else 0
                )
                mean_relative_error = (
                    duration_data["relative_error"].mean()
                    if "relative_error" in duration_data.columns
                    else 0
                )
                mean_estimate = (
                    duration_data["estimated_duration"].mean()
                    if "estimated_duration" in duration_data.columns
                    else 0
                )

                summary["duration_effects"][f"{duration}ms"] = {
                    "accuracy": accuracy,
                    "mean_absolute_error": mean_absolute_error,
                    "mean_relative_error": mean_relative_error,
                    "mean_estimate": mean_estimate,
                    "bias": mean_estimate - duration,  # Positive = overestimation
                    "n_trials": len(duration_data),
                }

        # Calculate scalar timing properties
        durations = sorted(df["actual_duration"].unique())
        absolute_errors = []
        relative_errors = []

        for duration in durations:
            duration_data = df[df["actual_duration"] == duration]
            if len(duration_data) > 0:
                absolute_errors.append(
                    duration_data["absolute_error"].mean()
                    if "absolute_error" in duration_data.columns
                    else 0
                )
                relative_errors.append(
                    duration_data["relative_error"].mean()
                    if "relative_error" in duration_data.columns
                    else 0
                )

        if len(durations) > 2:
            # Weber fraction calculation
            weber_fractions = []
            for i, duration in enumerate(durations):
                if i > 0:  # Skip first point
                    weber_fraction = absolute_errors[i] / duration
                    weber_fractions.append(weber_fraction)

            summary["scalar_timing"] = {
                "weber_fraction": np.mean(weber_fractions) if weber_fractions else 0.0,
                "duration_range": [min(durations), max(durations)],
                "mean_absolute_error": (
                    np.mean(absolute_errors) if absolute_errors else 0.0
                ),
                "overestimation_bias": (
                    np.mean([e for e in relative_errors if e > 0])
                    if relative_errors
                    else 0.0
                ),
                "underestimation_bias": (
                    np.mean([e for e in relative_errors if e < 0])
                    if relative_errors
                    else 0.0
                ),
            }

        return summary


def run_time_estimation_experiment(**kwargs):
    """Run the Time Estimation experiment."""
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
        if hasattr(TimeEstimationConfig, config_key):
            config_params[config_key] = value

    # Create config and experiment
    config = TimeEstimationConfig(**config_params)
    experiment = TimeEstimationTask(config)

    # Set up and run experiment
    experiment.setup()
    results = experiment.run_experiment()

    # Save results if output file specified
    if kwargs.get("output_file"):
        experiment.save_data(kwargs["output_file"])

    return experiment


if __name__ == "__main__":
    # Example usage
    config = TimeEstimationConfig(
        n_trials=100,
        n_participants=5,
        modalities=["visual", "auditory"],
        duration_range=(200, 2500),
        n_duration_levels=5,
    )

    experiment = TimeEstimationTask(config)
    experiment.setup()
    results = experiment.run_experiment()

    print("Time Estimation experiment completed!")
    print(f"Results shape: {results.shape}")

    # Print summary for first participant
    if experiment.participant_data:
        first_participant = list(experiment.participant_data.keys())[0]
        summary = experiment.participant_data[first_participant]["summary"]
        print(f"\nParticipant {first_participant} Summary:")
        print(f"Overall Accuracy: {summary.get('overall_accuracy', 0):.3f}")
        print(f"Mean Reaction Time: {summary.get('mean_reaction_time', 0):.1f} ms")
        print(
            f"Weber Fraction: {summary.get('scalar_timing', {}).get('weber_fraction', 0):.3f}"
        )
        print(f"Modality Performance: {summary.get('modality_performance', {})}")
        print(f"Duration Effects: {summary.get('duration_effects', {})}")
