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

# Pick any variable that is currently violating constraints and has
# at least one other value in its domain.
def any_conflicting_var(problem):
    return random.choice(
        [var for var in range(len(problem.values))
         if len(problem.domains[var]) > 1
         and problem.num_conflicts(var, problem.values[var]) > 0])

# Pick the (new) value that causes the fewest conflicts
def min_conflicts(problem, var):
    values = [val for val in problem.domains[var] if val != problem.values[var]]
    return min(
        values,
        key=lambda val: [problem.conflicted(var, val, var2, problem.values[var2])
                         for var2 in range(len(problem.values))
                         if var2 != var].count(True)
        )

# Solve a csp with the iterative improvement algorithm: start off
# by initializing everything then make improvements to decrease conflicts
# Initialize is a function to pick the initial values for the problem
# pick_var is a function to pick which variable to change next
# pick_value is a function for deciding the next value to assign to a variable
def iterative_improvement(problem,
                          initialize=random_values,
                          pick_var=any_conflicting_var,
                          pick_value=min_conflicts):
    start_time = time.time()
    iterations = 0

    print "Picking initial instatiation"
    if not problem.is_consistent():
        raise Exception('All variables must have non-empty domains')

    initialize(problem)

    while not problem.is_solution():
        var_to_change = pick_var(problem)
        new_value = pick_value(problem, var_to_change)
        problem.values[var_to_change] = new_value
        iterations += 1

    print "Solution found:"
    problem.display()
    print "Iterations: %d" % iterations
    print "Time spent: %.3f" % (time.time() - start_time)
