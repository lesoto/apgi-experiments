import numpy as np
from typing import Dict, List, Optional, Tuple
import random
from dataclasses import dataclass, field
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
import math

# Import ObjectType from environment
from .environment import ObjectType

@dataclass
class AgentConfig:
    perception_range: float = 5.0
    speed: float = 0.2
    initial_energy: float = 10.0
    movement_cost: float = 0.05
    action_cost: float = 0.01
    learning_rate: float = 0.001
    gamma: float = 0.99
    epsilon: float = 1.0
    epsilon_min: float = 0.01
    epsilon_decay: float = 0.995
    batch_size: int = 32
    memory_size: int = 10000
    update_target_every: int = 100

class BaseAgent:
    """Base class for all agent types."""
    
    def __init__(self, config: Optional[AgentConfig] = None):
        self.config = config or AgentConfig()
        self.position = np.zeros(2)
        self.energy = self.config.initial_energy
        self.radius = 0.2
        self.active = True
        self.perception_range = self.config.perception_range
        self.speed = self.config.speed
        self.movement_cost = self.config.movement_cost
        self.action_cost = self.config.action_cost
        self.food_consumed = 0
        self.memory = deque(maxlen=self.config.memory_size)
        self.steps = 0
        self.obj_type = ObjectType.AGENT  # Add obj_type attribute
    
    def act(self, observation: Dict) -> Dict:
        """Choose an action based on the observation."""
        raise NotImplementedError("Subclasses must implement this method")
    
    def remember(self, state, action, reward, next_state, done):
        """Store experience in memory."""
        self.memory.append((state, action, reward, next_state, done))
    
    def learn(self):
        """Learn from past experiences."""
        pass
    
    def _get_nearest_object(self, observation: Dict, obj_type: str) -> Optional[Dict]:
        """Get the nearest object of a specific type from observation."""
        nearest = None
        min_dist = float('inf')
        
        for obj in observation['nearby_objects']:
            if obj['type'].name.lower() == obj_type.lower():
                if obj['distance'] < min_dist:
                    min_dist = obj['distance']
                    nearest = obj
        
        return nearest

class RandomAgent(BaseAgent):
    """Agent that takes random actions."""
    
    def act(self, observation: Dict) -> Dict:
        # Random direction
        angle = random.uniform(0, 2 * math.pi)
        direction = np.array([math.cos(angle), math.sin(angle)])
        
        return {
            'type': 'move',
            'direction': direction,
            'speed': self.speed
        }

class ReactiveAgent(BaseAgent):
    """Rule-based agent that reacts to nearby objects."""
    
    def act(self, observation: Dict) -> Dict:
        # Default: wander randomly
        action = {
            'type': 'move',
            'direction': np.random.uniform(-1, 1, 2),
            'speed': self.speed
        }
        
        # Normalize direction
        norm = np.linalg.norm(action['direction'])
        if norm > 0:
            action['direction'] /= norm
        
        # Find nearest food and predator
        nearest_food = self._get_nearest_object(observation, 'FOOD')
        nearest_predator = self._get_nearest_object(observation, 'PREDATOR')
        
        # If predator is close, run away
        if nearest_predator and nearest_predator['distance'] < 2.0:
            # Run away from predator
            pred_dir = nearest_predator['relative_position']
            action['direction'] = -pred_dir / (np.linalg.norm(pred_dir) + 1e-6)
            action['speed'] = self.speed * 1.5  # Run faster from predators
        # If food is close, go towards it
        elif nearest_food and nearest_food['distance'] < 3.0:
            food_dir = nearest_food['relative_position']
            action['direction'] = food_dir / (np.linalg.norm(food_dir) + 1e-6)
        
        return action

class DQN(nn.Module):
    """Deep Q-Network for the DQN agent."""
    
    def __init__(self, input_size: int, output_size: int):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(input_size, 64)
        self.fc2 = nn.Linear(64, 64)
        self.fc3 = nn.Linear(64, output_size)
        
        self.relu = nn.ReLU()
    
    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        return self.fc3(x)

class DQNAgent(BaseAgent):
    """Deep Q-Learning agent with experience replay."""
    
    def __init__(self, config: Optional[AgentConfig] = None):
        super().__init__(config)
        self.state_size = 10  # Simplified state representation size
        self.action_size = 8  # 8 directions + no-op
        
        # Main network
        self.policy_net = DQN(self.state_size, self.action_size)
        self.target_net = DQN(self.state_size, self.action_size)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()
        
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=self.config.learning_rate)
        self.criterion = nn.MSELoss()
        self.steps_done = 0
    
    def _preprocess_state(self, observation: Dict) -> torch.Tensor:
        """Convert observation to a fixed-size state vector."""
        # Simplified state representation:
        # [self_energy, step, nearest_food_dist, nearest_food_dir_x, nearest_food_dir_y,
        #  nearest_predator_dist, nearest_predator_dir_x, nearest_predator_dir_y,
        #  nearest_obstacle_dist, nearest_obstacle_dir_x, nearest_obstacle_dir_y]
        state = np.zeros(11)
        
        # Self energy (normalized)
        state[0] = observation['self_energy'] / 20.0  # Assuming max energy of 20
        
        # Step (normalized)
        state[1] = observation['step']
        
        # Find nearest objects
        nearest_food = self._get_nearest_object(observation, 'FOOD')
        nearest_predator = self._get_nearest_object(observation, 'PREDATOR')
        nearest_obstacle = self._get_nearest_object(observation, 'OBSTACLE')
        
        # Food info
        if nearest_food:
            state[2] = min(nearest_food['distance'] / self.perception_range, 1.0)
            state[3:5] = nearest_food['relative_position']
        else:
            state[2] = 1.0  # Max distance
            
        # Predator info
        if nearest_predator:
            state[5] = min(nearest_predator['distance'] / self.perception_range, 1.0)
            state[6:8] = nearest_predator['relative_position']
        else:
            state[5] = 1.0  # Max distance
            
        # Obstacle info
        if nearest_obstacle:
            state[8] = min(nearest_obstacle['distance'] / self.perception_range, 1.0)
            state[9:11] = nearest_obstacle['relative_position']
        else:
            state[8] = 1.0  # Max distance
        
        return torch.FloatTensor(state)
    
    def act(self, observation: Dict) -> Dict:
        # Epsilon-greedy action selection
        if random.random() < self.config.epsilon:
            # Random action
            action_idx = random.randrange(self.action_size)
        else:
            # Greedy action from policy network
            with torch.no_grad():
                state = self._preprocess_state(observation).unsqueeze(0)
                q_values = self.policy_net(state)
                action_idx = q_values.argmax().item()
        
        # Convert action index to direction
        if action_idx < 8:  # 8 directions
            angle = (action_idx / 8.0) * 2 * math.pi
            direction = np.array([math.cos(angle), math.sin(angle)])
        else:  # No-op
            direction = np.zeros(2)
        
        return {
            'type': 'move',
            'direction': direction,
            'speed': self.speed
        }
    
    def learn(self):
        if len(self.memory) < self.config.batch_size:
            return 0.0
        
        # Sample batch from memory
        batch = random.sample(self.memory, self.config.batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        
        # Convert to tensors
        states = torch.stack([self._preprocess_state(s) for s in states])
        next_states = torch.stack([self._preprocess_state(s) for s in next_states])
        rewards = torch.FloatTensor(rewards)
        dones = torch.FloatTensor(dones)
        
        # Current Q values
        current_q = self.policy_net(states).gather(1, torch.LongTensor(actions).unsqueeze(1))
        
        # Next Q values from target network
        with torch.no_grad():
            next_q = self.target_net(next_states).max(1)[0]
            expected_q = rewards + (1 - dones) * self.config.gamma * next_q
        
        # Compute loss and update
        loss = self.criterion(current_q.squeeze(), expected_q)
        
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        # Update target network
        if self.steps_done % self.config.update_target_every == 0:
            self.target_net.load_state_dict(self.policy_net.state_dict())
        
        # Decay epsilon
        self.config.epsilon = max(
            self.config.epsilon_min, 
            self.config.epsilon * self.config.epsilon_decay
        )
        
        self.steps_done += 1
        return loss.item()

class APGIAgent(BaseAgent):
    """Agent using the Integrated Predictive Ignition framework."""
    
    def __init__(self, config: Optional[AgentConfig] = None):
        super().__init__(config)
        self.ignition_threshold = 1.5  # Threshold for conscious ignition
        self.precision = 1.0  # Initial precision
        self.somatic_markers = {}  # For storing learned associations
        
        # Habitual system (fast, model-free)
        self.habit_net = DQN(10, 8)  # Simplified state and action spaces
        
        # Deliberative system (slow, model-based)
        self.model_net = DQN(10, 8)  # For predicting outcomes
        
        self.optimizer = optim.Adam(
            list(self.habit_net.parameters()) + list(self.model_net.parameters()),
            lr=self.config.learning_rate
        )
    
    def act(self, observation: Dict) -> Dict:
        # Calculate surprise (prediction error)
        surprise = self._calculate_surprise(observation)
        
        # Check for ignition
        if surprise > self.ignition_threshold:
            # Conscious deliberation (slower but more accurate)
            return self._deliberate(observation)
        else:
            # Habitual response (fast but rigid)
            return self._habitual_response(observation)
    
    def _calculate_surprise(self, observation: Dict) -> float:
        """Calculate prediction error/surprise."""
        # Simplified: use distance to nearest unexpected object
        nearest_predator = self._get_nearest_object(observation, 'PREDATOR')
        if nearest_predator and nearest_predator['distance'] < 3.0:
            return 2.0  # High surprise for nearby predators
        
        nearest_food = self._get_nearest_object(observation, 'FOOD')
        if nearest_food and nearest_food['distance'] < 2.0:
            return 1.5  # Medium surprise for nearby food
            
        return 0.5  # Low surprise otherwise
    
    def _habitual_response(self, observation: Dict) -> Dict:
        """Generate a fast, habitual response."""
        # Similar to reactive agent but using a learned policy
        nearest_food = self._get_nearest_object(observation, 'FOOD')
        nearest_predator = self._get_nearest_object(observation, 'PREDATOR')
        
        if nearest_predator and nearest_predator['distance'] < 2.0:
            # Run away from predator
            direction = -nearest_predator['relative_position']
        elif nearest_food and nearest_food['distance'] < 3.0:
            # Move toward food
            direction = nearest_food['relative_position']
        else:
            # Random exploration
            angle = random.uniform(0, 2 * math.pi)
            direction = np.array([math.cos(angle), math.sin(angle)])
        
        # Normalize direction
        norm = np.linalg.norm(direction)
        if norm > 0:
            direction /= norm
        
        return {
            'type': 'move',
            'direction': direction,
            'speed': self.speed
        }
    
    def _deliberate(self, observation: Dict) -> Dict:
        """Generate a deliberate, goal-directed response."""
        # Use the model to simulate outcomes of different actions
        best_action = None
        best_value = -float('inf')
        
        # Evaluate possible actions
        for angle in np.linspace(0, 2 * math.pi, 8, endpoint=False):
            direction = np.array([math.cos(angle), math.sin(angle)])
            
            # Simulate outcome (simplified)
            # In a real implementation, this would use a learned forward model
            value = self._evaluate_action(observation, direction)
            
            if value > best_value:
                best_value = value
                best_direction = direction
        
        return {
            'type': 'move',
            'direction': best_direction,
            'speed': self.speed * 0.8  # Slower, more deliberate movement
        }
    
    def _evaluate_action(self, observation: Dict, direction: np.ndarray) -> float:
        """Evaluate the expected value of an action."""
        # Simplified evaluation function
        value = 0.0
        
        # Check for food in that direction
        nearest_food = self._get_nearest_object(observation, 'FOOD')
        if nearest_food:
            food_dir = nearest_food['relative_position']
            food_dist = nearest_food['distance']
            
            # Higher value for moving toward food
            dot_product = np.dot(direction, food_dir)
            value += max(0, dot_product) * (1.0 / (food_dist + 1e-6))
        
        # Avoid predators
        nearest_predator = self._get_nearest_object(observation, 'PREDATOR')
        if nearest_predator:
            pred_dir = nearest_predator['relative_position']
            pred_dist = nearest_predator['distance']
            
            # Lower value for moving toward predators
            dot_product = np.dot(direction, pred_dir)
            value -= max(0, dot_product) * (2.0 / (pred_dist + 1e-6))
        
        # Add some noise to break ties
        value += random.uniform(-0.1, 0.1)
        
        return value
    
    def learn(self):
        """Update the agent's models based on experience."""
        if len(self.memory) < self.config.batch_size:
            return 0.0
        
        # Sample batch from memory
        batch = random.sample(self.memory, self.config.batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        
        # Convert to tensors (simplified)
        # In a full implementation, we would update both habit_net and model_net
        
        # For now, just return a dummy loss
        return 0.0
