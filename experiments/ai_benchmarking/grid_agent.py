import pygame
import numpy as np
import sys
from enum import Enum

# --- Simulation Constants ---
WORLD_SIZE = 10
CELL_SIZE = 60
SCREEN_SIZE = WORLD_SIZE * CELL_SIZE
FPS = 10  # Slower FPS to see the simulation better

# Define world elements
class CellType(Enum):
    EMPTY = 0
    RESOURCE = 1
    THREAT = 2

# --- IPI Agent Class ---
class IPIAgent:
    def __init__(self, world):
        self.world = world
        self.pos = np.array([WORLD_SIZE // 2, WORLD_SIZE // 2])
        
        # Core IPI Variables
        self.viability = 75.0  # Allostatic state (0-100)
        self.viability_setpoint = 75.0
        
        # Generative Model
        self.prediction = CellType.EMPTY
        self.prediction_error_extero = 0.0
        self.prediction_error_intero = 0.0
        
        self.precision_extero = 1.0  # Π^e
        self.precision_intero = 1.0  # Π^i
        
        # Somatic Markers (learned associations: CellType -> value)
        self.somatic_markers = {
            CellType.EMPTY: 0.0,
            CellType.RESOURCE: +2.0,  # Positive valence
            CellType.THREAT: -3.0     # Negative valence
        }
        
        # Ignition Mechanism
        self.surprise_magnitude_S = 0.0  # S_t
        self.ignition_threshold_theta = 5.0  # θ_t
        self.is_ignited = False
        self.conscious_content = ""
        
        # Action repertoire - use tuples instead of numpy arrays for simplicity
        self.possible_actions = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # Up, Right, Down, Left
        
        # Track history for visualization
        self.ignition_history = []
        self.surprise_history = []

    def perceive_and_predict(self):
        """Step 1: Generate prediction and compute prediction error."""
        # Simple prediction: "I expect the next cell I look at to be EMPTY"
        current_cell_type = self.world[self.pos[1], self.pos[0]]
        
        # Exteroceptive Prediction Error (Did I see what I expected?)
        # More nuanced error based on somatic marker difference
        expected_value = self.somatic_markers[self.prediction]
        actual_value = self.somatic_markers[current_cell_type]
        self.prediction_error_extero = abs(actual_value - expected_value)
        
        # Interoceptive Prediction Error (Is my viability at its setpoint?)
        self.prediction_error_intero = abs(self.viability_setpoint - self.viability) / 100.0

    def update_precision(self):
        """Step 2: Dynamically update precision weights."""
        # Increase interoceptive precision if viability is low (the body is shouting)
        if self.viability < 40:
            self.precision_intero = 3.0
        else:
            self.precision_intero = 1.0 + (0.5 * (1 - self.viability/100))  # Scale with need
            
        # Increase exteroceptive precision if there's a large interoceptive error (be vigilant when unwell)
        self.precision_extero = 1.0 + (1.0 * self.prediction_error_intero)

    def check_ignition(self):
        """Step 3: Calculate surprise and check for global ignition."""
        current_cell_type = self.world[self.pos[1], self.pos[0]]
        somatic_gain_M = abs(self.somatic_markers[current_cell_type])  # Use absolute value for magnitude
        
        # The Core IPI Equation: S_t = Π^e * |ε^e| + (Π^i * M(c,a)) * |ε^i|
        self.surprise_magnitude_S = (
            self.precision_extero * self.prediction_error_extero +
            (self.precision_intero * somatic_gain_M) * self.prediction_error_intero
        )
        
        # Dynamic threshold - increases after recent ignitions (metabolic cost)
        self.ignition_threshold_theta = 5.0 + (2.0 if len(self.ignition_history) > 0 and self.ignition_history[-1] else 0)
        
        # Check for Ignition
        was_ignited = self.is_ignited
        self.is_ignited = self.surprise_magnitude_S > self.ignition_threshold_theta
        
        # Record ignition event
        self.ignition_history.append(self.is_ignited)
        self.surprise_history.append(self.surprise_magnitude_S)
        
        # Keep history manageable
        if len(self.ignition_history) > 100:
            self.ignition_history.pop(0)
            self.surprise_history.pop(0)
        
        # Set Conscious Content
        if self.is_ignited:
            if current_cell_type == CellType.RESOURCE:
                self.conscious_content = "CONSCIOUS: Found Food!"
            elif current_cell_type == CellType.THREAT:
                self.conscious_content = "CONSCIOUS: DANGER!"
            elif self.viability < 40:
                self.conscious_content = "CONSCIOUS: I feel terrible!"
            else:
                self.conscious_content = "CONSCIOUS: High Surprise!"
                
            # Print to console when ignition occurs
            if not was_ignited:
                print(f"🔥 IGNITION! S_t={self.surprise_magnitude_S:.2f}, θ_t={self.ignition_threshold_theta:.2f}")
                print(f"   Details: Π^e={self.precision_extero:.2f}, ε^e={self.prediction_error_extero:.2f}")
                print(f"             Π^i={self.precision_intero:.2f}, ε^i={self.prediction_error_intero:.2f}")
        else:
            self.conscious_content = "Unconscious Processing"

    def act(self):
        """Step 4: Select an action based on state (ignited or not)."""
        current_cell_type = self.world[self.pos[1], self.pos[0]]
        
        # Reflexive (Unconscious) Action
        if not self.is_ignited:
            # Simple hard-coded reflexes
            if current_cell_type == CellType.RESOURCE:
                self.consume_resource()
            elif current_cell_type == CellType.THREAT:
                # Simple avoidance: move away from threat
                self.move_away_from_threat()
            else:
                # Random walk if no strong stimulus
                action = self.possible_actions[np.random.randint(0, len(self.possible_actions))]
                self.move(action)
                
        # Deliberative (Conscious) Action
        else:
            # A simple form of deliberation: evaluate all possible next moves
            best_action = None
            best_value = -np.inf
            
            for action in self.possible_actions:
                new_pos = (self.pos[0] + action[0], self.pos[1] + action[1])
                if 0 <= new_pos[0] < WORLD_SIZE and 0 <= new_pos[1] < WORLD_SIZE:
                    # Check what's in the neighboring cell
                    neighbor_type = self.world[new_pos[1], new_pos[0]]
                    # Value is based on somatic marker of that cell type
                    value = self.somatic_markers[neighbor_type]
                    if value > best_value:
                        best_value = value
                        best_action = action
            
            if best_action is not None:
                self.move(best_action)
            
            # After conscious deliberation, consume if on a resource/threat
            if current_cell_type == CellType.RESOURCE:
                self.consume_resource()
            elif current_cell_type == CellType.THREAT:
                self.viability = max(0, self.viability - 15)  # Take more damage when conscious of threat

    def move(self, direction):
        new_pos = (self.pos[0] + direction[0], self.pos[1] + direction[1])
        if 0 <= new_pos[0] < WORLD_SIZE and 0 <= new_pos[1] < WORLD_SIZE:
            self.pos = np.array(new_pos)

    def move_away_from_threat(self):
        """Simple reflexive threat avoidance"""
        current_cell_type = self.world[self.pos[1], self.pos[0]]
        if current_cell_type == CellType.THREAT:
            # Try to move to an adjacent empty cell
            empty_actions = []
            for action in self.possible_actions:
                new_pos = (self.pos[0] + action[0], self.pos[1] + action[1])
                if 0 <= new_pos[0] < WORLD_SIZE and 0 <= new_pos[1] < WORLD_SIZE:
                    if self.world[new_pos[1], new_pos[0]] == CellType.EMPTY:
                        empty_actions.append(action)
            
            if empty_actions:
                self.move(empty_actions[np.random.randint(0, len(empty_actions))])
            else:
                # If no empty cells, just move randomly
                action = self.possible_actions[np.random.randint(0, len(self.possible_actions))]
                self.move(action)

    def consume_resource(self):
        if self.world[self.pos[1], self.pos[0]] == CellType.RESOURCE:
            self.viability = min(100, self.viability + 25)
            self.world[self.pos[1], self.pos[0]] = CellType.EMPTY  # Resource is consumed
            print(f"  Consumed resource! Viability: {self.viability:.1f}")

    def update(self):
        """Main update loop for the agent."""
        self.viability -= 0.2  # Natural decay of viability
        self.perceive_and_predict()
        self.update_precision()
        self.check_ignition()
        self.act()

# --- Visualization with Pygame ---
class Simulation:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE + 100))  # Extra space for metrics
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 16)
        self.small_font = pygame.font.SysFont('Arial', 12)
        self.reset_simulation()

    def reset_simulation(self):
        # Create a random world
        self.world = np.full((WORLD_SIZE, WORLD_SIZE), CellType.EMPTY, dtype=object)
        # Place some resources and threats
        for _ in range(8):
            x, y = np.random.randint(0, WORLD_SIZE, 2)
            self.world[y, x] = CellType.RESOURCE
        for _ in range(5):
            x, y = np.random.randint(0, WORLD_SIZE, 2)
            self.world[y, x] = CellType.THREAT
        
        self.agent = IPIAgent(self.world)
        self.step_count = 0

    def draw(self):
        self.screen.fill((255, 255, 255))  # White background
        
        # Draw the world
        for y in range(WORLD_SIZE):
            for x in range(WORLD_SIZE):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                cell_type = self.world[y, x]
                color = (200, 200, 200)  # EMPTY
                if cell_type == CellType.RESOURCE:
                    color = (0, 200, 0)  # GREEN
                elif cell_type == CellType.THREAT:
                    color = (200, 0, 0)  # RED
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, (50, 50, 50), rect, 1)  # Grid lines
        
        # Draw the agent
        agent_rect = pygame.Rect(self.agent.pos[0] * CELL_SIZE, self.agent.pos[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        agent_color = (255, 0, 0) if self.agent.is_ignited else (0, 0, 255)  # RED if ignited, BLUE otherwise
        pygame.draw.rect(self.screen, agent_color, agent_rect)
        
        # Draw metrics panel
        panel_y = SCREEN_SIZE
        panel_height = 100
        
        # Background for panel
        pygame.draw.rect(self.screen, (240, 240, 240), (0, panel_y, SCREEN_SIZE, panel_height))
        
        # Draw key metrics
        metrics = [
            f'Step: {self.step_count}',
            f'Viability: {self.agent.viability:.1f}',
            f'S_t (Surprise): {self.agent.surprise_magnitude_S:.2f}',
            f'θ_t (Threshold): {self.agent.ignition_threshold_theta:.2f}',
            f'Π^e (Extero Precision): {self.agent.precision_extero:.2f}',
            f'Π^i (Intero Precision): {self.agent.precision_intero:.2f}',
            f'ε^e (Extero Error): {self.agent.prediction_error_extero:.2f}',
            f'ε^i (Intero Error): {self.agent.prediction_error_intero:.2f}',
        ]
        
        for i, metric in enumerate(metrics):
            text = self.small_font.render(metric, True, (0, 0, 0))
            self.screen.blit(text, (10, panel_y + 5 + i * 12))
        
        # Draw ignition status
        status_color = (255, 0, 0) if self.agent.is_ignited else (0, 0, 0)
        ignition_text = self.font.render(f'IGNITION: {self.agent.is_ignited} - {self.agent.conscious_content}', True, status_color)
        self.screen.blit(ignition_text, (SCREEN_SIZE // 4, panel_y + 50))
        
        # Draw instructions
        instruct_text = self.small_font.render('Press R to reset simulation', True, (100, 100, 100))
        self.screen.blit(instruct_text, (SCREEN_SIZE - 150, panel_y + 80))
        
        pygame.display.flip()

    def run(self):
        running = True
        paused = False
        
        print("=== IPI Framework Simulation ===")
        print("Blue agent = Unconscious, Red agent = Conscious (Ignited)")
        print("Watch the console for ignition events!")
        print("-" * 50)
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset_simulation()
                        print("\n" + "="*50)
                        print("Simulation Reset!")
                        print("="*50)
                    elif event.key == pygame.K_SPACE:
                        paused = not paused
                        print("Simulation Paused" if paused else "Simulation Resumed")
            
            if not paused:
                self.agent.update()
                self.step_count += 1
                self.draw()
                
                # Check for agent death
                if self.agent.viability <= 0:
                    death_text = self.font.render("AGENT DIED - Press R to reset", True, (255, 0, 0))
                    self.screen.blit(death_text, (SCREEN_SIZE // 3, SCREEN_SIZE // 2))
                    pygame.display.flip()
                    print("💀 Agent died! Press R to reset.")
                    paused = True

            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

# --- Run the Simulation ---
if __name__ == "__main__":
    sim = Simulation()
    sim.run()