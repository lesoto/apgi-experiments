"""
Masking implementation.

Visual masking is a phenomenon where the visibility of one stimulus (the target)
is reduced by the presence of another stimulus (the mask). This is used to study
conscious perception and the neural correlates of consciousness.

APGI Integration:
- θₜ (threshold): Conscious perception threshold
- π (precision): Temporal precision of conscious processing
- ε (prediction error): Masking-induced prediction error
- β (inverse temperature): Confidence in conscious perception
"""

import random
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import time

from .. import TrialBasedTask, TrialBasedTaskConfig


@dataclass
class MaskingConfig(TrialBasedTaskConfig):
    """Configuration for Masking experiment."""

    n_trials: int = 160
    target_duration_ms: int = 20  # Very brief target presentation
    mask_duration_ms: int = 100
    response_window_ms: int = 2000
    inter_trial_interval_ms: int = 1500

    # Masking parameters
    stimulus_onset_asynchronies: List[int] = None  # SOAs between target and mask
    mask_types: List[str] = None  # forward, backward, sandwich
    target_types: List[str] = None  # letters, shapes, patterns

    # Stimulus parameters
    target_stimuli: List[str] = None  # Target stimuli to identify
    mask_patterns: List[str] = None  # Mask patterns
    stimulus_size: float = 2.0  # degrees of visual angle

    def __post_init__(self):
        if self.stimulus_onset_asynchronies is None:
            self.stimulus_onset_asynchronies = [0, 20, 40, 80, 120]  # ms

        if self.mask_types is None:
            self.mask_types = ["forward", "backward", "sandwich"]

        if self.target_types is None:
            self.target_types = ["letters"]

        if self.target_stimuli is None:
            self.target_stimuli = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")[
                :10
            ]  # First 10 letters

        if self.mask_patterns is None:
            self.mask_patterns = ["random_noise", "scrambled", "pattern_mask"]


class MaskingStimulus:
    """Generate masking stimuli."""

    def __init__(self, config: MaskingConfig):
        self.config = config
        self.mask_generators = {
            "random_noise": self._generate_noise_mask,
            "scrambled": self._generate_scrambled_mask,
            "pattern_mask": self._generate_pattern_mask,
        }

    def _generate_noise_mask(self, target_stimulus: str) -> str:
        """Generate random noise mask."""
        # Create random pattern of same length as target
        noise_chars = ["@", "#", "$", "%", "&", "*", "+", "=", "?", "!"]
        return "".join(random.choice(noise_chars) for _ in range(len(target_stimulus)))

    def _generate_scrambled_mask(self, target_stimulus: str) -> str:
        """Generate scrambled version of target."""
        chars = list(target_stimulus)
        random.shuffle(chars)
        return "".join(chars)

    def _generate_pattern_mask(self, target_stimulus: str) -> str:
        """Generate pattern mask."""
        patterns = ["||||||||", "########", "++++++++", "========"]
        return random.choice(patterns)[: len(target_stimulus)]

    def generate_trial(
        self, soa: int, mask_type: str, target_stimulus: str = None
    ) -> Dict[str, Any]:
        """Generate a single masking trial."""
        if target_stimulus is None:
            target_stimulus = random.choice(self.config.target_stimuli)

        # Generate mask
        mask_pattern = random.choice(self.config.mask_patterns)
        mask_stimulus = self.mask_generators[mask_pattern](target_stimulus)

        # Determine stimulus timing based on mask type
        if mask_type == "forward":
            # Mask comes before target
            mask_onset = 0
            target_onset = soa
        elif mask_type == "backward":
            # Mask comes after target
            target_onset = 0
            mask_onset = soa
        else:  # sandwich
            # Mask before and after target
            mask_onset = 0
            target_onset = soa // 2
            # Second mask will be at target_onset + target_duration + soa//2

        trial = {
            "target_stimulus": target_stimulus,
            "mask_stimulus": mask_stimulus,
            "mask_pattern": mask_pattern,
            "mask_type": mask_type,
            "soa_ms": soa,
            "target_onset_ms": target_onset,
            "mask_onset_ms": mask_onset,
            "target_duration_ms": self.config.target_duration_ms,
            "mask_duration_ms": self.config.mask_duration_ms,
            "correct_response": target_stimulus,
            "difficulty_level": self._calculate_difficulty(soa, mask_type),
        }

        return trial

    def _calculate_difficulty(self, soa: int, mask_type: str) -> float:
        """Calculate difficulty level based on SOA and mask type."""
        # Shorter SOA = higher difficulty
        base_difficulty = 1.0 - (soa / max(self.config.stimulus_onset_asynchronies))

        # Adjust for mask type
        type_modifier = {
            "forward": 0.8,
            "backward": 1.0,  # Most effective
            "sandwich": 1.2,  # Most difficult
        }

        return base_difficulty * type_modifier.get(mask_type, 1.0)


class MaskingTask(TrialBasedTask):
    """Masking task implementation."""

    def __init__(self, config: Optional[MaskingConfig] = None):
        super().__init__(config)
        self.config = config or MaskingConfig()
        self.stimulus_generator = MaskingStimulus(self.config)
        self.consciousness_thresholds = {}

    def setup(self, **kwargs):
        """Set up the masking task."""
        super().setup(**kwargs)
        self.stimulus_generator = MaskingStimulus(self.config)
        self.consciousness_thresholds = {}

    def generate_trial_sequence(self) -> List[Dict[str, Any]]:
        """Generate balanced trial sequence."""
        trials = []

        # Create all condition combinations
        for soa in self.config.stimulus_onset_asynchronies:
            for mask_type in self.config.mask_types:
                n_trials_condition = self.config.n_trials // (
                    len(self.config.stimulus_onset_asynchronies)
                    * len(self.config.mask_types)
                )

                for _ in range(n_trials_condition):
                    trials.append(
                        {
                            "soa": soa,
                            "mask_type": mask_type,
                            "condition": f"{mask_type}_soa{soa}",
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
                "soa": 40,
                "mask_type": "backward",
                "condition": "backward_soa40",
            }

        # Generate stimulus
        stimulus = self.stimulus_generator.generate_trial(
            trial_config["soa"], trial_config["mask_type"]
        )

        base_params.update(
            {
                "stimulus": stimulus,
                "target_stimulus": stimulus["target_stimulus"],
                "mask_stimulus": stimulus["mask_stimulus"],
                "mask_pattern": stimulus["mask_pattern"],
                "mask_type": trial_config["mask_type"],
                "soa_ms": trial_config["soa"],
                "target_onset_ms": stimulus["target_onset_ms"],
                "mask_onset_ms": stimulus["mask_onset_ms"],
                "correct_response": stimulus["correct_response"],
                "difficulty_level": stimulus["difficulty_level"],
                "condition": trial_config["condition"],
            }
        )

        return base_params

    def process_response(
        self, response: Any, correct_response: Any, trial_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Process masking response."""
        # Response should be the target stimulus identity
        if isinstance(response, str):
            response_stimulus = response
        else:
            response_stimulus = str(response)

        correct_stimulus = str(correct_response)
        is_correct = response_stimulus == correct_stimulus

        # Get consciousness parameters from trial data or use defaults
        soa = 40  # Default
        mask_type = "backward"  # Default
        difficulty = 0.5  # Default

        if trial_data:
            soa = trial_data.get("soa_ms", 40)
            mask_type = trial_data.get("mask_type", "backward")
            difficulty = trial_data.get("difficulty_level", 0.5)

        key = f"{mask_type}_soa{soa}"

        if key not in self.consciousness_thresholds:
            self.consciousness_thresholds[key] = {
                "accuracy": [],
                "awareness": [],
                "confidence": [],  # Add confidence tracking
                "rt": [],  # Add reaction time tracking
            }

        # Calculate confidence based on awareness
        base_confidence = 0.8 if is_correct else 0.3
        base_confidence *= 1.0 - difficulty * 0.3  # Lower confidence for harder trials

        # Store accuracy (awareness will be calculated later)
        self.consciousness_thresholds[key]["accuracy"].append(1 if is_correct else 0)
        self.consciousness_thresholds[key]["confidence"].append(base_confidence)
        self.consciousness_thresholds[key]["rt"].append(
            0
        )  # Will be updated with actual RT

        return {
            "response": response_stimulus,
            "accuracy": 1 if is_correct else 0,
            "reaction_time_ms": 0,  # Will be filled by simulate_response
            "confidence": base_confidence,
            "target_stimulus": correct_stimulus,
            "mask_type": mask_type,
            "soa_ms": soa,
            "difficulty_level": difficulty,
            "condition": (
                trial_data.get("condition", "unknown") if trial_data else "unknown"
            ),
        }

    def simulate_response(self, trial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate participant masking performance."""
        soa = trial_data["soa_ms"]
        mask_type = trial_data["mask_type"]
        target_stimulus = trial_data["target_stimulus"]
        difficulty = trial_data["difficulty_level"]

        # Base accuracy depends on SOA and mask type
        # Longer SOA = better visibility
        soa_factor = soa / max(self.config.stimulus_onset_asynchronies)

        # Mask type effectiveness
        mask_effectiveness = {
            "forward": 0.7,
            "backward": 1.0,  # Most effective
            "sandwich": 1.2,  # Most difficult
        }

        mask_factor = mask_effectiveness.get(mask_type, 1.0)

        # Calculate visibility (probability of conscious perception)
        visibility = soa_factor / mask_factor
        visibility = np.clip(visibility, 0.1, 0.9)

        # Base reaction time (longer for more difficult trials)
        base_rt = 800 + (1.0 - visibility) * 600  # 800-1400ms range

        # Determine if target is consciously perceived
        consciously_perceived = random.random() < visibility

        if consciously_perceived:
            # Target is visible - good accuracy
            accuracy = 0.85 + visibility * 0.1
            rt = base_rt - 100  # Faster when consciously perceived
        else:
            # Target is not visible - chance performance
            accuracy = 0.15 + (
                1.0 / len(self.config.target_stimuli)
            )  # Slightly above chance
            rt = base_rt + 200  # Slower when guessing

        # Add noise to RT
        rt = max(400, np.random.normal(rt, 150))

        # Determine response
        if random.random() < accuracy:
            response = target_stimulus
        else:
            # Random guess
            response = random.choice(
                [s for s in self.config.target_stimuli if s != target_stimulus]
            )

        # Calculate confidence
        if consciously_perceived:
            confidence = 0.7 + visibility * 0.2
        else:
            confidence = 0.2 + random.random() * 0.3  # Low confidence when guessing

        return {
            "response": response,
            "reaction_time_ms": int(rt),
            "confidence": confidence,
            "timestamp": time.time(),
        }

    def compute_participant_summary(
        self, trials: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compute comprehensive summary for masking task."""
        base_summary = super().compute_participant_summary(trials)

        if not trials:
            return base_summary

        df = pd.DataFrame(trials)

        # Masking specific metrics
        summary = {
            **base_summary,
            "overall_accuracy": 0,
            "mean_reaction_time": 0,
            "consciousness_threshold": {},
            "soa_effects": {},
            "mask_type_effects": {},
        }

        # Overall metrics
        if "accuracy" in df.columns:
            summary["overall_accuracy"] = df["accuracy"].mean()

        if "reaction_time_ms" in df.columns:
            summary["mean_reaction_time"] = df["reaction_time_ms"].mean()

        # SOA effects (temporal masking function)
        for soa in sorted(df["soa_ms"].unique()):
            soa_data = df[df["soa_ms"] == soa]
            if len(soa_data) > 0:
                accuracy = (
                    soa_data["accuracy"].mean() if "accuracy" in soa_data.columns else 0
                )
                mean_rt = (
                    soa_data["reaction_time_ms"].mean()
                    if "reaction_time_ms" in soa_data.columns
                    else 0
                )
                confidence = (
                    soa_data["confidence"].mean()
                    if "confidence" in soa_data.columns
                    else 0
                )

                summary["soa_effects"][f"soa_{soa}"] = {
                    "accuracy": accuracy,
                    "mean_rt": mean_rt,
                    "confidence": confidence,
                    "n_trials": len(soa_data),
                }

        # Mask type effects
        for mask_type in df["mask_type"].unique():
            mask_data = df[df["mask_type"] == mask_type]
            if len(mask_data) > 0:
                accuracy = (
                    mask_data["accuracy"].mean()
                    if "accuracy" in mask_data.columns
                    else 0
                )
                mean_rt = (
                    mask_data["reaction_time_ms"].mean()
                    if "reaction_time_ms" in mask_data.columns
                    else 0
                )

                summary["mask_type_effects"][mask_type] = {
                    "accuracy": accuracy,
                    "mean_rt": mean_rt,
                    "n_trials": len(mask_data),
                }

        # Estimate consciousness threshold (SOA at 50% accuracy)
        soa_accuracies = []
        soa_values = []

        for soa in sorted(df["soa_ms"].unique()):
            soa_data = df[df["soa_ms"] == soa]
            if len(soa_data) > 0 and "accuracy" in soa_data.columns:
                soa_accuracies.append(soa_data["accuracy"].mean())
                soa_values.append(soa)

        if len(soa_accuracies) > 2:
            # Interpolate to find 50% threshold
            from scipy import interpolate

            try:
                f = interpolate.interp1d(soa_accuracies, soa_values, kind="linear")
                threshold_50 = float(f(0.5))
                summary["consciousness_threshold"]["soa_50_percent"] = threshold_50
            except:
                # Fallback: find closest to 50%
                closest_idx = np.argmin(np.abs(np.array(soa_accuracies) - 0.5))
                summary["consciousness_threshold"]["soa_50_percent"] = soa_values[
                    closest_idx
                ]

        # Detailed consciousness thresholds by condition
        for key, data in self.consciousness_thresholds.items():
            if data["accuracy"]:
                mean_accuracy = np.mean(data["accuracy"])
                mean_confidence = np.mean(data["confidence"])
                mean_rt = np.mean(data["rt"])

                summary["consciousness_threshold"][f"condition_{key}"] = {
                    "accuracy": mean_accuracy,
                    "confidence": mean_confidence,
                    "mean_rt": mean_rt,
                    "n_trials": len(data["accuracy"]),
                }

        return summary


def run_masking_experiment(**kwargs):
    """Run the Masking experiment."""
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
        if hasattr(MaskingConfig, config_key):
            config_params[config_key] = value

    # Create config and experiment
    config = MaskingConfig(**config_params)
    experiment = MaskingTask(config)

    # Set up and run experiment
    experiment.setup()
    results = experiment.run_experiment()

    # Save results if output file specified
    if kwargs.get("output_file"):
        experiment.save_data(kwargs["output_file"])

    return experiment


if __name__ == "__main__":
    # Example usage
    config = MaskingConfig(
        n_trials=120,
        n_participants=5,
        stimulus_onset_asynchronies=[0, 20, 40, 80, 120],
        mask_types=["backward", "forward"],
    )

    experiment = MaskingTask(config)
    experiment.setup()
    results = experiment.run_experiment()

    print("Masking experiment completed!")
    print(f"Results shape: {results.shape}")

    # Print summary for first participant
    if experiment.participant_data:
        first_participant = list(experiment.participant_data.keys())[0]
        summary = experiment.participant_data[first_participant]["summary"]
        print(f"\nParticipant {first_participant} Summary:")
        print(f"Overall Accuracy: {summary.get('overall_accuracy', 0):.3f}")
        print(f"Mean Reaction Time: {summary.get('mean_reaction_time', 0):.1f} ms")
        print(
            f"Consciousness Threshold (50%): {summary.get('consciousness_threshold', {}).get('soa_50_percent', 'N/A')} ms"
        )
        print(f"SOA Effects: {summary.get('soa_effects', {})}")
