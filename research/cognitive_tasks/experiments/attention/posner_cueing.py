"""
Posner Cueing implementation.

The Posner cueing task measures spatial attention. Participants respond to targets
that appear at cued or uncued locations. Faster responses to cued locations indicate
attentional benefits, while slower responses to uncued locations indicate costs.

APGI Integration:
- θₜ (threshold): Spatial attention shift threshold
- π (precision): Spatial precision of attentional focus
- ε (prediction error): Invalid cue prediction error
- β (inverse temperature): Consistency of attentional allocation
"""

import random
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import time

from .. import TrialBasedTask, TrialBasedTaskConfig


@dataclass
class PosnerCueingConfig(TrialBasedTaskConfig):
    """Configuration for Posner Cueing experiment."""

    n_trials: int = 160
    fixation_duration_ms: int = 500
    cue_duration_ms: int = 100
    cue_target_interval_ms: int = 200  # SOA
    target_duration_ms: int = 150
    response_window_ms: int = 1500

    # Cue parameters
    cue_validity: float = 0.8  # Proportion of valid cues
    cue_types: List[str] = None  # central, peripheral, symbolic
    soa_values: List[int] = None  # Stimulus onset asynchronies

    # Spatial parameters
    n_locations: int = 4  # Number of possible target locations
    target_positions: List[str] = None  # left, right, up, down

    def __post_init__(self):
        if self.cue_types is None:
            self.cue_types = ["peripheral", "central"]

        if self.soa_values is None:
            self.soa_values = [100, 200, 400, 800]

        if self.target_positions is None:
            self.target_positions = ["left", "right", "up", "down"]


class PosnerDisplay:
    """Generate Posner cueing displays."""

    def __init__(self, config: PosnerCueingConfig):
        self.config = config
        self.locations = self._define_locations()

    def _define_locations(self) -> Dict[str, Tuple[float, float]]:
        """Define target locations in visual space."""
        eccentricity = 5.0  # degrees of visual angle

        return {
            "left": (-eccentricity, 0.0),
            "right": (eccentricity, 0.0),
            "up": (0.0, eccentricity),
            "down": (0.0, -eccentricity),
        }

    def generate_trial(
        self, cue_type: str, soa: int, target_position: str, cue_valid: bool
    ) -> Dict[str, Any]:
        """Generate a single Posner trial."""
        # Determine cue position
        if cue_valid:
            cue_position = target_position
        else:
            # Choose random different position
            other_positions = [
                pos for pos in self.config.target_positions if pos != target_position
            ]
            cue_position = random.choice(other_positions)

        # Generate trial structure
        trial = {
            "cue_type": cue_type,
            "soa_ms": soa,
            "target_position": target_position,
            "cue_position": cue_position,
            "cue_valid": cue_valid,
            "locations": self.locations,
            "fixation_duration_ms": self.config.fixation_duration_ms,
            "cue_duration_ms": self.config.cue_duration_ms,
            "target_duration_ms": self.config.target_duration_ms,
        }

        return trial


class PosnerCueingTask(TrialBasedTask):
    """Posner Cueing task implementation."""

    def __init__(self, config: Optional[PosnerCueingConfig] = None):
        super().__init__(config)
        self.config = config or PosnerCueingConfig()
        self.display_generator = PosnerDisplay(self.config)
        self.attentional_effects = {}

    def setup(self, **kwargs):
        """Set up the Posner cueing task."""
        super().setup(**kwargs)
        self.display_generator = PosnerDisplay(self.config)
        self.attentional_effects = {}

    def generate_trial_sequence(self) -> List[Dict[str, Any]]:
        """Generate balanced trial sequence."""
        trials = []

        # Create all condition combinations
        for cue_type in self.config.cue_types:
            for soa in self.config.soa_values:
                for target_position in self.config.target_positions:
                    # Valid and invalid trials
                    n_valid = int(
                        self.config.n_trials
                        * self.config.cue_validity
                        / (
                            len(self.config.cue_types)
                            * len(self.config.soa_values)
                            * len(self.config.target_positions)
                        )
                    )
                    n_invalid = (
                        self.config.n_trials
                        // (
                            len(self.config.cue_types)
                            * len(self.config.soa_values)
                            * len(self.config.target_positions)
                            * 2
                        )
                        - n_valid
                    )

                    # Valid trials
                    for _ in range(n_valid):
                        trials.append(
                            {
                                "cue_type": cue_type,
                                "soa": soa,
                                "target_position": target_position,
                                "cue_valid": True,
                                "condition": f"{cue_type}_valid_soa{soa}_{target_position}",
                            }
                        )

                    # Invalid trials
                    for _ in range(n_invalid):
                        trials.append(
                            {
                                "cue_type": cue_type,
                                "soa": soa,
                                "target_position": target_position,
                                "cue_valid": False,
                                "condition": f"{cue_type}_invalid_soa{soa}_{target_position}",
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
                "cue_type": "peripheral",
                "soa": 200,
                "target_position": "right",
                "cue_valid": True,
                "condition": "peripheral_valid_soa200_right",
            }

        # Generate trial display
        trial_display = self.display_generator.generate_trial(
            trial_config["cue_type"],
            trial_config["soa"],
            trial_config["target_position"],
            trial_config["cue_valid"],
        )

        base_params.update(
            {
                "trial_display": trial_display,
                "cue_type": trial_config["cue_type"],
                "soa_ms": trial_config["soa"],
                "target_position": trial_config["target_position"],
                "cue_position": trial_display["cue_position"],
                "cue_valid": trial_config["cue_valid"],
                "condition": trial_config["condition"],
            }
        )

        return base_params

    def process_response(
        self, response: Any, correct_response: Any, trial_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Process Posner cueing response."""
        # Response should be the target position (left/right)
        if isinstance(response, str):
            response_position = response.lower()
        else:
            response_position = str(response).lower()

        correct_position = (
            correct_response.lower() if correct_response is not None else "center"
        )
        is_correct = response_position == correct_position

        # Get attentional parameters from trial data or use defaults
        cue_valid = True  # Default
        soa = 200  # Default
        cue_type = "peripheral"  # Default

        if trial_data:
            cue_valid = trial_data.get("cue_valid", True)
            soa = trial_data.get("soa_ms", 200)
            cue_type = trial_data.get("cue_type", "peripheral")

        # Store attentional effects
        effect_key = f"{cue_type}_soa{soa}"
        if effect_key not in self.attentional_effects:
            self.attentional_effects[effect_key] = {
                "valid_cue_rt": [],
                "invalid_cue_rt": [],
                "valid_cue_accuracy": [],
                "invalid_cue_accuracy": [],
            }

        # Don't store RT here since it's not available yet
        if cue_valid:
            self.attentional_effects[effect_key]["valid_cue_accuracy"].append(
                1 if is_correct else 0
            )
        else:
            self.attentional_effects[effect_key]["invalid_cue_accuracy"].append(
                1 if is_correct else 0
            )

        # Calculate confidence based on accuracy and cue validity
        base_confidence = 0.8 if is_correct else 0.4
        if not cue_valid:
            base_confidence -= 0.1  # Lower confidence for invalid cues

        return {
            "response": response_position,
            "accuracy": 1 if is_correct else 0,
            "reaction_time_ms": 0,  # Will be filled by simulate_response
            "confidence": base_confidence,
            "cue_type": cue_type,
            "soa_ms": soa,
            "cue_valid": cue_valid,
            "target_position": correct_position,
            "cue_position": (
                trial_data.get("cue_position", "center") if trial_data else "center"
            ),
            "condition": (
                trial_data.get("condition", "valid") if trial_data else "valid"
            ),
        }

    def simulate_response(self, trial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate participant Posner cueing performance."""
        cue_valid = trial_data["cue_valid"]
        soa = trial_data["soa_ms"]
        cue_type = trial_data["cue_type"]
        target_position = trial_data["target_position"]

        # Base reaction time and accuracy
        base_rt = 400  # Base RT in ms
        base_accuracy = 0.95

        # Attentional benefits and costs
        if cue_valid:
            # Valid cue - attentional benefit
            rt_benefit = -50  # Faster RT
            accuracy_benefit = 0.03
        else:
            # Invalid cue - attentional cost
            rt_cost = 80  # Slower RT
            accuracy_cost = -0.05

        # SOA effects
        if soa <= 100:
            # Very short SOA - less time to shift attention
            soa_effect = 30 if not cue_valid else 10
        elif soa <= 400:
            # Optimal SOA
            soa_effect = 0
        else:
            # Long SOA - inhibition of return may occur
            soa_effect = 20 if cue_valid else -10

        # Cue type effects
        if cue_type == "peripheral":
            # Peripheral cues are more effective
            cue_effectiveness = 1.0
        else:  # central
            # Central cues are less effective
            cue_effectiveness = 0.7

        # Calculate reaction time
        rt = base_rt
        if cue_valid:
            rt += rt_benefit * cue_effectiveness
        else:
            rt += rt_cost * cue_effectiveness

        rt += soa_effect

        # Add noise
        rt = max(250, np.random.normal(rt, 80))

        # Calculate accuracy
        accuracy = base_accuracy
        if cue_valid:
            accuracy += accuracy_benefit * cue_effectiveness
        else:
            accuracy += accuracy_cost * cue_effectiveness

        # Ensure accuracy is within bounds
        accuracy = np.clip(accuracy, 0.5, 1.0)

        # Determine response
        if random.random() < accuracy:
            response = target_position
        else:
            # Random error
            other_positions = [
                pos for pos in self.config.target_positions if pos != target_position
            ]
            response = random.choice(other_positions)

        # Calculate confidence
        confidence = 0.8 if response == target_position else 0.5

        return {
            "response": response,
            "reaction_time_ms": int(rt),
            "confidence": confidence,
            "timestamp": time.time(),
        }

    def compute_participant_summary(
        self, trials: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compute comprehensive summary for Posner cueing task."""
        base_summary = super().compute_participant_summary(trials)

        if not trials:
            return base_summary

        df = pd.DataFrame(trials)

        # Posner specific metrics
        summary = {
            **base_summary,
            "overall_accuracy": 0,
            "mean_reaction_time": 0,
            "attentional_benefits": {},
            "attentional_costs": {},
            "cue_validity_effects": {},
            "soa_effects": {},
        }

        # Overall metrics
        if "accuracy" in df.columns:
            summary["overall_accuracy"] = df["accuracy"].mean()

        if "reaction_time_ms" in df.columns:
            summary["mean_reaction_time"] = df["reaction_time_ms"].mean()

        # Attentional benefits and costs
        valid_trials = df[df["cue_valid"] == True]
        invalid_trials = df[df["cue_valid"] == False]

        if len(valid_trials) > 0:
            summary["attentional_benefits"] = {
                "mean_rt": (
                    valid_trials["reaction_time_ms"].mean()
                    if "reaction_time_ms" in valid_trials.columns
                    else 0
                ),
                "accuracy": (
                    valid_trials["accuracy"].mean()
                    if "accuracy" in valid_trials.columns
                    else 0
                ),
                "n_trials": len(valid_trials),
            }

        if len(invalid_trials) > 0:
            summary["attentional_costs"] = {
                "mean_rt": (
                    invalid_trials["reaction_time_ms"].mean()
                    if "reaction_time_ms" in invalid_trials.columns
                    else 0
                ),
                "accuracy": (
                    invalid_trials["accuracy"].mean()
                    if "accuracy" in invalid_trials.columns
                    else 0
                ),
                "n_trials": len(invalid_trials),
            }

        # Calculate cue validity effect (difference between valid and invalid)
        if len(valid_trials) > 0 and len(invalid_trials) > 0:
            valid_rt = (
                valid_trials["reaction_time_ms"].mean()
                if "reaction_time_ms" in valid_trials.columns
                else 0
            )
            invalid_rt = (
                invalid_trials["reaction_time_ms"].mean()
                if "reaction_time_ms" in invalid_trials.columns
                else 0
            )

            summary["cue_validity_effects"] = {
                "rt_difference_ms": invalid_rt - valid_rt,  # Positive = benefit
                "validity_benefit": invalid_rt - valid_rt,
                "valid_accuracy": (
                    valid_trials["accuracy"].mean()
                    if "accuracy" in valid_trials.columns
                    else 0
                ),
                "invalid_accuracy": (
                    invalid_trials["accuracy"].mean()
                    if "accuracy" in invalid_trials.columns
                    else 0
                ),
            }

        # SOA effects
        for soa in sorted(df["soa_ms"].unique()):
            soa_data = df[df["soa_ms"] == soa]
            if len(soa_data) > 0:
                soa_valid = soa_data[soa_data["cue_valid"] == True]
                soa_invalid = soa_data[soa_data["cue_valid"] == False]

                soa_summary = {"soa": soa, "n_trials": len(soa_data)}

                if len(soa_valid) > 0:
                    soa_summary["valid_rt"] = (
                        soa_valid["reaction_time_ms"].mean()
                        if "reaction_time_ms" in soa_valid.columns
                        else 0
                    )
                    soa_summary["valid_accuracy"] = (
                        soa_valid["accuracy"].mean()
                        if "accuracy" in soa_valid.columns
                        else 0
                    )

                if len(soa_invalid) > 0:
                    soa_summary["invalid_rt"] = (
                        soa_invalid["reaction_time_ms"].mean()
                        if "reaction_time_ms" in soa_invalid.columns
                        else 0
                    )
                    soa_summary["invalid_accuracy"] = (
                        soa_invalid["accuracy"].mean()
                        if "accuracy" in soa_invalid.columns
                        else 0
                    )

                if len(soa_valid) > 0 and len(soa_invalid) > 0:
                    soa_summary["validity_effect"] = (
                        soa_summary["invalid_rt"] - soa_summary["valid_rt"]
                    )

                summary["soa_effects"][f"soa_{soa}"] = soa_summary

        return summary


def run_posner_cueing_experiment(**kwargs):
    """Run the Posner Cueing experiment."""
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
        if hasattr(PosnerCueingConfig, config_key):
            config_params[config_key] = value

    # Create config and experiment
    config = PosnerCueingConfig(**config_params)
    experiment = PosnerCueingTask(config)

    # Set up and run experiment
    experiment.setup()
    results = experiment.run_experiment()

    # Save results if output file specified
    if kwargs.get("output_file"):
        experiment.save_data(kwargs["output_file"])

    return experiment


if __name__ == "__main__":
    # Example usage
    config = PosnerCueingConfig(
        n_trials=100,
        n_participants=5,
        cue_types=["peripheral", "central"],
        soa_values=[100, 200, 400],
    )

    experiment = PosnerCueingTask(config)
    experiment.setup()
    results = experiment.run_experiment()

    print("Posner Cueing experiment completed!")
    print(f"Results shape: {results.shape}")

    # Print summary for first participant
    if experiment.participant_data:
        first_participant = list(experiment.participant_data.keys())[0]
        summary = experiment.participant_data[first_participant]["summary"]
        print(f"\nParticipant {first_participant} Summary:")
        print(f"Overall Accuracy: {summary.get('overall_accuracy', 0):.3f}")
        print(f"Mean Reaction Time: {summary.get('mean_reaction_time', 0):.1f} ms")
        print(
            f"Cue Validity Effect: {summary.get('cue_validity_effects', {}).get('rt_difference_ms', 0):.1f} ms"
        )
