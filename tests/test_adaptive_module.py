"""
Tests for adaptive module components.
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch
from datetime import datetime

from apgi_framework.adaptive.quest_plus_staircase import (
    QuestPlusParameters, QuestPlusStaircase, StaircaseState
)
from apgi_framework.adaptive.stimulus_generators import (
    StimulusType, StimulusParameters, GaborParameters, ToneParameters,
    CO2PuffParameters, StimulusGenerator, GaborPatchGenerator, ToneGenerator
)
from apgi_framework.adaptive.task_control import (
    TaskState, TaskStateMachine, SessionManager, SessionConfiguration
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
    
    def test_custom_parameters(self):
        """Test custom parameter initialization."""
        params = QuestPlusParameters(
            stimulus_min=0.1,
            stimulus_max=2.0,
            stimulus_steps=100,
            min_trials=30,
            max_trials=300
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
            threshold_std=0.15
        )
        
        # Add some trial data
        state.intensities = [0.5, 0.6, 0.7, 0.8, 0.7]
        state.responses = [True, False, True, True, False]
        state.timestamps = [datetime.now() for _ in range(5)]
        
        # Convert to dict
        state_dict = state.to_dict()
        
        assert state_dict['trial_number'] == 5
        assert state_dict['current_intensity'] == 0.7
        assert len(state_dict['intensities']) == 5
        assert len(state_dict['responses']) == 5
        assert len(state_dict['timestamps']) == 5
        
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
        staircase.update_staircase(intensity, response=True)
        
        assert staircase.state.trial_number == 1
        assert len(staircase.state.intensities) == 1
        assert len(staircase.state.responses) == 1
        assert staircase.state.responses[0] == True
        assert staircase.state.intensities[0] == intensity
    
    def test_convergence_checking(self):
        """Test convergence checking."""
        params = QuestPlusParameters(min_trials=5, max_trials=20, convergence_criterion=0.1)
        staircase = QuestPlusStaircase(params)
        
        # Should not converge initially
        assert not staircase.state.converged
        
        # Add some trials to reach minimum
        for i in range(10):
            intensity = staircase.get_next_intensity()
            staircase.update_staircase(intensity, response=True if intensity > 0.5 else False)
        
        # Check convergence state
        assert isinstance(staircase.state.converged, bool)


class TestStimulusParameters:
    """Test stimulus parameter classes."""
    
    def test_base_stimulus_parameters(self):
        """Test base stimulus parameters."""
        params = StimulusParameters(
            stimulus_type=StimulusType.GABOR_PATCH,
            intensity=0.7,
            duration_ms=1000.0
        )
        
        assert params.stimulus_type == StimulusType.GABOR_PATCH
        assert params.intensity == 0.7
        assert params.duration_ms == 1000.0
        assert params.validate() is True
    
    def test_base_stimulus_parameters_validation(self):
        """Test stimulus parameter validation."""
        # Valid parameters
        valid_params = StimulusParameters(
            stimulus_type=StimulusType.TONE,
            intensity=0.5,
            duration_ms=500.0
        )
        assert valid_params.validate() is True
        
        # Invalid intensity
        invalid_intensity = StimulusParameters(
            stimulus_type=StimulusType.TONE,
            intensity=1.5,  # Invalid: > 1.0
            duration_ms=500.0
        )
        assert invalid_intensity.validate() is False
        
        # Invalid duration
        invalid_duration = StimulusParameters(
            stimulus_type=StimulusType.TONE,
            intensity=0.5,
            duration_ms=-100.0  # Invalid: negative
        )
        assert invalid_duration.validate() is False
    
    def test_gabor_parameters(self):
        """Test Gabor patch parameters."""
        params = GaborParameters(
            intensity=0.6,
            contrast=0.8,
            spatial_frequency=2.0,
            size_degrees=5.0,
            orientation=45.0
        )
        
        assert params.stimulus_type == StimulusType.GABOR_PATCH
        assert params.intensity == 0.6
        assert params.contrast == 0.8
        assert params.spatial_frequency == 2.0
        assert params.size_degrees == 5.0
        assert params.orientation == 45.0
    
    def test_tone_parameters(self):
        """Test tone parameters."""
        params = ToneParameters(
            intensity=0.4,
            frequency=1000.0,
            amplitude=0.7
        )
        
        assert params.stimulus_type == StimulusType.TONE
        assert params.intensity == 0.4
        assert params.frequency == 1000.0
        assert params.amplitude == 0.7
    
    def test_co2_puff_parameters(self):
        """Test CO2 puff parameters."""
        params = CO2PuffParameters(
            intensity=0.3,
            co2_concentration=8.0,
            duration_ms=200.0
        )
        
        assert params.stimulus_type == StimulusType.CO2_PUFF
        assert params.intensity == 0.3
        assert params.co2_concentration == 8.0
        assert params.duration_ms == 200.0
    
    def test_heartbeat_flash_parameters(self):
        """Test heartbeat flash parameters."""
        params = HeartbeatFlashParameters(
            intensity=0.5,
            flash_duration_ms=100.0,
            timing_offset_ms=50.0
        )
        
        assert params.stimulus_type == StimulusType.HEARTBEAT_FLASH
        assert params.intensity == 0.5
        assert params.flash_duration_ms == 100.0
        assert params.timing_offset_ms == 50.0


class TestStimulusGenerator:
    """Test stimulus generator implementation."""
    
    def test_initialization(self):
        """Test stimulus generator initialization."""
        generator = StimulusGenerator()
        assert generator.is_active is False
        assert generator.current_stimulus is None
    
    def test_generate_gabor_stimulus(self):
        """Test Gabor stimulus generation."""
        generator = StimulusGenerator()
        params = GaborParameters(
            intensity=0.6,
            contrast=0.8,
            spatial_frequency=2.0
        )
        
        stimulus = generator.generate_stimulus(params)
        assert stimulus is not None
        assert stimulus.stimulus_type == StimulusType.GABOR_PATCH
        assert stimulus.intensity == params.intensity
        assert stimulus.timestamp is not None
    
    def test_generate_tone_stimulus(self):
        """Test tone stimulus generation."""
        generator = StimulusGenerator()
        params = ToneParameters(
            intensity=0.4,
            frequency=1000.0,
            amplitude=0.7
        )
        
        stimulus = generator.generate_stimulus(params)
        assert stimulus is not None
        assert stimulus.stimulus_type == StimulusType.TONE
        assert stimulus.intensity == params.intensity
    
    def test_generate_co2_puff_stimulus(self):
        """Test CO2 puff stimulus generation."""
        generator = StimulusGenerator()
        params = CO2PuffParameters(
            intensity=0.3,
            co2_concentration=8.0,
            duration_ms=200.0
        )
        
        stimulus = generator.generate_stimulus(params)
        assert stimulus is not None
        assert stimulus.stimulus_type == StimulusType.CO2_PUFF
        assert stimulus.intensity == params.intensity
    
    def test_generate_heartbeat_flash_stimulus(self):
        """Test heartbeat flash stimulus generation."""
        generator = StimulusGenerator()
        params = HeartbeatFlashParameters(
            intensity=0.5,
            flash_duration_ms=100.0,
            timing_offset_ms=50.0
        )
        
        stimulus = generator.generate_stimulus(params)
        assert stimulus is not None
        assert stimulus.stimulus_type == StimulusType.HEARTBEAT_FLASH
        assert stimulus.intensity == params.intensity
    
    def test_start_stop_stimulation(self):
        """Test starting and stopping stimulation."""
        generator = StimulusGenerator()
        
        # Start stimulation
        generator.start_stimulation()
        assert generator.is_active is True
        
        # Stop stimulation
        generator.stop_stimulation()
        assert generator.is_active is False


class TestTaskController:
    """Test task controller implementation."""
    
    def test_initialization(self):
        """Test task controller initialization."""
        params = TaskParameters(
            min_trials=10,
            max_trials=50,
            task_type="detection"
        )
        controller = TaskController(params)
        
        assert controller.parameters == params
        assert controller.state == TaskState.READY
        assert controller.trial_count == 0
        assert len(controller.trial_results) == 0
    
    def test_start_task(self):
        """Test starting a task."""
        params = TaskParameters(min_trials=5, max_trials=20)
        controller = TaskController(params)
        
        controller.start_task()
        assert controller.state == TaskState.RUNNING
        assert controller.trial_count == 0
    
    def test_run_trial(self):
        """Test running a single trial."""
        params = TaskParameters(min_trials=5, max_trials=20)
        controller = TaskController(params)
        controller.start_task()
        
        # Run a trial
        result = controller.run_trial()
        
        assert isinstance(result, TrialResult)
        assert controller.trial_count == 1
        assert len(controller.trial_results) == 1
        assert result.trial_number == 1
    
    def test_record_response(self):
        """Test recording participant response."""
        params = TaskParameters(min_trials=5, max_trials=20)
        controller = TaskController(params)
        controller.start_task()
        
        # Run trial and record response
        trial_result = controller.run_trial()
        controller.record_response(trial_result.trial_number, response=1, rt=0.350)
        
        # Check response was recorded
        updated_result = controller.trial_results[-1]
        assert updated_result.response == 1
        assert updated_result.reaction_time == 0.350
    
    def test_task_completion(self):
        """Test task completion conditions."""
        params = TaskParameters(min_trials=5, max_trials=10)
        controller = TaskController(params)
        controller.start_task()
        
        # Run minimum trials
        for i in range(5):
            trial_result = controller.run_trial()
            controller.record_response(trial_result.trial_number, response=1, rt=0.350)
        
        # Should be able to complete
        assert controller.can_complete_task()
        
        # Complete task
        controller.complete_task()
        assert controller.state == TaskState.COMPLETED
    
    def test_task_termination(self):
        """Test task termination."""
        params = TaskParameters(min_trials=5, max_trials=20)
        controller = TaskController(params)
        controller.start_task()
        
        # Terminate task
        controller.terminate_task()
        assert controller.state == TaskState.TERMINATED
    
    def test_get_performance_summary(self):
        """Test performance summary generation."""
        params = TaskParameters(min_trials=5, max_trials=20)
        controller = TaskController(params)
        controller.start_task()
        
        # Run some trials with responses
        for i in range(5):
            trial_result = controller.run_trial()
            response = 1 if i % 2 == 0 else 0  # Alternating responses
            controller.record_response(trial_result.trial_number, response=response, rt=0.350)
        
        # Get performance summary
        summary = controller.get_performance_summary()
        
        assert isinstance(summary, dict)
        assert 'total_trials' in summary
        assert 'accuracy' in summary
        assert 'mean_reaction_time' in summary
        assert summary['total_trials'] == 5
        assert 0.0 <= summary['accuracy'] <= 1.0


if __name__ == "__main__":
    pytest.main([__file__])
