import time
import random

# Pick the first value for each variable
def first_values(problem):
    for var in range(len(problem.values)):
        problem.values[var] = problem.domains[var][0]

# Pick random initial values
def random_values(problem):
    for var in range(len(problem.values)):
        problem.values[var] = random.choice(problem.domains[var])

# Pick a variable at random
def random_var(problem):
    return random.choice([var for var in range(len(problem.values))])

# Pick any variable that is currently violating constraints and has
# at least one other value in its domain.
def any_conflicting_var(problem):
    return random.choice(
        [var for var in range(len(problem.values))
         if len(problem.domains[var]) > 1
         and problem.num_conflicts(var, problem.values[var]) > 0])

# Pick a random new value
def random_value(problem, var):
    return random.choice([val for val in problem.domains[var] if val != problem.values[var]])

# Pick the (new) value that causes the fewest conflicts
def min_conflicts(problem, var):
    values = [val for val in problem.domains[var] if val != problem.values[var]]
    return min(
        values,
        key=lambda val: [problem.conflicted(var, val, var2, problem.values[var2])
                         for var2 in range(len(problem.values))
                         if var2 != var].count(True)
        )

# Generate a linear annealing schedule that decreases probability of random step
# linearly from initial_temp to 0 after iteration_limit
def linear_schedule(initial_temp, iteration_limit):
    return lambda problem, iterations: max(
        0, initial_temp * (iteration_limit - iterations) / iteration_limit)

# Solve a csp with the iterative improvement algorithm: start off
# by initializing everything then make improvements to decrease conflicts
# annealing is a function that takes the problem and iteration count and
# returns the probability of taking a random (potentially downhil) step
# Initialize is a function to pick the initial values for the problem
# pick_var is a function to pick which variable to change next
# pick_value is a function for deciding the next value to assign to a variable
def iterative_improvement(problem,
                          annealing=lambda i, prob: 0,
                          initialize=random_values,
                          pick_var=any_conflicting_var,
                          pick_value=min_conflicts):
    start_time = time.time()
    iterations = 0

    print "Picking initial instatiation"
    if not problem.is_consistent():
        raise Exception('All variables must have non-empty domains')

    initialize(problem)

    displayed = False
    while not problem.is_solution():
        if annealing(problem, iterations) > random.random():
            var_to_change = random_var(problem)
            new_value = random_value(problem, var_to_change)
        else:
            var_to_change = pick_var(problem)
            new_value = pick_value(problem, var_to_change)
        problem.values[var_to_change] = new_value
        iterations += 1

        if not displayed and annealing(problem, iterations) == 0:
            displayed = True
            print "Temperature reached zero"
            problem.display()
            print "Conflicts: %d" % problem.total_conflicts()

    print "Solution found:"
    problem.display()
    print "Iterations: %d" % iterations
    print "Time spent: %.3f" % (time.time() - start_time)
