"""
Simplified tests for adaptive module components that focus on existing functionality.
"""

import pytest
import numpy as np
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
)


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
        """Test tone parameters."""
        params = ToneParameters(intensity=0.4, amplitude=0.7)

        assert params.stimulus_type == StimulusType.TONE
        assert params.intensity == 0.4
        assert params.amplitude == 0.7

    def test_co2_puff_parameters(self):
        """Test CO2 puff parameters."""
        params = CO2PuffParameters(
            intensity=0.3, co2_concentration=8.0, duration_ms=200.0
        )

        assert params.stimulus_type == StimulusType.CO2_PUFF
        assert params.intensity == 0.3
        assert params.co2_concentration == 8.0
        assert params.duration_ms == 200.0


if __name__ == "__main__":
    pytest.main([__file__])
