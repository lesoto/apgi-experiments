"""
Dual N-back implementation.

The N-back task is a working memory paradigm where participants must indicate whether
the current stimulus matches the one presented n trials earlier. The dual N-back
uses two stimulus modalities simultaneously (typically visual and auditory).

APGI Integration:
- θₜ (threshold): Working memory capacity threshold
- π (precision): Memory precision/confidence
- ε (prediction error): Mismatch prediction error
- β (inverse temperature): Response consistency
"""

import random
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import time

from .. import TrialBasedTask, TrialBasedTaskConfig


@dataclass
class DualNBackConfig(TrialBasedTaskConfig):
    """Configuration for Dual N-back experiment."""

    n_trials: int = 200
    stimulus_duration_ms: int = 500
    inter_stimulus_interval_ms: int = 2500
    response_window_ms: int = 1500

    # N-back parameters
    n_levels: List[int] = None  # Different n-back levels to test
    current_n_level: int = 2  # Current n-back level

    # Stimulus parameters
    visual_stimuli: List[str] = None  # Visual stimuli
    auditory_stimuli: List[str] = None  # Auditory stimuli
    stimulus_types: List[str] = None  # visual, auditory, dual

    # Task parameters
    target_probability: float = 0.3  # Probability of target trials
    practice_trials: int = 20  # Practice trials before main task

    def __post_init__(self):
        if self.n_levels is None:
            self.n_levels = [1, 2, 3]

        if self.visual_stimuli is None:
            self.visual_stimuli = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")[:8]  # 8 letters

        if self.auditory_stimuli is None:
            self.auditory_stimuli = ["1", "2", "3", "4", "5", "6", "7", "8"]  # 8 digits

        if self.stimulus_types is None:
            self.stimulus_types = ["visual", "auditory", "dual"]


class NBackStimulus:
    """Generate N-back stimuli."""

    def __init__(self, config: DualNBackConfig):
        self.config = config
        self.visual_history = []
        self.auditory_history = []

    def generate_stimulus_sequence(
        self, n_trials: int, n_level: int
    ) -> List[Dict[str, Any]]:
        """Generate a sequence of N-back stimuli."""
        sequence = []

        for trial in range(n_trials):
            # Determine if this should be a target trial
            is_target = (
                trial >= n_level and random.random() < self.config.target_probability
            )

            if is_target:
                # Target: match stimulus from n trials back
                visual_stimulus = (
                    self.visual_history[-n_level]
                    if len(self.visual_history) >= n_level
                    else random.choice(self.config.visual_stimuli)
                )
                auditory_stimulus = (
                    self.auditory_history[-n_level]
                    if len(self.auditory_history) >= n_level
                    else random.choice(self.config.auditory_stimuli)
                )
            else:
                # Non-target: different stimulus
                available_visual = [
                    s
                    for s in self.config.visual_stimuli
                    if s
                    != (
                        self.visual_history[-n_level]
                        if len(self.visual_history) >= n_level
                        else None
                    )
                ]
                available_auditory = [
                    s
                    for s in self.config.auditory_stimuli
                    if s
                    != (
                        self.auditory_history[-n_level]
                        if len(self.auditory_history) >= n_level
                        else None
                    )
                ]

                visual_stimulus = (
                    random.choice(available_visual)
                    if available_visual
                    else random.choice(self.config.visual_stimuli)
                )
                auditory_stimulus = (
                    random.choice(available_auditory)
                    if available_auditory
                    else random.choice(self.config.auditory_stimuli)
                )

            # Create stimulus
            stimulus = {
                "trial_number": trial,
                "visual_stimulus": visual_stimulus,
                "auditory_stimulus": auditory_stimulus,
                "visual_target": is_target
                and (
                    len(self.visual_history) >= n_level
                    and visual_stimulus == self.visual_history[-n_level]
                ),
                "auditory_target": is_target
                and (
                    len(self.auditory_history) >= n_level
                    and auditory_stimulus == self.auditory_history[-n_level]
                ),
                "is_target": is_target,
                "n_level": n_level,
                "stimulus_type": "dual",
            }

            sequence.append(stimulus)

            # Update history
            self.visual_history.append(visual_stimulus)
            self.auditory_history.append(auditory_stimulus)

        return sequence


class DualNBackTask(TrialBasedTask):
    """Dual N-back task implementation."""

    def __init__(self, config: Optional[DualNBackConfig] = None):
        super().__init__(config)
        self.config = config or DualNBackConfig()
        self.stimulus_generator = NBackStimulus(self.config)
        self.performance_by_n = {}
        self.working_memory_load = []

    def setup(self, **kwargs):
        """Set up the Dual N-back task."""
        super().setup(**kwargs)
        self.stimulus_generator = NBackStimulus(self.config)
        self.performance_by_n = {}
        self.working_memory_load = []

    def generate_trial_sequence(self) -> List[Dict[str, Any]]:
        """Generate trial sequence for N-back task."""
        # Generate stimulus sequence
        sequence = self.stimulus_generator.generate_stimulus_sequence(
            self.config.n_trials, self.config.current_n_level
        )

        # Add practice trials at the beginning
        practice_sequence = self.stimulus_generator.generate_stimulus_sequence(
            self.config.practice_trials, 1  # Practice with 1-back
        )

        # Mark practice trials
        for trial in practice_sequence:
            trial["is_practice"] = True

        # Mark main task trials
        for trial in sequence:
            trial["is_practice"] = False

        # Combine sequences
        full_sequence = practice_sequence + sequence

        # Add trial numbers
        for i, trial in enumerate(full_sequence):
            trial["overall_trial_number"] = i

        return full_sequence

    def generate_trial_parameters(
        self, participant_id: int, trial_number: int
    ) -> Dict[str, Any]:
        """Generate parameters for a specific trial."""
        base_params = super().generate_trial_parameters(participant_id, trial_number)

        # Get trial from sequence
        if trial_number < len(self.trial_sequence):
            trial_data = self.trial_sequence[trial_number]
        else:
            # Default trial
            trial_data = {
                "visual_stimulus": "A",
                "auditory_stimulus": "1",
                "visual_target": False,
                "auditory_target": False,
                "is_target": False,
                "n_level": self.config.current_n_level,
                "is_practice": False,
            }

        base_params.update(
            {
                "visual_stimulus": trial_data["visual_stimulus"],
                "auditory_stimulus": trial_data["auditory_stimulus"],
                "visual_target": trial_data["visual_target"],
                "auditory_target": trial_data["auditory_target"],
                "is_target": trial_data["is_target"],
                "n_level": trial_data["n_level"],
                "is_practice": trial_data.get("is_practice", False),
                "stimulus_duration_ms": self.config.stimulus_duration_ms,
                "isi_ms": self.config.inter_stimulus_interval_ms,
            }
        )

        return base_params

    def process_response(
        self, response: Any, correct_response: Any, trial_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Process dual n-back response."""
        # Response can be a tuple (visual, auditory) or dict
        visual_response = None
        auditory_response = None

        if isinstance(response, tuple) and len(response) == 2:
            visual_response, auditory_response = response
        elif isinstance(response, dict):
            visual_response = response.get("visual")
            auditory_response = response.get("auditory")
        elif isinstance(response, (bool, int, str)):
            # Single response (assume visual)
            visual_response = response

        # Get correct responses from trial data or use defaults
        visual_correct = False
        auditory_correct = False
        n_level = 2
        is_practice = False

        if trial_data:
            visual_correct = trial_data.get("visual_target", False)
            auditory_correct = trial_data.get("auditory_target", False)
            n_level = trial_data.get("n_level", 2)
            is_practice = trial_data.get("is_practice", False)

        # Calculate accuracy
        visual_accuracy = (
            (visual_response == visual_correct)
            if visual_response is not None
            else False
        )
        auditory_accuracy = (
            (auditory_response == auditory_correct)
            if auditory_response is not None
            else False
        )
        overall_accuracy = (
            visual_accuracy and auditory_accuracy
            if auditory_response is not None
            else visual_accuracy
        )

        # Store performance by n-level
        if n_level not in self.performance_by_n:
            self.performance_by_n[n_level] = {
                "visual_accuracy": [],
                "auditory_accuracy": [],
                "overall_accuracy": [],
                "reaction_times": [],
            }

        self.performance_by_n[n_level]["visual_accuracy"].append(
            1 if visual_accuracy else 0
        )
        self.performance_by_n[n_level]["auditory_accuracy"].append(
            1 if auditory_accuracy else 0
        )
        self.performance_by_n[n_level]["overall_accuracy"].append(
            1 if overall_accuracy else 0
        )
        # Don't store RT here since it's not available yet

        # Calculate working memory load
        wm_load = n_level
        self.working_memory_load.append(wm_load)

        # Calculate confidence based on accuracy and n-level
        base_confidence = 0.6 if overall_accuracy else 0.3
        base_confidence -= (n_level - 1) * 0.05  # Lower confidence for higher n-levels

        return {
            "response": response,
            "visual_response": visual_response,
            "auditory_response": auditory_response,
            "accuracy": 1 if overall_accuracy else 0,
            "visual_accuracy": 1 if visual_accuracy else 0,
            "auditory_accuracy": 1 if auditory_accuracy else 0,
            "reaction_time_ms": 0,  # Will be filled by simulate_response
            "confidence": base_confidence,
            "visual_target": visual_correct,
            "auditory_target": auditory_correct,
            "n_level": n_level,
            "is_practice": is_practice,
        }

    def simulate_response(self, trial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate participant N-back performance."""
        n_level = trial_data["n_level"]
        visual_target = trial_data["visual_target"]
        auditory_target = trial_data["auditory_target"]
        is_practice = trial_data.get("is_practice", False)

        # Base accuracy decreases with n-level
        base_accuracy = 0.9 - (n_level * 0.15)
        base_accuracy = max(0.3, base_accuracy)

        # Practice trials have slightly better performance
        if is_practice:
            base_accuracy += 0.1

        # Calculate response probabilities
        visual_response_prob = base_accuracy
        auditory_response_prob = base_accuracy * 0.9  # Slightly harder for auditory

        # Generate responses
        if random.random() < visual_response_prob:
            visual_response = visual_target
        else:
            visual_response = not visual_target

        if random.random() < auditory_response_prob:
            auditory_response = auditory_target
        else:
            auditory_response = not auditory_target

        # Calculate reaction time (longer for higher n-levels)
        base_rt = 800 + (n_level * 150)
        rt = max(400, np.random.normal(base_rt, 200))

        # Calculate confidence
        actual_visual_accuracy = visual_response == visual_target
        actual_auditory_accuracy = auditory_response == auditory_target
        overall_correct = actual_visual_accuracy and actual_auditory_accuracy

        confidence = 0.8 if overall_correct else 0.4
        confidence *= 1.0 - n_level * 0.1  # Lower confidence for harder trials

        return {
            "response": (visual_response, auditory_response),
            "reaction_time_ms": int(rt),
            "confidence": confidence,
            "timestamp": time.time(),
        }

    def compute_participant_summary(
        self, trials: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compute comprehensive summary for N-back task."""
        base_summary = super().compute_participant_summary(trials)

        if not trials:
            return base_summary

        df = pd.DataFrame(trials)

        # N-back specific metrics
        summary = {
            **base_summary,
            "overall_accuracy": 0,
            "mean_reaction_time": 0,
            "n_level_performance": {},
            "working_memory_capacity": {},
            "modality_performance": {},
        }

        # Filter out practice trials for main analysis
        main_trials = (
            df[df["is_practice"] == False] if "is_practice" in df.columns else df
        )

        # Overall metrics
        if "accuracy" in main_trials.columns:
            summary["overall_accuracy"] = main_trials["accuracy"].mean()

        if "reaction_time_ms" in main_trials.columns:
            summary["mean_reaction_time"] = main_trials["reaction_time_ms"].mean()

        # Performance by n-level
        for n_level in sorted(main_trials["n_level"].unique()):
            n_level_data = main_trials[main_trials["n_level"] == n_level]
            if len(n_level_data) > 0:
                accuracy = (
                    n_level_data["accuracy"].mean()
                    if "accuracy" in n_level_data.columns
                    else 0
                )
                mean_rt = (
                    n_level_data["reaction_time_ms"].mean()
                    if "reaction_time_ms" in n_level_data.columns
                    else 0
                )
                visual_acc = (
                    n_level_data["visual_accuracy"].mean()
                    if "visual_accuracy" in n_level_data.columns
                    else 0
                )
                auditory_acc = (
                    n_level_data["auditory_accuracy"].mean()
                    if "auditory_accuracy" in n_level_data.columns
                    else 0
                )

                summary["n_level_performance"][f"n_{n_level}"] = {
                    "accuracy": accuracy,
                    "mean_rt": mean_rt,
                    "visual_accuracy": visual_acc,
                    "auditory_accuracy": auditory_acc,
                    "n_trials": len(n_level_data),
                }

        # Working memory capacity estimation
        # Find highest n-level with performance above chance
        chance_level = 0.5
        max_n = 0
        for n_level, performance in self.performance_by_n.items():
            if performance["overall_accuracy"]:
                mean_acc = np.mean(performance["overall_accuracy"])
                if mean_acc > chance_level:
                    max_n = n_level

        summary["working_memory_capacity"] = {
            "estimated_capacity": max_n,
            "chance_level": chance_level,
            "performance_by_n": {
                n: np.mean(perf["overall_accuracy"]) if perf["overall_accuracy"] else 0
                for n, perf in self.performance_by_n.items()
            },
        }

        # Modality performance
        if "visual_accuracy" in main_trials.columns:
            summary["modality_performance"]["visual"] = {
                "accuracy": main_trials["visual_accuracy"].mean(),
                "n_trials": len(main_trials),
            }

        if "auditory_accuracy" in main_trials.columns:
            summary["modality_performance"]["auditory"] = {
                "accuracy": main_trials["auditory_accuracy"].mean(),
                "n_trials": len(main_trials),
            }

        return summary


def run_dual_n_back_experiment(**kwargs):
    """Run the Dual N-back experiment."""
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
        if hasattr(DualNBackConfig, config_key):
            config_params[config_key] = value

    # Create config and experiment
    config = DualNBackConfig(**config_params)
    experiment = DualNBackTask(config)

    # Set up and run experiment
    experiment.setup()
    results = experiment.run_experiment()

    # Save results if output file specified
    if kwargs.get("output_file"):
        experiment.save_data(kwargs["output_file"])

    return experiment


if __name__ == "__main__":
    # Example usage
    config = DualNBackConfig(
        n_trials=100, n_participants=5, current_n_level=2, target_probability=0.3
    )

    experiment = DualNBackTask(config)
    experiment.setup()
    results = experiment.run_experiment()

    print("Dual N-back experiment completed!")
    print(f"Results shape: {results.shape}")

    # Print summary for first participant
    if experiment.participant_data:
        first_participant = list(experiment.participant_data.keys())[0]
        summary = experiment.participant_data[first_participant]["summary"]
        print(f"\nParticipant {first_participant} Summary:")
        print(f"Overall Accuracy: {summary.get('overall_accuracy', 0):.3f}")
        print(f"Mean Reaction Time: {summary.get('mean_reaction_time', 0):.1f} ms")
        print(
            f"Working Memory Capacity: {summary.get('working_memory_capacity', {}).get('estimated_capacity', 0)}"
        )
        print(f"N-level Performance: {summary.get('n_level_performance', {})}")
