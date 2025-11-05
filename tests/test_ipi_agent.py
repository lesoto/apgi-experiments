import pytest
import numpy as np
import matplotlib
import sys
from pathlib import Path

# Use non-interactive backend for testing
matplotlib.use('Agg')

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

# Import the IPI Agent
from core.models.ipi_agent import (
    IPIAgent,  # This will be our refactored class
    expit  # For testing the sigmoid function
)

# Test configuration
class TestConfig:
    T = 100  # Shorter duration for tests
    DT = 1.0
    THETA_BASE = 3.0
    THETA_MOD = 0.5
    ALPHA = 2.0
    PI_E = 1.0
    PI_I_BASE = 0.8
    M = 1.5
    BODY_NOISE_SD = 0.1  # Reduced noise for more predictable tests


class TestIPIAgent:
    @pytest.fixture
    def agent(self):
        """Create a test agent with default parameters."""
        return IPIAgent(
            T=TestConfig.T,
            dt=TestConfig.DT,
            theta_base=TestConfig.THETA_BASE,
            theta_mod=TestConfig.THETA_MOD,
            alpha=TestConfig.ALPHA,
            Pi_e=TestConfig.PI_E,
            Pi_i_base=TestConfig.PI_I_BASE,
            M=TestConfig.M,
            body_noise_sd=TestConfig.BODY_NOISE_SD
        )

    def test_initialization(self, agent):
        """Test that the IPI Agent initializes with correct default values."""
        assert agent.T == TestConfig.T
        assert agent.dt == TestConfig.DT
        assert agent.theta_base == TestConfig.THETA_BASE
        assert agent.theta_mod == TestConfig.THETA_MOD
        assert agent.alpha == TestConfig.ALPHA
        assert agent.Pi_e == TestConfig.PI_E
        assert agent.Pi_i_base == TestConfig.PI_I_BASE
        assert agent.M == TestConfig.M
        assert agent.body_noise_sd == TestConfig.BODY_NOISE_SD

    def test_reset(self, agent):
        """Test that reset() properly initializes all state variables."""
        agent.reset()
        
        # Check array shapes
        assert agent.body_state.shape == (TestConfig.T,)
        assert agent.pred_body.shape == (TestConfig.T,)
        assert agent.eps_i.shape == (TestConfig.T,)
        assert agent.eps_e.shape == (TestConfig.T,)
        assert agent.Pi_i.shape == (TestConfig.T,)
        assert agent.S.shape == (TestConfig.T,)
        assert agent.ignition.shape == (TestConfig.T,)
        assert agent.conscious.shape == (TestConfig.T,)
        
        # Check initial values
        assert np.all(agent.Pi_i == TestConfig.PI_I_BASE)
        assert np.all(agent.conscious == False)

    def test_context_modulation(self, agent):
        """Test that context properly modulates interoceptive precision."""
        agent.reset()
        
        # Before context onset
        agent.context_onset = 50
        agent._update_context(25)  # Before onset
        assert agent.Pi_i[25] == TestConfig.PI_I_BASE  # No modulation
        
        # After context onset
        agent._update_context(75)  # After onset
        assert agent.Pi_i[75] == TestConfig.PI_I_BASE * TestConfig.M  # Modulated by M

    def test_surprise_calculation(self, agent):
        """Test the calculation of total surprise."""
        agent.reset()
        
        # Set up test values
        t = 10
        eps_e = 1.5
        eps_i = 0.8
        Pi_i = 1.2
        
        # Manually set values
        agent.eps_e[t] = eps_e
        agent.eps_i[t] = eps_i
        agent.Pi_i[t] = Pi_i
        
        # Calculate surprise
        agent._calculate_surprise(t)
        
        # Expected surprise
        expected_S = TestConfig.PI_E * abs(eps_e) + Pi_i * abs(eps_i)
        assert np.isclose(agent.S[t], expected_S)

    def test_ignition_probability(self, agent):
        """Test the calculation of ignition probability."""
        agent.reset()
        
        # Set up test values
        t = 10
        S = 2.5
        theta_t = TestConfig.THETA_BASE - TestConfig.THETA_MOD  # With context
        
        # Set surprise and threshold
        agent.S[t] = S
        agent._calculate_ignition_probability(t, theta_t)
        
        # Expected ignition probability
        expected_ignition = expit(TestConfig.ALPHA * (S - theta_t))
        assert np.isclose(agent.ignition[t], expected_ignition)

    def test_conscious_access(self, agent):
        """Test the determination of conscious access."""
        agent.reset()
        
        # Test case where surprise is above threshold
        t = 10
        agent.S[t] = TestConfig.THETA_BASE + 1.0  # Above threshold
        agent._determine_conscious_access(t, TestConfig.THETA_BASE)
        assert agent.conscious[t] == True
        
        # Test case where surprise is below threshold
        agent.S[t] = TestConfig.THETA_BASE - 1.0  # Below threshold
        agent._determine_conscious_access(t, TestConfig.THETA_BASE)
        assert agent.conscious[t] == False

    def test_full_simulation(self, agent):
        """Test a complete simulation run."""
        agent.reset()
        
        # Add a test stimulus
        agent.ext_stim[20:30] = 2.0
        agent.context_onset = 40
        
        # Run the simulation
        agent.run()
        
        # Check that the simulation produced valid results
        assert np.any(agent.conscious)  # At least some conscious moments
        assert np.all(agent.ignition >= 0.0) and np.all(agent.ignition <= 1.0)
        
        # Check that context modulation was applied
        assert np.all(agent.Pi_i[:agent.context_onset] == TestConfig.PI_I_BASE)
        assert np.all(agent.Pi_i[agent.context_onset:] == TestConfig.PI_I_BASE * TestConfig.M)

    def test_visualization(self, agent):
        """Test that visualization functions run without errors."""
        agent.reset()
        agent.run()
        
        # Test plotting functions
        fig = agent.plot_signals()
        assert fig is not None
        
        # Clean up
        import matplotlib.pyplot as plt
        plt.close(fig)

    def test_parameter_validation(self):
        ""Test that invalid parameters raise appropriate errors.""
        with pytest.raises(ValueError):
            IPIAgent(T=0)  # Invalid duration
            
        with pytest.raises(ValueError):
            IPIAgent(dt=0)  # Invalid time step
            
        with pytest.raises(ValueError):
            IPIAgent(Pi_e=-1)  # Negative precision
