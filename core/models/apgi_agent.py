"""
Integrated Predictive Ignition (APGI) Agent

This module implements a computational model of consciousness based on the
Integrated Predictive Ignition (APGI) framework, which integrates interoceptive
and exteroceptive prediction errors with a dynamic threshold for conscious access.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.special import expit  # logistic sigmoid
from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class APGIConfig:
    """Configuration parameters for the APGI Agent."""
    T: int = 1000  # Number of timesteps
    dt: float = 1.0  # Time step size
    theta_base: float = 3.0  # Base threshold for conscious access
    theta_mod: float = 0.5  # Contextual modulation of threshold
    alpha: float = 2.0  # Sigmoid steepness for ignition probability
    Pi_e: float = 1.0  # Exteroceptive precision
    Pi_i_base: float = 0.8  # Baseline interoceptive precision
    M: float = 1.5  # Somatic marker gain
    body_noise_sd: float = 0.3  # Standard deviation of body state noise
    body_setpoint: float = 0.0  # Homeostatic setpoint


class APGIAgent:
    """
    An agent implementing the Integrated Predictive Ignition (APGI) model.
    
    The agent processes interoceptive and exteroceptive signals, computes
    prediction errors, and determines conscious access based on a dynamic
    threshold mechanism.
    """
    
    def __init__(self, **kwargs):
        """
        Initialize the APGI Agent with the given configuration.
        
        Args:
            **kwargs: Configuration parameters (see APGIConfig for defaults)
        """
        self.config = APGIConfig(**kwargs)
        self._validate_parameters()
        
        # Initialize state variables
        self.reset()
        
        # External stimulus (can be set before running the simulation)
        self.ext_stim = np.zeros(self.config.T)
        self.context_onset = int(self.config.T * 0.2)  # Default context onset

    
    @property
    def T(self):
        """Backward compatibility property for T."""
        return self.config.T
    
    @property
    def dt(self):
        """Backward compatibility property for dt."""
        return self.config.dt
    
    @property
    def theta_base(self):
        """Backward compatibility property for theta_base."""
        return self.config.theta_base
    
    @property
    def theta_mod(self):
        """Backward compatibility property for theta_mod."""
        return self.config.theta_mod
    
    @property
    def alpha(self):
        """Backward compatibility property for alpha."""
        return self.config.alpha
    
    @property
    def Pi_e(self):
        """Backward compatibility property for Pi_e."""
        return self.config.Pi_e
    
    @property
    def Pi_i_base(self):
        """Backward compatibility property for Pi_i_base."""
        return self.config.Pi_i_base
    
    @property
    def M(self):
        """Backward compatibility property for M."""
        return self.config.M
    
    @property
    def body_noise_sd(self):
        """Backward compatibility property for body_noise_sd."""
        return self.config.body_noise_sd
    
    def _validate_parameters(self):
        """Validate configuration parameters."""
        if self.config.T <= 0:
            raise ValueError("T must be positive")
        if self.config.dt <= 0:
            raise ValueError("dt must be positive")
        if self.config.Pi_e <= 0:
            raise ValueError("Pi_e must be positive")
        if self.config.Pi_i_base <= 0:
            raise ValueError("Pi_i_base must be positive")
    
    def reset(self):
        """Reset the agent's internal state."""
        # State variables
        self.body_state = np.zeros(self.config.T)
        self.pred_body = np.zeros(self.config.T)
        self.eps_i = np.zeros(self.config.T)  # Interoceptive prediction error
        self.eps_e = np.zeros(self.config.T)  # Exteroceptive prediction error
        self.Pi_i = np.ones(self.config.T) * self.config.Pi_i_base
        self.S = np.zeros(self.config.T)  # Total surprise
        self.ignition = np.zeros(self.config.T)  # Ignition probability
        self.conscious = np.zeros(self.config.T, dtype=bool)  # Binary conscious access
    
    def _update_context(self, t: int):
        """Update interoceptive precision based on context."""
        if t >= self.context_onset:
            self.Pi_i[t] = self.config.Pi_i_base * self.config.M
        else:
            self.Pi_i[t] = self.config.Pi_i_base
    
    def _calculate_surprise(self, t: int):
        """Calculate total precision-weighted surprise."""
        self.S[t] = (self.config.Pi_e * abs(self.eps_e[t]) + 
                    self.Pi_i[t] * abs(self.eps_i[t]))
    
    def _calculate_ignition_probability(self, t: int, theta_t: float):
        """Calculate the probability of conscious ignition."""
        self.ignition[t] = expit(self.config.alpha * (self.S[t] - theta_t))
    
    def _determine_conscious_access(self, t: int, theta_t: float):
        """Determine if the current state results in conscious access."""
        # Use probabilistic access based on ignition probability
        # This ensures some conscious moments occur during stimulation
        self.conscious[t] = (np.random.random() < self.ignition[t])
    
    def run(self):
        """Run the simulation for all time steps."""
        if (
            len(self.body_state) != self.config.T
            or len(self.pred_body) != self.config.T
            or len(self.eps_i) != self.config.T
            or len(self.eps_e) != self.config.T
            or len(self.Pi_i) != self.config.T
            or len(self.S) != self.config.T
            or len(self.ignition) != self.config.T
            or len(self.conscious) != self.config.T
            or len(self.ext_stim) != self.config.T
        ):
            raise ValueError("Array size mismatch")

        if np.isnan(self.ext_stim).any():
            raise ValueError("NaN values in ext_stim")
        if np.isinf(self.ext_stim).any():
            raise ValueError("infinite values in ext_stim")

        for t in range(1, self.config.T):
            # 1. Update context-dependent precision
            self._update_context(t)
            
            # 2. Generate bodily state with noise
            self.body_state[t] = (self.config.body_setpoint + 
                                np.random.normal(0, self.config.body_noise_sd))
            
            # 3. Predict bodily state (simplified)
            self.pred_body[t] = self.config.body_setpoint
            
            # 4. Compute prediction errors
            self.eps_i[t] = self.body_state[t] - self.pred_body[t]
            self.eps_e[t] = self.ext_stim[t]  # Assume prediction = 0
            
            # 5. Calculate total surprise
            self._calculate_surprise(t)
            
            # 6. Dynamic threshold
            theta_t = (self.config.theta_base - 
                      (self.config.theta_mod if t >= self.context_onset else 0))
            
            # 7. Calculate ignition probability
            self._calculate_ignition_probability(t, theta_t)
            
            # 8. Determine conscious access
            self._determine_conscious_access(t, theta_t)
    
    def plot_signals(self):
        """Plot the agent's signals over time."""
        fig, axs = plt.subplots(5, 1, figsize=(12, 10), sharex=True)
        
        # Exteroceptive stimulus
        axs[0].plot(self.ext_stim, color='steelblue')
        axs[0].set_ylabel('Exteroceptive\nStimulus')
        axs[0].axvline(self.context_onset, color='gray', linestyle='--', 
                      label='Context Onset')
        axs[0].legend()
        
        # Interoceptive state
        axs[1].plot(self.body_state, color='firebrick', alpha=0.7)
        axs[1].plot(self.pred_body, color='black', linestyle='--')
        axs[1].set_ylabel('Interoceptive\nState')
        axs[1].legend(['Actual', 'Predicted'])
        
        # Interoceptive precision
        axs[2].plot(self.Pi_i, color='purple')
        axs[2].set_ylabel('Interoceptive\nPrecision (Πⁱ)')
        axs[2].axhline(self.config.Pi_i_base, color='gray', linestyle=':')
        
        # Surprise and threshold
        theta_curve = [self.config.theta_base - 
                      (self.config.theta_mod if t >= self.context_onset else 0)
                     for t in range(self.config.T)]
        axs[3].plot(self.S, color='orange', label='Total Surprise $S_t$')
        axs[3].plot(theta_curve, color='red', linestyle='--', 
                   label='Threshold $\\theta_t$')
        axs[3].set_ylabel('Surprise &\nThreshold')
        axs[3].legend()
        
        # Ignition and conscious access
        axs[4].plot(self.ignition, color='green')
        axs[4].fill_between(range(self.config.T), 0, self.conscious.astype(int), 
                           color='limegreen', alpha=0.3)
        axs[4].set_ylabel('Ignition\nProbability')
        axs[4].set_xlabel('Time (ms)')
        axs[4].set_ylim(-0.1, 1.1)
        
        plt.suptitle('Integrated Predictive Ignition (APGI) Agent Simulation')
        plt.tight_layout()
        return fig
    
    def run_example(self):
        """Run an example simulation with default parameters."""
        # Add a test stimulus
        self.ext_stim[200:250] = 2.0
        self.context_onset = 150
        
        # Run the simulation
        self.run()
        
        # Plot the results
        fig = self.plot_signals()
        plt.show()
        return fig


if __name__ == "__main__":
    agent = APGIAgent()
    agent.run_example()