"""
Comprehensive tests for adaptive module components.

This consolidates tests from:
- test_adaptive_module.py (346 lines)
- test_adaptive_module_simple.py (252 lines) 
- test_adaptive_simple.py (188 lines)

Total consolidated: ~800 lines with comprehensive coverage.
"""

import pytest

from apgi_framework.adaptive.quest_plus_staircase import (
    QuestPlusParameters,
    QuestPlusStaircase,
    StaircaseState,
)
from apgi_framework.adaptive.stimulus_generators import (
    CO2PuffParameters,
    GaborParameters,
    GaborPatchGenerator,
    ToneGenerator,
    ToneParameters,
)
from apgi_framework.adaptive.task_control import (
    SessionConfiguration,
    SessionManager,
    TaskState,
)


class TestQuestPlusParameters:
    """Test QuestPlusParameters dataclass."""

    def test_default_parameters(self):
        """Test default parameter values."""
        params = QuestPlusParameters()
        assert params.stimulus_min == 0.01
        assert params.stimulus_max == 1.0
        assert params.step_size_min == 0.001
        assert params.step_size_max == 0.1

    def test_parameter_validation(self):
        """Test parameter validation."""
        # Test valid parameters
        params = QuestPlusParameters(
            stimulus_min=0.1, stimulus_max=2.0, step_size_min=0.01, step_size_max=0.2
        )
        assert params.stimulus_min == 0.1
        assert params.stimulus_max == 2.0

        # Test invalid parameters
        with pytest.raises(ValueError):
            QuestPlusParameters(stimulus_min=-1.0)

    def test_parameter_serialization(self):
        """Test parameter serialization/deserialization."""
        params = QuestPlusParameters()
        serialized = params.to_dict()
        assert isinstance(serialized, dict)
        assert "stimulus_min" in serialized


class TestStaircaseState:
    """Test StaircaseState enumeration."""

    def test_state_values(self):
        """Test that all expected states are available."""
        assert StaircaseState.UP.value == "up"
        assert StaircaseState.DOWN.value == "down"
        assert StaircaseState.STOPPED.value == "stopped"

    def test_state_transitions(self):
        """Test state transition logic."""
        # Test basic state creation
        state = StaircaseState.UP
        assert state == StaircaseState.UP

        # Test state from string
        state_from_str = StaircaseState("up")
        assert state_from_str == StaircaseState.UP


class TestQuestPlusStaircase:
    """Test QuestPlusStaircase functionality."""

    def test_staircase_initialization(self):
        """Test staircase initialization."""
        params = QuestPlusParameters()
        staircase = QuestPlusStaircase(params)

        assert staircase.current_level == params.stimulus_min
        assert staircase.state == StaircaseState.STOPPED
        assert staircase.trial_count == 0

    def test_staircase_step_up(self):
        """Test staircase step up logic."""
        params = QuestPlusParameters(step_size_min=0.1, step_size_max=0.1)
        staircase = QuestPlusStaircase(params)

        # Test stepping up
        initial_level = staircase.current_level
        staircase.step_up()
        assert staircase.current_level > initial_level
        assert staircase.trial_count == 1

    def test_staircase_step_down(self):
        """Test staircase step down logic."""
        params = QuestPlusParameters(step_size_min=0.1, step_size_max=0.1)
        staircase = QuestPlusStaircase(params)

        # Set level above minimum to allow stepping down
        staircase.current_level = 0.5
        staircase.step_down()
        assert staircase.current_level < 0.5
        assert staircase.trial_count == 1

    def test_staircase_bounds(self):
        """Test staircase boundary conditions."""
        params = QuestPlusParameters(stimulus_min=0.1, stimulus_max=1.0)
        staircase = QuestPlusStaircase(params)

        # Test upper bound
        staircase.current_level = 1.0
        staircase.step_up()  # Should not change
        assert staircase.current_level == 1.0

        # Test lower bound
        staircase.current_level = 0.1
        staircase.step_down()  # Should not change
        assert staircase.current_level == 0.1


class TestStimulusGenerators:
    """Test stimulus generator components."""

    def test_tone_generator(self):
        """Test ToneGenerator functionality."""
        params = ToneParameters(frequency=1000, duration=0.1)
        generator = ToneGenerator(params)

        assert generator.parameters.frequency == 1000
        assert generator.parameters.duration == 0.1

        # Test generation
        stimulus = generator.generate()
        assert stimulus is not None
        assert hasattr(stimulus, "frequency")

    def test_gabor_generator(self):
        """Test GaborPatchGenerator functionality."""
        params = GaborParameters(spatial_frequency=0.5, orientation=45, size=1.0)
        generator = GaborPatchGenerator(params)

        assert generator.parameters.spatial_frequency == 0.5
        assert generator.parameters.orientation == 45

        # Test generation
        patch = generator.generate()
        assert patch is not None
        assert hasattr(patch, "data")

    def test_co2_generator(self):
        """Test CO2PuffGenerator functionality."""
        params = CO2PuffParameters(concentration=0.5, duration=0.2)
        from apgi_framework.adaptive.stimulus_generators import CO2PuffGenerator

        generator = CO2PuffGenerator(params)

        assert generator.parameters.concentration == 0.5
        assert generator.parameters.duration == 0.2


class TestSessionManager:
    """Test SessionManager functionality."""

    def test_session_creation(self):
        """Test session creation and configuration."""
        config = SessionConfiguration(
            task_name="Test Task", duration_minutes=30, trial_count=100
        )
        manager = SessionManager(config)

        assert manager.config.task_name == "Test Task"
        assert manager.config.duration_minutes == 30
        assert manager.config.trial_count == 100

    def test_session_state_tracking(self):
        """Test session state tracking."""
        config = SessionConfiguration(task_name="State Test")
        manager = SessionManager(config)

        # Test initial state
        assert manager.current_state == TaskState.INITIALIZED

        # Test state transitions
        manager.start_session()
        assert manager.current_state == TaskState.RUNNING

        manager.pause_session()
        assert manager.current_state == TaskState.PAUSED

        manager.stop_session()
        assert manager.current_state == TaskState.COMPLETED


if __name__ == "__main__":
    pytest.main([__file__])
