import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import Tuple, List, Optional
import numpy.typing as npt

@dataclass
class IPIParams:
    """Parameters for the IPI model."""
    alpha: float = 1.0  # Sigmoid steepness
    theta_base: float = 5.0  # Base ignition threshold
    sigma_epsilon: float = 1.0  # Standard deviation of prediction errors
    sigma_pe: float = 0.5  # Standard deviation of precision for exteroception
    sigma_pi: float = 0.5  # Standard deviation of precision for interoception
    n_steps: int = 1000  # Number of time steps for simulation
    
    def __post_init__(self):
        assert self.alpha > 0, "Alpha must be positive"
        assert self.theta_base > 0, "Base threshold must be positive"

class IPIModel:
    """Implements the IPI (Interoceptive Predictive Integration) model."""
    
    def __init__(self, params: Optional[IPIParams] = None):
        self.params = params or IPIParams()
        
    def sigmoid(self, x: npt.ArrayLike) -> np.ndarray:
        """Logistic sigmoid function."""
        return 1 / (1 + np.exp(-self.params.alpha * x))
    
    def compute_precision(self, variance: float) -> float:
        """Compute precision (inverse variance)."""
        return 1.0 / (variance + 1e-10)  # Add small epsilon to avoid division by zero
    
    def generate_prediction_errors(self, n: int) -> Tuple[np.ndarray, np.ndarray]:
        """Generate random prediction errors (exteroceptive and interoceptive)."""
        # Generate random prediction errors with normal distribution
        epsilon_e = np.random.normal(0, self.params.sigma_epsilon, n)
        epsilon_i = np.random.normal(0, self.params.sigma_epsilon, n)
        return epsilon_e, epsilon_i
    
    def compute_somatic_marker(self, context: int, action: int) -> float:
        """Simple somatic marker function based on context and action."""
        # This is a placeholder - in a real implementation, this would be learned
        return 0.5  # Fixed value for demonstration
    
    def simulate(self, mc_a: Optional[float] = None) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Run the IPI model simulation.
        
        Args:
            mc_a: Optional somatic marker gain. If None, uses compute_somatic_marker.
            
        Returns:
            Tuple of (S_t, B_t, theta_t) arrays
        """
        n = self.params.n_steps
        
        # Generate prediction errors
        epsilon_e, epsilon_i = self.generate_prediction_errors(n)
        
        # Compute precisions
        Pi_e = self.compute_precision(self.params.sigma_pe**2)
        Pi_i = self.compute_precision(self.params.sigma_pi**2)
        
        # Use provided mc_a or compute it
        if mc_a is None:
            mc_a = self.compute_somatic_marker(context=0, action=0)
        
        # Compute total surprise and ignition probability
        S_t = Pi_e * np.abs(epsilon_e) + (Pi_i * mc_a) * np.abs(epsilon_i)
        theta_t = np.full_like(S_t, self.params.theta_base)  # Constant threshold for now
        B_t = self.sigmoid(S_t - theta_t)
        
        return S_t, B_t, theta_t

def plot_simulation(S_t: np.ndarray, B_t: np.ndarray, theta_t: np.ndarray, 
                   title: str = "IPI Model Simulation") -> None:
    """Plot the results of an IPI model simulation."""
    # Set style for this plot
    plt.style.use('ggplot')
    
    # Create figure with white background
    fig = plt.figure(figsize=(12, 8), facecolor='white')
    
    # Plot surprise and threshold
    ax1 = plt.subplot(2, 1, 1)
    ax1.plot(S_t, 'b-', label='Total Surprise (Sₜ)')
    ax1.axhline(y=theta_t[0], color='r', linestyle='--', label='Threshold (θₜ)')
    ax1.set_title(title)
    ax1.set_ylabel('Surprise / Threshold')
    ax1.legend()
    ax1.grid(True)
    
    # Plot ignition probability
    ax2 = plt.subplot(2, 1, 2)
    ax2.plot(B_t, 'g-', label='Ignition Probability (Bₜ)')
    ax2.set_xlabel('Time Step')
    ax2.set_ylabel('Probability')
    ax2.set_ylim(-0.05, 1.05)
    ax2.legend()
    ax2.grid(True)
    
    plt.tight_layout()
    plt.show()

def run_demo():
    """Run a demonstration of the IPI model with default parameters."""
    # Create and run the model
    model = IPIModel()
    S_t, B_t, theta_t = model.simulate()
    
    # Plot the results
    plot_simulation(S_t, B_t, theta_t, "IPI Model Demonstration")
    
    # Print some statistics
    print(f"Mean surprise: {np.mean(S_t):.2f} ± {np.std(S_t):.2f}")
    print(f"Ignition probability: {np.mean(B_t > 0.5) * 100:.1f}% of time steps")

if __name__ == "__main__":
    run_demo()
