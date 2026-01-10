"""
Binocular Rivalry implementation.

Binocular rivalry is a phenomenon where perception alternates between different
stimuli presented to each eye. This provides insights into conscious access
and neural competition mechanisms.

APGI Integration:
- θₜ (threshold): Conscious access threshold for perceptual switching
- π (precision): Precision of sensory evidence accumulation
- ε (prediction error): Prediction error from unexpected perceptual switches
- β (inverse temperature): Determinism of perceptual selection
"""

import random
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import time

from .. import TrialBasedTask, TrialBasedTaskConfig


@dataclass
class BinocularRivalryConfig(TrialBasedTaskConfig):
    """Configuration for Binocular Rivalry experiment."""

    n_trials: int = 120
    trial_duration_ms: int = 30000  # 30 seconds per rivalry block
    rivalry_stimuli: Dict[str, Dict] = (
        None  # {stimulus_id: {eye: 'left'/'right', pattern: str}}
    )
    switch_detection_threshold: float = (
        0.3  # Threshold for detecting perceptual switches
    )

    def __post_init__(self):
        if self.rivalry_stimuli is None:
            # Default rivalry stimuli (gratings vs. face)
            self.rivalry_stimuli = {
                "grating": {
                    "left_eye": "horizontal_grating",
                    "right_eye": "vertical_grating",
                    "description": "Orientation rivalry",
                },
                "face_house": {
                    "left_eye": "face",
                    "right_eye": "house",
                    "description": "Object rivalry",
                },
            }


class StimulusGenerator:
    """Generate binocular rivalry stimuli."""

    def __init__(self, config: BinocularRivalryConfig):
        self.config = config
        self.rivalry_pairs = list(config.rivalry_stimuli.keys())

    def generate_rivalry_stimulus(self, stimulus_type: str) -> Dict[str, Any]:
        """Generate a rivalry stimulus pair."""
        if stimulus_type not in self.config.rivalry_stimuli:
            stimulus_type = random.choice(self.rivalry_pairs)

        stimulus_config = self.config.rivalry_stimuli[stimulus_type]

        return {
            "stimulus_type": stimulus_type,
            "left_eye_stimulus": stimulus_config["left_eye"],
            "right_eye_stimulus": stimulus_config["right_eye"],
            "description": stimulus_config["description"],
            "initial_dominance": random.choice(["left", "right"]),
            "switch_rate": np.random.beta(2, 2),  # Random switch rate between 0-1
            "contrast": np.random.uniform(0.5, 1.0),
        }


class BinocularRivalryTask(TrialBasedTask):
    """Binocular Rivalry task implementation."""

    def __init__(self, config: Optional[BinocularRivalryConfig] = None):
        super().__init__(config)
        self.config = config or BinocularRivalryConfig()
        self.stimulus_generator = StimulusGenerator(self.config)
        self.rivalry_dynamics = {}
        self.switch_times = []

    def setup(self, **kwargs):
        """Set up the binocular rivalry task."""
        super().setup(**kwargs)
        self.stimulus_generator = StimulusGenerator(self.config)
        self.rivalry_dynamics = {}
        self.switch_times = []

    def generate_trial_sequence(self) -> List[Dict[str, Any]]:
        """Generate trial sequence with different rivalry conditions."""
        trials = []

        # Balance different rivalry types
        rivalry_types = list(self.config.rivalry_stimuli.keys())
        trials_per_type = self.config.n_trials // len(rivalry_types)

        for rivalry_type in rivalry_types:
            for _ in range(trials_per_type):
                stimulus = self.stimulus_generator.generate_rivalry_stimulus(
                    rivalry_type
                )

                trials.append(
                    {
                        "stimulus_type": rivalry_type,
                        "stimulus": stimulus,
                        "condition": f"{rivalry_type}_rivalry",
                        "trial_duration_ms": self.config.trial_duration_ms,
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
            stimulus = self.stimulus_generator.generate_rivalry_stimulus("grating")
            trial_config = {
                "stimulus_type": "grating",
                "stimulus": stimulus,
                "condition": "grating_rivalry",
                "trial_duration_ms": self.config.trial_duration_ms,
            }

        # Add rivalry-specific parameters
        base_params.update(
            {
                "left_eye_stimulus": trial_config["stimulus"]["left_eye_stimulus"],
                "right_eye_stimulus": trial_config["stimulus"]["right_eye_stimulus"],
                "stimulus_description": trial_config["stimulus"]["description"],
                "initial_dominance": trial_config["stimulus"]["initial_dominance"],
                "switch_rate": trial_config["stimulus"]["switch_rate"],
                "contrast": trial_config["stimulus"]["contrast"],
                "trial_duration_ms": trial_config["trial_duration_ms"],
                "condition": trial_config["condition"],
            }
        )

        return base_params

    def process_response(
        self, response: Any, correct_response: Any, trial_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Process binocular rivalry response."""
        # Response should be the dominant percept over time
        if isinstance(response, dict):
            dominant_percepts = response.get("percepts", [])
            switch_times = response.get("switch_times", [])
        elif isinstance(response, list):
            dominant_percepts = response
            switch_times = []
        else:
            # Default response
            dominant_percepts = ["left"]  # Default to left eye dominance
            switch_times = []

        # Get trial parameters or use defaults
        stimulus_type = "grating"
        switch_rate = 0.5
        contrast = 0.8

        if trial_data:
            stimulus_type = trial_data.get("stimulus_type", "grating")
            switch_rate = trial_data.get("switch_rate", 0.5)
            contrast = trial_data.get("contrast", 0.8)

        # Store rivalry dynamics
        if stimulus_type not in self.rivalry_dynamics:
            self.rivalry_dynamics[stimulus_type] = {
                "dominance_durations": [],
                "switch_rates": [],
                "contrast_effects": [],
            }

        # Calculate dominance durations (simplified)
        if len(dominant_percepts) > 1:
            # Simulate dominance duration based on switch rate
            avg_dominance_duration = (1.0 / (switch_rate + 0.1)) * 1000  # Convert to ms
            self.rivalry_dynamics[stimulus_type]["dominance_durations"].append(
                avg_dominance_duration
            )

        self.rivalry_dynamics[stimulus_type]["switch_rates"].append(switch_rate)
        self.rivalry_dynamics[stimulus_type]["contrast_effects"].append(contrast)

        # Calculate confidence based on response consistency
        base_confidence = 0.7
        if len(dominant_percepts) > 0:
            consistency = len(set(dominant_percepts)) / len(dominant_percepts)
            base_confidence *= (
                1.0 - consistency * 0.3
            )  # Higher confidence for consistent responses

        return {
            "response": response,
            "dominant_percepts": dominant_percepts,
            "switch_times": switch_times,
            "accuracy": 1,  # Rivalry tasks don't have right/wrong answers
            "reaction_time_ms": 0,  # Continuous task, no single RT
            "confidence": base_confidence,
            "stimulus_type": stimulus_type,
            "switch_rate": switch_rate,
            "contrast": contrast,
            "avg_dominance_duration": (
                avg_dominance_duration if len(dominant_percepts) > 1 else 0
            ),
            "condition": (
                trial_data.get("condition", "unknown") if trial_data else "unknown"
            ),
        }

    def simulate_response(self, trial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate participant rivalry perception."""
        stimulus_type = trial_data.get("stimulus_type", "grating")
        initial_dominance = trial_data.get("initial_dominance", "left")
        switch_rate = trial_data.get("switch_rate", 0.5)
        trial_duration = trial_data.get("trial_duration_ms", 30000)

        # Simulate perceptual switches over time
        percepts = []
        switch_times = []

        current_percept = initial_dominance
        percepts.append(current_percept)

        # Generate switches based on switch rate
        elapsed_time = 0
        while elapsed_time < trial_duration:
            # Time until next switch (exponential distribution)
            mean_switch_time = (1.0 / (switch_rate + 0.1)) * 1000  # ms
            next_switch_time = np.random.exponential(mean_switch_time)

            elapsed_time += next_switch_time
            if elapsed_time < trial_duration:
                # Switch perception
                current_percept = "right" if current_percept == "left" else "left"
                percepts.append(current_percept)
                switch_times.append(elapsed_time)

        # Add some noise to make it realistic
        if random.random() < 0.1:  # 10% chance of mixed perception
            percepts.append("mixed")

        return {
            "percepts": percepts,
            "switch_times": switch_times,
            "reaction_time_ms": trial_duration,  # Total trial duration
            "confidence": 0.6 + random.uniform(0, 0.3),
            "timestamp": time.time(),
        }

    def compute_participant_summary(
        self, trials: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compute comprehensive summary for binocular rivalry task."""
        base_summary = super().compute_participant_summary(trials)

        if not trials:
            return base_summary

        df = pd.DataFrame(trials)

        # Binocular rivalry specific metrics
        summary = {
            **base_summary,
            "mean_switch_rate": 0,
            "mean_dominance_duration": 0,
            "rivalry_types_tested": [],
            "switch_rate_by_stimulus": {},
            "dominance_bias": {},
            "contrast_sensitivity": 0,
        }

        # Calculate switch rate statistics
        if "switch_rate" in df.columns:
            summary["mean_switch_rate"] = df["switch_rate"].mean()

        # Calculate dominance duration
        if "avg_dominance_duration" in df.columns:
            summary["mean_dominance_duration"] = df["avg_dominance_duration"].mean()

        # Stimulus-specific analysis
        if "stimulus_type" in df.columns:
            summary["rivalry_types_tested"] = df["stimulus_type"].unique().tolist()

            for stimulus_type in df["stimulus_type"].unique():
                stimulus_data = df[df["stimulus_type"] == stimulus_type]
                summary["switch_rate_by_stimulus"][stimulus_type] = {
                    "mean_switch_rate": (
                        stimulus_data["switch_rate"].mean()
                        if "switch_rate" in stimulus_data.columns
                        else 0
                    ),
                    "mean_dominance_duration": (
                        stimulus_data["avg_dominance_duration"].mean()
                        if "avg_dominance_duration" in stimulus_data.columns
                        else 0
                    ),
                    "n_trials": len(stimulus_data),
                }

        # Dominance bias (which eye dominates more)
        if "dominant_percepts" in df.columns:
            left_dominance = 0
            right_dominance = 0
            total_percepts = 0

            for percepts in df["dominant_percepts"]:
                if isinstance(percepts, list):
                    for percept in percepts:
                        if percept == "left":
                            left_dominance += 1
                        elif percept == "right":
                            right_dominance += 1
                        total_percepts += 1

            if total_percepts > 0:
                summary["dominance_bias"] = {
                    "left_dominance_ratio": left_dominance / total_percepts,
                    "right_dominance_ratio": right_dominance / total_percepts,
                }

        return summary


def run_binocular_rivalry_experiment(**kwargs):
    """Run the Binocular Rivalry experiment."""
    # Create config with provided parameters
    config_params = {}

    # Map common parameters
    param_mapping = {
        "n_participants": "n_participants",
        "n_trials": "n_trials",
        "trial_duration_ms": "trial_duration_ms",
    }

    for key, value in kwargs.items():
        if key in param_mapping:
            config_params[param_mapping[key]] = value

    # Create experiment
    config = BinocularRivalryConfig(**config_params)
    experiment = BinocularRivalryTask(config)

    # Run experiment
    results = experiment.run_experiment(**kwargs)

    return experiment
