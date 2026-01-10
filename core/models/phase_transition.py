import numpy as np
from apgi_framework.logging.standardized_logging import get_logger

logger = get_logger("phase_transition")


class SomaticAgent:
    def __init__(self, n_states, n_actions, n_contexts):
        self.n_states = n_states
        self.n_actions = n_actions
        self.somatic_markers = np.zeros((n_contexts, n_actions))  # M(c,a)
        self.precision = 1.0  # Initial precision

    def expected_free_energy(self, beliefs, context):
        """Calculate G for each action, modified by somatic markers."""
        # Basic EFE calculation (simplified)
        G_basic = np.random.randn(self.n_actions) * 0.5  # Placeholder

        # Modify by somatic markers
        G_modified = G_basic - self.somatic_markers[context, :] * self.precision

        return G_modified, G_basic

    def update_somatic_marker(self, context, action, outcome_valence):
        """Update somatic marker based on outcome."""
        learning_rate = 0.1
        self.somatic_markers[context, action] += learning_rate * (
            outcome_valence - self.somatic_markers[context, action]
        )

    def decide(self, beliefs, context, surprise):
        """Make decision with potential conscious ignition."""
        G_modified, G_basic = self.expected_free_energy(beliefs, context)

        # Check for ignition
        ignition_threshold = 1.5
        if (
            surprise > ignition_threshold and np.std(G_modified) < 0.5
        ):  # High uncertainty
            logger.info("CONSCIOUS IGNITION: Deliberating with full access")
            # Simulate conscious deliberation - more thorough processing
            action_probs = np.exp(-G_modified * 5)  # Sharpened distribution
            action_probs = action_probs / np.sum(action_probs)
            chosen_action = np.random.choice(self.n_actions, p=action_probs)
            conscious = True
        else:
            # Habitual/automatic action selection
            chosen_action = np.argmin(G_modified)  # Simple minimization
            conscious = False

        return chosen_action, conscious, G_modified


# Simulation
agent = SomaticAgent(n_states=4, n_actions=3, n_contexts=2)

# Train somatic markers
logger.info("Training somatic markers...")
for episode in range(100):
    context = 0  # "Safe" context
    action = np.random.randint(3)
    # Negative outcome for action 1 in context 0
    if action == 1:
        agent.update_somatic_marker(context, action, -1.0)  # Bad outcome

# Test decision making
logger.info("\nTesting decisions...")
test_contexts = [0, 0, 1, 0]  # Last one is high surprise in safe context
surprises = [0.5, 0.8, 0.3, 2.5]  # Precision-weighted surprise

for i, (context, surprise) in enumerate(zip(test_contexts, surprises)):
    beliefs = np.random.dirichlet(np.ones(4))  # Random beliefs
    action, conscious, G = agent.decide(beliefs, context, surprise)

    logger.info(f"Test {i+1}: Context={context}, Surprise={surprise:.2f}")
    logger.info(f"  Somatic biases: {agent.somatic_markers[context]}")
    logger.info(f"  Modified EFE: {G}")
    logger.info(
        f"  Chose action {action} {'CONSCIOUSLY' if conscious else 'unconsciously'}"
    )
    logger.info("")
