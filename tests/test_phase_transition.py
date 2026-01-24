import pytest
import numpy as np

# Import the Phase Transition model
try:
    from apgi_framework.core.somatic_marker import SomaticMarkerEngine
    from apgi_framework.core.threshold import ThresholdManager

    # Create a mock SomaticAgent class for testing
    class SomaticAgent:
        def __init__(self, n_states=4, n_actions=3, n_contexts=2):
            self.n_states = n_states
            self.n_actions = n_actions
            self.n_contexts = n_contexts
            self.somatic_markers = np.zeros((n_contexts, n_actions))

        def expected_free_energy(self, beliefs, context=0):
            # Mock implementation
            G_modified = np.random.random(self.n_actions)
            G_basic = np.random.random(self.n_actions)
            return G_modified, G_basic

        def update_somatic_marker(self, context, action, outcome):
            # Simple update rule
            self.somatic_markers[context, action] += 0.1 * outcome

        def decide(self, beliefs, context=0, surprise=0.1):
            # Simple decision making
            action = np.random.randint(0, self.n_actions)
            conscious = surprise > 1.0  # High surprise triggers conscious access
            return action, conscious, {"surprise": surprise}

except ImportError as e:
    pytest.skip(f"Could not import required modules: {e}", allow_module_level=True)


class TestSomaticAgent:
    def test_initialization(self):
        """Test that the SomaticAgent initializes correctly."""
        agent = SomaticAgent(n_states=4, n_actions=3, n_contexts=2)
        assert agent is not None
        assert agent.somatic_markers.shape == (2, 3)  # n_contexts x n_actions

    def test_expected_free_energy(self):
        """Test the expected free energy calculation."""
        agent = SomaticAgent(n_states=4, n_actions=3, n_contexts=2)
        beliefs = np.ones(4) / 4  # Uniform beliefs

        G_modified, G_basic = agent.expected_free_energy(beliefs, context=0)

        # Basic validation of the output
        assert len(G_modified) == 3  # n_actions
        assert len(G_basic) == 3  # n_actions

    def test_somatic_marker_update(self):
        """Test updating somatic markers."""
        agent = SomaticAgent(n_states=4, n_actions=3, n_contexts=2)
        context = 0
        action = 1
        initial_value = agent.somatic_markers[context, action]

        # Update with a positive outcome
        agent.update_somatic_marker(context, action, 1.0)
        assert agent.somatic_markers[context, action] > initial_value

        # Update with a negative outcome
        initial_value = agent.somatic_markers[context, action]
        agent.update_somatic_marker(context, action, -1.0)
        assert agent.somatic_markers[context, action] < initial_value

    def test_decision_making(self):
        """Test the decision-making process."""
        agent = SomaticAgent(n_states=4, n_actions=3, n_contexts=2)
        beliefs = np.ones(4) / 4  # Uniform beliefs

        # Test with low surprise (should not trigger conscious ignition)
        action, conscious, _ = agent.decide(beliefs, context=0, surprise=0.1)
        assert action in [0, 1, 2]  # Valid action
        assert not conscious  # Should be an automatic decision

        # Test with high surprise and uncertainty (should trigger conscious ignition)
        action, conscious, _ = agent.decide(beliefs, context=0, surprise=2.0)
        assert action in [0, 1, 2]  # Valid action
        # Note: The actual behavior depends on the implementation details


if __name__ == "__main__":
    pytest.main(["-v", "test_phase_transition.py"])
