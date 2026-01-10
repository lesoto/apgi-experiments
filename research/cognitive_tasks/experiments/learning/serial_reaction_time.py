"""
Serial Reaction Time (SRTT) implementation.

The Serial Reaction Time task measures implicit sequence learning. Participants respond
to stimuli appearing in different locations. Unbeknownst to them, a repeating
sequence is embedded. Learning is evidenced by decreasing RTs for the sequence
compared to random trials.

APGI Integration:
- θₜ (threshold): Motor response threshold
- π (precision): Sequence learning precision
- ε (prediction error): Sequence violation prediction error
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
class SRTTConfig(TrialBasedTaskConfig):
    """Configuration for Serial Reaction Time experiment."""

    n_trials: int = 240
    stimulus_duration_ms: int = 200
    response_window_ms: int = 1500
    inter_trial_interval_ms: int = 250

    # SRTT parameters
    sequence_length: int = 12  # Length of repeating sequence
    n_positions: int = 4  # Number of spatial positions
    position_layout: str = "square"  # square, diamond, line

    # Learning parameters
    learning_blocks: int = 8  # Number of learning blocks
    random_blocks: int = 2  # Number of random blocks
    trials_per_block: int = 20  # Trials per block

    # Stimulus parameters
    stimulus_types: List[str] = None  # Types of stimuli to use
    response_keys: Dict[str, str] = None  # Response key mapping

    def __post_init__(self):
        if self.stimulus_types is None:
            self.stimulus_types = ["circle", "square", "triangle", "diamond"]

        if self.response_keys is None:
            self.response_keys = {
                "1": "1",
                "2": "2",
                "3": "3",
                "4": "4",
                "q": "1",
                "w": "2",
                "e": "3",
                "r": "4",
            }


class SRTTStimulus:
    """Generate SRTT stimuli and sequences."""

    def __init__(self, config: SRTTConfig):
        self.config = config
        self.positions = self._generate_positions()
        self.learning_sequence = None

    def _generate_positions(self) -> List[Tuple[float, float]]:
        """Generate spatial positions for stimuli."""
        positions = []

        if self.config.position_layout == "square":
            # 2x2 square
            coords = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
        elif self.config.position_layout == "diamond":
            # Diamond shape
            coords = [(0, -1.5), (1.5, 0), (0, 1.5), (-1.5, 0)]
        elif self.config.position_layout == "line":
            # Horizontal line
            coords = [(-3, 0), (-1, 0), (1, 0), (3, 0)]
        else:
            # Default square
            coords = [(-1, -1), (1, -1), (1, 1), (-1, 1)]

        for i, coord in enumerate(coords):
            positions.append((coord[0], coord[1], i + 1))  # Add position index

        return positions

    def generate_learning_sequence(self) -> List[int]:
        """Generate a repeating sequence for learning."""
        # Create a sequence that visits each position at least once
        base_sequence = list(range(1, self.config.n_positions + 1))

        # Add some repetitions and variations
        while len(base_sequence) < self.config.sequence_length:
            base_sequence.append(random.choice(base_sequence))

        # Trim to exact length
        sequence = base_sequence[: self.config.sequence_length]

        # Ensure it's not too predictable (avoid simple patterns)
        if len(set(sequence)) < 3:  # Need at least 3 unique positions
            sequence = random.sample(
                range(1, self.config.n_positions + 1),
                min(self.config.sequence_length, self.config.n_positions),
            )
            while len(sequence) < self.config.sequence_length:
                sequence.append(random.choice(range(1, self.config.n_positions + 1)))

        self.learning_sequence = sequence
        return sequence

    def generate_block_trials(
        self, block_type: str, block_number: int
    ) -> List[Dict[str, Any]]:
        """Generate trials for a block."""
        trials = []

        if block_type == "learning":
            # Use learning sequence
            if self.learning_sequence is None:
                self.learning_sequence = self.generate_learning_sequence()

            sequence = self.learning_sequence
            n_trials = self.config.trials_per_block

            # Repeat sequence to fill block
            full_sequence = []
            while len(full_sequence) < n_trials:
                full_sequence.extend(sequence)

            trials = full_sequence[:n_trials]

        elif block_type == "random":
            # Random sequence
            n_trials = self.config.trials_per_block
            trials = [
                random.randint(1, self.config.n_positions) for _ in range(n_trials)
            ]

        else:  # mixed
            # Mix of learning and random
            n_learning = self.config.trials_per_block // 2
            n_random = self.config.trials_per_block - n_learning

            if self.learning_sequence is None:
                self.learning_sequence = self.generate_learning_sequence()

            # Learning trials
            learning_trials = []
            full_sequence = []
            while len(full_sequence) < n_learning:
                full_sequence.extend(self.learning_sequence)
            learning_trials = full_sequence[:n_learning]

            # Random trials
            random_trials = [
                random.randint(1, self.config.n_positions) for _ in range(n_random)
            ]

            # Interleave
            trials = []
            for i in range(max(n_learning, n_random)):
                if i < len(learning_trials):
                    trials.append(learning_trials[i])
                if i < len(random_trials):
                    trials.append(random_trials[i])

        # Create trial objects
        trial_objects = []
        for i, position in enumerate(trials):
            pos_info = self.positions[position - 1]  # Convert to 0-index
            stimulus_type = self.config.stimulus_types[position - 1]

            trial_objects.append(
                {
                    "trial_number": i,
                    "position": position,
                    "x": pos_info[0],
                    "y": pos_info[1],
                    "stimulus_type": stimulus_type,
                    "block_type": block_type,
                    "block_number": block_number,
                    "is_learning": (
                        block_type in ["learning", "mixed"]
                        and position
                        in self.learning_sequence[: self.config.sequence_length]
                        if self.learning_sequence
                        else False
                    ),
                    "correct_response": str(position),
                }
            )

        return trial_objects


class SRTTTask(TrialBasedTask):
    """Serial Reaction Time task implementation."""

    def __init__(self, config: Optional[SRTTConfig] = None):
        super().__init__(config)
        self.config = config or SRTTConfig()
        self.stimulus_generator = SRTTStimulus(self.config)
        self.learning_data = {}
        self.current_block = 0

    def setup(self, **kwargs):
        """Set up SRTT task."""
        super().setup(**kwargs)
        self.stimulus_generator = SRTTStimulus(self.config)
        self.learning_data = {}
        self.current_block = 0
        self.current_response_data = {}  # Initialize current_response_data

    def generate_trial_sequence(self) -> List[Dict[str, Any]]:
        """Generate trial sequence with learning and random blocks."""
        trials = []

        # Create block structure
        block_sequence = []

        # Initial random blocks
        for i in range(self.config.random_blocks):
            block_sequence.append(("random", i))

        # Learning blocks
        for i in range(self.config.learning_blocks):
            block_sequence.append(("learning", i))

        # Final random block (to test transfer)
        block_sequence.append(
            ("random", self.config.random_blocks + self.config.learning_blocks)
        )

        # Generate trials for each block
        for block_type, block_number in block_sequence:
            block_trials = self.stimulus_generator.generate_block_trials(
                block_type, block_number
            )

            for trial in block_trials:
                trial["overall_trial_number"] = len(trials)
                trials.append(trial)

        return trials

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
                "position": 1,
                "x": -1,
                "y": -1,
                "stimulus_type": "circle",
                "block_type": "random",
                "correct_response": "1",
            }

        base_params.update(
            {
                "position": trial_data["position"],
                "x": trial_data["x"],
                "y": trial_data["y"],
                "stimulus_type": trial_data["stimulus_type"],
                "block_type": trial_data["block_type"],
                "block_number": trial_data.get("block_number", 0),
                "is_learning": trial_data.get("is_learning", False),
                "correct_response": trial_data["correct_response"],
                "condition": f"{trial_data['block_type']}_block_{trial_data.get('block_number', 0)}",
                "stimulus_duration_ms": self.config.stimulus_duration_ms,
                "response_window_ms": self.config.response_window_ms,
            }
        )

        return base_params

    def process_response(
        self, response: Any, correct_response: Any, trial_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Process SRTT response."""
        # Handle different response formats
        if isinstance(response, str):
            response_str = response.lower()
        elif isinstance(response, int):
            response_str = str(response)
        else:
            response_str = str(response).lower()

        correct_str = str(correct_response).lower()
        is_correct = response_str == correct_str

        # Get stimulus type from trial data or use default
        stimulus_type = "letter"  # Default
        if trial_data:
            stimulus_type = trial_data.get("stimulus_type", "letter")

        block_type = trial_data.get("block_type", "random")
        is_learning = trial_data.get("is_learning", False)

        key = f"{block_type}_{'learning' if is_learning else 'random'}"
        if key not in self.learning_data:
            self.learning_data[key] = {
                "accuracy": [],
                "positions": [],
                "reaction_times": [],
            }

        self.learning_data[key]["accuracy"].append(1 if is_correct else 0)
        self.learning_data[key]["positions"].append(
            trial_data.get("position", 0) if trial_data else 0
        )

        if (
            self.current_response_data
            and self.current_response_data.get("reaction_time_ms", 0) > 0
        ):
            self.learning_data[key]["reaction_times"].append(
                self.current_response_data.get("reaction_time_ms", 0)
            )
        elif trial_data and trial_data.get("reaction_time_ms", 0) > 0:
            self.learning_data[key]["reaction_times"].append(
                trial_data.get("reaction_time_ms", 0)
            )

        # Calculate confidence
        base_confidence = 0.8 if is_correct else 0.4

        # Higher confidence for learning trials (familiarity)
        if is_learning:
            base_confidence += 0.1

        return {
            "response": response_str,
            "accuracy": 1 if is_correct else 0,
            "reaction_time_ms": 0,  # Will be filled by simulate_response
            "confidence": base_confidence,
            "position": trial_data.get("position", 0) if trial_data else 0,
            "x": trial_data.get("x", 0) if trial_data else 0,
            "y": trial_data.get("y", 0) if trial_data else 0,
            "stimulus_type": stimulus_type,
            "block_type": block_type,
            "is_learning": is_learning,
            "correct_response": correct_str,
            "condition": (
                trial_data.get("condition", "unknown") if trial_data else "unknown"
            ),
        }

    def simulate_response(self, trial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate participant SRTT performance."""
        position = trial_data["position"]
        correct_response = trial_data["correct_response"]
        block_type = trial_data["block_type"]
        is_learning = trial_data.get("is_learning", False)

        # Base accuracy is very high for SRTT (simple task)
        base_accuracy = 0.98

        # Slightly lower accuracy for random blocks
        if block_type == "random":
            base_accuracy = 0.96

        # Learning effect: faster RTs for learned sequences
        base_rt = 600

        if is_learning:
            # Learning benefit: faster responses
            base_rt -= 150
        else:
            # Random block: no learning benefit
            base_rt += 50

        # Add noise and individual variation
        rt = max(200, np.random.normal(base_rt, 100))

        # Generate response
        if random.random() < base_accuracy:
            response = correct_response
        else:
            # Error: wrong position
            other_positions = [
                p for p in range(1, self.config.n_positions + 1) if p != position
            ]
            response = str(random.choice(other_positions))

        # Calculate confidence
        actual_correct = response == correct_response
        confidence = 0.9 if actual_correct else 0.5

        if is_learning and actual_correct:
            confidence += 0.1  # Higher confidence for learned sequences

        return {
            "response": response,
            "reaction_time_ms": int(rt),
            "confidence": confidence,
            "timestamp": time.time(),
        }

    def run_trial(self, participant_id: int, trial_params: Dict) -> Dict[str, Any]:
        """Override to update current_response_data."""
        trial_data = super().run_trial(participant_id, trial_params)
        # Update current_response_data with reaction time
        if "reaction_time_ms" in trial_data:
            self.current_response_data = {
                "reaction_time_ms": trial_data["reaction_time_ms"]
            }
        return trial_data

    def compute_participant_summary(
        self, trials: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compute comprehensive summary for SRTT task."""
        base_summary = super().compute_participant_summary(trials)

        if not trials:
            return base_summary

        df = pd.DataFrame(trials)

        # SRTT specific metrics
        summary = {
            **base_summary,
            "overall_accuracy": 0,
            "mean_reaction_time": 0,
            "learning_effects": {},
            "block_performance": {},
            "sequence_learning": {},
        }

        # Overall metrics
        if "accuracy" in df.columns:
            summary["overall_accuracy"] = df["accuracy"].mean()

        if "reaction_time_ms" in df.columns:
            summary["mean_reaction_time"] = df["reaction_time_ms"].mean()

        # Performance by block type
        for block_type in df["block_type"].unique():
            block_data = df[df["block_type"] == block_type]
            if len(block_data) > 0:
                accuracy = (
                    block_data["accuracy"].mean()
                    if "accuracy" in block_data.columns
                    else 0
                )
                mean_rt = (
                    block_data["reaction_time_ms"].mean()
                    if "reaction_time_ms" in block_data.columns
                    else 0
                )

                summary["block_performance"][block_type] = {
                    "accuracy": accuracy,
                    "mean_rt": mean_rt,
                    "n_trials": len(block_data),
                }

        # Learning effects
        learning_data = df[df["is_learning"] == True]
        random_data = df[df["is_learning"] == False]

        if len(learning_data) > 0 and len(random_data) > 0:
            learning_rt = (
                learning_data["reaction_time_ms"].mean()
                if "reaction_time_ms" in learning_data.columns
                else 0
            )
            random_rt = (
                random_data["reaction_time_ms"].mean()
                if "reaction_time_ms" in random_data.columns
                else 0
            )

            summary["learning_effects"] = {
                "learning_rt_benefit": random_rt - learning_rt,
                "learning_rt": learning_rt,
                "random_rt": random_rt,
                "learning_accuracy": (
                    learning_data["accuracy"].mean()
                    if "accuracy" in learning_data.columns
                    else 0
                ),
                "random_accuracy": (
                    random_data["accuracy"].mean()
                    if "accuracy" in random_data.columns
                    else 0
                ),
            }

        # Sequence-specific learning analysis
        if self.stimulus_generator.learning_sequence:
            sequence = self.stimulus_generator.learning_sequence

            # Analyze performance on specific sequence positions
            for i, seq_pos in enumerate(sequence):
                pos_data = df[df["position"] == seq_pos]
                if len(pos_data) > 0:
                    accuracy = (
                        pos_data["accuracy"].mean()
                        if "accuracy" in pos_data.columns
                        else 0
                    )
                    mean_rt = (
                        pos_data["reaction_time_ms"].mean()
                        if "reaction_time_ms" in pos_data.columns
                        else 0
                    )

                    summary["sequence_learning"][f"seq_pos_{i+1}_{seq_pos}"] = {
                        "accuracy": accuracy,
                        "mean_rt": mean_rt,
                        "n_trials": len(pos_data),
                    }

        # Calculate learning curve across blocks
        if "block_number" in df.columns:
            block_rts = df.groupby("block_number")["reaction_time_ms"].mean()
            summary["learning_curve"] = {
                "block_rts": block_rts.to_dict(),
                "learning_slope": self._calculate_learning_slope(block_rts),
            }

        return summary

    def _calculate_learning_slope(self, block_rts: pd.Series) -> float:
        """Calculate learning slope across blocks."""
        if len(block_rts) < 3:
            return 0.0

        block_numbers = list(block_rts.index)
        rt_values = list(block_rts.values)

        # Linear regression
        slope, _ = np.polyfit(block_numbers, rt_values, 1)
        return slope


def run_srtt_experiment(**kwargs):
    """Run the Serial Reaction Time experiment."""
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
        if hasattr(SRTTConfig, config_key):
            config_params[config_key] = value

    # Create config and experiment
    config = SRTTConfig(**config_params)
    experiment = SRTTTask(config)

    # Set up and run experiment
    experiment.setup()
    results = experiment.run_experiment()

    # Save results if output file specified
    if kwargs.get("output_file"):
        experiment.save_data(kwargs["output_file"])

    return experiment


if __name__ == "__main__":
    # Example usage
    config = SRTTConfig(
        n_trials=200,
        n_participants=5,
        sequence_length=12,
        learning_blocks=8,
        random_blocks=2,
    )

    experiment = SRTTTask(config)
    experiment.setup()
    results = experiment.run_experiment()

    print("Serial Reaction Time experiment completed!")
    print(f"Results shape: {results.shape}")

    # Print summary for first participant
    if experiment.participant_data:
        first_participant = list(experiment.participant_data.keys())[0]
        summary = experiment.participant_data[first_participant]["summary"]
        print(f"\nParticipant {first_participant} Summary:")
        print(f"Overall Accuracy: {summary.get('overall_accuracy', 0):.3f}")
        print(f"Mean Reaction Time: {summary.get('mean_reaction_time', 0):.1f} ms")
        print(
            f"Learning RT Benefit: {summary.get('learning_effects', {}).get('learning_rt_benefit', 0):.1f} ms"
        )
        print(f"Block Performance: {summary.get('block_performance', {})}")


def run_serial_reaction_time_experiment(**kwargs):
    """Run the Serial Reaction Time experiment."""
    # Create config with provided parameters
    config_params = {}

    # Map common parameters
    param_mapping = {
        "n_participants": "n_participants",
        "trials_per_block": "trials_per_block",
        "n_blocks": "n_blocks",
        "stimulus_duration_ms": "stimulus_duration_ms",
        "response_window_ms": "response_window_ms",
    }

    for key, value in kwargs.items():
        if key in param_mapping:
            config_params[param_mapping[key]] = value

    # Create experiment
    config = SRTTConfig(**config_params)
    experiment = SRTTTask(config)

    # Run experiment
    results = experiment.run_experiment(**kwargs)

    return experiment
