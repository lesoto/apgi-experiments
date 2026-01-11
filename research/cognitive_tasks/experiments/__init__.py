"""
Base classes for cognitive task experiments.

This module provides specialized base classes for different categories of cognitive experiments,
building on the core BaseExperiment class to provide category-specific functionality.
"""

import time
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pandas as pd
from dataclasses import dataclass

# Import core modules with graceful fallback
try:
    from core.experiment import BaseExperiment
except ImportError:
    BaseExperiment = None

try:
    from models.apgi_model import APGIParams, APGIModel
except ImportError:
    APGIParams = None
    APGIModel = None


@dataclass
class CognitiveTaskConfig:
    """Base configuration for cognitive tasks."""

    n_participants: int = 20
    n_trials_per_condition: int = 50
    n_conditions: int = 2
    response_timeout_ms: int = 2000
    inter_trial_interval_ms: int = 1000
    feedback_duration_ms: int = 500

    # APGI parameters
    theta_base: float = 5.0
    sigma_pe: float = 1.0
    sigma_pi: float = 1.0
    beta: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {k: v for k, v in self.__dict__.items()}


@dataclass
class TrialBasedTaskConfig(CognitiveTaskConfig):
    """Configuration for trial-based cognitive tasks."""

    practice_trials: int = 10
    randomize_trial_order: bool = True
    balanced_conditions: bool = True


@dataclass
class BlockBasedTaskConfig(CognitiveTaskConfig):
    """Configuration for block-based cognitive tasks."""

    n_blocks: int = 4
    trials_per_block: int = 25
    block_order_randomized: bool = True
    rest_between_blocks_ms: int = 30000


@dataclass
class AdaptiveTaskConfig(CognitiveTaskConfig):
    """Configuration for adaptive cognitive tasks."""

    adaptive_parameter: str = "difficulty"
    initial_difficulty: float = 0.5
    step_size: float = 0.1
    target_accuracy: float = 0.75
    min_difficulty: float = 0.1
    max_difficulty: float = 0.9


class CognitiveTaskExperiment(BaseExperiment if BaseExperiment is not None else object):
    """Base class for cognitive task experiments with APGI integration."""

    def __init__(self, config: Optional[CognitiveTaskConfig] = None):
        if BaseExperiment is not None:
            super().__init__(n_participants=config.n_participants if config else 20)
        self.config = config or CognitiveTaskConfig()
        self.apgi_model = None
        self.trial_data = []
        self.block_data = []

    def setup(self, **kwargs):
        """Set up cognitive task experiment."""
        # Initialize APGI model with parameters from config if available
        if APGIParams is not None and APGIModel is not None:
            apgi_params = APGIParams(
                theta_base=self.config.theta_base,
                sigma_pe=self.config.sigma_pe,
                sigma_pi=self.config.sigma_pi,
                beta=self.config.beta,
            )
            self.apgi_model = APGIModel(apgi_params)
        else:
            print("Warning: APGI model modules not available, using fallback behavior")

    @abstractmethod
    def generate_trial_parameters(
        self, participant_id: int, trial_number: int
    ) -> Dict[str, Any]:
        """Generate parameters for a specific trial."""
        pass

    @abstractmethod
    def process_response(self, response: Any, correct_response: Any) -> Dict[str, Any]:
        """Process participant response and compute metrics."""
        pass

    def compute_apgi_parameters(
        self, trial_params: Dict[str, Any], response_data: Dict[str, Any]
    ) -> Dict[str, float]:
        """Compute APGI parameters for a trial."""
        # Compute prediction error based on response accuracy
        prediction_error = 1.0 if response_data.get("accuracy", 0) == 0 else 0.1

        # Compute somatic marker based on reaction time and confidence
        rt = response_data.get("reaction_time_ms", 1000)
        confidence = response_data.get("confidence", 0.5)
        somatic_marker = confidence * (1.0 - rt / 2000.0)  # Normalize RT to 0-1 range

        # Compute precision based on task difficulty
        difficulty = trial_params.get("difficulty", 0.5)
        precision = 1.0 / (difficulty + 0.1)  # Higher precision for easier tasks

        return {
            "prediction_error": prediction_error,
            "somatic_marker": somatic_marker,
            "precision": precision,
        }

    def run_trial(self, participant_id: int, trial_params: Dict) -> Dict[str, Any]:
        """Run a single trial of the experiment."""
        # Get trial parameters from sequence or use provided params
        if hasattr(self, "trial_sequence") and trial_params.get(
            "trial_number", 0
        ) < len(self.trial_sequence):
            sequence_params = self.trial_sequence[trial_params.get("trial_number", 0)]
            # Merge sequence params with provided params (provided params take precedence)
            merged_params = {**sequence_params, **trial_params}
        else:
            merged_params = trial_params

        # Simulate response if not provided
        if "response" not in merged_params:
            simulated_response = self.simulate_response(merged_params)
            merged_params.update(simulated_response)

        # Process response and compute APGI metrics
        correct_response = merged_params.get("correct_response")
        response = merged_params.get("response")

        # Try to call process_response with trial_data if it supports it
        try:
            processed_response = self.process_response(
                response, correct_response, merged_params
            )
        except TypeError:
            # Fallback for methods that don't accept trial_data parameter
            processed_response = self.process_response(response, correct_response)

        # Create trial data
        trial_data = {
            "participant_id": participant_id,
            "trial_number": merged_params.get("trial_number", 0),
            "condition": merged_params.get("condition", "default"),
            "difficulty": merged_params.get("difficulty", 0.5),
            "timestamp": merged_params.get("timestamp", time.time()),
            **merged_params,
            **processed_response,
        }

        # Compute APGI metrics if enabled
        if hasattr(self, "config") and hasattr(self.config, "theta_base"):
            apgi_params = {
                "theta_base": self.config.theta_base,
                "sigma_pe": getattr(self.config, "sigma_pe", 1.0),
                "sigma_pi": getattr(self.config, "sigma_pi", 1.0),
                "beta": getattr(self.config, "beta", 1.0),
                "somatic_marker": 0.5,  # Default somatic marker
                "precision": 1.0,  # Default precision
            }

            # Simple APGI simulation
            surprise = np.random.normal(0, apgi_params["sigma_pe"], 10)
            ignition_prob = 1 / (
                1
                + np.exp(-apgi_params["beta"] * (surprise - apgi_params["theta_base"]))
            )

            # Store APGI metrics
            trial_data.update(
                {
                    "surprise": float(surprise[-1]) if len(surprise) > 0 else 0.0,
                    "ignition_probability": (
                        float(ignition_prob[-1]) if len(ignition_prob) > 0 else 0.0
                    ),
                    "somatic_marker": apgi_params["somatic_marker"],
                    "precision": apgi_params["precision"],
                }
            )

        return trial_data

    def simulate_response(self, trial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate a participant response for testing purposes."""
        import random
        import time

        # Simulate reaction time (normal distribution around 800ms)
        rt = max(200, np.random.normal(800, 200))

        # Simulate response accuracy based on difficulty
        difficulty = trial_data.get("difficulty", 0.5)
        accuracy_prob = 0.9 - (difficulty * 0.7)  # Higher difficulty = lower accuracy
        is_correct = random.random() < accuracy_prob

        # Simulate response
        correct_response = trial_data.get("correct_response")
        if isinstance(correct_response, (int, float)):
            response = correct_response if is_correct else random.choice([1, 2, 3, 4])
        elif isinstance(correct_response, str):
            response = (
                correct_response if is_correct else random.choice(["A", "B", "C", "D"])
            )
        else:
            response = correct_response if is_correct else not correct_response

        # Simulate confidence (higher for correct responses)
        confidence = (
            random.uniform(0.6, 0.95) if is_correct else random.uniform(0.3, 0.7)
        )

        return {
            "response": response,
            "reaction_time_ms": int(rt),
            "confidence": confidence,
            "timestamp": time.time(),
        }

    def run_participant(self, participant_id: int) -> Dict[str, Any]:
        """Run the experiment for a single participant."""
        participant_trials = []

        for trial in range(
            self.config.n_trials_per_condition * self.config.n_conditions
        ):
            trial_params = self.generate_trial_parameters(participant_id, trial)
            trial_data = self.run_trial(participant_id, trial_params)
            participant_trials.append(trial_data)

        return {
            "participant_id": participant_id,
            "trials": participant_trials,
            "summary": self.compute_participant_summary(participant_trials),
        }

    def compute_participant_summary(
        self, trials: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compute summary statistics for a participant."""
        if not trials:
            return {}

        df = pd.DataFrame(trials)

        summary = {
            "total_trials": len(trials),
            "accuracy": df["accuracy"].mean() if "accuracy" in df.columns else 0.0,
            "mean_reaction_time": (
                df["reaction_time_ms"].mean()
                if "reaction_time_ms" in df.columns
                else 0.0
            ),
            "mean_confidence": (
                df["confidence"].mean() if "confidence" in df.columns else 0.0
            ),
            "mean_surprise": df["surprise"].mean() if "surprise" in df.columns else 0.0,
            "mean_ignition_probability": (
                df["ignition_probability"].mean()
                if "ignition_probability" in df.columns
                else 0.0
            ),
            "condition_performance": {},
        }

        # Condition-specific performance
        if "condition" in df.columns:
            for condition in df["condition"].unique():
                condition_data = df[df["condition"] == condition]
                summary["condition_performance"][condition] = {
                    "accuracy": (
                        condition_data["accuracy"].mean()
                        if "accuracy" in condition_data.columns
                        else 0.0
                    ),
                    "mean_reaction_time": (
                        condition_data["reaction_time_ms"].mean()
                        if "reaction_time_ms" in condition_data.columns
                        else 0.0
                    ),
                    "n_trials": len(condition_data),
                }

        return summary


class TrialBasedTask(CognitiveTaskExperiment):
    """Base class for trial-based cognitive tasks."""

    def __init__(self, config: Optional[TrialBasedTaskConfig] = None):
        super().__init__(config)
        self.config = config or TrialBasedTaskConfig()

    def setup(self, **kwargs):
        """Set up trial-based task."""
        super().setup(**kwargs)
        self.trial_sequence = self.generate_trial_sequence()

    @abstractmethod
    def generate_trial_sequence(self) -> List[Dict[str, Any]]:
        """Generate the complete sequence of trials."""
        pass

    def run_block(
        self, participant_id: int, block_params: Dict
    ) -> List[Dict[str, Any]]:
        """Run a block of trials for trial-based tasks."""
        block_trials = []
        block_config = block_params.get("config", {})
        trials_in_block = block_params.get(
            "n_trials", self.config.n_trials_per_condition
        )

        for trial in range(trials_in_block):
            trial_params = self.generate_trial_parameters(
                participant_id, block_params.get("start_trial", 0) + trial
            )
            trial_data = self.run_trial(participant_id, trial_params)
            trial_data["block_number"] = block_params.get("block_number", 0)
            block_trials.append(trial_data)

        return block_trials

    def generate_trial_parameters(
        self, participant_id: int, trial_number: int
    ) -> Dict[str, Any]:
        """Get parameters for a specific trial from the sequence."""
        if trial_number < len(self.trial_sequence):
            trial_params = self.trial_sequence[trial_number].copy()
            trial_params.update(
                {"trial_number": trial_number, "participant_id": participant_id}
            )
            return trial_params
        else:
            # Default trial parameters if sequence is exhausted
            return {
                "trial_number": trial_number,
                "participant_id": participant_id,
                "condition": "default",
                "difficulty": 0.5,
            }


class BlockBasedTask(CognitiveTaskExperiment):
    """Base class for block-based cognitive tasks."""

    def __init__(self, config: Optional[BlockBasedTaskConfig] = None):
        super().__init__(config)
        self.config = config or BlockBasedTaskConfig()

    def setup(self, **kwargs):
        """Set up block-based task."""
        super().setup(**kwargs)
        self.block_sequence = self.generate_block_sequence()

    @abstractmethod
    def generate_block_sequence(self) -> List[Dict[str, Any]]:
        """Generate the sequence of blocks."""
        pass

    def run_block(
        self, participant_id: int, block_params: Dict
    ) -> List[Dict[str, Any]]:
        """Run a block of trials."""
        block_trials = []
        block_config = block_params.get("config", {})

        for trial in range(self.config.trials_per_block):
            trial_params = self.generate_trial_parameters(
                participant_id,
                block_params.get("block_number", 0) * self.config.trials_per_block
                + trial,
                block_config,
            )
            trial_data = self.run_trial(participant_id, trial_params)
            trial_data["block_number"] = block_params.get("block_number", 0)
            block_trials.append(trial_data)

        return block_trials

    def generate_trial_parameters(
        self,
        participant_id: int,
        trial_number: int,
        block_config: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Generate trial parameters within a block context."""
        base_params = {
            "trial_number": trial_number,
            "participant_id": participant_id,
            "block_config": block_config or {},
        }

        # Add block-specific parameters
        if block_config:
            base_params.update(block_config)

        return base_params


class AdaptiveTask(CognitiveTaskExperiment):
    """Base class for adaptive cognitive tasks."""

    def __init__(self, config: Optional[AdaptiveTaskConfig] = None):
        super().__init__(config)
        self.config = config or AdaptiveTaskConfig()
        self.current_difficulty = self.config.initial_difficulty

    def setup(self, **kwargs):
        """Set up adaptive task."""
        super().setup(**kwargs)
        self.performance_history = []

    def update_difficulty(self, accuracy: float):
        """Update task difficulty based on performance."""
        if accuracy > self.config.target_accuracy:
            # Increase difficulty
            self.current_difficulty = min(
                self.config.max_difficulty,
                self.current_difficulty + self.config.step_size,
            )
        elif accuracy < self.config.target_accuracy * 0.8:  # Some tolerance
            # Decrease difficulty
            self.current_difficulty = max(
                self.config.min_difficulty,
                self.current_difficulty - self.config.step_size,
            )

    def generate_trial_parameters(
        self, participant_id: int, trial_number: int
    ) -> Dict[str, Any]:
        """Generate trial parameters with current difficulty."""
        return {
            "trial_number": trial_number,
            "participant_id": participant_id,
            "difficulty": self.current_difficulty,
            "condition": "adaptive",
        }

    def run_trial(self, participant_id: int, trial_params: Dict) -> Dict[str, Any]:
        """Run a trial and update difficulty."""
        trial_data = super().run_trial(participant_id, trial_params)

        # Update difficulty based on performance
        if trial_data.get("accuracy", 0) == 1:
            self.performance_history.append(1)
        else:
            self.performance_history.append(0)

        # Update difficulty every 10 trials
        if len(self.performance_history) >= 10:
            recent_accuracy = np.mean(self.performance_history[-10:])
            self.update_difficulty(recent_accuracy)

        trial_data["current_difficulty"] = self.current_difficulty

        return trial_data

    def run_block(
        self, participant_id: int, block_params: Dict
    ) -> List[Dict[str, Any]]:
        """Run a block of adaptive trials."""
        block_trials = []
        trials_in_block = block_params.get(
            "n_trials", self.config.n_trials_per_condition
        )

        for trial in range(trials_in_block):
            trial_params = self.generate_trial_parameters(
                participant_id, block_params.get("start_trial", 0) + trial
            )
            trial_data = self.run_trial(participant_id, trial_params)
            trial_data["block_number"] = block_params.get("block_number", 0)
            block_trials.append(trial_data)

        return block_trials
