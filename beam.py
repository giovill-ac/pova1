from abc import ABC, abstractmethod
import random
import math
import signal
import datetime
import pickle
import sys
import time

from room.algos.utils import time_string

class StochasticBeamSearch(ABC):
    def __init__(self, population_size=100, temperature=100, max_generations=1000, acceptable_fitness=0):
        self.population_size = population_size
        self.temperature = temperature
        self.max_generations = max_generations
        self.acceptable_fitness = acceptable_fitness
        self.population = [self.random_assignment() for _ in range(population_size)]
        
    def save_state(self, fname=None):
        """Saves state to pickle"""
        if not fname:
            date = datetime.datetime.now().strftime("%Y-%m-%dT%Hh%Mm%Ss")
            fname = date + "_energy_" + str(self.energy()) + ".state"
        with open(fname, "wb") as fh:
            pickle.dump(self.state, fh)

    def load_state(self, fname=None):
        """Loads state from pickle"""
        with open(fname, 'rb') as fh:
            self.state = pickle.load(fh)

    def run(self):
        """
        Main method that runs the beam search algorithm.
        """
        self.start = time.time()
        generation = 0
        while True:
            # Calculate fitness of the population
            fitnesses = [self.fitness(assignment) for assignment in self.population]
            # Find the best assignment in the population
            best_fitness_idx = min(range(len(fitnesses)), key=lambda x : fitnesses[x])
            best_fitness = fitnesses[best_fitness_idx]
            # Check if any assignment satisfies the fitness function
            self.update(generation, self.temperature, best_fitness)
            if fitnesses[best_fitness_idx] <= self.acceptable_fitness or generation >= self.max_generations:
                if generation >= self.max_generations:
                    print("\nReached max generations")
                else:
                    print("\nFound solution in generation", generation)
                self.fitness(self.population[best_fitness_idx])
                return self.population[best_fitness_idx]

            # Create new population
            new_population = []

            # Perform selection, crossover, mutation k/2 times
            for _ in range(self.population_size // 2):
                # Random selection of two parents from population
                parent1 = self.random_selection()
                parent2 = self.random_selection()

                # Crossover to produce two children
                child1, child2 = self.crossover(parent1, parent2)

                # Mutate the children and add to the new population
                new_population.append(self.mutate(child1))
                new_population.append(self.mutate(child2))

            # Update population and temperature
            self.population = new_population
            self.update_temperature()
            generation += 1
            
    def update(self, *args, **kwargs):
        """Wrapper for internal update.

        If you override the self.update method,
        you can chose to call the self.default_update method
        from your own Annealer.
        """
        self.default_update(*args, **kwargs)

    def default_update(self, step, T, E):
        """Default update, outputs to stderr.

        Prints the current temperature, energy, acceptance rate,
        improvement rate, elapsed time, and remaining time.

        The acceptance rate indicates the percentage of moves since the last
        update that were accepted by the Metropolis algorithm.  It includes
        moves that decreased the energy, moves that left the energy
        unchanged, and moves that increased the energy yet were reached by
        thermal excitation.

        The improvement rate indicates the percentage of moves since the
        last update that strictly decreased the energy.  At high
        temperatures it will include both moves that improved the overall
        state and moves that simply undid previously accepted moves that
        increased the energy by thermal excititation.  At low temperatures
        it will tend toward zero as the moves that can decrease the energy
        are exhausted and moves that would increase the energy are no longer
        thermally accessible."""

        elapsed = time.time() - self.start
        if step == 0:
            print('\n Generation    Temperature        Best fit    Elapsed',
                file=sys.stderr)
            print('\r{Gen:10d}  {Temp:12.5f}  {Energy:12.2f}   {Elapsed:s}'
                .format(Gen=step,
                        Temp=T,
                        Energy=E,
                        Elapsed=time_string(elapsed)),
                file=sys.stderr, end="")
            sys.stderr.flush()
        else:
            print('\r{Gen:10d}  {Temp:12.5f}  {Energy:12.2f}   {Elapsed:s}'
                .format(Gen=step,
                        Temp=T,
                        Energy=E,
                        Elapsed=time_string(elapsed)),
                file=sys.stderr, end="")
            sys.stderr.flush()


    @abstractmethod
    def crossover(self, parent1, parent2):
        """
        Abstract method for crossover between two parents.
        Must be implemented in the subclass.
        """
        pass

    @abstractmethod
    def fitness(self, assignment):
        """
        Abstract method that calculates the fitness of an assignment.
        Must be implemented in the subclass.
        """
        pass

    def random_selection(self):
        """
        Select an assignment from the population with probability proportional to e^(-h(A)/T).
        """
        temperature = max(self.temperature, 1e-10)  # Evita temperature troppo basse

        # Calcola i pesi logaritmici
        log_weights = [-self.fitness(assignment) / temperature for assignment in self.population]
        max_log_weight = max(log_weights)  # Trova il valore massimo dei log pesi
        weights = [math.exp(log_weight - max_log_weight) for log_weight in log_weights]
        total_weight = sum(weights)
        
        if total_weight == 0:
            return random.choice(self.population)  # Evita divisione per 0

        probabilities = [w / total_weight for w in weights]
        return random.choices(self.population, probabilities)[0]

    @abstractmethod
    def mutate(self, state):
        """
        Abstract method to mutate the assignment.
        """
        pass

    def update_temperature(self):
        """
        Update the temperature based on the cooling schedule.
        """
        self.temperature *= 0.95  # Example cooling schedule, this could be customized

    @abstractmethod
    def random_assignment(self):
        """
        Create a random assignment of values to variables.
        """
        pass