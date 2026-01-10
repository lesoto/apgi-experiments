"""
Change Blindness implementation.

Change blindness is the failure to notice changes in a visual scene when the changes
occur during a visual disruption, such as a blink, saccade, or cut. This experiment
uses the "flicker" paradigm where images alternate with a blank screen.

APGI Integration:
- θₜ (threshold): Visual change detection threshold
- π (precision): Spatial precision of visual attention
- ε (prediction error): Unexpected visual changes
- β (inverse temperature): Confidence in change detection
"""

import random
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import time

from .. import TrialBasedTask, TrialBasedTaskConfig


@dataclass
class ChangeBlindnessConfig(TrialBasedTaskConfig):
    """Configuration for Change Blindness experiment."""

    n_trials: int = 80
    image_duration_ms: int = 500
    blank_duration_ms: int = 100
    max_alternations: int = 20
    response_timeout_ms: int = 30000

    # Change parameters
    change_types: List[str] = None  # Types of changes to implement
    change_sizes: List[str] = None  # Small, medium, large changes
    change_locations: List[str] = None  # Central, peripheral changes

    # Scene parameters
    scene_complexity: str = "medium"  # Simple, medium, complex
    distractor_count: int = 10  # Number of distractor elements

    def __post_init__(self):
        if self.change_types is None:
            self.change_types = [
                "color",
                "position",
                "size",
                "appearance",
                "disappearance",
            ]

        if self.change_sizes is None:
            self.change_sizes = ["small", "medium", "large"]

        if self.change_locations is None:
            self.change_locations = ["central", "peripheral"]


class SceneGenerator:
    """Generate visual scenes for change blindness experiments."""

    def __init__(self, config: ChangeBlindnessConfig):
        self.config = config
        self.scene_templates = self._create_scene_templates()

    def _create_scene_templates(self) -> List[Dict[str, Any]]:
        """Create basic scene templates."""
        templates = []

        # Simple geometric scenes
        for i in range(20):
            n_objects = random.randint(5, 15)
            objects = []

            for j in range(n_objects):
                obj = {
                    "id": f"obj_{j}",
                    "type": random.choice(["circle", "square", "triangle"]),
                    "x": random.uniform(0.1, 0.9),
                    "y": random.uniform(0.1, 0.9),
                    "size": random.uniform(0.05, 0.15),
                    "color": random.choice(
                        ["red", "blue", "green", "yellow", "purple"]
                    ),
                }
                objects.append(obj)

            templates.append(
                {
                    "scene_id": f"template_{i}",
                    "objects": objects,
                    "complexity": "medium",
                }
            )

        return templates

    def create_scene_pair(
        self, change_type: str, change_size: str, change_location: str
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Create a pair of scenes with a specific change."""
        # Start with a random template
        template = random.choice(self.scene_templates)
        original_scene = {
            "scene_id": f"original_{random.randint(1000, 9999)}",
            "objects": [obj.copy() for obj in template["objects"]],
        }

        changed_scene = {
            "scene_id": f"changed_{random.randint(1000, 9999)}",
            "objects": [obj.copy() for obj in template["objects"]],
        }

        # Select target object for change
        if change_location == "central":
            # Choose object near center
            central_objects = [
                obj
                for obj in changed_scene["objects"]
                if 0.3 < obj["x"] < 0.7 and 0.3 < obj["y"] < 0.7
            ]
            if central_objects:
                target_obj = random.choice(central_objects)
            else:
                target_obj = random.choice(changed_scene["objects"])
        else:
            # Choose peripheral object
            peripheral_objects = [
                obj
                for obj in changed_scene["objects"]
                if obj["x"] < 0.3 or obj["x"] > 0.7 or obj["y"] < 0.3 or obj["y"] > 0.7
            ]
            if peripheral_objects:
                target_obj = random.choice(peripheral_objects)
            else:
                target_obj = random.choice(changed_scene["objects"])

        # Apply change based on type and size
        change_magnitude = {"small": 0.1, "medium": 0.3, "large": 0.5}[change_size]

        if change_type == "color":
            colors = ["red", "blue", "green", "yellow", "purple"]
            original_color = target_obj["color"]
            available_colors = [c for c in colors if c != original_color]
            target_obj["color"] = random.choice(available_colors)

        elif change_type == "position":
            dx = random.uniform(-change_magnitude, change_magnitude)
            dy = random.uniform(-change_magnitude, change_magnitude)
            target_obj["x"] = np.clip(target_obj["x"] + dx, 0.1, 0.9)
            target_obj["y"] = np.clip(target_obj["y"] + dy, 0.1, 0.9)

        elif change_type == "size":
            size_change = random.uniform(
                -change_magnitude * 0.1, change_magnitude * 0.1
            )
            target_obj["size"] = np.clip(target_obj["size"] + size_change, 0.02, 0.2)

        elif change_type == "appearance":
            # Add new object
            new_obj = {
                "id": f"new_obj_{random.randint(1000, 9999)}",
                "type": random.choice(["circle", "square", "triangle"]),
                "x": random.uniform(0.1, 0.9),
                "y": random.uniform(0.1, 0.9),
                "size": random.uniform(0.05, 0.15),
                "color": random.choice(["red", "blue", "green", "yellow", "purple"]),
            }
            changed_scene["objects"].append(new_obj)

        elif change_type == "disappearance":
            # Remove object (but not the target if it's being tracked)
            if len(changed_scene["objects"]) > 3:
                removable_objects = [
                    obj for obj in changed_scene["objects"] if obj != target_obj
                ]
                if removable_objects:
                    obj_to_remove = random.choice(removable_objects)
                    changed_scene["objects"].remove(obj_to_remove)

        return original_scene, changed_scene, target_obj["id"]


class ChangeBlindnessTask(TrialBasedTask):
    """Change Blindness task implementation."""

    def __init__(self, config: Optional[ChangeBlindnessConfig] = None):
        super().__init__(config)
        self.config = config or ChangeBlindnessConfig()
        self.scene_generator = SceneGenerator(self.config)
        self.performance_by_condition = {}

    def setup(self, **kwargs):
        """Set up the change blindness task."""
        super().setup(**kwargs)
        self.scene_generator = SceneGenerator(self.config)
        self.performance_by_condition = {}

    def generate_trial_sequence(self) -> List[Dict[str, Any]]:
        """Generate balanced trial sequence."""
        trials = []

        # Create all condition combinations
        all_conditions = []
        for change_type in self.config.change_types:
            for change_size in self.config.change_sizes:
                for change_location in self.config.change_locations:
                    all_conditions.append(
                        {
                            "change_type": change_type,
                            "change_size": change_size,
                            "change_location": change_location,
                            "condition": f"{change_type}_{change_size}_{change_location}",
                        }
                    )

        # Balance trials across conditions
        trials_per_condition = self.config.n_trials // len(all_conditions)

        for condition in all_conditions:
            for _ in range(trials_per_condition):
                trials.append(condition.copy())

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
                "change_type": "color",
                "change_size": "medium",
                "change_location": "central",
                "condition": "color_medium_central",
            }

        # Generate scene pair
        original_scene, changed_scene, changed_object_id = (
            self.scene_generator.create_scene_pair(
                trial_config["change_type"],
                trial_config["change_size"],
                trial_config["change_location"],
            )
        )

        base_params.update(
            {
                "original_scene": original_scene,
                "changed_scene": changed_scene,
                "changed_object_id": changed_object_id,
                "change_type": trial_config["change_type"],
                "change_size": trial_config["change_size"],
                "change_location": trial_config["change_location"],
                "condition": trial_config["condition"],
                "image_duration_ms": self.config.image_duration_ms,
                "blank_duration_ms": self.config.blank_duration_ms,
                "max_alternations": self.config.max_alternations,
            }
        )

        return base_params

    def process_response(
        self, response: Any, correct_response: Any, trial_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Process change blindness response."""
        # Response should be whether change was detected
        if isinstance(response, (bool, int)):
            detected_change = bool(response)
        elif isinstance(response, str):
            detected_change = response.lower() in ["true", "yes", "change", "1"]
        else:
            detected_change = bool(response)

        is_correct = detected_change == correct_response

        # Store performance by condition
        condition = "unknown"
        if trial_data:
            condition = trial_data.get("condition", "unknown")

        # Calculate confidence based on accuracy
        confidence = 0.8 if is_correct else 0.4

        # Simulate alternations used (more alternations for harder trials)
        if trial_data and trial_data.get("change_size") == "small":
            alternations_used = random.randint(3, 8)
        else:
            alternations_used = random.randint(1, 4)

        if condition not in self.performance_by_condition:
            self.performance_by_condition[condition] = []

        self.performance_by_condition[condition].append(
            {
                "detected_change": detected_change,
                "is_correct": is_correct,
                "correct": is_correct,  # Add 'correct' key for compatibility
                "alternations_used": alternations_used,  # Add alternations_used
            }
        )

        return {
            "response": detected_change,
            "accuracy": 1 if is_correct else 0,
            "reaction_time_ms": alternations_used
            * (self.config.image_duration_ms + self.config.blank_duration_ms),
            "confidence": confidence,
            "alternations_used": alternations_used,
            "change_type": trial_data.get("change_type") if trial_data else "color",
            "change_size": trial_data.get("change_size") if trial_data else "large",
            "change_location": (
                trial_data.get("change_location") if trial_data else "center"
            ),
            "condition": condition,
        }

    def simulate_response(self, trial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate participant change detection."""
        change_type = trial_data["change_type"]
        change_size = trial_data["change_size"]
        change_location = trial_data["change_location"]
        correct_object_id = trial_data["changed_object_id"]

        # Simulate detection difficulty based on change parameters
        base_detection_prob = 0.7

        # Adjust for change type
        type_modifiers = {
            "color": 0.9,  # Easy to detect
            "position": 0.6,  # Medium difficulty
            "size": 0.5,  # Harder
            "appearance": 0.8,  # Easy
            "disappearance": 0.4,  # Hardest
        }
        base_detection_prob *= type_modifiers.get(change_type, 0.7)

        # Adjust for change size
        size_modifiers = {"small": 0.6, "medium": 0.8, "large": 1.0}
        base_detection_prob *= size_modifiers.get(change_size, 0.8)

        # Adjust for change location
        location_modifiers = {"central": 1.0, "peripheral": 0.7}
        base_detection_prob *= location_modifiers.get(change_location, 0.85)

        # Determine if change is detected
        detected = random.random() < base_detection_prob

        if detected:
            # Sometimes make errors even when detected
            if random.random() < 0.85:
                response_object_id = correct_object_id
            else:
                # Wrong object response
                scene_objects = trial_data["changed_scene"]["objects"]
                other_objects = [
                    obj["id"] for obj in scene_objects if obj["id"] != correct_object_id
                ]
                response_object_id = (
                    random.choice(other_objects) if other_objects else "none"
                )

            # Faster detection for easier changes
            base_alternations = 3 if base_detection_prob > 0.8 else 8
        else:
            # No detection - random guess or timeout
            scene_objects = trial_data["changed_scene"]["objects"]
            response_object_id = (
                random.choice([obj["id"] for obj in scene_objects])
                if scene_objects
                else "none"
            )
            base_alternations = self.config.max_alternations

        alternations_used = max(1, int(np.random.normal(base_alternations, 2)))
        alternations_used = min(alternations_used, self.config.max_alternations)

        return {
            "response": response_object_id,
            "reaction_time_ms": alternations_used
            * (self.config.image_duration_ms + self.config.blank_duration_ms),
            "confidence": 0.8 if detected else 0.3,
            "timestamp": time.time(),
        }

    def compute_participant_summary(
        self, trials: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compute comprehensive summary for change blindness task."""
        base_summary = super().compute_participant_summary(trials)

        if not trials:
            return base_summary

        df = pd.DataFrame(trials)

        # Change blindness specific metrics
        summary = {
            **base_summary,
            "overall_detection_rate": 0,
            "mean_alternations_to_detection": 0,
            "performance_by_change_type": {},
            "performance_by_change_size": {},
            "performance_by_change_location": {},
            "condition_performance": {},
        }

        # Overall detection rate
        if "accuracy" in df.columns:
            summary["overall_detection_rate"] = df["accuracy"].mean()

        # Mean alternations
        if "alternations_used" in df.columns:
            summary["mean_alternations_to_detection"] = df["alternations_used"].mean()

        # Performance by change type
        if "change_type" in df.columns:
            for change_type in df["change_type"].unique():
                type_trials = df[df["change_type"] == change_type]
                if len(type_trials) > 0:
                    detection_rate = (
                        type_trials["accuracy"].mean()
                        if "accuracy" in type_trials.columns
                        else 0
                    )
                    mean_alternations = (
                        type_trials["alternations_used"].mean()
                        if "alternations_used" in type_trials.columns
                        else 0
                    )

                    summary["performance_by_change_type"][change_type] = {
                        "detection_rate": detection_rate,
                        "mean_alternations": mean_alternations,
                        "n_trials": len(type_trials),
                    }

        # Performance by change size
        if "change_size" in df.columns:
            for change_size in df["change_size"].unique():
                size_trials = df[df["change_size"] == change_size]
                if len(size_trials) > 0:
                    detection_rate = (
                        size_trials["accuracy"].mean()
                        if "accuracy" in size_trials.columns
                        else 0
                    )
                    mean_alternations = (
                        size_trials["alternations_used"].mean()
                        if "alternations_used" in size_trials.columns
                        else 0
                    )

                    summary["performance_by_change_size"][change_size] = {
                        "detection_rate": detection_rate,
                        "mean_alternations": mean_alternations,
                        "n_trials": len(size_trials),
                    }

        # Performance by change location
        if "change_location" in df.columns:
            for change_location in df["change_location"].unique():
                location_trials = df[df["change_location"] == change_location]
                if len(location_trials) > 0:
                    detection_rate = (
                        location_trials["accuracy"].mean()
                        if "accuracy" in location_trials.columns
                        else 0
                    )
                    mean_alternations = (
                        location_trials["alternations_used"].mean()
                        if "alternations_used" in location_trials.columns
                        else 0
                    )

                    summary["performance_by_change_location"][change_location] = {
                        "detection_rate": detection_rate,
                        "mean_alternations": mean_alternations,
                        "n_trials": len(location_trials),
                    }

        # Detailed condition performance
        for condition, performances in self.performance_by_condition.items():
            if performances:
                detection_rate = sum(p["correct"] for p in performances) / len(
                    performances
                )
                mean_alternations = sum(
                    p["alternations_used"] for p in performances
                ) / len(performances)

                summary["condition_performance"][condition] = {
                    "detection_rate": detection_rate,
                    "mean_alternations": mean_alternations,
                    "n_trials": len(performances),
                }

        return summary


def run_change_blindness_experiment(**kwargs):
    """Run the Change Blindness experiment."""
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
        if hasattr(ChangeBlindnessConfig, config_key):
            config_params[config_key] = value

    # Create config and experiment
    config = ChangeBlindnessConfig(**config_params)
    experiment = ChangeBlindnessTask(config)

    # Set up and run experiment
    experiment.setup()
    results = experiment.run_experiment()

    # Save results if output file specified
    if kwargs.get("output_file"):
        experiment.save_data(kwargs["output_file"])

    return experiment


if __name__ == "__main__":
    # Example usage
    config = ChangeBlindnessConfig(
        n_trials=60,
        n_participants=5,
        change_types=["color", "position", "size"],
        change_sizes=["small", "medium", "large"],
    )

    experiment = ChangeBlindnessTask(config)
    experiment.setup()
    results = experiment.run_experiment()

    print("Change Blindness experiment completed!")
    print(f"Results shape: {results.shape}")

    # Print summary for first participant
    if experiment.participant_data:
        first_participant = list(experiment.participant_data.keys())[0]
        summary = experiment.participant_data[first_participant]["summary"]
        print(f"\nParticipant {first_participant} Summary:")
        print(f"Overall Detection Rate: {summary.get('overall_detection_rate', 0):.3f}")
        print(
            f"Mean Alternations to Detection: {summary.get('mean_alternations_to_detection', 0):.1f}"
        )
        print(
            f"Performance by Change Type: {summary.get('performance_by_change_type', {})}"
        )
