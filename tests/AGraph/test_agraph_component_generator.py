# Ignoring some linting rules in tests
# pylint: disable=redefined-outer-name
# pylint: disable=missing-docstring
import pytest
import numpy as np

from bingo.AGraph.ComponentGenerator import ComponentGenerator


@pytest.fixture
def sample_generator():
    generator = ComponentGenerator(input_x_dimension=2,
                                   num_initial_load_statements=2,
                                   terminal_probability=0.4,
                                   constant_probability=0.5)
    generator.add_operator(2)
    generator.add_operator(6)
    return generator


@pytest.mark.parametrize("x_dim,expected_error", [
    (-1, ValueError),
    ("string", TypeError)
])
def test_raises_error_invalid_x_dimension(x_dim, expected_error):
    with pytest.raises(expected_error):
        _ = ComponentGenerator(input_x_dimension=x_dim)


@pytest.mark.parametrize("num_loads,expected_error", [
    (0, ValueError),
    ("string", TypeError)
])
def test_raises_error_invalid_initial_loads(num_loads, expected_error):
    with pytest.raises(expected_error):
        _ = ComponentGenerator(input_x_dimension=1,
                               num_initial_load_statements=num_loads)


@pytest.mark.parametrize("term_prob,expected_error", [
    (-0.1, ValueError),
    ("string", TypeError),
    (2, ValueError)
])
def test_raises_error_invalid_terminal_probability(term_prob, expected_error):
    with pytest.raises(expected_error):
        _ = ComponentGenerator(input_x_dimension=1,
                               terminal_probability=term_prob)


@pytest.mark.parametrize("const_prob,expected_error", [
    (-0.1, ValueError),
    ("string", TypeError),
    (2, ValueError)
])
def test_raises_error_invalid_constant_probability(const_prob, expected_error):
    with pytest.raises(expected_error):
        _ = ComponentGenerator(input_x_dimension=1,
                               constant_probability=const_prob)


def test_raises_error_random_operator_with_no_operators():
    no_operator_generator = ComponentGenerator(input_x_dimension=1,
                                               terminal_probability=0.0)
    _ = no_operator_generator.random_command(0)
    with pytest.raises(ValueError):
        _ = no_operator_generator.random_command(1)
    with pytest.raises(ValueError):
        _ = no_operator_generator.random_operator()


def test_random_terminal(sample_generator):
    np.random.seed(0)
    terminals = [sample_generator.random_terminal() for _ in range(10)]
    expected_terminals = [0, 0, 0, 0, 1, 0, 1, 0, 0, 1]
    np.testing.assert_array_equal(terminals, expected_terminals)


def test_random_operator(sample_generator):
    np.random.seed(0)
    operators = [sample_generator.random_operator() for _ in range(10)]
    expected_operators = [6, 6, 6, 6, 2, 6, 2, 6, 6, 2]
    np.testing.assert_array_equal(operators, expected_operators)


def test_random_operator_parameter(sample_generator):
    for command_location in np.random.randint(1, 100, 50):
        command_param = \
            sample_generator.random_operator_parameter(command_location)
        assert command_param < command_location


def test_random_terminal_parameter(sample_generator):
    for _ in range(20):
        assert sample_generator.random_terminal_parameter(0) in [0, 1]
        assert sample_generator.random_terminal_parameter(1) == -1


def test_add_operator(sample_generator):
    np.random.seed(0)
    sample_generator.add_operator(3)
    operators = [sample_generator.random_operator() for _ in range(10)]
    assert 3 in operators


def test_add_operator_with_weight(sample_generator):
    sample_generator.add_operator(3, operator_weight=0.0)
    operators = [sample_generator.random_operator() for _ in range(10)]
    assert 3 not in operators


def test_random_command(sample_generator):
    generated_commands = np.empty((6, 3))
    expected_commands = np.array([[0, 0, 1],
                                  [1, -1, -1],
                                  [2, 0, 1],
                                  [0, 1, 0],
                                  [2, 3, 2],
                                  [6, 0, 4]])
    for stack_location in range(generated_commands.shape[0]):
        generated_commands[stack_location, :] = \
            sample_generator.random_command(stack_location)
    np.testing.assert_array_equal(generated_commands, expected_commands)
