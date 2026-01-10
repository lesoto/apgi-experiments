"""
Stop Signal implementation.

The Stop Signal Task (SST) measures response inhibition and the ability to cancel
prepotent responses. Participants typically respond to Go stimuli, but must
withhold their response when a stop signal occurs. The stop-signal reaction
time (SSRT) estimates the time needed for inhibition.

APGI Integration:
- θₜ (threshold): Response cancellation threshold
- π (precision): Inhibition precision
- ε (prediction error): Stop signal prediction error
- β (inverse temperature): Response consistency under conflict
"""

import random
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import time

from .. import TrialBasedTask, TrialBasedTaskConfig


@dataclass
class StopSignalConfig(TrialBasedTaskConfig):
    """Configuration for Stop Signal experiment."""

    n_trials: int = 200
    go_stimulus_duration_ms: int = 1000
    stop_signal_delay_ms: int = 250  # Initial SSD
    response_window_ms: int = 1500
    inter_trial_interval_ms: int = 2000

    # Stop signal parameters
    stop_probability: float = 0.25  # Probability of stop trials
    ssd_adjustment: bool = True  # Whether to track SSD adjustment
    min_ssd: int = 50  # Minimum stop signal delay
    max_ssd: int = 500  # Maximum stop signal delay
    ssd_step: int = 50  # SSD adjustment step

    # Stimulus parameters
    go_stimuli: List[str] = None  # Go stimuli
    stop_stimulus: str = None  # Stop signal

    # Response parameters
    go_response: str = "space"  # Response for Go trials
    tracking_method: str = "integration"  # integration or mean RT method

    def __post_init__(self):
        if self.go_stimuli is None:
            self.go_stimuli = ["→", "O", "X", "→"]  # Common Go stimuli

        if self.stop_stimulus is None:
            self.stop_stimulus = "■"  # Common stop signal


class StopSignalStimulus:
    """Generate Stop Signal stimuli."""

    def __init__(self, config: StopSignalConfig):
        self.config = config
        self.current_ssd = config.stop_signal_delay_ms
        self.recent_go_rts = []

    def generate_trial(self, is_stop: bool = False) -> Dict[str, Any]:
        """Generate a single Stop Signal trial."""
        go_stimulus = random.choice(self.config.go_stimuli)

        if is_stop:
            # Stop trial
            trial = {
                "go_stimulus": go_stimulus,
                "stop_signal": self.config.stop_stimulus,
                "is_stop": True,
                "ssd": self.current_ssd,
                "correct_response": None,  # No response on successful stop
                "trial_type": "stop",
            }
        else:
            # Go trial
            trial = {
                "go_stimulus": go_stimulus,
                "stop_signal": None,
                "is_stop": False,
                "ssd": None,
                "correct_response": self.config.go_response,
                "trial_type": "go",
            }

        return trial

    def adjust_ssd(self, was_successful_stop: bool, go_rt: float = None):
        """Adjust SSD based on performance."""
        if not self.config.ssd_adjustment:
            return

        if was_successful_stop:
            # Successful stop - increase SSD (make it harder)
            self.current_ssd = min(
                self.current_ssd + self.config.ssd_step, self.config.max_ssd
            )
        else:
            # Failed stop - decrease SSD (make it easier)
            self.current_ssd = max(
                self.current_ssd - self.config.ssd_step, self.config.min_ssd
            )

    def record_go_rt(self, rt: float):
        """Record Go RT for tracking."""
        self.recent_go_rts.append(rt)
        # Keep only recent RTs
        if len(self.recent_go_rts) > 10:
            self.recent_go_rts = self.recent_go_rts[-10:]


class StopSignalTask(TrialBasedTask):
    """Stop Signal task implementation."""

    def __init__(self, config: Optional[StopSignalConfig] = None):
        super().__init__(config)
        self.config = config or StopSignalConfig()
        self.stimulus_generator = StopSignalStimulus(self.config)
        self.inhibition_data = {}
        self.ssd_history = []

    def setup(self, **kwargs):
        """Set up the Stop Signal task."""
        super().setup(**kwargs)
        self.stimulus_generator = StopSignalStimulus(self.config)
        self.inhibition_data = {}
        self.ssd_history = []

    def generate_trial_sequence(self) -> List[Dict[str, Any]]:
        """Generate trial sequence with appropriate stop trial distribution."""
        trials = []

        # Calculate number of stop and go trials
        n_stop = int(self.config.n_trials * self.config.stop_probability)
        n_go = self.config.n_trials - n_stop

        # Create trials
        for _ in range(n_go):
            trials.append({"is_stop": False, "condition": "go"})

        for _ in range(n_stop):
            trials.append({"is_stop": True, "condition": "stop"})

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
            trial_config = {"is_stop": False, "condition": "go"}

        # Generate stimulus
        stimulus = self.stimulus_generator.generate_trial(trial_config["is_stop"])

        base_params.update(
            {
                "go_stimulus": stimulus["go_stimulus"],
                "stop_signal": stimulus["stop_signal"],
                "is_stop": stimulus["is_stop"],
                "ssd": stimulus["ssd"],
                "correct_response": stimulus["correct_response"],
                "trial_type": stimulus["trial_type"],
                "condition": trial_config["condition"],
                "go_stimulus_duration_ms": self.config.go_stimulus_duration_ms,
                "response_window_ms": self.config.response_window_ms,
            }
        )

        return base_params

    def process_response(
        self, response: Any, correct_response: Any, trial_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Process Stop Signal response."""
        # Get trial data from parameters if available
        if trial_data:
            is_stop = trial_data.get("is_stop", False)
            go_stimulus = trial_data.get("go_stimulus", "unknown")
            ssd = trial_data.get("ssd", 200)
            condition = trial_data.get("condition", "default")
            reaction_time_ms = trial_data.get("reaction_time_ms", 800)
        else:
            # Default values
            is_stop = False
            go_stimulus = "unknown"
            ssd = 200
            condition = "default"
            reaction_time_ms = 800

        # Handle different response formats
        if isinstance(response, str):
            response_str = response.lower()
        elif isinstance(response, bool):
            response_str = self.config.go_response if response else "no_response"
        else:
            response_str = str(response).lower()

        made_response = response_str == self.config.go_response.lower()
        rt = reaction_time_ms

        # Calculate accuracy and outcome
        if is_stop:
            # Stop trial
            if not made_response:
                # Successful inhibition
                is_correct = True
                outcome = "successful_stop"
                self.stimulus_generator.adjust_ssd(True)
            else:
                # Failed inhibition (responded on stop trial)
                is_correct = False
                outcome = "failed_stop"
                self.stimulus_generator.adjust_ssd(False)
        else:
            # Go trial
            if made_response:
                # Correct response
                is_correct = True
                outcome = "correct_go"
                self.stimulus_generator.record_go_rt(rt)
            else:
                # Omission error
                is_correct = False
                outcome = "omission_error"

        # Store SSD history
        if is_stop:
            self.ssd_history.append(
                {"ssd": ssd, "outcome": outcome, "rt": rt if made_response else None}
            )

        # Store inhibition data
        trial_type = "stop" if is_stop else "go"
        if trial_type not in self.inhibition_data:
            self.inhibition_data[trial_type] = {
                "accuracy": [],
                "reaction_times": [],
                "outcomes": [],
            }

        self.inhibition_data[trial_type]["accuracy"].append(1 if is_correct else 0)
        self.inhibition_data[trial_type]["outcomes"].append(outcome)

        if made_response:
            self.inhibition_data[trial_type]["reaction_times"].append(rt)

        # Calculate confidence
        base_confidence = 0.8 if is_correct else 0.3
        if is_stop and not made_response:
            base_confidence += 0.1  # Higher confidence for successful inhibition
        elif is_stop and made_response:
            base_confidence -= 0.2  # Lower confidence for failed inhibition

        return {
            "response": response_str,
            "accuracy": 1 if is_correct else 0,
            "reaction_time_ms": rt,
            "confidence": base_confidence,
            "made_response": made_response,
            "go_stimulus": go_stimulus,
            "is_stop": is_stop,
            "ssd": ssd,
            "outcome": outcome,
            "correct_response": correct_response,
            "condition": condition,
        }

    def simulate_response(self, trial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate participant Stop Signal performance."""
        is_stop = trial_data["is_stop"]
        ssd = trial_data.get("ssd", 250)

        if not is_stop:
            # Go trial - respond quickly
            go_rt = np.random.normal(450, 80)
            go_rt = max(250, go_rt)

            return {
                "response": self.config.go_response,
                "reaction_time_ms": int(go_rt),
                "confidence": 0.8,
                "timestamp": time.time(),
            }
        else:
            # Stop trial - race between go and stop processes
            # Go process time
            go_process_time = np.random.normal(450, 80)

            # Stop process time = SSD + stop_process_duration
            stop_process_duration = np.random.normal(200, 50)
            stop_process_time = ssd + stop_process_duration

            if stop_process_time < go_process_time:
                # Successful inhibition
                return {
                    "response": "no_response",
                    "reaction_time_ms": 0,
                    "confidence": 0.9,
                    "timestamp": time.time(),
                }
            else:
                # Failed inhibition - response occurs before stop completes
                failed_stop_rt = go_process_time
                return {
                    "response": self.config.go_response,
                    "reaction_time_ms": int(failed_stop_rt),
                    "confidence": 0.4,
                    "timestamp": time.time(),
                }

    def compute_participant_summary(
        self, trials: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compute comprehensive summary for Stop Signal task."""
        base_summary = super().compute_participant_summary(trials)

        if not trials:
            return base_summary

        df = pd.DataFrame(trials)

        # Stop Signal specific metrics
        summary = {
            **base_summary,
            "overall_accuracy": 0,
            "mean_go_rt": 0,
            "stop_signal_metrics": {},
            "ssrt_estimate": 0,
            "inhibition_function": {},
        }

        # Overall metrics
        if "accuracy" in df.columns:
            summary["overall_accuracy"] = df["accuracy"].mean()

        # Go trial RT (only correct Go trials)
        go_trials = df[df["trial_type"] == "go"]
        correct_go = (
            go_trials[go_trials["accuracy"] == 1] if len(go_trials) > 0 else go_trials
        )

        if len(correct_go) > 0 and "reaction_time_ms" in correct_go.columns:
            summary["mean_go_rt"] = correct_go["reaction_time_ms"].mean()

        # Stop trial analysis
        stop_trials = df[df["trial_type"] == "stop"]
        if len(stop_trials) > 0:
            successful_stops = stop_trials[stop_trials["outcome"] == "successful_stop"]
            failed_stops = stop_trials[stop_trials["outcome"] == "failed_stop"]

            summary["stop_signal_metrics"] = {
                "n_stop_trials": len(stop_trials),
                "successful_stop_rate": (
                    len(successful_stops) / len(stop_trials)
                    if len(stop_trials) > 0
                    else 0
                ),
                "failed_stop_rate": (
                    len(failed_stops) / len(stop_trials) if len(stop_trials) > 0 else 0
                ),
                "mean_failed_stop_rt": (
                    failed_stops["reaction_time_ms"].mean()
                    if len(failed_stops) > 0
                    and "reaction_time_ms" in failed_stops.columns
                    else 0
                ),
            }

        # Calculate SSRT using integration method
        if len(self.ssd_history) > 0:
            ssd_df = pd.DataFrame(self.ssd_history)
            successful_stops_df = ssd_df[ssd_df["outcome"] == "successful_stop"]
            failed_stops_df = ssd_df[ssd_df["outcome"] == "failed_stop"]

            if len(successful_stops_df) > 0 and len(failed_stops_df) > 0:
                # Integration method: SSRT = mean SSD - mean RT of failed stops
                mean_ssd_successful = successful_stops_df["ssd"].mean()
                mean_rt_failed = (
                    failed_stops_df["rt"].mean()
                    if "rt" in failed_stops_df.columns
                    else 0
                )

                ssrt_integration = mean_ssd_successful - mean_rt_failed

                # Alternative method: mean RT method
                if summary["mean_go_rt"] > 0:
                    # Calculate inhibition function at each SSD
                    ssd_groups = (
                        successful_stops_df.groupby("ssd")
                        .agg({"n_successful": "size", "n_total": lambda x: len(x)})
                        .reset_index()
                    )

                    # Merge with total stop trials at each SSD
                    total_by_ssd = (
                        ssd_df.groupby("ssd").size().reset_index(name="n_total")
                    )
                    ssd_groups = ssd_groups.merge(total_by_ssd, on="ssd", how="right")
                    ssd_groups["inhibition_rate"] = (
                        ssd_groups["n_successful"] / ssd_groups["n_total"]
                    )

                    # Find SSD where inhibition rate = 0.5
                    if len(ssd_groups) > 0:
                        ssd_50 = (
                            ssd_groups.loc[
                                ssd_groups["inhibition_rate"].idxmin(), "ssd"
                            ]
                            if len(ssd_groups) > 0
                            else mean_ssd_successful
                        )
                        ssrt_mean_method = ssd_50 - summary["mean_go_rt"]
                    else:
                        ssrt_mean_method = ssrt_integration
                else:
                    ssrt_mean_method = ssrt_integration

                summary["ssrt_estimate"] = {
                    "integration_method": ssrt_integration,
                    "mean_rt_method": ssrt_mean_method,
                    "preferred_ssrt": ssrt_integration,  # Integration method is preferred
                }

                # Store inhibition function data
                summary["inhibition_function"] = {
                    "ssd_values": (
                        ssd_groups["ssd"].tolist() if len(ssd_groups) > 0 else []
                    ),
                    "inhibition_rates": (
                        ssd_groups["inhibition_rate"].tolist()
                        if len(ssd_groups) > 0
                        else []
                    ),
                    "n_trials_per_ssd": (
                        ssd_groups["n_total"].tolist() if len(ssd_groups) > 0 else []
                    ),
                }

        # Performance by trial type
        for trial_type in ["go", "stop"]:
            type_data = df[df["trial_type"] == trial_type]
            if len(type_data) > 0:
                accuracy = (
                    type_data["accuracy"].mean()
                    if "accuracy" in type_data.columns
                    else 0
                )
                mean_rt = (
                    type_data[type_data["made_response"] == True][
                        "reaction_time_ms"
                    ].mean()
                    if len(type_data[type_data["made_response"] == True]) > 0
                    and "reaction_time_ms" in type_data.columns
                    else 0
                )

                summary[f"{trial_type}_performance"] = {
                    "accuracy": accuracy,
                    "mean_rt": mean_rt,
                    "n_trials": len(type_data),
                }

        return summary


def run_stop_signal_experiment(**kwargs):
    """Run the Stop Signal experiment."""
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
        if hasattr(StopSignalConfig, config_key):
            config_params[config_key] = value

    # Create config and experiment
    config = StopSignalConfig(**config_params)
    experiment = StopSignalTask(config)

    # Set up and run experiment
    experiment.setup()
    results = experiment.run_experiment()

    # Save results if output file specified
    if kwargs.get("output_file"):
        experiment.save_data(kwargs["output_file"])

    return experiment


if __name__ == "__main__":
    # Example usage
    config = StopSignalConfig(
        n_trials=150, n_participants=5, stop_probability=0.25, ssd_adjustment=True
    )

    experiment = StopSignalTask(config)
    experiment.setup()
    results = experiment.run_experiment()

    print("Stop Signal experiment completed!")
    print(f"Results shape: {results.shape}")

    # Print summary for first participant
    if experiment.participant_data:
        first_participant = list(experiment.participant_data.keys())[0]
        summary = experiment.participant_data[first_participant]["summary"]
        print(f"\nParticipant {first_participant} Summary:")
        print(f"Overall Accuracy: {summary.get('overall_accuracy', 0):.3f}")
        print(f"Mean Go RT: {summary.get('mean_go_rt', 0):.1f} ms")
        print(
            f"SSRT (Integration): {summary.get('ssrt_estimate', {}).get('integration_method', 0):.1f} ms"
        )
        print(
            f"Successful Stop Rate: {summary.get('stop_signal_metrics', {}).get('successful_stop_rate', 0):.3f}"
        )
        print(
            f"Failed Stop Rate: {summary.get('stop_signal_metrics', {}).get('failed_stop_rate', 0):.3f}"
        )
