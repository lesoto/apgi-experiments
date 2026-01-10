"""
Virtual Navigation implementation.

Virtual navigation measures spatial learning and memory in virtual environments.
Participants navigate through virtual spaces to find targets or learn locations,
revealing cognitive mapping abilities and spatial strategies.

APGI Integration:
- θₜ (threshold): Spatial decision threshold
- π (precision): Spatial navigation precision
- ε (prediction error): Spatial prediction error
- β (inverse temperature): Navigation consistency
"""

import random
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import time

from .. import TrialBasedTask, TrialBasedTaskConfig


@dataclass
class VirtualNavigationConfig(TrialBasedTaskConfig):
    """Configuration for Virtual Navigation experiment."""

    n_trials: int = 60  # Number of navigation trials
    trial_timeout_ms: int = 30000  # Maximum time per trial
    inter_trial_interval_ms: int = 2000

    # Environment parameters
    environment_size: Tuple[int, int] = (20, 20)  # Width x Height
    wall_color: str = "black"  # Color of walls
    target_color: str = "red"  # Color of targets
    path_color: str = "blue"  # Color of participant path

    # Navigation parameters
    navigation_tasks: List[str] = None  # search, learning, wayfinding
    target_visibility: float = 1.0  # How visible targets are
    landmark_density: int = 4  # Number of landmarks

    # Response parameters
    movement_speed: float = 1.0  # Movement speed units per second
    control_scheme: str = "keyboard"  # keyboard, mouse, joystick

    def __post_init__(self):
        if self.navigation_tasks is None:
            self.navigation_tasks = ["search", "learning"]


class VirtualEnvironment:
    """Generate virtual navigation environments."""

    def __init__(self, config: VirtualNavigationConfig):
        self.config = config
        self.grid = np.zeros(config.environment_size)
        self.landmarks = self._generate_landmarks()
        self.current_position = None
        self.target_position = None
        self.path_history = []

    def _generate_landmarks(self) -> List[Dict[str, Any]]:
        """Generate landmarks in the environment."""
        landmarks = []

        for i in range(self.config.landmark_density):
            # Place landmarks at different locations
            x = random.randint(2, self.config.environment_size[0] - 3)
            y = random.randint(2, self.config.environment_size[1] - 3)

            landmarks.append(
                {
                    "id": i,
                    "x": x,
                    "y": y,
                    "symbol": f"L{i+1}",
                    "color": f"hsl({i*60}, 70%, 50%)",
                }
            )

        return landmarks

    def generate_search_trial(self) -> Dict[str, Any]:
        """Generate a search trial with hidden target."""
        # Place target at random location
        target_x = random.randint(2, self.config.environment_size[0] - 3)
        target_y = random.randint(2, self.config.environment_size[1] - 3)

        # Place participant at random starting position
        start_x = random.randint(2, self.config.environment_size[0] - 3)
        start_y = random.randint(2, self.config.environment_size[1] - 3)

        return {
            "task_type": "search",
            "target_position": (target_x, target_y),
            "start_position": (start_x, start_y),
            "target_distance": abs(target_x - start_x) + abs(target_y - start_y),
            "landmarks": self.landmarks.copy(),
        }

    def generate_learning_trial(self, trial_number: int) -> Dict[str, Any]:
        """Generate a learning trial with consistent target locations."""
        # Use consistent target locations for learning
        target_positions = [(5, 5), (15, 5), (15, 15), (5, 15)]

        target_idx = trial_number % len(target_positions)
        target_pos = target_positions[target_idx]

        # Place participant at fixed starting position
        start_pos = (2, 2)

        return {
            "task_type": "learning",
            "target_position": target_pos,
            "start_position": start_pos,
            "target_number": target_idx,
            "target_distance": abs(target_pos[0] - start_pos[0])
            + abs(target_pos[1] - start_pos[1]),
            "landmarks": self.landmarks.copy(),
        }

    def calculate_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """Calculate Euclidean distance between two positions."""
        return np.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)

    def get_visible_landmarks(
        self, position: Tuple[int, int], visibility_range: float = 5.0
    ) -> List[Dict[str, Any]]:
        """Get landmarks within visibility range."""
        visible = []

        for landmark in self.landmarks:
            distance = self.calculate_distance(position, (landmark["x"], landmark["y"]))
            if distance <= visibility_range:
                visible.append(landmark)

        return visible


class VirtualNavigationTask(TrialBasedTask):
    """Virtual Navigation task implementation."""

    def __init__(self, config: Optional[VirtualNavigationConfig] = None):
        super().__init__(config)
        self.config = config or VirtualNavigationConfig()
        self.environment = VirtualEnvironment(self.config)
        self.navigation_data = {}
        self.current_trial = 0

    def setup(self, **kwargs):
        """Set up the Virtual Navigation task."""
        super().setup(**kwargs)
        self.environment = VirtualEnvironment(self.config)
        self.navigation_data = {}
        self.current_trial = 0

    def generate_trial_sequence(self) -> List[Dict[str, Any]]:
        """Generate trial sequence."""
        trials = []

        # Mix of search and learning trials
        n_search = self.config.n_trials // 2
        n_learning = self.config.n_trials - n_search

        # Generate search trials
        for i in range(n_search):
            trial = self.environment.generate_search_trial()
            trial["trial_number"] = i
            trials.append(trial)

        # Generate learning trials
        for i in range(n_learning):
            trial = self.environment.generate_learning_trial(i)
            trial["trial_number"] = n_search + i
            trials.append(trial)

        # Randomize order
        random.shuffle(trials)

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
            trial_data = self.environment.generate_search_trial()
            trial_data["trial_number"] = 0

        base_params.update(
            {
                "task_type": trial_data["task_type"],
                "target_position": trial_data["target_position"],
                "start_position": trial_data["start_position"],
                "target_distance": trial_data["target_distance"],
                "landmarks": trial_data["landmarks"],
                "target_number": trial_data.get("target_number", 0),
                "condition": f"{trial_data['task_type']}_trial_{trial_data['trial_number']}",
                "trial_timeout_ms": self.config.trial_timeout_ms,
            }
        )

        return base_params

    def process_response(
        self, response: Any, correct_response: Any, trial_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Process virtual navigation response."""
        # Get trial data from parameters if available
        if trial_data:
            start_position = trial_data.get("start_position", (0, 0))
            target_position = trial_data.get("target_position", (10, 10))
            target_distance = trial_data.get("target_distance", 0)
            task_type = trial_data.get("task_type", "search")
            condition = trial_data.get("condition", "default")
        else:
            # Default values
            start_position = (0, 0)
            target_position = (10, 10)
            target_distance = 0
            task_type = "search"
            condition = "default"

        # Response should be navigation path data
        if isinstance(response, dict):
            path_data = response
        else:
            # Default empty path
            path_data = {"path": [], "actions": [], "final_position": None}

        # Extract navigation metrics
        path = path_data.get("path", [])
        actions = path_data.get("actions", [])
        final_position = path_data.get("final_position", start_position)

        target_reached = (
            self.environment.calculate_distance(final_position, target_position) < 2.0
        )  # Within 2 units

        # Calculate path efficiency
        if len(path) > 0:
            total_distance = 0
            for i in range(len(path) - 1):
                total_distance += self.environment.calculate_distance(
                    path[i], path[i + 1]
                )

            optimal_distance = target_distance
            path_efficiency = (
                optimal_distance / total_distance if total_distance > 0 else 1.0
            )
        else:
            path_efficiency = 0.0
            total_distance = 0

        # Store navigation data
        key = f"{task_type}_trial_{self.current_trial}"
        if key not in self.navigation_data:
            self.navigation_data[key] = {
                "target_reached": [],
                "path_efficiency": [],
                "total_distance": [],
            }

        self.navigation_data[key]["target_reached"].append(target_reached)
        self.navigation_data[key]["path_efficiency"].append(path_efficiency)
        self.navigation_data[key]["total_distance"].append(total_distance)

        # Calculate confidence based on performance
        base_confidence = 0.7 if target_reached else 0.4
        if path_efficiency > 0.8:
            base_confidence += 0.2  # Higher confidence for efficient paths

        return {
            "response": path_data,
            "accuracy": 1 if target_reached else 0,
            "reaction_time_ms": 0,  # Will be filled by simulate_response
            "confidence": base_confidence,
            "target_reached": target_reached,
            "path_efficiency": path_efficiency,
            "total_distance": total_distance,
            "task_type": task_type,
            "condition": condition,
        }

    def simulate_response(self, trial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate participant virtual navigation performance."""
        task_type = trial_data["task_type"]
        start_position = trial_data["start_position"]
        target_position = trial_data["target_position"]
        landmarks = trial_data["landmarks"]

        if task_type == "search":
            # Search task: random exploration with some learning
            return self._simulate_search_response(
                start_position, target_position, landmarks
            )
        else:
            # Learning task: more direct navigation with learning
            return self._simulate_learning_response(
                start_position,
                target_position,
                landmarks,
                trial_data.get("target_number", 0),
            )

    def _simulate_search_response(
        self,
        start: Tuple[int, int],
        target: Tuple[int, int],
        landmarks: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Simulate search navigation response."""
        current_pos = start
        path = [current_pos]
        actions = []
        found_target = False

        # Simulate search with random walk and occasional goal-directed moves
        max_steps = 100
        step_size = 1

        for step in range(max_steps):
            if found_target:
                break

            # Check if target is visible
            visible_landmarks = self.environment.get_visible_landmarks(current_pos, 3.0)

            # 30% chance of goal-directed move toward target
            if random.random() < 0.3 and visible_landmarks:
                # Move toward target
                dx = target[0] - current_pos[0]
                dy = target[1] - current_pos[1]

                # Normalize direction
                distance = np.sqrt(dx**2 + dy**2)
                if distance > 0:
                    dx /= distance
                    dy /= distance

                # Add some noise
                dx += np.random.normal(0, 0.2)
                dy += np.random.normal(0, 0.2)

                new_x = current_pos[0] + int(np.sign(dx) * min(step_size, abs(dx)))
                new_y = current_pos[1] + int(np.sign(dy) * min(step_size, abs(dy)))

                action = f"move_toward_target"
            else:
                # Random walk
                directions = [
                    (0, 1),
                    (1, 0),
                    (0, -1),
                    (-1, 0),
                    (1, 1),
                    (-1, 1),
                    (-1, -1),
                ]
                dx, dy = random.choice(directions)
                new_x = current_pos[0] + dx
                new_y = current_pos[1] + dy
                action = f"random_move_{dx}_{dy}"

            # Check boundaries
            new_x = np.clip(new_x, 0, self.config.environment_size[0] - 1)
            new_y = np.clip(new_y, 0, self.config.environment_size[1] - 1)

            current_pos = (new_x, new_y)
            path.append(current_pos)
            actions.append(action)

            # Check if target found
            if self.environment.calculate_distance(current_pos, target) < 2.0:
                found_target = True

        # Calculate time based on steps
        time_taken = len(path) * 1000  # 1 second per step

        return {
            "response": {
                "path": path,
                "actions": actions,
                "final_position": current_pos,
            },
            "reaction_time_ms": time_taken,
            "confidence": 0.7 if found_target else 0.3,
            "timestamp": time.time(),
        }

    def _simulate_learning_response(
        self,
        start: Tuple[int, int],
        target: Tuple[int, int],
        landmarks: List[Dict[str, Any]],
        target_number: int,
    ) -> Dict[str, Any]:
        """Simulate learning navigation response."""
        current_pos = start
        path = [current_pos]
        actions = []

        # Learning: more efficient path to learned target
        # Use learned target positions to guide navigation
        if target_number % 2 == 0:
            # Even targets: use more direct path
            dx = target[0] - start[0]
            dy = target[1] - start[1]
            steps_x = int(np.sign(dx) * min(abs(dx), 3))
            steps_y = int(np.sign(dy) * min(abs(dy), 3))

            # Move in correct direction
            for _ in range(max(abs(steps_x), abs(steps_y))):
                if steps_x != 0:
                    current_pos = (current_pos[0] + np.sign(steps_x), current_pos[1])
                    path.append(current_pos)
                    actions.append(f"move_x_{np.sign(steps_x)}")

                if steps_y != 0 and len(path) < len(path) + abs(steps_y):
                    current_pos = (current_pos[0], current_pos[1] + np.sign(steps_y))
                    path.append(current_pos)
                    actions.append(f"move_y_{np.sign(steps_y)}")
        else:
            # Odd targets: use landmark-based navigation
            current_pos = start
            path = [current_pos]

            # Navigate via landmarks
            for landmark in landmarks:
                if (
                    self.environment.calculate_distance(
                        current_pos, (landmark["x"], landmark["y"])
                    )
                    < 3.0
                ):
                    # Move toward landmark
                    dx = landmark["x"] - current_pos[0]
                    dy = landmark["y"] - current_pos[1]

                    # Normalize direction
                    distance = np.sqrt(dx**2 + dy**2)
                    if distance > 0:
                        dx /= distance
                        dy /= distance

                    # Add some noise
                    dx += np.random.normal(0, 0.1)
                    dy += np.random.normal(0, 0.1)

                    step_size = 1
                    new_x = current_pos[0] + int(np.sign(dx) * step_size)
                    new_y = current_pos[1] + int(np.sign(dy) * step_size)

                    action = f'move_toward_landmark_{landmark["id"]}'
                else:
                    # Random move
                    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
                    dx, dy = random.choice(directions)
                    new_x = current_pos[0] + dx
                    new_y = current_pos[1] + dy
                    action = f"random_move_{dx}_{dy}"

                # Check boundaries
                new_x = np.clip(new_x, 0, self.config.environment_size[0] - 1)
                new_y = np.clip(new_y, 0, self.config.environment_size[1] - 1)

                current_pos = (new_x, new_y)
                path.append(current_pos)
                actions.append(action)

                # Check if target reached
                if self.environment.calculate_distance(current_pos, target) < 2.0:
                    break

        # Calculate time based on path efficiency
        time_taken = len(path) * 800  # Faster for learned targets

        return {
            "response": {
                "path": path,
                "actions": actions,
                "final_position": current_pos,
            },
            "reaction_time_ms": time_taken,
            "confidence": 0.8,
            "timestamp": time.time(),
        }

    def compute_participant_summary(
        self, trials: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compute comprehensive summary for virtual navigation task."""
        base_summary = super().compute_participant_summary(trials)

        if not trials:
            return base_summary

        df = pd.DataFrame(trials)

        # Virtual navigation specific metrics
        summary = {
            **base_summary,
            "overall_success_rate": 0,
            "mean_reaction_time": 0,
            "navigation_performance": {},
            "spatial_learning": {},
            "task_comparison": {},
        }

        # Overall metrics
        if "accuracy" in df.columns:
            summary["overall_success_rate"] = df["accuracy"].mean()

        if "reaction_time_ms" in df.columns:
            summary["mean_reaction_time"] = df["reaction_time_ms"].mean()

        # Performance by task type
        for task_type in df["task_type"].unique():
            task_data = df[df["task_type"] == task_type]
            if len(task_data) > 0:
                success_rate = (
                    task_data["accuracy"].mean()
                    if "accuracy" in task_data.columns
                    else 0
                )
                mean_rt = (
                    task_data["reaction_time_ms"].mean()
                    if "reaction_time_ms" in task_data.columns
                    else 0
                )
                mean_path_length = (
                    task_data["path_length"].mean()
                    if "path_length" in task_data.columns
                    else 0
                )
                mean_efficiency = (
                    task_data["path_efficiency"].mean()
                    if "path_efficiency" in task_data.columns
                    else 0
                )

                summary["navigation_performance"][task_type] = {
                    "success_rate": success_rate,
                    "mean_rt": mean_rt,
                    "mean_path_length": mean_path_length,
                    "mean_efficiency": mean_efficiency,
                    "n_trials": len(task_data),
                }

        # Learning effects (compare early vs late trials)
        if task_type == "learning":
            learning_trials = df[df["task_type"] == "learning"]
            if len(learning_trials) > 0:
                # Split into halves
                mid_point = len(learning_trials) // 2
                early_trials = learning_trials.iloc[:mid_point]
                late_trials = learning_trials.iloc[mid_point:]

                if len(early_trials) > 0 and len(late_trials) > 0:
                    early_success = (
                        early_trials["accuracy"].mean()
                        if "accuracy" in early_trials.columns
                        else 0
                    )
                    late_success = (
                        late_trials["accuracy"].mean()
                        if "accuracy" in late_trials.columns
                        else 0
                    )
                    early_efficiency = (
                        early_trials["path_efficiency"].mean()
                        if "path_efficiency" in early_trials.columns
                        else 0
                    )
                    late_efficiency = (
                        late_trials["path_efficiency"].mean()
                        if "path_efficiency" in late_trials.columns
                        else 0
                    )

                    summary["spatial_learning"] = {
                        "early_success_rate": early_success,
                        "late_success_rate": late_success,
                        "learning_improvement": late_success - early_success,
                        "early_efficiency": early_efficiency,
                        "late_efficiency": late_efficiency,
                        "early_rt": (
                            early_trials["reaction_time_ms"].mean()
                            if "reaction_time_ms" in early_trials.columns
                            else 0
                        ),
                        "late_rt": (
                            late_trials["reaction_time_ms"].mean()
                            if "reaction_time_ms" in late_trials.columns
                            else 0
                        ),
                    }

        return summary


def run_virtual_navigation_experiment(**kwargs):
    """Run the Virtual Navigation experiment."""
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
        if hasattr(VirtualNavigationConfig, config_key):
            config_params[config_key] = value

    # Create config and experiment
    config = VirtualNavigationConfig(**config_params)
    experiment = VirtualNavigationTask(config)

    # Set up and run experiment
    experiment.setup()
    results = experiment.run_experiment()

    # Save results if output file specified
    if kwargs.get("output_file"):
        experiment.save_data(kwargs["output_file"])

    return experiment


if __name__ == "__main__":
    # Example usage
    config = VirtualNavigationConfig(
        n_trials=40,
        n_participants=5,
        environment_size=(20, 20),
        navigation_tasks=["search", "learning"],
    )

    experiment = VirtualNavigationTask(config)
    experiment.setup()
    results = experiment.run_experiment()

    print("Virtual Navigation experiment completed!")
    print(f"Results shape: {results.shape}")

    # Print summary for first participant
    if experiment.participant_data:
        first_participant = list(experiment.participant_data.keys())[0]
        summary = experiment.participant_data[first_participant]["summary"]
        print(f"\nParticipant {first_participant} Summary:")
        print(f"Overall Success Rate: {summary.get('overall_success_rate', 0):.3f}")
        print(f"Mean Reaction Time: {summary.get('mean_reaction_time', 0):.1f} ms")
        print(f"Navigation Performance: {summary.get('navigation_performance', {})}")
        print(f"Spatial Learning: {summary.get('spatial_learning', {})}")
