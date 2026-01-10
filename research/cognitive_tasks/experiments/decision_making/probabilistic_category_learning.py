"""
Probabilistic Category Learning implementation.

Participants learn to categorize stimuli into categories based on probabilistic feedback.
Each stimulus has a certain probability of belonging to each category, requiring participants
to learn statistical regularities and make decisions under uncertainty.

APGI Integration:
- θₜ (threshold): Decision threshold for category assignment
- π (precision): Confidence in category judgment
- ε (prediction error): Difference between expected and actual feedback
- β (inverse temperature): Determinism in category selection
"""

import random
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import time

from .. import TrialBasedTask, TrialBasedTaskConfig


@dataclass
class ProbabilisticCategoryLearningConfig(TrialBasedTaskConfig):
    """Configuration for Probabilistic Category Learning."""

    n_trials: int = 200
    n_categories: int = 2
    n_stimuli_per_category: int = 4
    stimulus_dimensions: int = 3  # Number of features per stimulus
    feedback_probability: float = 1.0  # Probability of providing feedback
    category_probabilities: Dict[str, float] = None  # Base rates for categories

    # Stimulus generation parameters
    feature_range: Tuple[float, float] = (0.0, 1.0)
    noise_level: float = 0.2  # Add noise to stimulus features

    def __post_init__(self):
        if self.category_probabilities is None:
            # Equal base rates by default
            self.category_probabilities = {
                f"Category_{i+1}": 1.0 / self.n_categories
                for i in range(self.n_categories)
            }


class StimulusGenerator:
    """Generate stimuli for probabilistic category learning."""

    def __init__(self, config: ProbabilisticCategoryLearningConfig):
        self.config = config
        self.category_prototypes = self._generate_prototypes()
        self.stimuli = self._generate_stimuli()

    def _generate_prototypes(self) -> Dict[str, np.ndarray]:
        """Generate prototype stimuli for each category."""
        prototypes = {}

        for i in range(self.config.n_categories):
            category_name = f"Category_{i+1}"
            # Create prototype with distinct feature values
            prototype = np.random.uniform(
                self.config.feature_range[0],
                self.config.feature_range[1],
                self.config.stimulus_dimensions,
            )
            prototypes[category_name] = prototype

        return prototypes

    def _generate_stimuli(self) -> List[Dict[str, Any]]:
        """Generate individual stimuli with category probabilities."""
        stimuli = []

        for category_name, prototype in self.category_prototypes.items():
            for i in range(self.config.n_stimuli_per_category):
                # Add noise to prototype to create individual stimulus
                noise = np.random.normal(
                    0, self.config.noise_level, self.config.stimulus_dimensions
                )
                features = prototype + noise

                # Clip to valid range
                features = np.clip(
                    features, self.config.feature_range[0], self.config.feature_range[1]
                )

                # Calculate category membership probabilities
                category_probs = self._calculate_category_probabilities(features)

                stimulus = {
                    "stimulus_id": f"{category_name}_{i+1}",
                    "features": features.tolist(),
                    "true_category": category_name,
                    "category_probabilities": category_probs,
                    "prototype_distance": np.linalg.norm(features - prototype),
                }
                stimuli.append(stimulus)

        return stimuli

    def _calculate_category_probabilities(
        self, features: np.ndarray
    ) -> Dict[str, float]:
        """Calculate probability of stimulus belonging to each category."""
        probs = {}
        total_similarity = 0
        similarities = {}

        # Calculate similarity to each prototype
        for category_name, prototype in self.category_prototypes.items():
            # Inverse distance as similarity
            distance = np.linalg.norm(features - prototype)
            similarity = 1.0 / (1.0 + distance)
            similarities[category_name] = similarity
            total_similarity += similarity

        # Normalize to probabilities
        for category_name, similarity in similarities.items():
            base_rate = self.config.category_probabilities.get(
                category_name, 1.0 / self.config.n_categories
            )
            probs[category_name] = (similarity / total_similarity) * base_rate

        # Normalize again to ensure sum = 1
        total_prob = sum(probs.values())
        if total_prob > 0:
            for category_name in probs:
                probs[category_name] /= total_prob

        return probs

    def get_random_stimulus(self) -> Dict[str, Any]:
        """Get a random stimulus from the stimulus set."""
        return random.choice(self.stimuli)


class ProbabilisticCategoryLearning(TrialBasedTask):
    """Probabilistic Category Learning implementation."""

    def __init__(self, config: Optional[ProbabilisticCategoryLearningConfig] = None):
        super().__init__(config)
        self.config = config or ProbabilisticCategoryLearningConfig()
        self.stimulus_generator = StimulusGenerator(self.config)
        self.learning_history = []
        self.category_beliefs = {
            cat: 0.5 for cat in self.config.category_probabilities.keys()
        }

    def setup(self, **kwargs):
        """Set up the probabilistic category learning task."""
        super().setup(**kwargs)
        self.stimulus_generator = StimulusGenerator(self.config)
        self.learning_history = []
        self.category_beliefs = {
            cat: 0.5 for cat in self.config.category_probabilities.keys()
        }

    def generate_trial_sequence(self) -> List[Dict[str, Any]]:
        """Generate trial sequence with balanced stimulus presentation."""
        trials = []
        stimuli = self.stimulus_generator.stimuli.copy()

        # Create balanced sequence
        for trial in range(self.config.n_trials):
            if trial < len(stimuli):
                # Present each stimulus once first
                stimulus = stimuli[trial]
            else:
                # Then random presentation
                stimulus = self.stimulus_generator.get_random_stimulus()

            trials.append(
                {
                    "trial_number": trial,
                    "stimulus": stimulus,
                    "provide_feedback": random.random()
                    < self.config.feedback_probability,
                }
            )

        return trials

    def generate_trial_parameters(
        self, participant_id: int, trial_number: int
    ) -> Dict[str, Any]:
        """Generate parameters for a specific trial."""
        base_params = super().generate_trial_parameters(participant_id, trial_number)

        # Get stimulus for this trial
        if trial_number < len(self.trial_sequence):
            stimulus_data = self.trial_sequence[trial_number]["stimulus"]
        else:
            stimulus_data = self.stimulus_generator.get_random_stimulus()

        base_params.update(
            {
                "stimulus_id": stimulus_data["stimulus_id"],
                "stimulus_features": stimulus_data["features"],
                "true_category": stimulus_data["true_category"],
                "category_probabilities": stimulus_data["category_probabilities"],
                "available_categories": list(self.config.category_probabilities.keys()),
                "current_beliefs": self.category_beliefs.copy(),
            }
        )

        return base_params

    def process_response(
        self, response: Any, correct_response: Any, trial_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Process category selection and update learning."""
        selected_category = response

        # Get true category from trial_data if available
        if trial_data:
            true_category = trial_data.get("true_category", "unknown")
        elif correct_response is not None:
            true_category = correct_response
        else:
            true_category = "unknown"

        # Determine accuracy
        is_correct = selected_category == true_category

        # Update category beliefs based on feedback
        if (
            trial_data
            and "provide_feedback" in trial_data
            and trial_data["provide_feedback"]
        ):
            if is_correct:
                # Reinforce correct category
                self.category_beliefs[selected_category] = min(
                    1.0, self.category_beliefs[selected_category] + 0.1
                )
            else:
                # Decrease belief in incorrect category, increase in correct one
                self.category_beliefs[selected_category] = max(
                    0.0, self.category_beliefs[selected_category] - 0.05
                )
                if true_category in self.category_beliefs:
                    self.category_beliefs[true_category] = min(
                        1.0, self.category_beliefs[true_category] + 0.05
                    )

        # Store learning event
        learning_event = {
            "selected_category": selected_category,
            "true_category": true_category,
            "is_correct": is_correct,
            "beliefs_before": self.category_beliefs.copy(),
        }
        self.learning_history.append(learning_event)

        # Calculate confidence based on belief strength
        belief_strength = self.category_beliefs.get(selected_category, 0.5)
        confidence = abs(belief_strength - 0.5) * 2  # Convert to 0-1 range

        return {
            "response": selected_category,
            "accuracy": 1 if is_correct else 0,
            "reaction_time_ms": 0,  # Will be filled by simulate_response
            "confidence": confidence,
            "true_category": true_category,
            "belief_strength": belief_strength,
            "category_beliefs": self.category_beliefs.copy(),
            "learning_trial": len(self.learning_history),
        }

    def simulate_response(self, trial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate participant category selection with learning."""
        available_categories = trial_data["available_categories"]
        current_beliefs = trial_data.get("current_beliefs", {})

        # Simulate learning over trials
        trial_number = trial_data.get("trial_number", 0)

        if trial_number < 20:
            # Early trials: more random exploration
            selected_category = random.choice(available_categories)
            confidence = random.uniform(0.3, 0.6)
        else:
            # Later trials: use learned beliefs with some exploration
            if random.random() < 0.8:  # 80% exploitation
                # Select category with highest belief
                selected_category = max(
                    available_categories, key=lambda x: current_beliefs.get(x, 0.5)
                )
                confidence = random.uniform(0.6, 0.9)
            else:  # 20% exploration
                selected_category = random.choice(available_categories)
                confidence = random.uniform(0.3, 0.6)

        # Simulate reaction time (faster with higher confidence)
        base_rt = 1000 - (confidence * 300)  # Higher confidence = faster RT
        rt = max(400, np.random.normal(base_rt, 150))

        return {
            "response": selected_category,
            "reaction_time_ms": int(rt),
            "confidence": confidence,
            "timestamp": time.time(),
        }

    def compute_participant_summary(
        self, trials: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compute comprehensive summary for probabilistic category learning."""
        base_summary = super().compute_participant_summary(trials)

        if not trials:
            return base_summary

        df = pd.DataFrame(trials)

        # Category learning specific metrics
        summary = {
            **base_summary,
            "learning_curve": {},
            "category_accuracy": {},
            "final_beliefs": self.category_beliefs,
            "total_learning_trials": len(self.learning_history),
            "block_performance": {},
        }

        # Calculate accuracy by category
        if "true_category" in df.columns and "accuracy" in df.columns:
            for category in df["true_category"].unique():
                category_trials = df[df["true_category"] == category]
                summary["category_accuracy"][category] = {
                    "accuracy": category_trials["accuracy"].mean(),
                    "n_trials": len(category_trials),
                    "mean_confidence": (
                        category_trials["confidence"].mean()
                        if "confidence" in category_trials.columns
                        else 0
                    ),
                }

        # Calculate learning curve (performance over blocks)
        if "trial_number" in df.columns and "accuracy" in df.columns:
            block_size = 20
            n_blocks = len(trials) // block_size

            for block in range(n_blocks):
                start_idx = block * block_size
                end_idx = (block + 1) * block_size
                block_trials = df.iloc[start_idx:end_idx]

                if len(block_trials) > 0:
                    accuracy = block_trials["accuracy"].mean()
                    confidence = (
                        block_trials["confidence"].mean()
                        if "confidence" in block_trials.columns
                        else 0
                    )

                    summary["block_performance"][f"block_{block+1}"] = {
                        "accuracy": accuracy,
                        "confidence": confidence,
                        "n_trials": len(block_trials),
                    }

                    summary["learning_curve"][block * block_size] = accuracy

        # Calculate learning rate (slope of learning curve)
        if len(summary["learning_curve"]) > 1:
            x = list(summary["learning_curve"].keys())
            y = list(summary["learning_curve"].values())
            if len(x) > 1:
                learning_slope = np.polyfit(x, y, 1)[0]
                summary["learning_rate"] = learning_slope
            else:
                summary["learning_rate"] = 0
        else:
            summary["learning_rate"] = 0

        return summary


def run_probabilistic_category_learning_experiment(**kwargs):
    """Run the Probabilistic Category Learning experiment."""
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
        if hasattr(ProbabilisticCategoryLearningConfig, config_key):
            config_params[config_key] = value

    # Create config and experiment
    config = ProbabilisticCategoryLearningConfig(**config_params)
    experiment = ProbabilisticCategoryLearning(config)

    # Set up and run experiment
    experiment.setup()
    results = experiment.run_experiment()

    # Save results if output file specified
    if kwargs.get("output_file"):
        experiment.save_data(kwargs["output_file"])

    return experiment


if __name__ == "__main__":
    # Example usage
    config = ProbabilisticCategoryLearningConfig(
        n_trials=100, n_participants=5, n_categories=2, n_stimuli_per_category=4
    )

    experiment = ProbabilisticCategoryLearning(config)
    experiment.setup()
    results = experiment.run_experiment()

    print("Probabilistic Category Learning completed!")
    print(f"Results shape: {results.shape}")

    # Print summary for first participant
    if experiment.participant_data:
        first_participant = list(experiment.participant_data.keys())[0]
        summary = experiment.participant_data[first_participant]["summary"]
        print(f"\nParticipant {first_participant} Summary:")
        print(f"Overall Accuracy: {summary.get('accuracy', 0):.3f}")
        print(f"Learning Rate: {summary.get('learning_rate', 0):.4f}")
        print(f"Category Accuracy: {summary.get('category_accuracy', {})}")
        print(f"Final Beliefs: {summary.get('final_beliefs', {})}")
