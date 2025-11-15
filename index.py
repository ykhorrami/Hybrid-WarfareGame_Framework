import pygame
import matplotlib.pyplot as plt
from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from tqdm import tqdm
import time


# Define colors for the actors
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

class Actor(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.capability = self.random.randint(1, 10) # Assign random capabilities to each actor
        self.strategy = "attack" # Set strategy to "attack" for all actors
        self.color = None
        self.economic_capability = self.random.randint(1, 10) # Assign random economic capabilities to each actor
        self.cyber_capability = self.random.randint(1, 10) # Assign random cyber capabilities to each actor

    def step(self):
        # Implement actor's strategy
        if self.strategy == "attack":
            # Find neighboring cells with other actors
            neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False)
            targets = [agent for agent in neighbors if isinstance(agent, Actor) and agent.unique_id != self.unique_id]
            if targets:
                # Attack a random target
                target = self.random.choice(targets)
                damage = self.random.randint(1, self.capability)
                target.capability -= damage
                # Check if the target is defeated
                if target.capability <= 0:
                    self.model.grid.remove_agent(target)
                    self.model.schedule.remove(target)
                    # Update economic casualties
                    economic_damage = self.random.randint(1, self.economic_capability)
                    target.economic_capability -= economic_damage
                    if target.economic_capability <= 0:
                        self.model.economic_casualties += 1
                        self.model.grid.remove_agent(target)
                        self.model.schedule.remove(target)
                    # Update cyber casualties
                    cyber_damage = self.random.randint(1, self.cyber_capability)
                    target.cyber_capability -= cyber_damage
                    if target.cyber_capability <= 0:
                        self.model.cyber_casualties += 1
                        self.model.grid.remove_agent(target)
                        self.model.schedule.remove(target)

class HybridWarfare(Model):
    def __init__(self, num_actors, width, height):
        self.num_actors = num_actors
        self.grid = MultiGrid(width, height, torus=True)
        self.schedule = RandomActivation(self)
        self.casualties = []
        self.economic_casualties = 0
        self.cyber_casualties = 0
        self.winner = "Draw" # Set the initial value of self.winner to "Draw"
        # Create actors
        for i in range(self.num_actors):
            actor = Actor(i, self)
            actor.color = RED if i % 2 == 0 else BLUE # Assign colors to actors based on their unique_id
            self.schedule.add(actor)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(actor, (x, y))
        
        self.running = True
        self.winner = None

    def step(self):
        self.schedule.step()
        # Check for victory or defeat conditions
        num_alive = sum([1 for agent in self.schedule.agents if isinstance(agent, Actor)])
        if num_alive == 0:
            self.running = False
            self.winner = "Draw"
        elif num_alive == 1:
            self.running = False
            self.winner = "Actor " + str([agent for agent in self.schedule.agents if isinstance(agent, Actor)][0].unique_id)
        self.casualties.append(self.num_actors - len(self.schedule.agents))
    
    def get_casualties(self):
        return self.num_actors - len(self.schedule.agents)
    
    def get_economic_casualties(self):
        return self.economic_casualties
    
    def get_cyber_casualties(self):
        return self.cyber_casualties



if __name__ == "__main__":
    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((500, 500))
    pygame.display.set_caption("Hybrid Warfare Simulation")

    # Create model
    model = HybridWarfare(num_actors=32, width=100, height=100)

    # Main simulation loop
    with tqdm(total=100) as pbar:
        while model.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    model.running = False

            # Clear the screen
            screen.fill((255, 255, 255))

            # Draw actors
            for actor in model.schedule.agents:
                x, y = actor.pos
                pygame.draw.rect(screen, actor.color, (x*10, y*10, 10, 10))

            # Update the model
            model.step()

            # Update the screen
            pygame.display.flip()

            # Update the progress bar
            pbar.update(1)

            # Optional delay to slow down the simulation
            # time.sleep(0.1)

    # Print the outcomes of the simulation
    print("Overall simulation results:")
    if model.winner:
        print("The winner is:", model.winner)
    else:
        print("The simulation ended in a draw")

    print("Overall casualties:", model.get_casualties())
    print("Economic casualties:", model.get_economic_casualties())
    print("Cyber casualties:", model.get_cyber_casualties())

    # Plot the casualties over time
    plt.plot(model.casualties)
    plt.title("Casualties over time")
    plt.xlabel("Iteration")
    plt.ylabel("Casualties")
    plt.show()

    # Plot economic casualties over time
    plt.plot(range(len(model.casualties)), [model.get_economic_casualties() for i in range(len(model.casualties))], label="Economic")
    plt.title("Economic Casualties over time")
    plt.xlabel("Iteration")
    plt.ylabel("Economic Casualties")
    plt.legend()
    plt.show()

    # Plot cyber casualties over time
    plt.plot(range(len(model.casualties)), [model.get_cyber_casualties() for i in range(len(model.casualties))], label="Cyber")
    plt.title("Cyber Casualties over time")
    plt.xlabel("Iteration")
    plt.ylabel("Cyber Casualties")
    plt.legend()
    plt.show()

    # Create a report on the simulation
    report = f"""Overall simulation results:
    Winner: {model.winner or 'Draw'}
    Overall casualties: {model.get_casualties()}
    Economic casualties: {model.get_economic_casualties()}
    Cyber casualties: {model.get_cyber_casualties()}
    """

    print(report)

    # Quit Pygame
    pygame.quit()
"""
The updated code now includes two new layers for the economy and cyber aspects of the simulation. Each actor now has a random economic and cyber capability, and when an actor is defeated, the economic and cyber capabilities of the defeated actor are subtracted from a separate economic and cyber casualty count, respectively.

After the simulation has completed, the script now prints the overall casualties, as well as the economic and cyber casualties separately. It also generates three new plots: one for the overall casualties over time, and two for the economic and cyber casualties over time.

Finally, the script generates a report on the simulation that includes the same information as the printed output.

Overall, these additions provide a more nuanced view of the simulation and its results, allowing for further analysis and understanding of the various factors that contributed to the outcome.
"""

