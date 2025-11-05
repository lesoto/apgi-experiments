import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum, auto
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
import random

class ObjectType(Enum):
    AGENT = auto()
    FOOD = auto()
    OBSTACLE = auto()
    PREDATOR = auto()

@dataclass
class GameObject:
    obj_type: ObjectType
    position: np.ndarray  # [x, y] coordinates
    radius: float = 0.2
    energy: float = 0.0
    active: bool = True
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def __eq__(self, other):
        if not isinstance(other, GameObject):
            return False
        return (self.obj_type == other.obj_type and 
                np.array_equal(self.position, other.position) and 
                self.radius == other.radius and 
                self.energy == other.energy and 
                self.active == other.active and 
                self.metadata == other.metadata)

class GridWorld:
    def __init__(self, size: int = 10, n_food: int = 15, n_obstacles: int = 10, n_predators: int = 2):
        self.size = size
        self.agents = []
        self.food = []
        self.obstacles = []
        self.predators = []
        self.time_step = 0
        self.max_steps = 1000
        
        # Initialize environment
        self._place_objects(n_food, ObjectType.FOOD, self.food, energy=1.0)
        self._place_objects(n_obstacles, ObjectType.OBSTACLE, self.obstacles, radius=0.3)
        self._place_objects(n_predators, ObjectType.PREDATOR, self.predators, energy=10.0)
    
    def _place_objects(self, n: int, obj_type: ObjectType, container: List, **kwargs):
        """Place n objects of given type in the environment."""
        for _ in range(n):
            while True:
                pos = np.random.uniform(0, self.size, 2)
                radius = kwargs.get('radius', 0.2)
                
                # Check for collisions with existing objects
                if not self._check_collision(pos, radius, exclude=container):
                    obj = GameObject(obj_type=obj_type, position=pos, **kwargs)
                    container.append(obj)
                    break
    
    def _check_collision(self, position: np.ndarray, radius: float, 
                        exclude: Optional[List[GameObject]] = None) -> bool:
        """Check if a position collides with any object in the environment."""
        if exclude is None:
            exclude = []
            
        # Check boundaries - ensure we're using scalar values for comparison
        x, y = position[0], position[1]
        if (x - radius < 0 or x + radius > self.size or
            y - radius < 0 or y + radius > self.size):
            return True
        
        # Check against all game objects
        for obj_list in [self.agents, self.food, self.obstacles, self.predators]:
            for obj in obj_list:
                if obj in exclude or not obj.active:
                    continue
                # Ensure we're using scalar values for distance calculation
                obj_x, obj_y = obj.position[0], obj.position[1]
                dx = x - obj_x
                dy = y - obj_y
                dist_sq = dx*dx + dy*dy
                min_dist = radius + obj.radius
                if dist_sq < min_dist * min_dist:
                    return True
        return False
    
    def add_agent(self, agent, position: Optional[np.ndarray] = None):
        """Add an agent to the environment."""
        if position is None:
            while True:
                pos = np.random.uniform(1, self.size-1, 2)
                if not self._check_collision(pos, agent.radius):
                    break
        else:
            pos = position.copy()
            
        agent.position = pos
        self.agents.append(agent)
    
    def get_observation(self, agent) -> Dict:
        """Get the observation for a specific agent."""
        obs = {
            'self_position': agent.position,
            'self_energy': agent.energy,
            'nearby_objects': [],
            'step': self.time_step / self.max_steps
        }
        
        # Get nearby objects within perception range
        for obj_list in [self.agents, self.food, self.obstacles, self.predators]:
            for obj in obj_list:
                if not obj.active or obj == agent:
                    continue
                    
                dist = np.linalg.norm(agent.position - obj.position)
                if dist <= agent.perception_range:
                    rel_pos = (obj.position - agent.position) / agent.perception_range
                    obs['nearby_objects'].append({
                        'type': obj.obj_type,
                        'relative_position': rel_pos,
                        'distance': dist,
                        'radius': obj.radius,
                        'energy': getattr(obj, 'energy', 0)
                    })
        
        return obs
    
    def step(self) -> bool:
        """Advance the simulation by one time step."""
        if self.time_step >= self.max_steps:
            return False
            
        # Update agents
        for agent in self.agents:
            if not agent.active:
                continue
                
            # Get observation and get action from agent
            obs = self.get_observation(agent)
            action = agent.act(obs)
            
            # Apply movement
            if action['type'] == 'move':
                direction = action['direction']
                speed = min(action.get('speed', agent.speed), agent.speed)
                
                # Calculate new position
                new_pos = agent.position + direction * speed
                
                # Check for collisions
                if not self._check_collision(new_pos, agent.radius, exclude=[agent]):
                    agent.position = new_pos
                
                # Apply energy cost for movement
                agent.energy -= agent.movement_cost * speed
            
            # Apply action cost
            agent.energy -= agent.action_cost
            
            # Check for food consumption
            self._check_food_consumption(agent)
            
            # Check for predator encounters
            self._check_predator_encounter(agent)
            
            # Check if agent is still alive
            if agent.energy <= 0:
                agent.active = False
                agent.survival_time = self.time_step
        
        # Update predators
        self._update_predators()
        
        # Respawn food with some probability
        if random.random() < 0.05:  # 5% chance per step
            self._respawn_food(1)
        
        self.time_step += 1
        return True
    
    def _check_food_consumption(self, agent):
        """Check if agent is close enough to food to consume it."""
        for food in self.food:
            if not food.active:
                continue
                
            dist = np.linalg.norm(agent.position - food.position)
            if dist < (agent.radius + food.radius):
                agent.energy += food.energy
                food.active = False
                agent.food_consumed += 1
    
    def _check_predator_encounter(self, agent):
        """Check if agent is caught by a predator."""
        for predator in self.predators:
            if not predator.active:
                continue
                
            dist = np.linalg.norm(agent.position - predator.position)
            if dist < (agent.radius + predator.radius + 0.1):  # Slightly larger radius for catching
                agent.energy -= 5.0  # Significant energy loss when caught
                predator.energy += 2.0  # Predator gains energy
                break
    
    def _update_predators(self):
        """Update predator behavior."""
        for predator in self.predators:
            if not predator.active:
                continue
                
            # Simple predator behavior: move toward nearest agent
            nearest_agent = None
            min_dist = float('inf')
            
            for agent in self.agents:
                if not agent.active:
                    continue
                    
                dist = np.linalg.norm(predator.position - agent.position)
                if dist < min_dist:
                    min_dist = dist
                    nearest_agent = agent
            
            # Move toward nearest agent if in range
            if nearest_agent and min_dist < 5.0:  # Detection range
                direction = (nearest_agent.position - predator.position)
                direction = direction / (np.linalg.norm(direction) + 1e-6)
                predator.position += direction * 0.3  # Predator speed
            else:
                # Random movement
                predator.position += np.random.uniform(-0.2, 0.2, 2)
            
            # Keep predators within bounds
            predator.position = np.clip(predator.position, 0, self.size)
            
            # Predator loses energy over time
            predator.energy -= 0.01
            if predator.energy <= 0:
                predator.active = False
    
    def _respawn_food(self, n: int = 1):
        """Respawn food items that have been consumed."""
        available_positions = []
        
        # Try to find empty spots
        for _ in range(100):  # Max attempts
            pos = np.random.uniform(0, self.size, 2)
            if not self._check_collision(pos, 0.2, exclude=self.food):
                available_positions.append(pos)
                if len(available_positions) >= n:
                    break
        
        # Add new food items
        for pos in available_positions:
            food = GameObject(
                obj_type=ObjectType.FOOD,
                position=pos,
                radius=0.15,
                energy=random.uniform(0.8, 1.2)
            )
            self.food.append(food)
    
    def render(self):
        """Render the current state of the environment."""
        plt.figure(figsize=(8, 8))
        ax = plt.gca()
        ax.set_xlim(0, self.size)
        ax.set_ylim(0, self.size)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        
        # Draw agents
        for agent in self.agents:
            if agent.active:
                color = 'blue' if agent.active else 'gray'
                circle = Circle(agent.position, agent.radius, color=color, alpha=0.7)
                ax.add_patch(circle)
                # Draw perception range
                perception = plt.Circle(
                    agent.position, agent.perception_range, 
                    color='blue', fill=False, alpha=0.2, linestyle='--'
                )
                ax.add_patch(perception)
                # Draw energy as text
                plt.text(agent.position[0], agent.position[1] + agent.radius + 0.2, 
                        f"{agent.energy:.1f}", ha='center', fontsize=8)
        
        # Draw food
        for food in self.food:
            if food.active:
                circle = Circle(food.position, food.radius, color='green', alpha=0.7)
                ax.add_patch(circle)
        
        # Draw obstacles
        for obs in self.obstacles:
            if obs.active:
                circle = Circle(obs.position, obs.radius, color='brown', alpha=0.7)
                ax.add_patch(circle)
        
        # Draw predators
        for pred in self.predators:
            if pred.active:
                circle = Circle(pred.position, pred.radius, color='red', alpha=0.7)
                ax.add_patch(circle)
        
        plt.title(f"Step: {self.time_step}")
        plt.show()
    
    def get_metrics(self) -> Dict:
        """Get performance metrics for all agents."""
        metrics = {}
        for i, agent in enumerate(self.agents):
            metrics[f'agent_{i}'] = {
                'survival_time': getattr(agent, 'survival_time', self.time_step),
                'food_consumed': getattr(agent, 'food_consumed', 0),
                'energy': max(0, agent.energy),
                'active': agent.active
            }
        return metrics
