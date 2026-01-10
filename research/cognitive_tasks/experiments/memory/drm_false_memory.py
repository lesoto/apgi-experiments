"""
DRM False Memory implementation.

The Deese-Roediger-McDermott (DRM) paradigm demonstrates false memory creation.
Participants study word lists where all words are semantically related to a critical
lure word that wasn't presented. During testing, participants often falsely remember
the lure word, revealing memory reconstruction processes.

APGI Integration:
- θₜ (threshold): Memory recognition threshold
- π (precision): Memory precision and confidence
- ε (prediction error): False memory prediction error
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
class DRMConfig(TrialBasedTaskConfig):
    """Configuration for DRM False Memory experiment."""

    n_lists: int = 10  # Number of word lists to study
    words_per_list: int = 12  # Words per study list
    study_duration_per_word_ms: int = 1500
    inter_word_interval_ms: int = 500

    # Test parameters
    test_trials_per_list: int = 6  # Test trials per list
    lure_probability: float = 0.25  # Probability of lure trials
    filler_probability: float = 0.25  # Probability of filler trials

    # Response parameters
    confidence_scale: List[str] = None  # Confidence rating scale
    response_window_ms: int = 3000

    def __post_init__(self):
        if self.confidence_scale is None:
            self.confidence_scale = ["1", "2", "3", "4", "5", "6"]  # 1=low, 6=high


class DRMWordLists:
    """Generate DRM word lists with semantic associates."""

    def __init__(self):
        # Classic DRM lists with critical lures
        self.drm_lists = {
            "sleep": [
                "bed",
                "rest",
                "awake",
                "tired",
                "dream",
                "wake",
                "snooze",
                "blanket",
                "doze",
                "slumber",
                "snore",
                "nap",
            ],
            "sweet": [
                "candy",
                "sugar",
                "bitter",
                "good",
                "taste",
                "tooth",
                "nice",
                "honey",
                "soda",
                "chocolate",
                "heart",
                "cake",
            ],
            "cold": [
                "hot",
                "snow",
                "winter",
                "ice",
                "wet",
                "frigid",
                "chilly",
                "frost",
                "air",
                "shiver",
                "arctic",
                "freeze",
            ],
            "soft": [
                "hard",
                "pillow",
                "cushion",
                "gentle",
                "light",
                "fluffy",
                "fur",
                "smooth",
                "touch",
                "plush",
                "fuzzy",
                "down",
            ],
            "doctor": [
                "nurse",
                "sick",
                "medicine",
                "health",
                "hospital",
                "stethoscope",
                "cure",
                "pain",
                "disease",
                "patient",
                "office",
                "injury",
            ],
            "chair": [
                "table",
                "sit",
                "legs",
                "seat",
                "couch",
                "desk",
                "recliner",
                "sofa",
                "wood",
                "cushion",
                "stool",
                "swivel",
            ],
            "high": [
                "low",
                "clouds",
                "up",
                "sky",
                "tall",
                "tower",
                "jump",
                "above",
                "building",
                "dizzy",
                "airplane",
                "elevated",
            ],
            "rough": [
                "smooth",
                "bumpy",
                "road",
                "tough",
                "sandpaper",
                "jagged",
                "rocky",
                "coarse",
                "sand",
                "gravel",
                "uneven",
                "rigid",
            ],
            "river": [
                "water",
                "stream",
                "lake",
                "flow",
                "boat",
                "bank",
                "fish",
                "bridge",
                "current",
                "rapids",
                "wade",
                "tributary",
            ],
            "music": [
                "note",
                "sound",
                "piano",
                "sing",
                "beat",
                "rhythm",
                "instrument",
                "orchestra",
                "melody",
                "loud",
                "concert",
                "symphony",
            ],
        }

        # Filler words (unrelated to any lists)
        self.filler_words = [
            "apple",
            "bicycle",
            "camera",
            "diamond",
            "elephant",
            "forest",
            "guitar",
            "hammer",
            "island",
            "jungle",
            "kitchen",
            "lemon",
            "mountain",
            "notebook",
            "orange",
            "picture",
            "quarter",
            "rainbow",
            "sunset",
            "telephone",
            "umbrella",
            "volcano",
            "window",
            "yellow",
            "zebra",
        ]

    def get_random_lists(self, n_lists: int) -> List[Dict[str, Any]]:
        """Get random DRM word lists."""
        available_themes = list(self.drm_lists.keys())
        selected_themes = random.sample(
            available_themes, min(n_lists, len(available_themes))
        )

        lists = []
        for theme in selected_themes:
            word_list = self.drm_lists[theme].copy()
            random.shuffle(word_list)

            lists.append(
                {
                    "theme": theme,
                    "critical_lure": theme,
                    "words": word_list,
                    "list_id": len(lists),
                }
            )

        return lists

    def generate_test_trials(
        self,
        study_lists: List[Dict[str, Any]],
        trials_per_list: int,
        lure_prob: float,
        filler_prob: float,
    ) -> List[Dict[str, Any]]:
        """Generate test trials with studied words, lures, and fillers."""
        test_trials = []

        for study_list in study_lists:
            # Select studied words for testing
            studied_words = random.sample(
                study_list["words"], min(trials_per_list // 2, len(study_list["words"]))
            )

            # Add studied word trials
            for word in studied_words:
                test_trials.append(
                    {
                        "word": word,
                        "list_id": study_list["list_id"],
                        "theme": study_list["theme"],
                        "word_type": "studied",
                        "critical_lure": study_list["critical_lure"],
                        "is_target": True,
                    }
                )

            # Add critical lure trial
            if random.random() < lure_prob:
                test_trials.append(
                    {
                        "word": study_list["critical_lure"],
                        "list_id": study_list["list_id"],
                        "theme": study_list["theme"],
                        "word_type": "critical_lure",
                        "critical_lure": study_list["critical_lure"],
                        "is_target": False,
                    }
                )

            # Add filler trials
            n_fillers = (
                trials_per_list
                - len(studied_words)
                - (1 if random.random() < lure_prob else 0)
            )
            filler_words = random.sample(
                self.filler_words, min(n_fillers, len(self.filler_words))
            )

            for word in filler_words:
                test_trials.append(
                    {
                        "word": word,
                        "list_id": None,
                        "theme": None,
                        "word_type": "filler",
                        "critical_lure": study_list["critical_lure"],
                        "is_target": False,
                    }
                )

        # Randomize test trial order
        random.shuffle(test_trials)

        # Add trial numbers
        for i, trial in enumerate(test_trials):
            trial["trial_number"] = i

        return test_trials


class DRMTask(TrialBasedTask):
    """DRM False Memory task implementation."""

    def __init__(self, config: Optional[DRMConfig] = None):
        super().__init__(config)
        self.config = config or DRMConfig()
        self.word_lists_generator = DRMWordLists()
        self.false_memory_data = {}

    def setup(self, **kwargs):
        """Set up the DRM task."""
        super().setup(**kwargs)
        self.word_lists_generator = DRMWordLists()
        self.false_memory_data = {}

    def generate_trial_sequence(self) -> List[Dict[str, Any]]:
        """Generate trial sequence for DRM task."""
        # Generate study lists
        study_lists = self.word_lists_generator.get_random_lists(self.config.n_lists)

        # Generate test trials
        test_trials = self.word_lists_generator.generate_test_trials(
            study_lists,
            self.config.test_trials_per_list,
            self.config.lure_probability,
            self.config.filler_probability,
        )

        # Combine study and test phases
        all_trials = []

        # Add study phase trials
        for study_list in study_lists:
            for i, word in enumerate(study_list["words"]):
                all_trials.append(
                    {
                        "phase": "study",
                        "word": word,
                        "list_id": study_list["list_id"],
                        "theme": study_list["theme"],
                        "critical_lure": study_list["critical_lure"],
                        "word_position": i,
                        "condition": f"study_{study_list['theme']}",
                    }
                )

        # Add test phase trials
        for test_trial in test_trials:
            test_trial["phase"] = "test"
            test_trial["condition"] = f"test_{test_trial['word_type']}"
            all_trials.append(test_trial)

        # Add overall trial numbers
        for i, trial in enumerate(all_trials):
            trial["overall_trial_number"] = i

        return all_trials

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
                "phase": "test",
                "word": "test",
                "word_type": "studied",
                "is_target": True,
            }

        base_params.update(
            {
                "phase": trial_data["phase"],
                "word": trial_data["word"],
                "word_type": trial_data.get("word_type", "studied"),
                "is_target": trial_data.get("is_target", True),
                "list_id": trial_data.get("list_id"),
                "theme": trial_data.get("theme"),
                "critical_lure": trial_data.get("critical_lure"),
                "condition": trial_data.get("condition"),
                "study_duration_ms": self.config.study_duration_per_word_ms,
                "inter_word_interval_ms": self.config.inter_word_interval_ms,
            }
        )

        return base_params

    def process_response(
        self, response: Any, correct_response: Any, trial_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Process DRM response."""
        # Get trial data from parameters if available
        if trial_data:
            is_target = trial_data.get("is_target", True)
            word_type = trial_data.get("word_type", "studied")
            word = trial_data.get("word", "unknown")
            critical_lure = trial_data.get("critical_lure", "unknown")
            phase = trial_data.get("phase", "test")
            condition = trial_data.get("condition", "default")
        else:
            # Default values
            is_target = True
            word_type = "studied"
            word = "unknown"
            critical_lure = "unknown"
            phase = "test"
            condition = "default"

        # Response should be (old/new, confidence)
        if isinstance(response, tuple) and len(response) == 2:
            old_new_response, confidence = response
        elif isinstance(response, dict):
            old_new_response = response.get("old_new_response")
            confidence = response.get("confidence", 3)
        else:
            # Single response (just old/new)
            old_new_response = response
            confidence = 3  # Default confidence

        # Convert to standardized format
        if isinstance(old_new_response, str):
            old_new_response = old_new_response.lower()

        is_old = old_new_response in ["old", "yes", "true", "1"]
        correct_response = is_target
        is_correct = is_old == correct_response

        # Store false memory data
        if word_type not in self.false_memory_data:
            self.false_memory_data[word_type] = {
                "old_responses": [],
                "accuracies": [],
                "confidences": [],
            }

        self.false_memory_data[word_type]["old_responses"].append(is_old)
        self.false_memory_data[word_type]["accuracies"].append(1 if is_correct else 0)
        self.false_memory_data[word_type]["confidences"].append(confidence)

        # Calculate confidence normalization
        normalized_confidence = confidence / 5.0  # Normalize to 0-1 range

        return {
            "response": old_new_response,
            "accuracy": 1 if is_correct else 0,
            "reaction_time_ms": 0,  # Will be filled by simulate_response
            "confidence": normalized_confidence,
            "old_new_response": is_old,
            "confidence_rating": confidence,
            "word": word,
            "word_type": word_type,
            "is_target": correct_response,
            "critical_lure": critical_lure,
            "phase": phase,
            "condition": condition,
        }

    def simulate_response(self, trial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate participant DRM performance."""
        phase = trial_data["phase"]
        word_type = trial_data.get("word_type", "studied")
        is_target = trial_data.get("is_target", True)

        if phase == "study":
            # Study phase: always "pay attention" response
            return {
                "response": ("studied", 5),
                "reaction_time_ms": 100,
                "confidence": 0.9,
                "timestamp": time.time(),
            }

        # Test phase responses
        base_old_probability = 0.7  # Base tendency to say "old"

        # Adjust based on word type
        if word_type == "studied":
            old_probability = 0.85  # High probability of saying "old" to studied words
        elif word_type == "critical_lure":
            old_probability = 0.65  # Moderate probability of false memory
        else:  # filler
            old_probability = 0.25  # Low probability of saying "old" to fillers

        # Add noise
        if random.random() < old_probability:
            old_response = True
        else:
            old_response = False

        # Calculate confidence
        if word_type == "studied":
            base_confidence = 5 if old_response else 2
        elif word_type == "critical_lure":
            base_confidence = (
                4 if old_response else 3
            )  # False memories often have high confidence
        else:  # filler
            base_confidence = 2 if old_response else 5

        confidence = np.clip(
            base_confidence + random.randint(-1, 1),
            1,
            len(self.config.confidence_scale),
        )

        # Calculate reaction time
        base_rt = 1200
        if word_type == "critical_lure":
            base_rt += 200  # Slower for lures (uncertainty)
        elif word_type == "filler":
            base_rt -= 100  # Faster for clear new items

        rt = max(600, np.random.normal(base_rt, 300))

        return {
            "response": (old_response, confidence),
            "reaction_time_ms": int(rt),
            "confidence": (confidence - 1) / (len(self.config.confidence_scale) - 1),
            "timestamp": time.time(),
        }

    def compute_participant_summary(
        self, trials: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compute comprehensive summary for DRM task."""
        base_summary = super().compute_participant_summary(trials)

        if not trials:
            return base_summary

        df = pd.DataFrame(trials)

        # DRM specific metrics
        summary = {
            **base_summary,
            "overall_accuracy": 0,
            "mean_reaction_time": 0,
            "false_memory_rates": {},
            "confidence_patterns": {},
            "signal_detection": {},
        }

        # Filter test phase only for main analysis
        test_trials = df[df["phase"] == "test"] if "phase" in df.columns else df

        # Overall metrics
        if "accuracy" in test_trials.columns:
            summary["overall_accuracy"] = test_trials["accuracy"].mean()

        if "reaction_time_ms" in test_trials.columns:
            summary["mean_reaction_time"] = test_trials["reaction_time_ms"].mean()

        # False memory rates by word type
        for word_type in test_trials["word_type"].unique():
            type_data = test_trials[test_trials["word_type"] == word_type]
            if len(type_data) > 0:
                old_rate = (
                    type_data["old_new_response"].mean()
                    if "old_new_response" in type_data.columns
                    else 0
                )
                accuracy = (
                    type_data["accuracy"].mean()
                    if "accuracy" in type_data.columns
                    else 0
                )
                mean_confidence = (
                    type_data["confidence"].mean()
                    if "confidence" in type_data.columns
                    else 0
                )

                summary["false_memory_rates"][word_type] = {
                    "old_response_rate": old_rate,
                    "accuracy": accuracy,
                    "mean_confidence": mean_confidence,
                    "n_trials": len(type_data),
                }

        # Calculate false memory rate specifically for critical lures
        lure_data = test_trials[test_trials["word_type"] == "critical_lure"]
        if len(lure_data) > 0:
            false_memory_rate = (
                lure_data["old_new_response"].mean()
                if "old_new_response" in lure_data.columns
                else 0
            )
            summary["false_memory_rates"][
                "critical_lure_false_memory_rate"
            ] = false_memory_rate

        # Confidence patterns
        for word_type in test_trials["word_type"].unique():
            type_data = test_trials[test_trials["word_type"] == word_type]
            if len(type_data) > 0 and "confidence_rating" in type_data.columns:
                summary["confidence_patterns"][word_type] = {
                    "mean_confidence": type_data["confidence_rating"].mean(),
                    "confidence_std": type_data["confidence_rating"].std(),
                    "n_trials": len(type_data),
                }

        # Signal detection analysis
        studied_data = test_trials[test_trials["word_type"] == "studied"]
        filler_data = test_trials[test_trials["word_type"] == "filler"]

        if len(studied_data) > 0 and len(filler_data) > 0:
            hit_rate = (
                studied_data["old_new_response"].mean()
                if "old_new_response" in studied_data.columns
                else 0
            )
            false_alarm_rate = (
                filler_data["old_new_response"].mean()
                if "old_new_response" in filler_data.columns
                else 0
            )

            # Avoid extreme values
            hit_rate = np.clip(hit_rate, 0.01, 0.99)
            false_alarm_rate = np.clip(false_alarm_rate, 0.01, 0.99)

            # Calculate d' and criterion
            from scipy import stats

            d_prime = stats.norm.ppf(hit_rate) - stats.norm.ppf(false_alarm_rate)
            criterion = (
                -(stats.norm.ppf(hit_rate) + stats.norm.ppf(false_alarm_rate)) / 2
            )

            summary["signal_detection"] = {
                "d_prime": d_prime,
                "criterion": criterion,
                "hit_rate": hit_rate,
                "false_alarm_rate": false_alarm_rate,
            }

        # DRM-specific false memory index
        if "critical_lure_false_memory_rate" in summary["false_memory_rates"]:
            studied_old_rate = (
                summary["false_memory_rates"]
                .get("studied", {})
                .get("old_response_rate", 0)
            )
            lure_old_rate = summary["false_memory_rates"][
                "critical_lure_false_memory_rate"
            ]

            # False memory index: how likely to say "old" to lures vs. studied items
            if studied_old_rate > 0:
                false_memory_index = lure_old_rate / studied_old_rate
                summary["false_memory_rates"]["false_memory_index"] = false_memory_index

        return summary


def run_drm_false_memory_experiment(**kwargs):
    """Run the DRM False Memory experiment."""
    # Create config with provided parameters
    config_params = {}

    # Map common parameters
    param_mapping = {
        "n_participants": "n_participants",
        "n_trials": "n_lists",
        "n_trials_per_condition": "n_lists",
    }

    for key, value in kwargs.items():
        config_key = param_mapping.get(key, key)
        if hasattr(DRMConfig, config_key):
            config_params[config_key] = value

    # Create config and experiment
    config = DRMConfig(**config_params)
    experiment = DRMTask(config)

    # Set up and run experiment
    experiment.setup()
    results = experiment.run_experiment()

    # Save results if output file specified
    if kwargs.get("output_file"):
        experiment.save_data(kwargs["output_file"])

    return experiment


if __name__ == "__main__":
    # Example usage
    config = DRMConfig(
        n_lists=8, n_participants=5, words_per_list=12, lure_probability=0.25
    )

    experiment = DRMTask(config)
    experiment.setup()
    results = experiment.run_experiment()

    print("DRM False Memory experiment completed!")
    print(f"Results shape: {results.shape}")

    # Print summary for first participant
    if experiment.participant_data:
        first_participant = list(experiment.participant_data.keys())[0]
        summary = experiment.participant_data[first_participant]["summary"]
        print(f"\nParticipant {first_participant} Summary:")
        print(f"Overall Accuracy: {summary.get('overall_accuracy', 0):.3f}")
        print(f"Mean Reaction Time: {summary.get('mean_reaction_time', 0):.1f} ms")
        print(
            f"False Memory Rate: {summary.get('false_memory_rates', {}).get('critical_lure_false_memory_rate', 0):.3f}"
        )
        print(f"False Memory Rates: {summary.get('false_memory_rates', {})}")
