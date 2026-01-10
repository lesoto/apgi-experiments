"""
Visual Search implementation.

Visual search is the task of finding a target stimulus among distractor stimuli.
This experiment measures how efficiently participants can find targets and examines
factors like feature vs. conjunction searches and pop-out effects.

APGI Integration:
- θₜ (threshold): Visual attention allocation threshold
- π (precision): Spatial precision of attentional focus
- ε (prediction error): Unexpected target locations
- β (inverse temperature): Search strategy consistency
"""

import random
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import time

from .. import TrialBasedTask, TrialBasedTaskConfig


@dataclass
class VisualSearchConfig(TrialBasedTaskConfig):
    """Configuration for Visual Search experiment."""

    n_trials: int = 120
    display_duration_ms: int = 5000  # Max time to respond
    fixation_duration_ms: int = 500

    # Search parameters
    set_sizes: List[int] = None  # Number of items in display
    search_types: List[str] = None  # feature, conjunction, spatial
    target_present_trials: float = 0.5  # Proportion of trials with target

    # Stimulus parameters
    stimulus_size: float = 1.0  # Visual angle in degrees
    stimulus_colors: List[str] = None
    stimulus_shapes: List[str] = None

    def __post_init__(self):
        if self.set_sizes is None:
            self.set_sizes = [4, 8, 16, 24]

        if self.search_types is None:
            self.search_types = ["feature", "conjunction", "spatial"]

        if self.stimulus_colors is None:
            self.stimulus_colors = ["red", "green", "blue"]

        if self.stimulus_shapes is None:
            self.stimulus_shapes = ["circle", "square", "triangle"]


class VisualSearchDisplay:
    """Generate visual search displays."""

    def __init__(self, config: VisualSearchConfig):
        self.config = config
        self.display_size = 20  # Degrees of visual angle

    def generate_display(
        self, set_size: int, search_type: str, target_present: bool
    ) -> Dict[str, Any]:
        """Generate a visual search display."""
        # Define target and distractor properties based on search type
        if search_type == "feature":
            # Feature search: target differs by single feature
            target_color = "red"
            target_shape = "circle"
            distractor_color = "green"
            distractor_shape = "circle"

        elif search_type == "conjunction":
            # Conjunction search: target differs by combination of features
            target_color = "red"
            target_shape = "circle"
            distractor_colors = ["red", "green"]
            distractor_shapes = ["circle", "square"]

        else:  # spatial
            # Spatial search: target defined by location
            target_color = "red"
            target_shape = "circle"
            distractor_color = "red"
            distractor_shape = "circle"
            target_location = "center"  # Target always in center

        # Generate stimulus positions
        positions = self._generate_positions(
            set_size, search_type == "spatial" and target_present
        )

        # Generate stimuli
        stimuli = []
        target_idx = None

        for i, pos in enumerate(positions):
            if target_present and (target_idx is None):
                # Place target at random position (or center for spatial)
                if search_type == "spatial":
                    target_idx = 0  # First position is center
                else:
                    target_idx = random.randint(0, len(positions) - 1)

            if i == target_idx:
                # Target stimulus
                stimulus = {
                    "id": f"target_{i}",
                    "x": pos[0],
                    "y": pos[1],
                    "color": target_color,
                    "shape": target_shape,
                    "is_target": True,
                }
            else:
                # Distractor stimulus
                if search_type == "feature":
                    color = distractor_color
                    shape = distractor_shape
                elif search_type == "conjunction":
                    # Ensure distractors don't match target combination
                    color = random.choice(
                        [c for c in distractor_colors if c != target_color]
                    )
                    shape = random.choice(
                        [s for s in distractor_shapes if s != target_shape]
                    )
                else:  # spatial
                    color = distractor_color
                    shape = distractor_shape

                stimulus = {
                    "id": f"distractor_{i}",
                    "x": pos[0],
                    "y": pos[1],
                    "color": color,
                    "shape": shape,
                    "is_target": False,
                }

            stimuli.append(stimulus)

        return {
            "stimuli": stimuli,
            "set_size": set_size,
            "search_type": search_type,
            "target_present": target_present,
            "target_index": target_idx,
        }

    def _generate_positions(
        self, n_items: int, include_center: bool = False
    ) -> List[Tuple[float, float]]:
        """Generate positions for stimuli in circular array."""
        positions = []

        if include_center:
            positions.append((0.0, 0.0))  # Center position
            n_items -= 1

        # Generate positions in concentric circles
        if n_items > 0:
            # Calculate number of rings needed
            max_per_ring = 8
            n_rings = max(1, (n_items + max_per_ring - 1) // max_per_ring)

            items_placed = 0
            for ring in range(n_rings):
                radius = 2.0 + ring * 2.0  # Rings at 2°, 4°, 6°, etc.
                items_in_ring = min(max_per_ring, n_items - items_placed)

                if items_in_ring > 0:
                    angles = np.linspace(0, 2 * np.pi, items_in_ring, endpoint=False)
                    for angle in angles:
                        x = radius * np.cos(angle)
                        y = radius * np.sin(angle)
                        positions.append((x, y))
                        items_placed += 1

                    if items_placed >= n_items:
                        break

        return positions[: n_items + (1 if include_center else 0)]


class VisualSearchTask(TrialBasedTask):
    """Visual Search task implementation."""

    def __init__(self, config: Optional[VisualSearchConfig] = None):
        super().__init__(config)
        self.config = config or VisualSearchConfig()
        self.display_generator = VisualSearchDisplay(self.config)
        self.performance_by_condition = {}

    def setup(self, **kwargs):
        """Set up the visual search task."""
        super().setup(**kwargs)
        self.display_generator = VisualSearchDisplay(self.config)
        self.performance_by_condition = {}

    def generate_trial_sequence(self) -> List[Dict[str, Any]]:
        """Generate balanced trial sequence."""
        trials = []

        # Create all condition combinations
        for set_size in self.config.set_sizes:
            for search_type in self.config.search_types:
                for target_present in [True, False]:
                    n_trials_condition = self.config.n_trials // (
                        len(self.config.set_sizes) * len(self.config.search_types) * 2
                    )

                    for _ in range(n_trials_condition):
                        trials.append(
                            {
                                "set_size": set_size,
                                "search_type": search_type,
                                "target_present": target_present,
                                "condition": f"{search_type}_set{set_size}_{'present' if target_present else 'absent'}",
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
                "set_size": 8,
                "search_type": "feature",
                "target_present": True,
                "condition": "feature_set8_present",
            }

        # Generate display
        display = self.display_generator.generate_display(
            trial_config["set_size"],
            trial_config["search_type"],
            trial_config["target_present"],
        )

        base_params.update(
            {
                "display": display,
                "set_size": trial_config["set_size"],
                "search_type": trial_config["search_type"],
                "target_present": trial_config["target_present"],
                "condition": trial_config["condition"],
                "display_duration_ms": self.config.display_duration_ms,
            }
        )

        return base_params

    def process_response(
        self, response: Any, correct_response: Any, trial_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Process visual search response."""
        # Response should be whether target was present
        if isinstance(response, (bool, int)):
            target_detected = bool(response)
        elif isinstance(response, str):
            target_detected = response.lower() in [
                "true",
                "yes",
                "present",
                "1",
                "target",
            ]
        else:
            target_detected = bool(response)

        is_correct = target_detected == correct_response

        # Store performance by condition
        condition = "unknown"
        if trial_data:
            condition = trial_data.get("condition", "unknown")

        if condition not in self.performance_by_condition:
            self.performance_by_condition[condition] = []

        self.performance_by_condition[condition].append(
            {"target_detected": target_detected, "is_correct": is_correct}
        )

        # Calculate confidence based on accuracy and difficulty
        base_confidence = 0.8 if is_correct else 0.4
        if trial_data and trial_data.get("set_size", 4) > 8:
            base_confidence -= 0.1  # Lower confidence for larger sets

        return {
            "response": target_detected,
            "accuracy": 1 if is_correct else 0,
            "reaction_time_ms": 0,  # Will be filled by simulate_response
            "confidence": base_confidence,
            "set_size": trial_data.get("set_size", 4) if trial_data else 4,
            "search_type": (
                trial_data.get("search_type", "feature") if trial_data else "feature"
            ),
            "target_present": (
                trial_data.get("target_present", True) if trial_data else True
            ),
            "condition": condition,
        }

    def simulate_response(self, trial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate participant visual search performance."""
        search_type = trial_data["search_type"]
        set_size = trial_data["set_size"]
        target_present = trial_data["target_present"]

        # Base reaction time and accuracy parameters
        base_rt = 600  # Base RT in ms
        base_accuracy = 0.95

        # Adjust based on search type
        if search_type == "feature":
            # Feature search: efficient, RT independent of set size
            rt_slope = 5  # ms per item
            accuracy_factor = 1.0
        elif search_type == "conjunction":
            # Conjunction search: inefficient, RT depends on set size
            rt_slope = 25  # ms per item
            accuracy_factor = 0.85
        else:  # spatial
            # Spatial search: moderately efficient
            rt_slope = 15  # ms per item
            accuracy_factor = 0.9

        # Calculate reaction time
        rt = base_rt + (rt_slope * set_size)

        # Add noise
        rt = max(300, np.random.normal(rt, 100))

        # Calculate accuracy
        accuracy = base_accuracy * accuracy_factor

        # Target absent trials typically have longer RTs and slightly lower accuracy
        if not target_present:
            rt += 100
            accuracy *= 0.95

        # Determine response
        if random.random() < accuracy:
            response = target_present
        else:
            response = not target_present

        # Calculate confidence
        confidence = 0.7 if response == target_present else 0.5

        return {
            "response": response,
            "reaction_time_ms": int(rt),
            "confidence": confidence,
            "timestamp": time.time(),
        }

    def compute_participant_summary(
        self, trials: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compute comprehensive summary for visual search task."""
        base_summary = super().compute_participant_summary(trials)

        if not trials:
            return base_summary

        df = pd.DataFrame(trials)

        # Visual search specific metrics
        summary = {
            **base_summary,
            "overall_accuracy": 0,
            "mean_reaction_time": 0,
            "search_efficiency": {},
            "set_size_effects": {},
            "search_type_performance": {},
        }

        # Overall metrics
        if "accuracy" in df.columns:
            summary["overall_accuracy"] = df["accuracy"].mean()

        if "reaction_time_ms" in df.columns:
            summary["mean_reaction_time"] = df["reaction_time_ms"].mean()

        # Search efficiency (RT slope as function of set size)
        for search_type in df["search_type"].unique():
            search_type_data = df[df["search_type"] == search_type]

            # Calculate RT slope for this search type
            set_sizes = []
            mean_rts = []

            for set_size in sorted(search_type_data["set_size"].unique()):
                size_data = search_type_data[search_type_data["set_size"] == set_size]
                if len(size_data) > 0 and "reaction_time_ms" in size_data.columns:
                    set_sizes.append(set_size)
                    mean_rts.append(size_data["reaction_time_ms"].mean())

            if len(set_sizes) > 1:
                slope = np.polyfit(set_sizes, mean_rts, 1)[0]
                summary["search_efficiency"][search_type] = {
                    "rt_slope_ms_per_item": slope,
                    "efficiency": (
                        "efficient"
                        if slope < 10
                        else "inefficient" if slope > 20 else "moderate"
                    ),
                }

            # Overall performance by search type
            accuracy = (
                search_type_data["accuracy"].mean()
                if "accuracy" in search_type_data.columns
                else 0
            )
            mean_rt = (
                search_type_data["reaction_time_ms"].mean()
                if "reaction_time_ms" in search_type_data.columns
                else 0
            )

            summary["search_type_performance"][search_type] = {
                "accuracy": accuracy,
                "mean_rt": mean_rt,
                "n_trials": len(search_type_data),
            }

        # Set size effects
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

                summary["set_size_effects"][f"set_size_{set_size}"] = {
                    "accuracy": accuracy,
                    "mean_rt": mean_rt,
                    "n_trials": len(size_data),
                }

        return summary


def run_visual_search_experiment(**kwargs):
    """Run the Visual Search experiment."""
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
        if hasattr(VisualSearchConfig, config_key):
            config_params[config_key] = value

    # Create config and experiment
    config = VisualSearchConfig(**config_params)
    experiment = VisualSearchTask(config)

    # Set up and run experiment
    experiment.setup()
    results = experiment.run_experiment()

    # Save results if output file specified
    if kwargs.get("output_file"):
        experiment.save_data(kwargs["output_file"])

    return experiment


if __name__ == "__main__":
    # Example usage
    config = VisualSearchConfig(
        n_trials=80,
        n_participants=5,
        set_sizes=[4, 8, 16],
        search_types=["feature", "conjunction"],
    )

    experiment = VisualSearchTask(config)
    experiment.setup()
    results = experiment.run_experiment()

    print("Visual Search experiment completed!")
    print(f"Results shape: {results.shape}")

    # Print summary for first participant
    if experiment.participant_data:
        first_participant = list(experiment.participant_data.keys())[0]
        summary = experiment.participant_data[first_participant]["summary"]
        print(f"\nParticipant {first_participant} Summary:")
        print(f"Overall Accuracy: {summary.get('overall_accuracy', 0):.3f}")
        print(f"Mean Reaction Time: {summary.get('mean_reaction_time', 0):.1f} ms")
        print(f"Search Efficiency: {summary.get('search_efficiency', {})}")
