import numpy as np
import matplotlib.pyplot as plt
from scipy.special import expit

class PredictiveIgnitionNetwork:
    def __init__(self, n_features, n_global_units, threshold, alpha):
        self.W = np.random.randn(n_global_units, n_features) * 0.1  # Weights
        self.precision = np.ones(n_features)  # Π - precision weights
        self.threshold = threshold
        self.alpha = alpha
        self.global_activation = np.zeros(n_global_units)
        
    def forward_pass(self, sensory_input, somatic_gain=1.0):
        # Generate predictions from global to sensory
        predictions = self.global_activation @ self.W
        
        # Calculate prediction errors
        errors = sensory_input - predictions
        
        # Precision-weight errors (including somatic gain for interoceptive channels)
        weighted_errors = self.precision * errors * somatic_gain
        
        # Check for ignition in global workspace
        total_surprise = np.sum(np.abs(weighted_errors))
        ignition_prob = expit(self.alpha * (total_surprise - self.threshold))
        
        # If ignition occurs, update global workspace
        if ignition_prob > 0.5:  # Binary ignition for demonstration
            # Global workspace updates based on weighted errors
            self.global_activation = np.tanh(weighted_errors @ self.W.T)
            ignited = True
        else:
            ignited = False
            
        return predictions, errors, weighted_errors, ignited, ignition_prob

# Simulation
network = PredictiveIgnitionNetwork(n_features=10, n_global_units=5, threshold=2.0, alpha=2.0)

# Test with different inputs
inputs = [np.random.randn(10) * 0.1 for _ in range(20)]  # Mostly predictable
inputs[5] = np.random.randn(10) * 2.0  # Unexpected event
inputs[15] = np.random.randn(10) * 1.5  # Another unexpected event

ignition_events = []
for i, input_data in enumerate(inputs):
    # Increase somatic gain for emotional stimuli
    somatic_gain = 2.0 if i in [5, 15] else 1.0
    
    preds, errs, w_errs, ignited, prob = network.forward_pass(input_data, somatic_gain)
    ignition_events.append((i, ignited, prob, np.sum(np.abs(w_errs))))

# Plot results
time_points = [x[0] for x in ignition_events]
surprise = [x[3] for x in ignition_events]
ignited = [x[1] for x in ignition_events]

plt.figure(figsize=(12, 4))
plt.plot(time_points, surprise, 'b-', label='Precision-Weighted Surprise')
plt.axhline(y=network.threshold, color='r', linestyle='--', label='Ignition Threshold')
plt.fill_between(time_points, surprise, network.threshold, where=[s > network.threshold for s in surprise], 
                 alpha=0.3, color='red', label='Above Threshold')
plt.scatter(time_points, surprise, c=['red' if ig else 'blue' for ig in ignited], 
           s=50, zorder=3)
plt.ylabel('S_t (Precision-Weighted Surprise)')
plt.xlabel('Time Step')
plt.title('Ignition Events in Predictive Network')
plt.legend()
plt.grid(True)
plt.show()