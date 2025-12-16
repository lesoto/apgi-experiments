import os
import sys
import numpy as np
import matplotlib.pyplot as plt

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from research.ai_benchmarking.experiments.environment import GridWorld, GameObject, ObjectType
from research.ai_benchmarking.experiments.agents import RandomAgent

def test_environment():
    # Create a small test environment
    env = GridWorld(size=10, n_food=3, n_obstacles=2, n_predators=1)
    
    # Add a single random agent
    agent = RandomAgent()
    env.add_agent(agent)
    
    # Run a few steps
    for step in range(10):
        print(f"\n--- Step {step} ---")
        
        # Get observation for the agent
        obs = env.get_observation(agent)
        print(f"Agent position: {agent.position}")
        print(f"Agent energy: {agent.energy}")
        
        # Let the agent act
        action = agent.act(obs)
        print(f"Agent action: {action}")
        
        # Step the environment
        env.step()
        
        # Render the environment every 5 steps to avoid too many plots
        if step % 5 == 0:
            plt.figure(step)  # Create a new figure for each render
            env.render()
            plt.savefig(f'env_step_{step}.png')
            plt.close()
        
        # Check if agent is still alive
        if not agent.active:
            print("Agent died!")
            break
    
    print("\nTest completed successfully!")

if __name__ == "__main__":
    test_environment()
