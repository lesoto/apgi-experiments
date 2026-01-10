import os
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
import json
import random
import torch
from datetime import datetime

from core.experiment import BaseExperiment
from .environment import GridWorld
from .agents import RandomAgent, ReactiveAgent, DQNAgent, APGIAgent, AgentConfig


@dataclass
class AIBenchmarkingConfig:
    """Configuration for the AI Benchmarking experiment."""

    n_episodes: int = 100
    max_steps: int = 1000
    n_agents_per_type: int = 3
    world_size: int = 20
    n_food: int = 30
    n_obstacles: int = 20
    n_predators: int = 3
    render: bool = False
    render_every: int = 10
    save_dir: str = "data/ai_benchmarking"

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith("__")}


class AIBenchmarkingExperiment(BaseExperiment):
    """Experiment to benchmark different AI agent architectures."""

    def __init__(self, config: Optional[AIBenchmarkingConfig] = None):
        super().__init__(n_participants=1)  # Participants not used in this experiment
        self.config = config or AIBenchmarkingConfig()
        self.agent_types = ["random", "reactive", "dqn", "ipi"]
        self.results = []
        self.metrics_history = []

        # Create save directory
        os.makedirs(self.config.save_dir, exist_ok=True)

    def run_trial(self, participant_id: int, trial_params: Dict):
        """Run a single trial of the experiment.

        In this experiment, a trial is a single episode with all agent types.
        """
        return self._run_episode(participant_id, trial_params)

    def run_block(self, participant_id: int, block_params: Dict):
        """Run a block of trials.

        In this experiment, we don't use blocks, so we just run all trials.
        """
        return self.run_experiment()

    def run_participant(self, participant_id: int):
        """Run the experiment for a single participant.

        In this experiment, we don't have human participants, so we just run the experiment.
        """
        return self.run_experiment()

    def setup(self, **kwargs):
        """Set up the experiment."""
        # Save config
        with open(os.path.join(self.config.save_dir, "config.json"), "w") as f:
            json.dump(self.config.to_dict(), f, indent=2)

    def run_experiment(self, **kwargs):
        """Run the AI benchmarking experiment."""
        print("Starting AI Benchmarking Experiment...")
        start_time = time.time()

        # Run multiple episodes
        for episode in range(self.config.n_episodes):
            episode_start = time.time()

            # Initialize environment
            env = GridWorld(
                size=self.config.world_size,
                n_food=self.config.n_food,
                n_obstacles=self.config.n_obstacles,
                n_predators=self.config.n_predators,
            )

            # Initialize agents
            agents = self._initialize_agents(env)

            # Run episode
            episode_metrics = self._run_episode(env, agents, episode)

            # Store results
            self.metrics_history.append(episode_metrics)

            # Print progress
            episode_time = time.time() - episode_start
            print(
                f"Episode {episode + 1}/{self.config.n_episodes} completed in {episode_time:.1f}s"
            )

            # Save intermediate results
            if (episode + 1) % 10 == 0:
                self._save_results()

        # Save final results
        self._save_results()

        # Generate analysis
        self._analyze_results()

        total_time = time.time() - start_time
        print(f"\nExperiment completed in {total_time/60:.1f} minutes")
        print(f"Results saved to: {os.path.abspath(self.config.save_dir)}")

    def _initialize_agents(self, env: GridWorld) -> Dict[str, List[Any]]:
        """Initialize agents of different types."""
        agents = {agent_type: [] for agent_type in self.agent_types}

        # Create agents for each type
        for agent_type in self.agent_types:
            for _ in range(self.config.n_agents_per_type):
                if agent_type == "random":
                    agent = RandomAgent()
                elif agent_type == "reactive":
                    agent = ReactiveAgent()
                elif agent_type == "dqn":
                    agent = DQNAgent()
                elif agent_type == "ipi":
                    agent = APGIAgent()
                else:
                    raise ValueError(f"Unknown agent type: {agent_type}")

                env.add_agent(agent)
                agents[agent_type].append(agent)

        return agents

    def _run_episode(
        self, env: GridWorld, agents: Dict[str, List[Any]], episode: int
    ) -> Dict:
        """Run a single episode of the experiment."""
        episode_metrics = {
            "episode": episode,
            "steps": 0,
            "agent_metrics": {},
            "start_time": datetime.now().isoformat(),
        }

        # Initialize metrics for each agent type
        for agent_type in self.agent_types:
            episode_metrics["agent_metrics"][agent_type] = {
                "survival_times": [],
                "food_consumed": [],
                "final_energy": [],
            }

        # Run the episode
        for step in range(self.config.max_steps):
            # Step the environment
            env.step()

            # Render if enabled
            if self.config.render and (step % self.config.render_every == 0):
                env.render()
                time.sleep(0.1)  # Small delay for visualization

            # Check if all agents are done
            all_done = all(
                not agent.active
                for agent_list in agents.values()
                for agent in agent_list
            )
            if all_done:
                break

        # Collect metrics
        episode_metrics["steps"] = step + 1
        episode_metrics["end_time"] = datetime.now().isoformat()

        # Get metrics for each agent type
        for agent_type, agent_list in agents.items():
            for agent in agent_list:
                episode_metrics["agent_metrics"][agent_type]["survival_times"].append(
                    getattr(agent, "survival_time", step + 1)
                )
                episode_metrics["agent_metrics"][agent_type]["food_consumed"].append(
                    getattr(agent, "food_consumed", 0)
                )
                episode_metrics["agent_metrics"][agent_type]["final_energy"].append(
                    max(0, agent.energy)
                )

        return episode_metrics

    def _save_results(self):
        """Save experiment results to disk."""
        # Save metrics history
        metrics_file = os.path.join(self.config.save_dir, "metrics_history.json")
        with open(metrics_file, "w") as f:
            json.dump(self.metrics_history, f, indent=2)

        # Save summary statistics
        summary = self._compute_summary_statistics()
        summary_file = os.path.join(self.config.save_dir, "summary_statistics.json")
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)

        print(f"Results saved to {self.config.save_dir}")

    def _compute_summary_statistics(self) -> Dict:
        """Compute summary statistics from the metrics history."""
        if not self.metrics_history:
            return {}

        summary = {}

        # Aggregate metrics across all episodes
        for agent_type in self.agent_types:
            survival_times = []
            food_consumed = []
            final_energy = []

            for episode in self.metrics_history:
                agent_metrics = episode["agent_metrics"][agent_type]
                survival_times.extend(agent_metrics["survival_times"])
                food_consumed.extend(agent_metrics["food_consumed"])
                final_energy.extend(agent_metrics["final_energy"])

            summary[agent_type] = {
                "mean_survival_time": np.mean(survival_times) if survival_times else 0,
                "std_survival_time": np.std(survival_times) if survival_times else 0,
                "mean_food_consumed": np.mean(food_consumed) if food_consumed else 0,
                "std_food_consumed": np.std(food_consumed) if food_consumed else 0,
                "mean_final_energy": np.mean(final_energy) if final_energy else 0,
                "n_episodes": len(self.metrics_history),
            }

        return summary

    def _analyze_results(self):
        """Analyze and visualize the experiment results."""
        if not self.metrics_history:
            print("No data to analyze")
            return

        # Create plots directory
        plots_dir = os.path.join(self.config.save_dir, "plots")
        os.makedirs(plots_dir, exist_ok=True)

        # Plot survival times over episodes
        self._plot_metric_over_episodes(
            "survival_times", "Mean Survival Time", "Time Steps", plots_dir
        )

        # Plot food consumed over episodes
        self._plot_metric_over_episodes(
            "food_consumed", "Mean Food Consumed", "Count", plots_dir
        )

        # Plot final energy over episodes
        self._plot_metric_over_episodes(
            "final_energy", "Mean Final Energy", "Energy", plots_dir
        )

        # Plot summary bar charts
        self._plot_summary_barcharts(plots_dir)

    def _plot_metric_over_episodes(
        self, metric: str, title: str, ylabel: str, save_dir: str
    ):
        """Plot a metric over episodes for all agent types."""
        plt.figure(figsize=(12, 6))

        for agent_type in self.agent_types:
            # Calculate mean and std for each episode
            means = []
            stds = []

            for episode in self.metrics_history:
                values = episode["agent_metrics"][agent_type][metric]
                means.append(np.mean(values) if values else 0)
                stds.append(np.std(values) if len(values) > 1 else 0)

            # Plot with error bars
            x = np.arange(len(means))
            plt.plot(x, means, label=agent_type.capitalize())
            plt.fill_between(
                x,
                np.array(means) - np.array(stds),
                np.array(means) + np.array(stds),
                alpha=0.2,
            )

        plt.title(f"{title} Over Episodes")
        plt.xlabel("Episode")
        plt.ylabel(ylabel)
        plt.legend()
        plt.grid(True, alpha=0.3)

        # Save the plot
        filename = f"{metric}_over_episodes.png"
        plt.savefig(os.path.join(save_dir, filename), dpi=300, bbox_inches="tight")
        plt.close()

    def _plot_summary_barcharts(self, save_dir: str):
        """Create bar charts comparing agent performance."""
        if not self.metrics_history:
            return

        # Get summary statistics
        summary = self._compute_summary_statistics()
        if not summary:
            return

        # Plot survival time comparison
        self._plot_summary_barchart(
            summary,
            "mean_survival_time",
            "std_survival_time",
            "Mean Survival Time (Steps)",
            "survival_time_comparison.png",
            save_dir,
        )

        # Plot food consumed comparison
        self._plot_summary_barchart(
            summary,
            "mean_food_consumed",
            "std_food_consumed",
            "Mean Food Consumed",
            "food_consumed_comparison.png",
            save_dir,
        )

        # Plot final energy comparison
        self._plot_summary_barchart(
            summary,
            "mean_final_energy",
            "std_final_energy",
            "Mean Final Energy",
            "final_energy_comparison.png",
            save_dir,
        )

    def _plot_summary_barchart(
        self,
        summary: Dict,
        metric: str,
        error_metric: str,
        ylabel: str,
        filename: str,
        save_dir: str,
    ):
        """Helper function to create a bar chart for a specific metric."""
        agent_types = list(summary.keys())
        means = [summary[agent_type][metric] for agent_type in agent_types]
        stds = [summary[agent_type].get(error_metric, 0) for agent_type in agent_types]

        plt.figure(figsize=(10, 6))
        x = np.arange(len(agent_types))

        bars = plt.bar(x, means, yerr=stds, capsize=5, alpha=0.7)

        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"{height:.1f}",
                ha="center",
                va="bottom",
            )

        plt.xticks(x, [agent_type.capitalize() for agent_type in agent_types])
        plt.ylabel(ylabel)
        plt.title(f"Agent Performance: {ylabel}")
        plt.grid(True, alpha=0.3, axis="y")

        # Save the plot
        plt.savefig(os.path.join(save_dir, filename), dpi=300, bbox_inches="tight")
        plt.close()


def run_ai_benchmarking_experiment(**kwargs):
    """Run the AI benchmarking experiment with the given configuration.

    Args:
        **kwargs: Configuration parameters that will be passed to AIBenchmarkingConfig
    """
    # Create config with default values, then update with any provided kwargs
    config_params = {}

    # Map command line arguments to config parameters
    arg_mapping = {"n_participants": "n_agents_per_type", "n_trials": "n_episodes"}

    # Map and filter valid config parameters
    for key, value in kwargs.items():
        # Use mapped key if it exists, otherwise use the key as-is
        config_key = arg_mapping.get(key, key)
        if hasattr(AIBenchmarkingConfig, config_key):
            config_params[config_key] = value

    # Create config with provided parameters
    config = AIBenchmarkingConfig(**config_params)

    # Run the experiment
    experiment = AIBenchmarkingExperiment(config)
    experiment.setup()
    experiment.run_experiment()

    return experiment


if __name__ == "__main__":
    # Example configuration
    config = AIBenchmarkingConfig(
        n_episodes=50,
        max_steps=500,
        n_agents_per_type=3,
        world_size=20,
        n_food=30,
        n_obstacles=20,
        n_predators=3,
        render=False,
        render_every=10,
        save_dir="data/ai_benchmarking",
    )

    # Run the experiment
    run_ai_benchmarking_experiment(config)
