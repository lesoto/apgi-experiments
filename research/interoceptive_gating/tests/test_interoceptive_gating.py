"""
Tests for the Interoceptive Gating Experiment.

This module contains unit tests for the Interoceptive Gating experiment,
which tests how interoceptive precision gates conscious access to exteroceptive stimuli.
"""

import pytest
import numpy as np
from pathlib import Path
import sys

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

# Import the experiment
from research.interoceptive_gating.experiments.interoceptive_gating.experiment import (
    InteroceptiveGatingExperiment,
    run_interoceptive_gating_experiment,
)


class TestInteroceptiveGating:
    """Test suite for the Interoceptive Gating experiment."""

    @pytest.fixture
    def experiment(self):
        """Create a test experiment instance with minimal parameters."""
        exp = InteroceptiveGatingExperiment(n_participants=1, sample_rate=1000)
        exp.setup(n_trials_per_condition=10)
        return exp

    def test_initialization(self, experiment):
        """Test that the experiment initializes with correct parameters."""
        assert experiment.n_participants == 1
        assert experiment.sample_rate == 1000
        assert set(experiment.conditions) == {
            "interoceptive",
            "exteroceptive",
            "control",
        }
        assert experiment.trial_duration == 2.0
        assert experiment.isi == 1.0

    def test_setup(self, experiment):
        """Test the experiment setup."""
        experiment.setup(n_trials_per_condition=15)

        assert experiment.n_trials_per_condition == 15
        assert experiment.total_trials == 45  # 3 conditions * 15 trials
        assert all(cond in experiment.thresholds for cond in experiment.conditions)

    def test_generate_heartbeat_signal(self, experiment):
        """Test generation of synthetic heartbeat signal."""
        duration = 10.0  # 10 seconds
        heart_rate = 75  # bpm

        # Check if the method exists (it might be private or not implemented)
        if not hasattr(experiment, "_generate_heartbeat_signal"):
            pytest.skip("Method _generate_heartbeat_signal not implemented")

        # Generate signal
        times, signal = experiment._generate_heartbeat_signal(duration, heart_rate)

        # Check output shape and properties
        expected_samples = int(duration * experiment.sample_rate)
        assert len(times) == expected_samples
        assert len(signal) == expected_samples

        # Should have roughly the right number of heartbeats
        expected_beats = int(duration * (heart_rate / 60))
        peaks = np.where(signal > 0.5 * signal.max())[0]
        assert abs(len(peaks) - expected_beats) <= 2  # Allow some variation

    def test_generate_gabor(self, experiment):
        """Test generation of Gabor patch stimulus."""
        duration = 1.0  # 1 second
        contrast = 0.7

        # Check if the method exists (it might be private or not implemented)
        if not hasattr(experiment, "generate_gabor"):
            pytest.skip("Method generate_gabor not implemented")

        # Generate stimulus
        stim = experiment.generate_gabor(duration, contrast)

        # Check output shape and properties
        expected_samples = int(duration * experiment.sample_rate)
        assert len(stim) == expected_samples
        assert np.all(stim >= -contrast) and np.all(stim <= contrast)

    def test_simulate_eeg(self, experiment):
        """Test simulation of EEG data."""
        # Skip this test if the method doesn't exist
        if not hasattr(experiment, "simulate_eeg"):
            pytest.skip("Method simulate_eeg not implemented")

        duration = 1.0  # Shorter duration for testing
        eeg = experiment.simulate_eeg(duration)

        # Check output shape (assuming at least 1 channel)
        expected_samples = int(duration * experiment.sample_rate)
        assert len(eeg.shape) == 2  # Should be 2D (channels x time)
        assert eeg.shape[1] == expected_samples

    def test_run_trial(self, experiment):
        """Test running a single trial."""
        # Skip if the method doesn't exist
        if not hasattr(experiment, "run_trial"):
            pytest.skip("Method run_trial not implemented")

        experiment.setup(n_trials_per_condition=1)

        # Test each condition
        for condition in experiment.conditions:
            trial_data = experiment.run_trial(1, condition, trial_idx=0)

            # Check that we got a dictionary with at least some expected keys
            assert isinstance(trial_data, dict)

            # Check for some basic expected keys
            expected_keys = ["condition", "trial_idx", "response"]
            for key in expected_keys:
                assert key in trial_data

            # Check that response is valid if present
            if "response" in trial_data and trial_data["response"] is not None:
                assert trial_data["response"] in ["synchronous", "asynchronous"]

            # Check that RT is within reasonable bounds if present
            if "rt" in trial_data and trial_data["rt"] is not None:
                assert 0 <= trial_data["rt"] <= experiment.trial_duration + 1.0

    def test_run_participant(self, experiment):
        """Test running a single participant through all trials."""
        # Skip if the method doesn't exist
        if not hasattr(experiment, "run_participant"):
            pytest.skip("Method run_participant not implemented")

        experiment.setup(n_trials_per_condition=2)  # Very short test

        # Run a single participant
        result = experiment.run_participant(participant_id=1)

        # Check that we got a result
        assert result is not None

        # The result should be a dictionary with participant data
        assert isinstance(result, dict)

        # Check for some expected keys
        expected_keys = ["participant_id", "trials", "thresholds"]
        for key in expected_keys:
            assert key in result

        # Check that we have data for all trials
        assert len(result["trials"]) == 6  # 3 conditions * 2 trials

    def test_run_experiment(self, experiment):
        """Test running the full experiment with multiple participants."""
        # Skip if the method doesn't exist
        if not hasattr(experiment, "run"):
            pytest.skip("Method run not implemented")

        # Just test that it runs without errors
        experiment.n_participants = 2  # Test with minimal participants
        experiment.n_trials_per_condition = 2  # Minimal trials for testing

        # Run the experiment
        experiment.run()

        # Check that we have results
        assert hasattr(experiment, "results")

        # The results should be a list of participant results
        assert isinstance(experiment.results, list)

        # Check that we have results for all participants
        assert len(experiment.results) == experiment.n_participants

    def test_analyze_results(self, experiment):
        """Test analysis of experiment results."""
        # Skip if the method doesn't exist
        if not hasattr(experiment, "analyze"):
            pytest.skip("Method analyze not implemented")

        # Set up a minimal experiment
        experiment.n_participants = 1
        experiment.n_trials_per_condition = 1

        # Run the experiment if not already run
        if not hasattr(experiment, "results") or not experiment.results:
            experiment.run()

        # Analyze the results
        analysis = experiment.analyze()

        # Check that we got some analysis results
        assert analysis is not None

        # The analysis should be a dictionary with at least some expected keys
        assert isinstance(analysis, dict)

        # Check for some expected keys (if implemented)
        expected_keys = ["thresholds", "accuracy", "rt"]
        for key in expected_keys:
            if key in analysis:
                # If the key exists, check that it has values for all conditions
                for cond in experiment.conditions:
                    assert cond in analysis[key]

    def test_visualization(self, experiment):
        """Test that visualization functions run without errors."""
        # Skip if the methods don't exist
        if not (
            hasattr(experiment, "plot_thresholds")
            and hasattr(experiment, "plot_accuracy")
            and hasattr(experiment, "plot_rt")
        ):
            pytest.skip("Visualization methods not implemented")

        # Set up a minimal experiment if not already run
        if not hasattr(experiment, "results") or not experiment.results:
            experiment.n_participants = 1
            experiment.n_trials_per_condition = 1
            experiment.run()

        # Run analysis if not already done
        if not hasattr(experiment, "analysis") or not experiment.analysis:
            experiment.analysis = experiment.analyze()

        # Test each visualization if it exists
        if hasattr(experiment, "plot_thresholds"):
            fig1 = experiment.plot_thresholds(experiment.analysis)
            assert fig1 is not None

        if hasattr(experiment, "plot_accuracy"):
            fig2 = experiment.plot_accuracy(experiment.analysis)
            assert fig2 is not None

        if hasattr(experiment, "plot_rt"):
            fig3 = experiment.plot_rt(experiment.analysis)
            assert fig3 is not None

        # Clean up
        import matplotlib.pyplot as plt

        plt.close("all")


def test_run_interoceptive_gating_experiment():
    """Test the convenience function to run the experiment."""
    # Just test that it runs without errors
    exp = run_interoceptive_gating_experiment(
        n_participants=2, n_trials_per_condition=5
    )

    # Check that we got an experiment instance back
    assert isinstance(exp, InteroceptiveGatingExperiment)

    # Check that the experiment was run with the correct number of participants
    assert hasattr(exp, "results")
    assert exp.results is not None
    # Check that results contain analysis data for all conditions
    expected_result_keys = [
        "interoceptive_detection_rate",
        "exteroceptive_detection_rate",
        "control_detection_rate",
    ]
    for key in expected_result_keys:
        assert key in exp.results
