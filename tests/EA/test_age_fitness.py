import pytest
import numpy as np

from bingo.AgeFitness import AgeFitness
from bingo.MultipleValues import MultipleValueGenerator, \
                                 MultipleValueChromosome
from bingo.Base.Mutation import Mutation
from bingo.Base.Crossover import Crossover                                 
from bingo.Base.FitnessEvaluator import FitnessEvaluator
from bingo.EA.AgeFitnessEA import AgeFitnessEA
from bingo.EA.SimpleEvaluation import SimpleEvaluation

INITIAL_POP_SIZE = 10
TARGET_POP_SIZE = 5
SIMPLE_INDV_SIZE = 1
COMPLEX_INDV_SIZE = 6

class MultipleValueFitnessEvaluator(FitnessEvaluator):
    def __call__(self, individual):
        fitness = np.count_nonzero(individual.list_of_values)
        self.eval_count += 1
        return len(individual.list_of_values) - fitness

class DumbyCrossover(Crossover):
    def __call__(self, parent1, parent2):
        pass

class DumbyMutation(Mutation):
    def __call__(self, parent1):
        pass

def return_true():
    return True

def return_false():
    return False

@pytest.fixture
def fit_individual():
    generator = MultipleValueGenerator(return_true, SIMPLE_INDV_SIZE)
    indv = generator()
    return indv

@pytest.fixture
def strong_population():
    generator = MultipleValueGenerator(return_true, SIMPLE_INDV_SIZE)
    return [generator() for i in range(INITIAL_POP_SIZE)]

@pytest.fixture
def weak_individual():
    generator = MultipleValueGenerator(return_false, SIMPLE_INDV_SIZE)
    indv = generator()
    indv.genetic_age = 100
    return indv

@pytest.fixture
def weak_population():
    generator = MultipleValueGenerator(return_false, COMPLEX_INDV_SIZE)
    return [generator() for i in range(INITIAL_POP_SIZE)]

@pytest.fixture
def non_dominated_population():
    young_weak = MultipleValueChromosome([False, False])
    middle_average = MultipleValueChromosome([False, True])
    middle_average.genetic_age = 1
    old_fit = MultipleValueChromosome([True, True])
    old_fit.genetic_age = 2
    return [young_weak, middle_average, old_fit]

@pytest.fixture
def all_dominated_population(non_dominated_population):
    non_dominated_population[0].genetic_age = 2
    non_dominated_population[2].genetic_age = 0
    return non_dominated_population

@pytest.fixture
def pareto_front_population():
    size_of_list = 6
    population = []
    for i in range (size_of_list):
        values = [False]*(size_of_list - i) + [True]*(i)
        indv = MultipleValueChromosome(values)
        indv.genetic_age = i
        population.append(indv)
    return population

@pytest.fixture
def selected_indiviudals(pareto_front_population):
    list_size = len(pareto_front_population[0].list_of_values)
    list_one = [False]*int(list_size/2)+[True]*int((list_size+1)/2)
    list_two = [False]*int((list_size+1)/2)+[True]*int(list_size/2)

    selected_indv_one = MultipleValueChromosome(list_one)
    selected_indv_two = MultipleValueChromosome(list_two)

    selected_indv_one.genetic_age = list_size
    selected_indv_two.genetic_age = list_size + 1
    return [selected_indv_one, selected_indv_two]

@pytest.fixture
def evaluator():
    fitness = MultipleValueFitnessEvaluator()
    evaluator = SimpleEvaluation(fitness)
    return evaluator

def test_remove_nan(fit_individual):
    indv_1 = fit_individual
    indv_2 = indv_1.copy()
    indv_1.fitness = 1e8
    indv_2.fitness = np.sqrt(-2)

    population = [indv_1, indv_2]
    pop_reverse = population[::-1]
    print(population)
    print(pop_reverse)

    age_fitness_selection = AgeFitness()
    target_population_size = 1
    new_population = age_fitness_selection(population, target_population_size)
    new_pop_reverse = age_fitness_selection(pop_reverse, target_population_size)

    assert len(new_pop_reverse) == len(new_population) == 1
    assert new_pop_reverse[0] == new_population[0] == indv_1



def test_target_population_size_is_valid(strong_population):
    age_fitness_selection = AgeFitness()
    with pytest.raises(ValueError):
        age_fitness_selection(strong_population, len(strong_population) + 1)

def test_none_selected_for_removal(non_dominated_population, evaluator):
    age_fitness_selection = AgeFitness()
    evaluator(non_dominated_population)

    target_pop_size = 1
    new_population = age_fitness_selection(non_dominated_population,
                                           target_pop_size)
    assert len(new_population) == len(non_dominated_population)

def test_all_but_one_removed(all_dominated_population, evaluator):
    age_fitness_selection = AgeFitness()
    evaluator(all_dominated_population)

    target_pop_size = 1
    new_population = age_fitness_selection(all_dominated_population,
                                           target_pop_size)
    assert len(new_population) == target_pop_size 

def test_all_but_one_removed_large_selection_size(strong_population,
                                                  weak_individual,
                                                  evaluator):
    population = strong_population +[weak_individual]
    evaluator(population)

    age_fitness_selection = AgeFitness(selection_size=10)

    target_pop_size = 1
    new_population = age_fitness_selection(population, target_pop_size)

    assert len(new_population) == target_pop_size
    assert new_population[0].list_of_values == [True]
    assert age_fitness_selection._selection_attempts == 2

def test_all_removed_in_one_iteration(weak_individual,
                                      fit_individual,
                                      evaluator):
    population = [weak_individual for i in range(10)] + [fit_individual]
    evaluator(population)

    age_fitness_selection = AgeFitness(selection_size=len(population))

    target_pop_size = 1
    new_population = age_fitness_selection(population, target_pop_size)

    assert len(new_population) == target_pop_size
    assert new_population[0].list_of_values == [True]
    assert age_fitness_selection._selection_attempts == 1

def test_selection_size_larger_than_population(weak_population, fit_individual, evaluator):
    population = weak_population + [fit_individual]
    evaluator(population)

    age_fitness_selection = AgeFitness(selection_size=(len(population)+100))

    target_pop_size = 2
    new_population = age_fitness_selection(population, target_pop_size)

    assert len(new_population) == target_pop_size
    assert age_fitness_selection._selection_attempts == 1
    count = 1
    for indv in new_population:
        if not any(indv.list_of_values):
            count *= 2
        elif all(indv.list_of_values):
            count *= 3

    assert count == 6

def test_keep_pareto_front_miss_target_pop_size(pareto_front_population,
                                                evaluator,
                                                selected_indiviudals):
    selected_indv_one = selected_indiviudals[0]
    selected_indv_two = selected_indiviudals[1]
    population = pareto_front_population + selected_indiviudals
    evaluator(population)

    age_fitness_selection = AgeFitness(selection_size=len(population))
    new_population = age_fitness_selection(population, TARGET_POP_SIZE)

    assert len(new_population) == len(pareto_front_population)

    selected_indvs_removed = True
    for indv in new_population:
        if (indv.genetic_age == selected_indv_one and \
                indv.list_of_values == selected_indv_one.list_of_values) or \
                (indv.genetic_age == selected_indv_two and \
                indv.list_of_values == selected_indv_two.list_of_values):
            selected_indvs_removed = False
            break
    assert selected_indvs_removed

def test_age_fitness_ea_step(pareto_front_population, evaluator, selected_indiviudals):
    population = pareto_front_population + selected_indiviudals
    mutation = DumbyMutation()
    crossover = DumbyCrossover()
    generator = MultipleValueGenerator(return_false, 6)
    ea = AgeFitnessEA(evaluator, generator, crossover, mutation, 0, 0,
                      len(pareto_front_population))
    new_population = ea.generational_step(pareto_front_population)
    assert len(new_population) == len(pareto_front_population)
