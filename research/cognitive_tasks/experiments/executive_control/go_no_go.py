"""
Go/No-Go implementation.

The Go/No-Go task measures response inhibition and cognitive control.
Participants must respond to "Go" stimuli and withhold responses to "No-Go"
stimuli. Commission errors (responding to No-Go) and omission errors (failing
to respond to Go) reveal inhibitory control capabilities.

APGI Integration:
- θₜ (threshold): Response inhibition threshold
- π (precision): Action selection precision
- ε (prediction error): Inhibition failure prediction error
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
class GoNoGoConfig(TrialBasedTaskConfig):
    """Configuration for Go/No-Go experiment."""

    n_trials: int = 200
    stimulus_duration_ms: int = 500
    response_window_ms: int = 1000
    inter_trial_interval_ms: int = 1500

    # Task parameters
    go_probability: float = 0.7  # Probability of Go trials
    nogo_probability: float = 0.3  # Probability of No-Go trials

    # Stimulus parameters
    go_stimuli: List[str] = None  # Stimuli for Go trials
    nogo_stimuli: List[str] = None  # Stimuli for No-Go trials
    stimulus_types: List[str] = None  # Types of stimuli

    # Response parameters
    go_response: str = "space"  # Response key for Go trials
    response_timeout_ms: int = 2000  # Maximum time to respond

    def __post_init__(self):
        if self.go_stimuli is None:
            self.go_stimuli = ["O", "X", "+", "→"]  # Common Go stimuli

        if self.nogo_stimuli is None:
            self.nogo_stimuli = ["Q", "Y", "-", "■"]  # Common No-Go stimuli

        if self.stimulus_types is None:
            self.stimulus_types = ["shapes", "letters", "arrows"]


class GoNoGoStimulus:
    """Generate Go/No-Go stimuli."""

    def __init__(self, config: GoNoGoConfig):
        self.config = config

    def generate_trial(self, trial_type: str) -> Dict[str, Any]:
        """Generate a single Go/No-Go trial."""
        if trial_type == "go":
            stimulus = random.choice(self.config.go_stimuli)
            is_go = True
        elif trial_type == "nogo":
            stimulus = random.choice(self.config.nogo_stimuli)
            is_go = False
        else:
            # Random selection based on probabilities
            if random.random() < self.config.go_probability:
                stimulus = random.choice(self.config.go_stimuli)
                is_go = True
            else:
                stimulus = random.choice(self.config.nogo_stimuli)
                is_go = False

        trial = {
            "stimulus": stimulus,
            "is_go": is_go,
            "trial_type": "go" if is_go else "nogo",
            "correct_response": self.config.go_response if is_go else None,
            "response_required": is_go,
        }

        return trial


class GoNoGoTask(TrialBasedTask):
    """Go/No-Go task implementation."""

    def __init__(self, config: Optional[GoNoGoConfig] = None):
        super().__init__(config)
        self.config = config or GoNoGoConfig()
        self.stimulus_generator = GoNoGoStimulus(self.config)
        self.inhibition_data = {}

    def setup(self, **kwargs):
        """Set up the Go/No-Go task."""
        super().setup(**kwargs)
        self.stimulus_generator = GoNoGoStimulus(self.config)
        self.inhibition_data = {}

    def generate_trial_sequence(self) -> List[Dict[str, Any]]:
        """Generate balanced trial sequence."""
        trials = []

        # Calculate number of Go and No-Go trials
        n_go = int(self.config.n_trials * self.config.go_probability)
        n_nogo = self.config.n_trials - n_go

        # Create Go trials
        for _ in range(n_go):
            trials.append({"trial_type": "go", "condition": "go"})

        # Create No-Go trials
        for _ in range(n_nogo):
            trials.append({"trial_type": "nogo", "condition": "nogo"})

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
            trial_config = {"trial_type": "go", "condition": "go"}

        # Generate stimulus
        stimulus = self.stimulus_generator.generate_trial(trial_config["trial_type"])

        base_params.update(
            {
                "stimulus": stimulus["stimulus"],
                "is_go": stimulus["is_go"],
                "trial_type": stimulus["trial_type"],
                "correct_response": stimulus["correct_response"],
                "response_required": stimulus["response_required"],
                "condition": trial_config["condition"],
                "stimulus_duration_ms": self.config.stimulus_duration_ms,
                "response_window_ms": self.config.response_window_ms,
            }
        )

        return base_params

    def process_response(
        self, response: Any, correct_response: Any, trial_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Process Go/No-Go response."""
        # Get trial data from parameters if available
        if trial_data:
            is_go = trial_data.get("is_go", True)
            correct_response = trial_data.get("correct_response")
            response_required = trial_data.get("response_required", True)
            stimulus = trial_data.get("stimulus", "unknown")
            condition = trial_data.get("condition", "default")
        else:
            # Default values
            is_go = True
            correct_response = self.config.go_response
            response_required = True
            stimulus = "unknown"
            condition = "default"

        # Handle different response formats
        if isinstance(response, str):
            response_str = response.lower()
        elif isinstance(response, bool):
            response_str = "space" if response else "no_response"
        else:
            response_str = str(response).lower()

        # Determine response type
        if response_str == self.config.go_response.lower():
            made_response = True
        else:
            made_response = False

        # Calculate accuracy
        if is_go:
            # Go trial: correct if response was made
            is_correct = made_response
            error_type = "omission" if not made_response else None
        else:
            # No-Go trial: correct if no response was made
            is_correct = not made_response
            error_type = "commission" if made_response else None

        # Store inhibition data
        trial_type = "go" if is_go else "nogo"
        if trial_type not in self.inhibition_data:
            self.inhibition_data[trial_type] = {
                "accuracy": [],
                "reaction_times": [],
                "responses": [],
            }

        self.inhibition_data[trial_type]["accuracy"].append(1 if is_correct else 0)
        self.inhibition_data[trial_type]["responses"].append(made_response)

        if made_response:
            rt = trial_data.get("reaction_time_ms", 800) if trial_data else 800
            self.inhibition_data[trial_type]["reaction_times"].append(rt)

        # Calculate confidence based on accuracy and trial type
        base_confidence = 0.8 if is_correct else 0.3
        if not is_go and is_correct:
            base_confidence += 0.1  # Higher confidence for successful inhibition
        elif not is_go and not is_correct:
            base_confidence -= 0.2  # Lower confidence for commission errors

        return {
            "response": response_str,
            "accuracy": 1 if is_correct else 0,
            "reaction_time_ms": (
                trial_data.get("reaction_time_ms", 800) if trial_data else 800
            ),
            "confidence": base_confidence,
            "made_response": made_response,
            "stimulus": stimulus,
            "is_go": is_go,
            "trial_type": trial_type,
            "error_type": error_type,
            "correct_response": correct_response,
            "condition": condition,
        }

    def simulate_response(self, trial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate participant Go/No-Go performance."""
        is_go = trial_data["is_go"]
        stimulus = trial_data["stimulus"]

        # Base response probabilities
        go_hit_rate = 0.95  # Probability of responding to Go trials
        nogo_commission_rate = 0.15  # Probability of false alarm on No-Go trials

        if is_go:
            # Go trial
            if random.random() < go_hit_rate:
                made_response = True
                rt = np.random.normal(450, 100)  # Fast responses for Go trials
            else:
                made_response = False  # Omission error
                rt = 0
        else:
            # No-Go trial
            if random.random() < nogo_commission_rate:
                made_response = True  # Commission error
                rt = np.random.normal(350, 80)  # Very fast responses (prepotent)
            else:
                made_response = (
                    True  # Successful inhibition (still register as "response" for RT)
                )
                rt = np.random.normal(500, 120)  # Slower for inhibition

        rt = max(200, rt) if rt > 0 else 0

        # Calculate confidence
        if is_go:
            confidence = 0.8 if made_response else 0.2  # Low confidence for omissions
        else:
            confidence = (
                0.9 if not made_response else 0.3
            )  # High confidence for successful inhibition

        return {
            "response": self.config.go_response if made_response else "no_response",
            "reaction_time_ms": int(rt),
            "confidence": confidence,
            "timestamp": time.time(),
        }

    def compute_participant_summary(
        self, trials: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compute comprehensive summary for Go/No-Go task."""
        base_summary = super().compute_participant_summary(trials)

        if not trials:
            return base_summary

        df = pd.DataFrame(trials)

        # Go/No-Go specific metrics
        summary = {
            **base_summary,
            "overall_accuracy": 0,
            "mean_reaction_time": 0,
            "inhibition_metrics": {},
            "trial_type_performance": {},
            "error_analysis": {},
        }

        # Overall metrics
        if "accuracy" in df.columns:
            summary["overall_accuracy"] = df["accuracy"].mean()

        # Calculate mean RT for Go trials only (responses to Go stimuli)
        go_trials = df[df["is_go"] == True]
        go_responses = go_trials[go_trials["made_response"] == True]

        if len(go_responses) > 0 and "reaction_time_ms" in go_responses.columns:
            summary["mean_reaction_time"] = go_responses["reaction_time_ms"].mean()

        # Performance by trial type
        for trial_type in ["go", "nogo"]:
            type_data = df[df["trial_type"] == trial_type]
            if len(type_data) > 0:
                accuracy = (
                    type_data["accuracy"].mean()
                    if "accuracy" in type_data.columns
                    else 0
                )
                response_rate = (
                    type_data["made_response"].mean()
                    if "made_response" in type_data.columns
                    else 0
                )

                # RT for this trial type
                type_responses = type_data[type_data["made_response"] == True]
                mean_rt = (
                    type_responses["reaction_time_ms"].mean()
                    if len(type_responses) > 0
                    and "reaction_time_ms" in type_responses.columns
                    else 0
                )

                summary["trial_type_performance"][trial_type] = {
                    "accuracy": accuracy,
                    "response_rate": response_rate,
                    "mean_rt": mean_rt,
                    "n_trials": len(type_data),
                }

        # Inhibition metrics
        go_data = df[df["trial_type"] == "go"]
        nogo_data = df[df["trial_type"] == "nogo"]

        if len(go_data) > 0 and len(nogo_data) > 0:
            # Hit rate (correct responses to Go trials)
            hit_rate = (
                go_data["accuracy"].mean() if "accuracy" in go_data.columns else 0
            )

            # Commission rate (incorrect responses to No-Go trials)
            commission_rate = (
                1 - nogo_data["accuracy"].mean()
                if "accuracy" in nogo_data.columns
                else 0
            )

            # Omission rate (missed Go trials)
            omission_rate = 1 - hit_rate

            summary["inhibition_metrics"] = {
                "hit_rate": hit_rate,
                "commission_rate": commission_rate,
                "omission_rate": omission_rate,
                "inhibition_success_rate": 1 - commission_rate,
                "d_prime": self._calculate_d_prime(hit_rate, commission_rate),
                "response_bias": self._calculate_response_bias(
                    hit_rate, commission_rate
                ),
            }

        # Error analysis
        commission_errors = df[
            (df["trial_type"] == "nogo") & (df["made_response"] == True)
        ]
        omission_errors = df[
            (df["trial_type"] == "go") & (df["made_response"] == False)
        ]

        if len(commission_errors) > 0:
            summary["error_analysis"]["commission_errors"] = {
                "count": len(commission_errors),
                "rate": (
                    len(commission_errors) / len(nogo_data) if len(nogo_data) > 0 else 0
                ),
                "mean_rt": (
                    commission_errors["reaction_time_ms"].mean()
                    if "reaction_time_ms" in commission_errors.columns
                    else 0
                ),
                "mean_confidence": (
                    commission_errors["confidence"].mean()
                    if "confidence" in commission_errors.columns
                    else 0
                ),
            }

        if len(omission_errors) > 0:
            summary["error_analysis"]["omission_errors"] = {
                "count": len(omission_errors),
                "rate": len(omission_errors) / len(go_data) if len(go_data) > 0 else 0,
                "mean_confidence": (
                    omission_errors["confidence"].mean()
                    if "confidence" in omission_errors.columns
                    else 0
                ),
            }

        return summary

    def _calculate_d_prime(self, hit_rate: float, commission_rate: float) -> float:
        """Calculate d' for signal detection."""
        # Correct rejection rate = 1 - commission_rate
        correct_rejection_rate = 1 - commission_rate

        # Avoid extreme values
        hit_rate = np.clip(hit_rate, 0.01, 0.99)
        correct_rejection_rate = np.clip(correct_rejection_rate, 0.01, 0.99)

        try:
            from scipy import stats

            d_prime = stats.norm.ppf(hit_rate) - stats.norm.ppf(
                1 - correct_rejection_rate
            )
            return d_prime
        except:
            return 0.0

    def _calculate_response_bias(
        self, hit_rate: float, commission_rate: float
    ) -> float:
        """Calculate response bias (criterion)."""
        correct_rejection_rate = 1 - commission_rate

        # Avoid extreme values
        hit_rate = np.clip(hit_rate, 0.01, 0.99)
        correct_rejection_rate = np.clip(correct_rejection_rate, 0.01, 0.99)

        try:
            from scipy import stats

            criterion = (
                -(stats.norm.ppf(hit_rate) + stats.norm.ppf(correct_rejection_rate)) / 2
            )
            return criterion
        except:
            return 0.0


def run_go_no_go_experiment(**kwargs):
    """Run the Go/No-Go experiment."""
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
        if hasattr(GoNoGoConfig, config_key):
            config_params[config_key] = value

    # Create config and experiment
    config = GoNoGoConfig(**config_params)
    experiment = GoNoGoTask(config)

    # Set up and run experiment
    experiment.setup()
    results = experiment.run_experiment()

    # Save results if output file specified
    if kwargs.get("output_file"):
        experiment.save_data(kwargs["output_file"])

    return experiment


if __name__ == "__main__":
    # Example usage
    config = GoNoGoConfig(
        n_trials=150, n_participants=5, go_probability=0.7, nogo_probability=0.3
    )

    experiment = GoNoGoTask(config)
    experiment.setup()
    results = experiment.run_experiment()

    print("Go/No-Go experiment completed!")
    print(f"Results shape: {results.shape}")

    # Print summary for first participant
    if experiment.participant_data:
        first_participant = list(experiment.participant_data.keys())[0]
        summary = experiment.participant_data[first_participant]["summary"]
        print(f"\nParticipant {first_participant} Summary:")
        print(f"Overall Accuracy: {summary.get('overall_accuracy', 0):.3f}")
        print(f"Mean Reaction Time: {summary.get('mean_reaction_time', 0):.1f} ms")
        print(
            f"Commission Rate: {summary.get('inhibition_metrics', {}).get('commission_rate', 0):.3f}"
        )
        print(
            f"Inhibition Success Rate: {summary.get('inhibition_metrics', {}).get('inhibition_success_rate', 0):.3f}"
        )
        print(f"Trial Type Performance: {summary.get('trial_type_performance', {})}")
