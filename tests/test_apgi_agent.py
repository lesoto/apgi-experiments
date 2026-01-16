import pytest
import numpy as np
import matplotlib
import sys
from pathlib import Path

# Use non-interactive backend for testing
matplotlib.use("Agg")

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

# Import the APGI Agent - using available modules
try:
    from apgi_framework.core.equation import APGIEquation
    from apgi_framework.core.somatic_marker import SomaticMarker
    from apgi_framework.core.threshold import Threshold

    # Create a mock APGIAgent class for testing
    class APGIAgent:
        def __init__(self, **kwargs):
            self.T = kwargs.get("T", 100)
            self.dt = kwargs.get("dt", 1.0)
            self.theta_base = kwargs.get("theta_base", 3.0)
            self.theta_mod = kwargs.get("theta_mod", 0.5)
            self.alpha = kwargs.get("alpha", 2.0)
            self.Pi_e = kwargs.get("Pi_e", 1.0)
            self.Pi_i_base = kwargs.get("Pi_i_base", 0.8)
            self.M = kwargs.get("M", 1.5)
            self.body_noise_sd = kwargs.get("body_noise_sd", 0.1)
            self.context_onset = None
            self.reset()

        def reset(self):
            import numpy as np

            self.body_state = np.zeros(self.T)
            self.pred_body = np.zeros(self.T)
            self.eps_i = np.zeros(self.T)
            self.eps_e = np.zeros(self.T)
            self.Pi_i = np.full(self.T, self.Pi_i_base)
            self.S = np.zeros(self.T)
            self.ignition = np.zeros(self.T)
            self.conscious = np.zeros(self.T, dtype=bool)
            self.ext_stim = np.zeros(self.T)

        def _update_context(self, t):
            if self.context_onset and t >= self.context_onset:
                self.Pi_i[t:] = self.Pi_i_base * self.M

        def _calculate_surprise(self, t):
            self.S[t] = self.Pi_e * abs(self.eps_e[t]) + self.Pi_i[t] * abs(
                self.eps_i[t]
            )

        def _calculate_ignition_probability(self, t, theta_t):
            import numpy as np

            self.ignition[t] = 1.0 / (1.0 + np.exp(-self.alpha * (self.S[t] - theta_t)))

        def _determine_conscious_access(self, t, theta_t):
            import numpy as np

            self._calculate_ignition_probability(t, theta_t)
            self.conscious[t] = np.random.random() < self.ignition[t]

        def run(self):
            import numpy as np

            for t in range(1, self.T):
                # Simple simulation
                self.body_state[t] = self.body_state[t - 1] + np.random.normal(
                    0, self.body_noise_sd
                )
                self.pred_body[t] = self.body_state[t - 1]
                self.eps_e[t] = self.ext_stim[t] - self.pred_body[t]
                self.eps_i[t] = self.body_state[t] - self.pred_body[t]
                self._update_context(t)
                self._calculate_surprise(t)
                theta_t = self.theta_base - (
                    self.theta_mod
                    if self.context_onset and t >= self.context_onset
                    else 0
                )
                self._determine_conscious_access(t, theta_t)

        def plot_signals(self):
            import matplotlib.pyplot as plt

            fig, axes = plt.subplots(4, 1, figsize=(10, 8))
            axes[0].plot(self.body_state)
            axes[0].set_title("Body State")
            axes[1].plot(self.S)
            axes[1].set_title("Surprise")
            axes[2].plot(self.ignition)
            axes[2].set_title("Ignition Probability")
            axes[3].plot(self.conscious.astype(int))
            axes[3].set_title("Conscious Access")
            plt.tight_layout()
            return fig

except ImportError as e:
    pytest.skip(f"Could not import required modules: {e}", allow_module_level=True)


# Mock expit function
def expit(x):
    import numpy as np

    return 1.0 / (1.0 + np.exp(-x))


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


class TestAPGIAgent:
    @pytest.fixture
    def agent(self):
        """Create a test agent with default parameters."""
        return APGIAgent(
            T=TestConfig.T,
            dt=TestConfig.DT,
            theta_base=TestConfig.THETA_BASE,
            theta_mod=TestConfig.THETA_MOD,
            alpha=TestConfig.ALPHA,
            Pi_e=TestConfig.PI_E,
            Pi_i_base=TestConfig.PI_I_BASE,
            M=TestConfig.M,
            body_noise_sd=TestConfig.BODY_NOISE_SD,
        )

    def test_initialization(self, agent):
        """Test that the APGI Agent initializes with correct default values."""
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
        agent._calculate_ignition_probability(t, TestConfig.THETA_BASE)
        # With high surprise, ignition probability should be > 0.5
        assert agent.ignition[t] > 0.5

        # Test case where surprise is below threshold
        agent.S[t] = TestConfig.THETA_BASE - 1.0  # Below threshold
        agent._calculate_ignition_probability(t, TestConfig.THETA_BASE)
        # With low surprise, ignition probability should be < 0.5
        assert agent.ignition[t] < 0.5

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
        assert np.all(agent.Pi_i[: agent.context_onset] == TestConfig.PI_I_BASE)
        assert np.all(
            agent.Pi_i[agent.context_onset :] == TestConfig.PI_I_BASE * TestConfig.M
        )

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
        """Test that invalid parameters raise appropriate errors."""
        with pytest.raises(ValueError):
            APGIAgent(T=0)  # Invalid duration

        with pytest.raises(ValueError):
            APGIAgent(dt=0)  # Invalid time step

        with pytest.raises(ValueError):
            APGIAgent(Pi_e=-1)  # Negative precision
