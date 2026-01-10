"""
Tests for adaptive module components.
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch
from datetime import datetime

from apgi_framework.adaptive.quest_plus_staircase import (
    QuestPlusParameters,
    QuestPlusStaircase,
    StaircaseState,
)
from apgi_framework.adaptive.stimulus_generators import (
    StimulusType,
    StimulusParameters,
    GaborParameters,
    ToneParameters,
    CO2PuffParameters,
    StimulusGenerator,
    GaborPatchGenerator,
    ToneGenerator,
)
from apgi_framework.adaptive.task_control import (
    TaskState,
    SessionManager,
    SessionConfiguration,
)
from apgi_framework.adaptive.quest_plus_staircase import QuestPlusParameters


class TestQuestPlusParameters:
    """Test QuestPlusParameters dataclass."""

    def test_default_parameters(self):
        """Test default parameter values."""
        params = QuestPlusParameters()
        assert params.stimulus_min == 0.01
        assert params.stimulus_max == 1.0
        assert params.stimulus_steps == 50
        assert params.threshold_min == 0.01
        assert params.threshold_max == 1.0
        assert params.threshold_steps == 40
        assert params.slope_min == 1.0
        assert params.slope_max == 10.0
        assert params.slope_steps == 20
        assert params.lapse_rate == 0.02
        assert params.guess_rate == 0.5
        assert params.min_trials == 20
        assert params.max_trials == 200
        assert params.convergence_criterion == 0.05
        assert params.min_reversals == 4

    def test_custom_parameters(self):
        """Test custom parameter initialization."""
        params = QuestPlusParameters(
            stimulus_min=0.1,
            stimulus_max=2.0,
            stimulus_steps=100,
            min_trials=30,
            max_trials=300,
        )
        assert params.stimulus_min == 0.1
        assert params.stimulus_max == 2.0
        assert params.stimulus_steps == 100
        assert params.min_trials == 30
        assert params.max_trials == 300


class TestStaircaseState:
    """Test StaircaseState dataclass."""

    def test_default_state(self):
        """Test default state values."""
        state = StaircaseState()

        assert state.trial_number == 0
        assert state.current_intensity == 0.5
        assert state.threshold_estimate == 0.5
        assert state.threshold_std == 0.2
        assert state.intensities == []
        assert state.responses == []
        assert state.reversals == 0
        assert state.last_direction is None
        assert state.converged is False
        assert state.convergence_trial is None
        assert state.posterior is None


class TestQuestPlusStaircase:
    """Test QUEST+ staircase implementation."""

    def test_initialization(self):
        """Test QUEST+ staircase initialization."""
        params = QuestPlusParameters(min_trials=10, max_trials=50)
        staircase = QuestPlusStaircase(params)

        assert staircase.parameters == params
        assert staircase.state.trial_number == 0
        assert len(staircase.state.intensities) == 0
        assert len(staircase.state.responses) == 0
        assert not staircase.state.converged

    def test_state_serialization(self):
        """Test state serialization to dictionary."""
        state = StaircaseState(
            trial_number=5,
            current_intensity=0.7,
            threshold_estimate=0.6,
            threshold_std=0.15,
        )

        # Add some trial data
        state.intensities = [0.5, 0.6, 0.7, 0.8, 0.7]
        state.responses = [True, False, True, True, False]
        state.timestamps = [datetime.now() for _ in range(5)]

        # Convert to dict
        state_dict = state.to_dict()

        assert state_dict["trial_number"] == 5
        assert state_dict["current_intensity"] == 0.7
        assert len(state_dict["intensities"]) == 5
        assert len(state_dict["responses"]) == 5
        assert len(state_dict["timestamps"]) == 5

        # Test reconstruction
        reconstructed = StaircaseState.from_dict(state_dict)
        assert reconstructed.trial_number == 5
        assert reconstructed.current_intensity == 0.7
        assert reconstructed.intensities == state.intensities
        assert reconstructed.responses == state.responses

    def test_get_next_intensity(self):
        """Test getting next stimulus intensity."""
        params = QuestPlusParameters(min_trials=10, max_trials=50)
        staircase = QuestPlusStaircase(params)

        # First trial should return a reasonable stimulus level
        intensity = staircase.get_next_intensity()
        assert isinstance(intensity, float)
        assert params.stimulus_min <= intensity <= params.stimulus_max

    def test_update_staircase(self):
        """Test updating staircase with response."""
        params = QuestPlusParameters(min_trials=10, max_trials=50)
        staircase = QuestPlusStaircase(params)

        # Get initial intensity
        intensity = staircase.get_next_intensity()

        # Update with response
        staircase.update(intensity, response=True)

        assert staircase.state.trial_number == 1
        assert len(staircase.state.intensities) == 1
        assert len(staircase.state.responses) == 1
        assert staircase.state.responses[0] == True
        assert staircase.state.intensities[0] == intensity

    def test_convergence_checking(self):
        """Test convergence checking."""
        params = QuestPlusParameters(
            min_trials=5, max_trials=20, convergence_criterion=0.1
        )
        staircase = QuestPlusStaircase(params)

        # Simulate some trials
        for i in range(10):
            intensity = staircase.get_next_intensity()
            staircase.update(intensity, response=i % 2 == 0)

        # Check if converged
        assert staircase.state.trial_number >= params.min_trials


class TestStimulusParameters:
    """Test stimulus parameter classes."""

    def test_base_stimulus_parameters(self):
        """Test base stimulus parameters."""
        params = StimulusParameters(
            stimulus_type=StimulusType.GABOR_PATCH, intensity=0.7, duration_ms=1000.0
        )

        assert params.stimulus_type == StimulusType.GABOR_PATCH
        assert params.intensity == 0.7
        assert params.duration_ms == 1000.0
        assert params.validate() is True

    def test_base_stimulus_parameters_validation(self):
        """Test stimulus parameter validation."""
        # Valid parameters
        valid_params = StimulusParameters(
            stimulus_type=StimulusType.TONE, intensity=0.5, duration_ms=500.0
        )
        assert valid_params.validate() is True

        # Invalid intensity
        invalid_intensity = StimulusParameters(
            stimulus_type=StimulusType.TONE,
            intensity=1.5,  # Invalid: > 1.0
            duration_ms=500.0,
        )
        assert invalid_intensity.validate() is False

        # Invalid duration
        invalid_duration = StimulusParameters(
            stimulus_type=StimulusType.TONE,
            intensity=0.5,
            duration_ms=-100.0,  # Invalid: negative
        )
        assert invalid_duration.validate() is False

    def test_gabor_parameters(self):
        """Test Gabor patch parameters."""
        params = GaborParameters(
            intensity=0.6,
            contrast=0.8,
            spatial_frequency=2.0,
            size_degrees=5.0,
            orientation=45.0,
        )

        assert params.stimulus_type == StimulusType.GABOR_PATCH
        assert params.intensity == 0.6
        assert params.contrast == 0.8
        assert params.spatial_frequency == 2.0
        assert params.size_degrees == 5.0
        assert params.orientation == 45.0

    def test_tone_parameters(self):
        """Test tone parameters initialization."""
        params = ToneParameters(intensity=0.4, frequency_hz=1000.0, amplitude=0.7)
        assert params.stimulus_type == StimulusType.TONE
        assert params.intensity == 0.4
        assert params.frequency_hz == 1000.0
        assert params.amplitude == 0.7

    def test_co2_puff_parameters(self):
        """Test CO2 puff parameters initialization."""
        params = CO2PuffParameters(
            intensity=0.3, co2_concentration=8.0, duration_ms=200.0
        )
        assert params.stimulus_type == StimulusType.CO2_PUFF
        assert params.intensity == 0.3
        assert params.co2_concentration == 8.0
        assert params.duration_ms == 200.0


class TestStimulusGenerator:
    """Test stimulus generator implementation."""

    def test_initialization(self):
        """Test stimulus generator initialization."""
        generator = GaborPatchGenerator()
        assert generator.is_initialized is False
        assert generator.generator_id == "gabor_generator"

    def test_generate_gabor_stimulus(self):
        """Test Gabor stimulus generation."""
        generator = GaborPatchGenerator()
        params = GaborParameters(intensity=0.6, contrast=0.8, spatial_frequency=2.0)

        # Initialize first
        generator.initialize()
        assert generator.is_initialized is True

        result = generator.generate_stimulus(params)
        assert result is True
        assert params.timestamp is not None

    def test_generate_tone_stimulus(self):
        """Test tone stimulus generation."""
        generator = ToneGenerator()
        params = ToneParameters(intensity=0.4, frequency_hz=1000.0, amplitude=0.7)

        # Initialize first
        generator.initialize()
        result = generator.generate_stimulus(params)
        assert result is True
        assert params.timestamp is not None

    def test_timing_validation(self):
        """Test timing validation functionality."""
        generator = GaborPatchGenerator()
        generator.initialize()

        # Test timing validation
        assert generator.validate_timing(0.0) is True

        # Test cleanup
        generator.cleanup()


class TestSessionManager:
    """Test session manager implementation."""

    def test_initialization(self):
        """Test session manager initialization."""
        manager = SessionManager()

        assert manager.current_session is None
        assert manager.state_machine.current_state == TaskState.IDLE
        assert manager.session_start_time is None

    def test_configure_and_start_session(self):
        """Test configuring and starting a session."""
        config = SessionConfiguration(
            session_id="test_session", participant_id="test_participant"
        )
        manager = SessionManager()

        # Configure session
        result = manager.configure_session(config)
        assert result is True
        assert manager.current_session == config

        # Start session
        result = manager.start_session()
        assert result is True
        assert manager.session_start_time is not None

    def test_complete_session(self):
        """Test completing a session."""
        config = SessionConfiguration(
            session_id="test_session", participant_id="test_participant"
        )
        manager = SessionManager()
        manager.configure_session(config)
        manager.start_session()

        # Start a task first to get into RUNNING state
        task_name = manager.run_next_task()

        # Complete the task
        if task_name:
            manager.complete_current_task()

        # Complete session
        result = manager.complete_session()
        assert result is True
        assert manager.state_machine.current_state == TaskState.COMPLETED


if __name__ == "__main__":
    pytest.main([__file__])
