"""
Multisensory Integration implementation.

Multisensory integration examines how the brain combines information from different
sensory modalities (visual, auditory, tactile). This experiment measures the
superadditive effect where combined stimuli produce stronger responses than the sum
of unimodal stimuli.

APGI Integration:
- θₜ (threshold): Multisensory integration threshold
- π (precision): Cross-modal precision weighting
- ε (prediction error): Cross-modal prediction error
- β (inverse temperature): Integration consistency
"""

import random
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import time

from .. import TrialBasedTask, TrialBasedTaskConfig


@dataclass
class MultisensoryIntegrationConfig(TrialBasedTaskConfig):
    """Configuration for Multisensory Integration experiment."""

    n_trials: int = 180
    stimulus_duration_ms: int = 1000
    response_window_ms: int = 2000
    inter_trial_interval_ms: int = 1500

    # Modality parameters
    modalities: List[str] = None  # visual, auditory, tactile, multisensory
    stimulus_types: List[str] = None  # simple, complex, ecological

    # Visual stimuli
    visual_stimuli: List[str] = None  # Visual stimulus set
    visual_intensity_levels: List[float] = None  # Intensity levels

    # Auditory stimuli
    auditory_stimuli: List[str] = None  # Auditory stimulus set
    auditory_intensity_levels: List[float] = None  # Intensity levels

    # Tactile stimuli
    tactile_stimuli: List[str] = None  # Tactile stimulus set
    tactile_intensity_levels: List[float] = None  # Intensity levels

    # Integration parameters
    soa_ms: int = 100  # Stimulus onset asynchrony
    spatial_coincidence: bool = True  # Whether stimuli are spatially coincident

    def __post_init__(self):
        if self.modalities is None:
            self.modalities = ["visual", "auditory", "multisensory"]

        if self.stimulus_types is None:
            self.stimulus_types = ["simple"]

        if self.visual_stimuli is None:
            self.visual_stimuli = ["●", "■", "▲", "◆"]

        if self.auditory_stimuli is None:
            self.auditory_stimuli = ["1000Hz", "2000Hz", "4000Hz", "8000Hz"]

        if self.tactile_stimuli is None:
            self.tactile_stimuli = [
                "vibration_1",
                "vibration_2",
                "vibration_3",
                "vibration_4",
            ]

        if self.visual_intensity_levels is None:
            self.visual_intensity_levels = [0.3, 0.6, 1.0]

        if self.auditory_intensity_levels is None:
            self.auditory_intensity_levels = [0.3, 0.6, 1.0]

        if self.tactile_intensity_levels is None:
            self.tactile_intensity_levels = [0.3, 0.6, 1.0]


class MultisensoryStimulus:
    """Generate multisensory integration stimuli."""

    def __init__(self, config: MultisensoryIntegrationConfig):
        self.config = config

    def generate_stimulus(
        self, modality: str, intensity: float = None
    ) -> Dict[str, Any]:
        """Generate a stimulus for a specific modality."""
        if intensity is None:
            intensity = random.choice(
                self.config.visual_intensity_levels
                if modality == "visual"
                else (
                    self.config.auditory_intensity_levels
                    if modality == "auditory"
                    else self.config.tactile_intensity_levels
                )
            )

        stimulus = {
            "modality": modality,
            "intensity": intensity,
            "stimulus_type": "simple",
        }

        if modality == "visual":
            stimulus["visual_stimulus"] = random.choice(self.config.visual_stimuli)
            stimulus["auditory_stimulus"] = None
            stimulus["tactile_stimulus"] = None
        elif modality == "auditory":
            stimulus["visual_stimulus"] = None
            stimulus["auditory_stimulus"] = random.choice(self.config.auditory_stimuli)
            stimulus["tactile_stimulus"] = None
        elif modality == "tactile":
            stimulus["visual_stimulus"] = None
            stimulus["auditory_stimulus"] = None
            stimulus["tactile_stimulus"] = random.choice(self.config.tactile_stimuli)
        elif modality == "multisensory":
            # Combined stimulus
            stimulus["visual_stimulus"] = random.choice(self.config.visual_stimuli)
            stimulus["auditory_stimulus"] = random.choice(self.config.auditory_stimuli)
            stimulus["tactile_stimulus"] = None  # Could add tactile too
            stimulus["component_intensities"] = {
                "visual": intensity,
                "auditory": intensity,
            }

        return stimulus

    def generate_trial(
        self, modality: str, target_present: bool = True
    ) -> Dict[str, Any]:
        """Generate a complete trial."""
        stimulus = self.generate_stimulus(modality)
        stimulus["target_present"] = target_present
        stimulus["correct_response"] = "yes" if target_present else "no"

        return stimulus


class MultisensoryIntegrationTask(TrialBasedTask):
    """Multisensory Integration task implementation."""

    def __init__(self, config: Optional[MultisensoryIntegrationConfig] = None):
        super().__init__(config)
        self.config = config or MultisensoryIntegrationConfig()
        self.stimulus_generator = MultisensoryStimulus(self.config)
        self.integration_data = {}

    def setup(self, **kwargs):
        """Set up the Multisensory Integration task."""
        super().setup(**kwargs)
        self.stimulus_generator = MultisensoryStimulus(self.config)
        self.integration_data = {}

    def generate_trial_sequence(self) -> List[Dict[str, Any]]:
        """Generate balanced trial sequence."""
        trials = []

        # Create balanced design across modalities
        for modality in self.config.modalities:
            n_trials_modality = self.config.n_trials // len(self.config.modalities)

            for _ in range(n_trials_modality):
                # 50% target present, 50% target absent
                target_present = random.random() < 0.5

                trials.append(
                    {
                        "modality": modality,
                        "target_present": target_present,
                        "condition": f"{modality}_{'target' if target_present else 'nontarget'}",
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
                "target_present": True,
                "condition": "visual_target",
            }

        # Generate stimulus
        stimulus = self.stimulus_generator.generate_trial(
            trial_config["modality"], trial_config["target_present"]
        )

        base_params.update(
            {
                "stimulus": stimulus,
                "modality": stimulus["modality"],
                "target_present": stimulus["target_present"],
                "correct_response": stimulus["correct_response"],
                "condition": trial_config["condition"],
                "stimulus_duration_ms": self.config.stimulus_duration_ms,
                "soa_ms": self.config.soa_ms,
                "spatial_coincidence": self.config.spatial_coincidence,
            }
        )

        return base_params

    def process_response(
        self, response: Any, correct_response: Any, trial_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Process multisensory integration response."""
        # Response should be the stimulus identity
        if isinstance(response, str):
            response_str = response.lower()
        else:
            response_str = str(response).lower()

        correct_str = str(correct_response).lower()
        is_correct = response_str == correct_str

        # Get integration parameters from trial data or use defaults
        modality = "visual"  # Default
        target_present = True  # Default
        stimulus = {}  # Default

        if trial_data:
            modality = trial_data.get("modality", "visual")
            target_present = trial_data.get("target_present", True)
            stimulus = trial_data.get("stimulus", {})

        key = f"{modality}_{'target' if target_present else 'nontarget'}"
        if key not in self.integration_data:
            self.integration_data[key] = {
                "accuracy": [],
                "intensities": [],
                "reaction_times": [],
            }

        self.integration_data[key]["accuracy"].append(1 if is_correct else 0)
        self.integration_data[key]["intensities"].append(stimulus.get("intensity", 0.5))

        # Calculate confidence based on accuracy and modality
        base_confidence = 0.8 if is_correct else 0.4
        if modality == "tactile":
            base_confidence -= 0.1  # Lower confidence for tactile

        return {
            "response": response_str,
            "accuracy": 1 if is_correct else 0,
            "reaction_time_ms": 0,  # Will be filled by simulate_response
            "confidence": base_confidence,
            "modality": modality,
            "target_present": target_present,
            "stimulus": stimulus,
            "intensity": stimulus.get("intensity", 0.5),
            "correct_response": correct_str,
            "condition": (
                trial_data.get("condition", "unknown") if trial_data else "unknown"
            ),
        }

    def simulate_response(self, trial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate participant multisensory integration performance."""
        modality = trial_data["modality"]
        target_present = trial_data["target_present"]
        intensity = trial_data["stimulus"]["intensity"]
        correct_response = trial_data["correct_response"]

        # Base detection probability depends on intensity and modality
        base_detection_prob = 0.6 + (intensity * 0.3)  # Intensity effect

        # Modality effects
        modality_effects = {
            "visual": 1.0,
            "auditory": 0.95,
            "multisensory": 1.2,  # Superadditive effect
        }

        detection_prob = base_detection_prob * modality_effects.get(modality, 1.0)
        detection_prob = np.clip(detection_prob, 0.2, 0.95)

        # Generate response
        if target_present:
            # Target present trial
            if random.random() < detection_prob:
                response = "yes"  # Hit
            else:
                response = "no"  # Miss
        else:
            # Target absent trial
            false_alarm_prob = detection_prob * 0.3  # Lower false alarm rate
            if random.random() < false_alarm_prob:
                response = "yes"  # False alarm
            else:
                response = "no"  # Correct rejection

        # Calculate reaction time
        base_rt = 800

        # Faster for multisensory stimuli
        if modality == "multisensory":
            base_rt -= 150

        # RT depends on intensity
        base_rt -= (intensity - 0.5) * 200  # Higher intensity = faster RT

        rt = max(300, np.random.normal(base_rt, 150))

        # Calculate confidence
        actual_correct = response == correct_response
        confidence = 0.8 if actual_correct else 0.4

        if modality == "multisensory" and actual_correct:
            confidence += 0.1  # Higher confidence for correct multisensory detection

        return {
            "response": response,
            "reaction_time_ms": int(rt),
            "confidence": confidence,
            "timestamp": time.time(),
        }

    def compute_participant_summary(
        self, trials: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compute comprehensive summary for multisensory integration task."""
        base_summary = super().compute_participant_summary(trials)

        if not trials:
            return base_summary

        df = pd.DataFrame(trials)

        # Multisensory integration specific metrics
        summary = {
            **base_summary,
            "overall_accuracy": 0,
            "mean_reaction_time": 0,
            "modality_performance": {},
            "multisensory_benefit": {},
            "intensity_effects": {},
            "signal_detection": {},
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
                mean_intensity = (
                    modality_data["intensity"].mean()
                    if "intensity" in modality_data.columns
                    else 0.5
                )

                summary["modality_performance"][modality] = {
                    "accuracy": accuracy,
                    "mean_rt": mean_rt,
                    "mean_intensity": mean_intensity,
                    "n_trials": len(modality_data),
                }

        # Calculate multisensory benefit
        visual_data = df[df["modality"] == "visual"]
        auditory_data = df[df["modality"] == "auditory"]
        multisensory_data = df[df["modality"] == "multisensory"]

        if len(visual_data) > 0 and len(multisensory_data) > 0:
            visual_acc = (
                visual_data["accuracy"].mean()
                if "accuracy" in visual_data.columns
                else 0
            )
            visual_rt = (
                visual_data["reaction_time_ms"].mean()
                if "reaction_time_ms" in visual_data.columns
                else 0
            )

            multisensory_acc = (
                multisensory_data["accuracy"].mean()
                if "accuracy" in multisensory_data.columns
                else 0
            )
            multisensory_rt = (
                multisensory_data["reaction_time_ms"].mean()
                if "reaction_time_ms" in multisensory_data.columns
                else 0
            )

            summary["multisensory_benefit"] = {
                "accuracy_improvement": multisensory_acc - visual_acc,
                "rt_improvement": visual_rt - multisensory_rt,
                "visual_accuracy": visual_acc,
                "multisensory_accuracy": multisensory_acc,
                "visual_rt": visual_rt,
                "multisensory_rt": multisensory_rt,
            }

        # Signal detection analysis
        target_trials = df[df["target_present"] == True]
        nontarget_trials = df[df["target_present"] == False]

        if len(target_trials) > 0 and len(nontarget_trials) > 0:
            for modality in df["modality"].unique():
                mod_target = target_trials[target_trials["modality"] == modality]
                mod_nontarget = nontarget_trials[
                    nontarget_trials["modality"] == modality
                ]

                if len(mod_target) > 0 and len(mod_nontarget) > 0:
                    hit_rate = (
                        mod_target["accuracy"].mean()
                        if "accuracy" in mod_target.columns
                        else 0
                    )
                    false_alarm_rate = (
                        1 - mod_nontarget["accuracy"].mean()
                        if "accuracy" in mod_nontarget.columns
                        else 0
                    )

                    # Avoid extreme values
                    hit_rate = np.clip(hit_rate, 0.01, 0.99)
                    false_alarm_rate = np.clip(false_alarm_rate, 0.01, 0.99)

                    try:
                        from scipy import stats

                        d_prime = stats.norm.ppf(hit_rate) - stats.norm.ppf(
                            1 - false_alarm_rate
                        )
                        criterion = (
                            -(
                                stats.norm.ppf(hit_rate)
                                + stats.norm.ppf(false_alarm_rate)
                            )
                            / 2
                        )

                        summary["signal_detection"][f"{modality}_d_prime"] = d_prime
                        summary["signal_detection"][f"{modality}_criterion"] = criterion
                    except:
                        summary["signal_detection"][f"{modality}_d_prime"] = 0.0
                        summary["signal_detection"][f"{modality}_criterion"] = 0.0

        # Intensity effects
        for modality in df["modality"].unique():
            modality_data = df[df["modality"] == modality]
            if len(modality_data) > 0 and "intensity" in modality_data.columns:
                # Correlate intensity with performance
                intensity = modality_data["intensity"]
                accuracy = (
                    modality_data["accuracy"]
                    if "accuracy" in modality_data.columns
                    else pd.Series([0] * len(modality_data))
                )

                if len(intensity) > 1 and len(accuracy) > 1:
                    # Handle zero variance cases to avoid runtime warnings
                    if np.std(intensity) == 0 or np.std(accuracy) == 0:
                        correlation = 0.0
                    else:
                        correlation = np.corrcoef(intensity, accuracy)[0, 1]
                    summary["intensity_effects"][
                        f"{modality}_intensity_correlation"
                    ] = correlation

        return summary


def run_multisensory_integration_experiment(**kwargs):
    """Run the Multisensory Integration experiment."""
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
        if hasattr(MultisensoryIntegrationConfig, config_key):
            config_params[config_key] = value

    # Create config and experiment
    config = MultisensoryIntegrationConfig(**config_params)
    experiment = MultisensoryIntegrationTask(config)

    # Set up and run experiment
    experiment.setup()
    results = experiment.run_experiment()

    # Save results if output file specified
    if kwargs.get("output_file"):
        experiment.save_data(kwargs["output_file"])

    return experiment


if __name__ == "__main__":
    # Example usage
    config = MultisensoryIntegrationConfig(
        n_trials=150,
        n_participants=5,
        modalities=["visual", "auditory", "multisensory"],
        spatial_coincidence=True,
    )

    experiment = MultisensoryIntegrationTask(config)
    experiment.setup()
    results = experiment.run_experiment()

    print("Multisensory Integration experiment completed!")
    print(f"Results shape: {results.shape}")

    # Print summary for first participant
    if experiment.participant_data:
        first_participant = list(experiment.participant_data.keys())[0]
        summary = experiment.participant_data[first_participant]["summary"]
        print(f"\nParticipant {first_participant} Summary:")
        print(f"Overall Accuracy: {summary.get('overall_accuracy', 0):.3f}")
        print(f"Mean Reaction Time: {summary.get('mean_reaction_time', 0):.1f} ms")
        print(f"Multisensory Benefit: {summary.get('multisensory_benefit', {})}")
        print(f"Modality Performance: {summary.get('modality_performance', {})}")
