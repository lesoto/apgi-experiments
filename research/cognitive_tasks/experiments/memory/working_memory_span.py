"""
Working Memory Span implementation.

Working memory span tasks measure the capacity of working memory by requiring
participants to store and manipulate increasingly larger amounts of information.
Common variants include digit span, letter span, and spatial span.

APGI Integration:
- θₜ (threshold): Working memory capacity threshold
- π (precision): Memory precision and maintenance
- ε (prediction error): Capacity overflow prediction error
- β (inverse temperature): Response consistency under load
"""

import random
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import time

from .. import TrialBasedTask, TrialBasedTaskConfig


@dataclass
class WorkingMemorySpanConfig(TrialBasedTaskConfig):
    """Configuration for Working Memory Span experiment."""

    n_trials: int = 100
    stimulus_duration_ms: int = 800
    inter_stimulus_interval_ms: int = 400
    response_window_ms: int = 5000

    # Span parameters
    min_span_length: int = 2
    max_span_length: int = 9
    span_types: List[str] = None  # forward, backward, spatial

    # Stimulus parameters
    stimulus_modalities: List[str] = None  # digits, letters, spatial
    digit_range: Tuple[int, int] = (1, 9)  # Range for digit span
    letter_set: List[str] = None  # Letters for letter span

    # Adaptive parameters
    adaptive_span: bool = True  # Whether to adapt span length based on performance
    consecutive_correct_threshold: int = 2  # Correct trials needed to increase span
    consecutive_incorrect_threshold: int = 1  # Incorrect trials needed to decrease span

    def __post_init__(self):
        if self.span_types is None:
            self.span_types = ["forward", "backward"]

        if self.stimulus_modalities is None:
            self.stimulus_modalities = ["digits", "letters"]

        if self.letter_set is None:
            self.letter_set = list("ABCDEFGHJKLMNPQRSTVWXYZ")  # 20 consonants


class SpanStimulus:
    """Generate working memory span stimuli."""

    def __init__(self, config: WorkingMemorySpanConfig):
        self.config = config
        self.spatial_positions = self._generate_spatial_positions()

    def _generate_spatial_positions(self) -> List[Tuple[float, float]]:
        """Generate spatial positions for spatial span."""
        positions = []
        grid_size = 3  # 3x3 grid

        for row in range(grid_size):
            for col in range(grid_size):
                x = (col - 1) * 2.0  # -2, 0, 2
                y = (row - 1) * 2.0  # -2, 0, 2
                positions.append((x, y))

        return positions

    def generate_sequence(
        self, span_length: int, span_type: str, modality: str
    ) -> Dict[str, Any]:
        """Generate a span sequence."""
        if modality == "digits":
            stimuli = [
                str(random.randint(*self.config.digit_range))
                for _ in range(span_length)
            ]
        elif modality == "letters":
            stimuli = random.sample(self.config.letter_set, span_length)
        elif modality == "spatial":
            positions = random.sample(self.spatial_positions, span_length)
            stimuli = [(i, pos) for i, pos in enumerate(positions)]
        else:
            raise ValueError(f"Unknown modality: {modality}")

        sequence = {
            "stimuli": stimuli,
            "span_length": span_length,
            "span_type": span_type,
            "modality": modality,
            "correct_response": (
                stimuli if span_type == "forward" else list(reversed(stimuli))
            ),
        }

        return sequence


class WorkingMemorySpanTask(TrialBasedTask):
    """Working Memory Span task implementation."""

    def __init__(self, config: Optional[WorkingMemorySpanConfig] = None):
        super().__init__(config)
        self.config = config or WorkingMemorySpanConfig()
        self.stimulus_generator = SpanStimulus(self.config)
        self.span_performance = {}
        self.current_span_length = self.config.min_span_length
        self.consecutive_correct = 0
        self.consecutive_incorrect = 0

    def setup(self, **kwargs):
        """Set up the Working Memory Span task."""
        super().setup(**kwargs)
        self.stimulus_generator = SpanStimulus(self.config)
        self.span_performance = {}
        self.current_span_length = self.config.min_span_length
        self.consecutive_correct = 0
        self.consecutive_incorrect = 0

    def generate_trial_sequence(self) -> List[Dict[str, Any]]:
        """Generate trial sequence for span task."""
        trials = []

        # Create balanced design
        for span_type in self.config.span_types:
            for modality in self.config.stimulus_modalities:
                n_trials_condition = self.config.n_trials // (
                    len(self.config.span_types) * len(self.config.stimulus_modalities)
                )

                for _ in range(n_trials_condition):
                    trials.append(
                        {
                            "span_type": span_type,
                            "modality": modality,
                            "condition": f"{span_type}_{modality}",
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
                "span_type": "forward",
                "modality": "digits",
                "condition": "forward_digits",
            }

        # Determine span length
        if self.config.adaptive_span:
            span_length = self.current_span_length
        else:
            # Use fixed span lengths across trials
            span_length = self.config.min_span_length + (
                trial_number
                % (self.config.max_span_length - self.config.min_span_length + 1)
            )

        # Generate sequence
        sequence = self.stimulus_generator.generate_sequence(
            span_length, trial_config["span_type"], trial_config["modality"]
        )

        base_params.update(
            {
                "stimuli": sequence["stimuli"],
                "span_length": sequence["span_length"],
                "span_type": sequence["span_type"],
                "modality": sequence["modality"],
                "correct_response": sequence["correct_response"],
                "condition": trial_config["condition"],
                "stimulus_duration_ms": self.config.stimulus_duration_ms,
                "isi_ms": self.config.inter_stimulus_interval_ms,
            }
        )

        return base_params

    def process_response(
        self, response: Any, correct_response: Any, trial_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Process working memory span response."""
        # Response should be a list or tuple of stimuli
        if isinstance(response, (list, tuple)):
            response_list = list(response)
        elif isinstance(response, str):
            # Parse string response
            response_list = list(response)
        else:
            response_list = [response]

        correct_list = (
            list(correct_response)
            if not isinstance(correct_response, list)
            else correct_response
        )

        # Get memory parameters from trial data or use defaults
        set_size = len(correct_list)  # Infer from correct response
        list_type = "words"  # Default
        span_length = set_size
        span_type = "forward"  # Default
        modality = "verbal"  # Default

        if trial_data:
            set_size = trial_data.get("set_size", set_size)
            list_type = trial_data.get("list_type", list_type)
            span_length = trial_data.get("span_length", span_length)
            span_type = trial_data.get("span_type", span_type)
            modality = trial_data.get("modality", modality)

        # Calculate accuracy
        is_correct = response_list == correct_list

        # Update adaptive span if enabled
        if self.config.adaptive_span:
            if is_correct:
                self.consecutive_correct += 1
                self.consecutive_incorrect = 0

                if (
                    self.consecutive_correct
                    >= self.config.consecutive_correct_threshold
                ):
                    self.current_span_length = min(
                        self.current_span_length + 1, self.config.max_span_length
                    )
                    self.consecutive_correct = 0
            else:
                self.consecutive_incorrect += 1
                self.consecutive_correct = 0

                if (
                    self.consecutive_incorrect
                    >= self.config.consecutive_incorrect_threshold
                ):
                    self.current_span_length = max(
                        self.current_span_length - 1, self.config.min_span_length
                    )
                    self.consecutive_incorrect = 0

        # Store performance
        span_length = trial_data.get("span_length", 3)
        if span_length not in self.span_performance:
            self.span_performance[span_length] = {"accuracy": [], "reaction_times": []}

        self.span_performance[span_length]["accuracy"].append(1 if is_correct else 0)
        self.span_performance[span_length]["reaction_times"].append(
            trial_data.get("reaction_time_ms", 0)
        )

        # Calculate confidence based on accuracy and span length
        base_confidence = 0.8 if is_correct else 0.3
        base_confidence *= 1.0 - span_length * 0.08  # Lower confidence for longer spans

        return {
            "response": response_list,
            "accuracy": 1 if is_correct else 0,
            "reaction_time_ms": 0,  # Will be filled by simulate_response
            "confidence": base_confidence,
            "set_size": set_size,
            "list_type": list_type,
            "span_type": span_type,
            "modality": modality,
            "correct_response": correct_list,
            "current_adaptive_span": (
                self.current_span_length if self.config.adaptive_span else None
            ),
            "condition": (
                trial_data.get("condition", "unknown") if trial_data else "unknown"
            ),
        }

    def simulate_response(self, trial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate participant working memory span performance."""
        span_length = trial_data["span_length"]
        span_type = trial_data["span_type"]
        modality = trial_data["modality"]
        correct_response = trial_data["correct_response"]

        # Base accuracy decreases with span length
        base_accuracy = 0.95 - (span_length * 0.08)
        base_accuracy = max(0.2, base_accuracy)

        # Backward span is harder than forward span
        if span_type == "backward":
            base_accuracy -= 0.1

        # Different modalities have different difficulties
        modality_modifiers = {"digits": 1.0, "letters": 0.9, "spatial": 0.85}
        base_accuracy *= modality_modifiers.get(modality, 1.0)

        # Generate response
        if random.random() < base_accuracy:
            response = correct_response.copy()
        else:
            # Generate incorrect response
            if modality in ["digits", "letters"]:
                # Random permutation or substitution
                if random.random() < 0.5:
                    # Permutation error
                    response = correct_response.copy()
                    random.shuffle(response)
                else:
                    # Substitution error
                    response = correct_response.copy()
                    if modality == "digits":
                        available_items = [
                            str(i) for i in range(*self.config.digit_range)
                        ]
                    else:
                        available_items = self.config.letter_set

                    for i in range(len(response)):
                        if random.random() < 0.3:  # 30% chance of error per item
                            response[i] = random.choice(
                                [
                                    item
                                    for item in available_items
                                    if item != response[i]
                                ]
                            )
            else:  # spatial
                # Spatial errors
                response = correct_response.copy()
                for i in range(len(response)):
                    if random.random() < 0.3:
                        available_positions = [
                            pos
                            for pos in self.stimulus_generator.spatial_positions
                            if pos != response[i][1]
                        ]
                        if available_positions:
                            response[i] = (
                                response[i][0],
                                random.choice(available_positions),
                            )

        # Calculate reaction time (increases with span length)
        base_rt = 1000 + (span_length * 200)

        if span_type == "backward":
            base_rt += 300

        rt = max(500, np.random.normal(base_rt, 250))

        # Calculate confidence
        actual_correct = response == correct_response
        confidence = 0.8 if actual_correct else 0.3
        confidence *= 1.0 - span_length * 0.08

        return {
            "response": response,
            "reaction_time_ms": int(rt),
            "confidence": confidence,
            "timestamp": time.time(),
        }

    def compute_participant_summary(
        self, trials: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compute comprehensive summary for working memory span task."""
        base_summary = super().compute_participant_summary(trials)

        if not trials:
            return base_summary

        df = pd.DataFrame(trials)

        # Working memory span specific metrics
        summary = {
            **base_summary,
            "overall_accuracy": 0,
            "mean_reaction_time": 0,
            "span_capacity": {},
            "modality_performance": {},
            "span_type_performance": {},
        }

        # Overall metrics
        if "accuracy" in df.columns:
            summary["overall_accuracy"] = df["accuracy"].mean()

        if "reaction_time_ms" in df.columns:
            summary["mean_reaction_time"] = df["reaction_time_ms"].mean()

        # Performance by span length
        span_lengths = []
        accuracies = []

        for span_length in sorted(df["span_length"].unique()):
            span_data = df[df["span_length"] == span_length]
            if len(span_data) > 0:
                accuracy = (
                    span_data["accuracy"].mean()
                    if "accuracy" in span_data.columns
                    else 0
                )
                mean_rt = (
                    span_data["reaction_time_ms"].mean()
                    if "reaction_time_ms" in span_data.columns
                    else 0
                )

                summary["span_capacity"][f"span_{span_length}"] = {
                    "accuracy": accuracy,
                    "mean_rt": mean_rt,
                    "n_trials": len(span_data),
                }

                span_lengths.append(span_length)
                accuracies.append(accuracy)

        # Estimate working memory span capacity
        # Find highest span with accuracy above 50%
        max_span = 0
        for span_length, accuracy in zip(span_lengths, accuracies):
            if accuracy > 0.5:
                max_span = span_length

        summary["span_capacity"]["estimated_span"] = max_span
        summary["span_capacity"]["performance_curve"] = dict(
            zip(span_lengths, accuracies)
        )

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

                summary["modality_performance"][modality] = {
                    "accuracy": accuracy,
                    "mean_rt": mean_rt,
                    "n_trials": len(modality_data),
                }

        # Performance by span type
        for span_type in df["span_type"].unique():
            type_data = df[df["span_type"] == span_type]
            if len(type_data) > 0:
                accuracy = (
                    type_data["accuracy"].mean()
                    if "accuracy" in type_data.columns
                    else 0
                )
                mean_rt = (
                    type_data["reaction_time_ms"].mean()
                    if "reaction_time_ms" in type_data.columns
                    else 0
                )

                summary["span_type_performance"][span_type] = {
                    "accuracy": accuracy,
                    "mean_rt": mean_rt,
                    "n_trials": len(type_data),
                }

        # Adaptive span performance
        if self.config.adaptive_span and "current_adaptive_span" in df.columns:
            adaptive_spans = df["current_adaptive_span"].dropna()
            if len(adaptive_spans) > 0:
                summary["adaptive_performance"] = {
                    "final_span": int(adaptive_spans.iloc[-1]),
                    "max_span_reached": int(adaptive_spans.max()),
                    "mean_span": adaptive_spans.mean(),
                    "span_progression": adaptive_spans.tolist(),
                }

        return summary


def run_working_memory_span_experiment(**kwargs):
    """Run the Working Memory Span experiment."""
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
        if hasattr(WorkingMemorySpanConfig, config_key):
            config_params[config_key] = value

    # Create config and experiment
    config = WorkingMemorySpanConfig(**config_params)
    experiment = WorkingMemorySpanTask(config)

    # Set up and run experiment
    experiment.setup()
    results = experiment.run_experiment()

    # Save results if output file specified
    if kwargs.get("output_file"):
        experiment.save_data(kwargs["output_file"])

    return experiment


if __name__ == "__main__":
    # Example usage
    config = WorkingMemorySpanConfig(
        n_trials=80,
        n_participants=5,
        span_types=["forward", "backward"],
        adaptive_span=True,
    )

    experiment = WorkingMemorySpanTask(config)
    experiment.setup()
    results = experiment.run_experiment()

    print("Working Memory Span experiment completed!")
    print(f"Results shape: {results.shape}")

    # Print summary for first participant
    if experiment.participant_data:
        first_participant = list(experiment.participant_data.keys())[0]
        summary = experiment.participant_data[first_participant]["summary"]
        print(f"\nParticipant {first_participant} Summary:")
        print(f"Overall Accuracy: {summary.get('overall_accuracy', 0):.3f}")
        print(f"Mean Reaction Time: {summary.get('mean_reaction_time', 0):.1f} ms")
        print(
            f"Estimated Span: {summary.get('span_capacity', {}).get('estimated_span', 0)}"
        )
        print(f"Span Capacity: {summary.get('span_capacity', {})}")
