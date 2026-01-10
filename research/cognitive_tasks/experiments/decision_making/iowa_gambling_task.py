"""
Iowa Gambling Task implementation.

The Iowa Gambling Task is a psychological task thought to simulate real-life decision making.
Participants must choose between four decks of cards that yield different rewards and penalties.
Some decks are advantageous (net gain) while others are disadvantageous (net loss).

APGI Integration:
- θₜ (threshold): Represents decision threshold for risk-taking
- π (precision): Confidence in deck evaluation
- ε (prediction error): Difference between expected and actual outcomes
- β (inverse temperature): Exploration vs exploitation balance
"""

import random
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import time

from .. import TrialBasedTask, TrialBasedTaskConfig


@dataclass
class IowaGamblingConfig(TrialBasedTaskConfig):
    """Configuration for Iowa Gambling Task."""

    n_trials: int = 100
    deck_rewards: Dict[str, float] = None  # {deck_id: reward_amount}
    deck_penalties: Dict[str, List[float]] = None  # {deck_id: [penalty_values]}
    penalty_probabilities: Dict[str, float] = None  # {deck_id: penalty_probability}
    show_cumulative: bool = True  # Show running total

    def __post_init__(self):
        if self.deck_rewards is None:
            # Default deck configuration based on original IGT
            self.deck_rewards = {
                "A": 100,  # Bad deck: high reward, higher losses
                "B": 100,  # Bad deck: high reward, higher losses
                "C": 50,  # Good deck: lower reward, lower losses
                "D": 50,  # Good deck: lower reward, lower losses
            }

        if self.deck_penalties is None:
            self.deck_penalties = {
                "A": [150, 200, 250, 300, 350],  # Large penalties
                "B": [1250, 1500],  # Very large penalties
                "C": [25, 50, 75],  # Small penalties
                "D": [50, 75],  # Medium-small penalties
            }

        if self.penalty_probabilities is None:
            self.penalty_probabilities = {
                "A": 0.5,  # 50% chance of penalty
                "B": 0.1,  # 10% chance of penalty but very large
                "C": 0.5,  # 50% chance of penalty
                "D": 0.1,  # 10% chance of penalty
            }


class IowaGamblingTask(TrialBasedTask):
    """Iowa Gambling Task implementation."""

    def __init__(self, config: Optional[IowaGamblingConfig] = None):
        super().__init__(config)
        self.config = config or IowaGamblingConfig()
        self.deck_selections = {deck: 0 for deck in self.config.deck_rewards.keys()}
        self.deck_outcomes = {deck: [] for deck in self.config.deck_rewards.keys()}
        self.cumulative_score = 0
        self.trial_history = []

    def setup(self, **kwargs):
        """Set up the Iowa Gambling Task."""
        super().setup(**kwargs)
        self.deck_selections = {deck: 0 for deck in self.config.deck_rewards.keys()}
        self.deck_outcomes = {deck: [] for deck in self.config.deck_rewards.keys()}
        self.cumulative_score = 0
        self.trial_history = []

    def generate_trial_sequence(self) -> List[Dict[str, Any]]:
        """Generate trial sequence for Iowa Gambling Task."""
        trials = []

        for trial in range(self.config.n_trials):
            trials.append(
                {
                    "trial_number": trial,
                    "available_decks": list(self.config.deck_rewards.keys()),
                    "show_cumulative": self.config.show_cumulative,
                }
            )

        return trials

    def generate_trial_parameters(
        self, participant_id: int, trial_number: int
    ) -> Dict[str, Any]:
        """Generate parameters for a specific trial."""
        base_params = super().generate_trial_parameters(participant_id, trial_number)

        # Add deck information
        base_params.update(
            {
                "available_decks": list(self.config.deck_rewards.keys()),
                "deck_rewards": self.config.deck_rewards.copy(),
                "cumulative_score": self.cumulative_score,
                "deck_selections": self.deck_selections.copy(),
                "trial_number": trial_number,
            }
        )

        return base_params

    def process_response(self, response: Any, correct_response: Any) -> Dict[str, Any]:
        """Process deck selection and compute outcome."""
        selected_deck = response

        if selected_deck not in self.config.deck_rewards.keys():
            # Invalid selection
            return {
                "response": selected_deck,
                "accuracy": 0,
                "reaction_time_ms": 0,
                "confidence": 0.1,
                "outcome": "invalid_selection",
                "reward": 0,
                "penalty": 0,
                "net_gain": 0,
                "cumulative_score": self.cumulative_score,
            }

        # Get reward for selected deck
        reward = self.config.deck_rewards[selected_deck]

        # Determine if penalty occurs
        penalty = 0
        if random.random() < self.config.penalty_probabilities[selected_deck]:
            penalty = random.choice(self.config.deck_penalties[selected_deck])

        net_gain = reward - penalty
        self.cumulative_score += net_gain

        # Update tracking
        self.deck_selections[selected_deck] += 1
        self.deck_outcomes[selected_deck].append(net_gain)

        # Determine if choice was advantageous
        advantageous_decks = ["C", "D"]  # Good decks
        is_advantageous = selected_deck in advantageous_decks

        return {
            "response": selected_deck,
            "accuracy": 1 if is_advantageous else 0,  # Accuracy based on deck quality
            "reaction_time_ms": 0,  # Will be filled by simulate_response
            "confidence": 0.8 if is_advantageous else 0.6,
            "outcome": "win" if net_gain > 0 else "loss",
            "reward": reward,
            "penalty": penalty,
            "net_gain": net_gain,
            "cumulative_score": self.cumulative_score,
            "is_advantageous": is_advantageous,
            "deck_selection_count": self.deck_selections[selected_deck],
        }

    def simulate_response(self, trial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate participant deck selection."""
        # Simulate learning process - participants gradually learn to prefer good decks
        trial_number = trial_data.get("trial_number", 0)

        # Early trials: random selection
        if trial_number < 10:
            selected_deck = random.choice(trial_data["available_decks"])
            confidence = random.uniform(0.4, 0.7)
        else:
            # Later trials: prefer good decks with some probability
            # Calculate preference for good decks based on experience
            good_deck_preference = min(0.8, trial_number / 100.0)  # Gradually learn

            if random.random() < good_deck_preference:
                selected_deck = random.choice(["C", "D"])  # Good decks
                confidence = random.uniform(0.6, 0.9)
            else:
                selected_deck = random.choice(["A", "B"])  # Bad decks (occasionally)
                confidence = random.uniform(0.3, 0.6)

        # Simulate reaction time (longer for early trials)
        base_rt = 1200 if trial_number < 20 else 800
        rt = max(300, np.random.normal(base_rt, 200))

        return {
            "response": selected_deck,
            "reaction_time_ms": int(rt),
            "confidence": confidence,
            "timestamp": time.time(),
        }

    def compute_participant_summary(
        self, trials: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compute comprehensive summary for Iowa Gambling Task."""
        base_summary = super().compute_participant_summary(trials)

        if not trials:
            return base_summary

        df = pd.DataFrame(trials)

        # IGT-specific metrics
        summary = {
            **base_summary,
            "final_score": self.cumulative_score,
            "total_reward": df["reward"].sum() if "reward" in df.columns else 0,
            "total_penalty": df["penalty"].sum() if "penalty" in df.columns else 0,
            "net_gain": df["net_gain"].sum() if "net_gain" in df.columns else 0,
            "deck_preferences": self.deck_selections,
            "advantageous_deck_percentage": 0,
            "learning_slope": 0,
            "block_performance": {},
        }

        # Calculate advantageous deck selection percentage
        total_selections = sum(self.deck_selections.values())
        if total_selections > 0:
            advantageous_selections = self.deck_selections.get(
                "C", 0
            ) + self.deck_selections.get("D", 0)
            summary["advantageous_deck_percentage"] = (
                advantageous_selections / total_selections
            ) * 100

        # Calculate learning slope (improvement over time)
        if "trial_number" in df.columns and "is_advantageous" in df.columns:
            # Split into blocks of 20 trials
            block_size = 20
            n_blocks = len(trials) // block_size

            for block in range(n_blocks):
                start_idx = block * block_size
                end_idx = (block + 1) * block_size
                block_trials = df.iloc[start_idx:end_idx]

                if len(block_trials) > 0:
                    advantageous_pct = (
                        block_trials["is_advantageous"].sum() / len(block_trials)
                    ) * 100
                    summary["block_performance"][f"block_{block+1}"] = {
                        "advantageous_selection_pct": advantageous_pct,
                        "mean_net_gain": (
                            block_trials["net_gain"].mean()
                            if "net_gain" in block_trials.columns
                            else 0
                        ),
                        "n_trials": len(block_trials),
                    }

        return summary


def run_iowa_gambling_task_experiment(**kwargs):
    """Run the Iowa Gambling Task experiment."""
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
        if hasattr(IowaGamblingConfig, config_key):
            config_params[config_key] = value

    # Create config and experiment
    config = IowaGamblingConfig(**config_params)
    experiment = IowaGamblingTask(config)

    # Set up and run experiment
    experiment.setup()
    results = experiment.run_experiment()

    # Save results if output file specified
    if kwargs.get("output_file"):
        experiment.save_data(kwargs["output_file"])

    return experiment


if __name__ == "__main__":
    # Example usage
    config = IowaGamblingConfig(n_trials=100, n_participants=5)

    experiment = IowaGamblingTask(config)
    experiment.setup()
    results = experiment.run_experiment()

    print("Iowa Gambling Task completed!")
    print(f"Results shape: {results.shape}")

    # Print summary for first participant
    if experiment.participant_data:
        first_participant = list(experiment.participant_data.keys())[0]
        summary = experiment.participant_data[first_participant]["summary"]
        print(f"\nParticipant {first_participant} Summary:")
        print(f"Final Score: {summary.get('final_score', 0)}")
        print(
            f"Advantageous Deck Selection: {summary.get('advantageous_deck_percentage', 0):.1f}%"
        )
        print(f"Deck Preferences: {summary.get('deck_preferences', {})}")
