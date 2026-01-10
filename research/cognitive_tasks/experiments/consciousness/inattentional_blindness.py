"""
Inattentional Blindness implementation.

Inattentional blindness occurs when observers fail to perceive unexpected stimuli
when their attention is engaged in a demanding primary task. This experiment
demonstrates the limits of conscious attention and awareness.

APGI Integration:
- θₜ (threshold): Attentional threshold for detecting unexpected stimuli
- π (precision): Precision allocated to primary vs. unexpected stimuli
- ε (prediction error): Prediction error from unexpected stimulus appearance
- β (inverse temperature): Trade-off between task focus and novelty detection
"""

import random
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import time

from .. import TrialBasedTask, TrialBasedTaskConfig


@dataclass
class InattentionalBlindnessConfig(TrialBasedTaskConfig):
    """Configuration for Inattentional Blindness experiment."""

    n_trials: int = 60
    primary_task_duration_ms: int = 30000  # 30 seconds per trial
    unexpected_stimulus_probability: float = (
        0.3  # 30% of trials have unexpected stimulus
    )
    unexpected_stimulus_types: List[str] = None
    primary_task_difficulty: str = "medium"  # 'easy', 'medium', 'hard'

    def __post_init__(self):
        if self.unexpected_stimulus_types is None:
            self.unexpected_stimulus_types = [
                "crossing_person",
                "color_change",
                "shape_morph",
                "text_appear",
            ]


class StimulusGenerator:
    """Generate inattentional blindness stimuli."""

    def __init__(self, config: InattentionalBlindnessConfig):
        self.config = config
        self.primary_task_elements = self._create_primary_task_elements()
        self.unexpected_stimuli = self._create_unexpected_stimuli()

    def _create_primary_task_elements(self) -> Dict[str, List]:
        """Create elements for the primary attention task."""
        return {
            "moving_objects": ["circle", "square", "triangle", "pentagon", "hexagon"],
            "colors": ["red", "blue", "green", "yellow", "purple"],
            "directions": ["up", "down", "left", "right", "diagonal"],
        }

    def _create_unexpected_stimuli(self) -> Dict[str, Dict]:
        """Create unexpected stimuli."""
        return {
            "crossing_person": {
                "description": "Person walking across the screen",
                "duration_ms": 2000,
                "salience": 0.8,
                "category": "biological_motion",
            },
            "color_change": {
                "description": "Sudden color change of background",
                "duration_ms": 500,
                "salience": 0.6,
                "category": "visual_change",
            },
            "shape_morph": {
                "description": "Object gradually changing shape",
                "duration_ms": 3000,
                "salience": 0.7,
                "category": "geometric_change",
            },
            "text_appear": {
                "description": "Unexpected text appearing",
                "duration_ms": 1500,
                "salience": 0.5,
                "category": "semantic_stimulus",
            },
        }

    def generate_primary_task(self, difficulty: str) -> Dict[str, Any]:
        """Generate primary task parameters."""
        if difficulty == "easy":
            n_objects = 3
            speed_variation = 0.2
        elif difficulty == "medium":
            n_objects = 5
            speed_variation = 0.4
        else:  # hard
            n_objects = 8
            speed_variation = 0.6

        objects = []
        for i in range(n_objects):
            obj = {
                "id": i,
                "shape": random.choice(self.primary_task_elements["moving_objects"]),
                "color": random.choice(self.primary_task_elements["colors"]),
                "direction": random.choice(self.primary_task_elements["directions"]),
                "speed": np.random.uniform(1.0, 3.0)
                * (1 + speed_variation * np.random.randn()),
                "size": np.random.uniform(20, 50),
            }
            objects.append(obj)

        return {
            "objects": objects,
            "difficulty": difficulty,
            "task_type": "tracking",
            "target_object": random.choice(objects) if n_objects > 0 else None,
        }

    def generate_unexpected_stimulus(self) -> Optional[Dict[str, Any]]:
        """Generate an unexpected stimulus."""
        stimulus_type = random.choice(self.config.unexpected_stimulus_types)
        stimulus_config = self.unexpected_stimuli[stimulus_type]

        return {
            "type": stimulus_type,
            "description": stimulus_config["description"],
            "duration_ms": stimulus_config["duration_ms"],
            "salience": stimulus_config["salience"],
            "category": stimulus_config["category"],
            "appearance_time": np.random.uniform(
                5000, 25000
            ),  # Appears between 5-25 seconds
            "position": {
                "x": np.random.uniform(0.1, 0.9),
                "y": np.random.uniform(0.1, 0.9),
            },
        }


class InattentionalBlindnessTask(TrialBasedTask):
    """Inattentional Blindness task implementation."""

    def __init__(self, config: Optional[InattentionalBlindnessConfig] = None):
        super().__init__(config)
        self.config = config or InattentionalBlindnessConfig()
        self.stimulus_generator = StimulusGenerator(self.config)
        self.detection_rates = {}
        self.attentional_load_scores = []

    def setup(self, **kwargs):
        """Set up the inattentional blindness task."""
        super().setup(**kwargs)
        self.stimulus_generator = StimulusGenerator(self.config)
        self.detection_rates = {}
        self.attentional_load_scores = []

    def generate_trial_sequence(self) -> List[Dict[str, Any]]:
        """Generate trial sequence with and without unexpected stimuli."""
        trials = []

        for trial in range(self.config.n_trials):
            # Determine if this trial has an unexpected stimulus
            has_unexpected = (
                random.random() < self.config.unexpected_stimulus_probability
            )

            # Generate primary task
            primary_task = self.stimulus_generator.generate_primary_task(
                self.config.primary_task_difficulty
            )

            trial_data = {
                "primary_task": primary_task,
                "has_unexpected": has_unexpected,
                "trial_duration_ms": self.config.primary_task_duration_ms,
                "difficulty": self.config.primary_task_difficulty,
                "condition": f"{self.config.primary_task_difficulty}_{'with' if has_unexpected else 'without'}_unexpected",
            }

            # Add unexpected stimulus if applicable
            if has_unexpected:
                unexpected_stimulus = (
                    self.stimulus_generator.generate_unexpected_stimulus()
                )
                trial_data["unexpected_stimulus"] = unexpected_stimulus
            else:
                trial_data["unexpected_stimulus"] = None

            trials.append(trial_data)

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
            primary_task = self.stimulus_generator.generate_primary_task(
                self.config.primary_task_difficulty
            )
            trial_config = {
                "primary_task": primary_task,
                "has_unexpected": False,
                "unexpected_stimulus": None,
                "trial_duration_ms": self.config.primary_task_duration_ms,
                "difficulty": self.config.primary_task_difficulty,
                "condition": f"{self.config.primary_task_difficulty}_without_unexpected",
            }

        # Add trial-specific parameters
        base_params.update(
            {
                "primary_task_objects": trial_config["primary_task"]["objects"],
                "target_object": trial_config["primary_task"]["target_object"],
                "task_difficulty": trial_config["difficulty"],
                "has_unexpected": trial_config["has_unexpected"],
                "unexpected_stimulus": trial_config["unexpected_stimulus"],
                "trial_duration_ms": trial_config["trial_duration_ms"],
                "condition": trial_config["condition"],
            }
        )

        return base_params

    def process_response(
        self, response: Any, correct_response: Any, trial_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Process inattentional blindness response."""
        # Response should include primary task performance and unexpected stimulus detection
        if isinstance(response, dict):
            primary_task_performance = response.get("primary_task_performance", {})
            unexpected_detected = response.get("unexpected_detected", False)
            unexpected_identified = response.get("unexpected_identified", None)
        else:
            # Default response
            primary_task_performance = {"accuracy": 0.5, "reaction_time_ms": 1000}
            unexpected_detected = False
            unexpected_identified = None

        # Get trial parameters or use defaults
        has_unexpected = False
        task_difficulty = "medium"
        unexpected_stimulus = None

        if trial_data:
            has_unexpected = trial_data.get("has_unexpected", False)
            task_difficulty = trial_data.get("task_difficulty", "medium")
            unexpected_stimulus = trial_data.get("unexpected_stimulus")

        # Calculate primary task accuracy
        primary_accuracy = primary_task_performance.get("accuracy", 0.5)

        # Calculate detection accuracy
        detection_accuracy = 0
        if has_unexpected:
            # Correct if detected
            detection_accuracy = 1 if unexpected_detected else 0
        else:
            # Correct if not falsely detected
            detection_accuracy = 1 if not unexpected_detected else 0

        # Store detection rates by stimulus type
        if has_unexpected and unexpected_stimulus:
            stimulus_type = unexpected_stimulus.get("type", "unknown")
            if stimulus_type not in self.detection_rates:
                self.detection_rates[stimulus_type] = {"detected": 0, "total": 0}

            self.detection_rates[stimulus_type]["total"] += 1
            if unexpected_detected:
                self.detection_rates[stimulus_type]["detected"] += 1

        # Store attentional load (inverse of primary task performance)
        attentional_load = 1.0 - primary_accuracy
        self.attentional_load_scores.append(attentional_load)

        # Calculate confidence based on task performance
        base_confidence = 0.6 + (primary_accuracy * 0.3)
        if has_unexpected and unexpected_detected:
            base_confidence += 0.1  # Bonus for detecting unexpected stimulus

        return {
            "response": response,
            "primary_accuracy": primary_accuracy,
            "detection_accuracy": detection_accuracy,
            "overall_accuracy": (primary_accuracy + detection_accuracy) / 2,
            "unexpected_detected": unexpected_detected,
            "unexpected_identified": unexpected_identified,
            "reaction_time_ms": primary_task_performance.get("reaction_time_ms", 1000),
            "confidence": base_confidence,
            "task_difficulty": task_difficulty,
            "has_unexpected": has_unexpected,
            "unexpected_stimulus_type": (
                unexpected_stimulus.get("type") if unexpected_stimulus else None
            ),
            "attentional_load": attentional_load,
            "condition": (
                trial_data.get("condition", "unknown") if trial_data else "unknown"
            ),
        }

    def simulate_response(self, trial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate participant inattentional blindness performance."""
        has_unexpected = trial_data["has_unexpected"]
        task_difficulty = trial_data["task_difficulty"]
        unexpected_stimulus = trial_data["unexpected_stimulus"]

        # Primary task performance depends on difficulty
        if task_difficulty == "easy":
            primary_accuracy = 0.9
            primary_rt = 800
        elif task_difficulty == "medium":
            primary_accuracy = 0.75
            primary_rt = 1000
        else:  # hard
            primary_accuracy = 0.6
            primary_rt = 1200

        # Add some variability
        primary_accuracy += np.random.normal(0, 0.1)
        primary_accuracy = np.clip(primary_accuracy, 0, 1)
        primary_rt += np.random.normal(0, 200)
        primary_rt = max(300, primary_rt)

        # Unexpected stimulus detection depends on attentional load
        attentional_load = 1.0 - primary_accuracy

        if has_unexpected and unexpected_stimulus:
            # Detection probability decreases with attentional load
            salience = unexpected_stimulus.get("salience", 0.5)
            detection_prob = salience * (1 - attentional_load)

            unexpected_detected = random.random() < detection_prob

            if unexpected_detected:
                # Sometimes identify correctly, sometimes not
                unexpected_identified = (
                    unexpected_stimulus.get("type")
                    if random.random() < 0.7
                    else "unknown"
                )
            else:
                unexpected_identified = None
        else:
            unexpected_detected = False
            unexpected_identified = None

        return {
            "primary_task_performance": {
                "accuracy": primary_accuracy,
                "reaction_time_ms": int(primary_rt),
            },
            "unexpected_detected": unexpected_detected,
            "unexpected_identified": unexpected_identified,
            "confidence": 0.6 + primary_accuracy * 0.2,
            "timestamp": time.time(),
        }

    def compute_participant_summary(
        self, trials: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compute comprehensive summary for inattentional blindness task."""
        base_summary = super().compute_participant_summary(trials)

        if not trials:
            return base_summary

        df = pd.DataFrame(trials)

        # Inattentional blindness specific metrics
        summary = {
            **base_summary,
            "overall_detection_rate": 0,
            "detection_by_stimulus_type": {},
            "inattentional_blindness_rate": 0,
            "attentional_load_mean": 0,
            "primary_task_accuracy": 0,
            "difficulty_effects": {},
        }

        # Calculate overall detection rate
        unexpected_trials = df[df["has_unexpected"] == True]
        if len(unexpected_trials) > 0:
            summary["overall_detection_rate"] = unexpected_trials[
                "detection_accuracy"
            ].mean()
            summary["inattentional_blindness_rate"] = (
                1 - summary["overall_detection_rate"]
            )

        # Detection by stimulus type
        for stimulus_type, data in self.detection_rates.items():
            if data["total"] > 0:
                summary["detection_by_stimulus_type"][stimulus_type] = {
                    "detection_rate": data["detected"] / data["total"],
                    "n_trials": data["total"],
                }

        # Attentional load
        if "attentional_load" in df.columns:
            summary["attentional_load_mean"] = df["attentional_load"].mean()

        # Primary task accuracy
        if "primary_accuracy" in df.columns:
            summary["primary_task_accuracy"] = df["primary_accuracy"].mean()

        # Effects of difficulty
        if "task_difficulty" in df.columns:
            for difficulty in df["task_difficulty"].unique():
                difficulty_data = df[df["task_difficulty"] == difficulty]
                summary["difficulty_effects"][difficulty] = {
                    "primary_accuracy": (
                        difficulty_data["primary_accuracy"].mean()
                        if "primary_accuracy" in difficulty_data.columns
                        else 0
                    ),
                    "detection_rate": (
                        difficulty_data["detection_accuracy"].mean()
                        if "detection_accuracy" in difficulty_data.columns
                        else 0
                    ),
                    "attentional_load": (
                        difficulty_data["attentional_load"].mean()
                        if "attentional_load" in difficulty_data.columns
                        else 0
                    ),
                    "n_trials": len(difficulty_data),
                }

        return summary


def run_inattentional_blindness_experiment(**kwargs):
    """Run the Inattentional Blindness experiment."""
    # Create config with provided parameters
    config_params = {}

    # Map common parameters
    param_mapping = {
        "n_participants": "n_participants",
        "n_trials": "n_trials",
        "primary_task_duration_ms": "primary_task_duration_ms",
        "unexpected_stimulus_probability": "unexpected_stimulus_probability",
        "primary_task_difficulty": "primary_task_difficulty",
    }

    for key, value in kwargs.items():
        if key in param_mapping:
            config_params[param_mapping[key]] = value

    # Create experiment
    config = InattentionalBlindnessConfig(**config_params)
    experiment = InattentionalBlindnessTask(config)

    # Run experiment
    results = experiment.run_experiment(**kwargs)

    return experiment
