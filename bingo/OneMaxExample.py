import numpy as np

from Base.Chromosome import Chromosome
from Base.FitnessEvaluator import FitnessEvaluator
from Base.Mutation import Mutation
from Base.Crossover import Crossover
from Base.Variation import Variation
from Base.Evaluation import Evaluation
from Base.Selection import Selection
from bingo.EA.SimpleEa import SimpleEa
from bingo.EA.VarAnd import VarAnd
from bingo.EA.TournamentSelection import Tournament
from bingo.EA.SimpleEvaluation import SimpleEvaluation
from MultipleValues import *


class MultipleValueFitnessEvaluator(FitnessEvaluator):
    """Fitness for multiple value chromosomes

    Fitness equals the number of true values in the chromosome's list of values 

    """
    def __call__(self, individual):
        """Calculates the fitness of an individual in a population

        Parameters
        ----------
        individual : MultipleValueChromosome
                the individual on which a fitness evaluation will be performed

        Returns
        -------
        fitness : int
                the fitness value of the individual (in this case, how many False values the chromosome contains)

        """
        fitness = np.count_nonzero(individual._list_of_values)
        self.eval_count += 1
        return len(individual._list_of_values) - fitness

def mutation_onemax_specific():
    """Generates a random boolean value that will replace an existing value in a chromosome

    Returns
    -------
    bool : boolean 
            A randomly generated boolean value
    """
    return np.random.choice([True, False])

def population_input():
    """Prompts the user for input with which to create a population of chromosomes

    Returns
    -------
    population : list of MultipleValueChromosome
            A list of user-specified length of chromosomes 
    """
    while True:
        values_per_list  = input("Enter the number of values each List Chromosome will hold:\n")
        population_size = input("Enter the desired population size: \n")
        try:
            generator = MultipleValueGenerator()
            int_vals_per_list = int(values_per_list)
            int_pop_size = int(population_size)
            population = generator(get_random_list_for_chromosome, population_size=int_pop_size, values_per_chromosome=int_vals_per_list)
            if int_vals_per_list <= 0 or int_pop_size <= 0:
                print("\nError: List length and population size must be positive integers")
                continue
            break
        except ValueError:
            print("\nValueError, please enter a number for list length and population size\n")

        except TypeError:
            print("\nTypeError, please enter a valid number for list length and population size\n")
    return population

def execute_generational_steps():
    """Executes 10 generations of a SimpleEa class

    Creates a SimpleEa and uses Tournament selection to run through 10 generational steps.
    With each new generation, a report about the max/min/mean fitness values is printed to stdout.

    """
    population= population_input()
    selection = Tournament(10)
    crossover = MultipleValueCrossover()
    mutation = MultipleValueMutation(mutation_onemax_specific)
    fitness = MultipleValueFitnessEvaluator()
    evaluation = SimpleEvaluation(fitness)
    variation = VarAnd(crossover, mutation, 0.8, 0.8)
    ea = SimpleEa(variation, evaluation, selection)
    
    for i in range(10):
        next_gen = ea.generational_step(population)
        print("\nGeneration #", i)
        print("----------------------\n")
        report_max_min_mean_fitness(next_gen)
        print("\nparents: \n")
        for indv in population:
            print(indv._list_of_values)
        print("\noffspring: \n")
        for indv in next_gen:
            print(indv._list_of_values)
        population = next_gen

def report_max_min_mean_fitness(population):
    """Outputs the max/min/mean fitness values of a population of chromosomes

    Parameters
    ----------
    population : list of MultipleValueChromosome
            The population for which a fitness report is calculated
    """
    fitness = [indv.fitness for indv in population]
    print(fitness)
    print("Max fitness: \t", np.max(fitness))
    print("Min fitness: \t", np.min(fitness))
    print("Mean fitness: \t", np.mean(fitness))

def get_random_list_for_chromosome(number_of_values):
    """Produces list of randomly generated boolean values

    Parameters
    ----------
    number_of_values : int
            The desired length of list to populate and return

    Returns
    -------
    list of bools : list of booleans
            The list of length 'number_of_values' full of random True/False values
    """
    return [np.random.choice([True, False]) for i in range(number_of_values)]

def main():
    execute_generational_steps()
