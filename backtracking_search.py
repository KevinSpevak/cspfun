import Queue
import time


# Variable ordering function that picks variables
# in increasing order of numerical representation
def increasing_order(problem):
    return problem.values.index(None)

# Variable ordering function that picks variables with the smallest
# remaining domains first
def mrv(problem):
    unassigned = [v for v in range(len(problem.values)) if problem.values[v] == None]
    return min(unassigned, key=lambda v: len(problem.domains[v]))

# Value ordering function that picks values that least constrict other
# variables' domains first
def lcv(children):
    return sorted(children,
                  key=lambda c: sum([len(c.domains[i]) for i in range(len(c.values))]),
                  reverse=True)

# The queue priority for an instantiation in backtracking search
# The value just assigned is the ith out of n possible
# Instantiations with more values assigned should be checked first
# (dfs) and at a given depth, lower values of i should be checked first
def bts_priority(problem, i, n):
    return problem.values.count(None) + float(i) / n

# Use backtracking search to solve a CSP
# next_var: function on csp that picks next variable to assign
# order_values: order a list of instantiations in the order they should be checked
# Filtering: if "fc" use forward checking, if "ac" use arc consistency
def solve(problem, filtering=None, pick_next_var=increasing_order, order_values=lambda arr: arr):
    start_time = time.time()
    iterations = 0

    if filtering == "fc":
        print "Using forward checking"
        problem.use_forward_checking = True
    elif filtering == "ac":
        print "Using arc consistency.\nRunning initial arc consistency on entire problem...",
        problem.check_all_arcs()
        print " Done."
        problem.use_arc_consistency = True
    elif filtering != None:
        raise Exception("Unrecognized filter: " + str(filtering))

    fringe = Queue.PriorityQueue()
    fringe.put((0, problem))

    while not fringe.empty():
        instantiation = fringe.get()[1]
        iterations += 1

        if instantiation.is_complete():
            if instantiation.is_solution():
                print "Found solution:"
                print instantiation.display()
                break
        else:
            next_var = pick_next_var(instantiation)
            children = []
            for val in instantiation.domains[next_var]:
                nextInstantiation = instantiation.copy()
                nextInstantiation.set_var_val(next_var, val)
                if nextInstantiation.is_consistent():
                    children.append(nextInstantiation)
            children = order_values(children)

            for i in range(len(children)):
                fringe.put((bts_priority(children[i], i, len(children)), children[i]))
    else:
        print "No solution found"

    print "Instantiations checked: %d" % iterations
    print "Time spent: %.3f" % (time.time() - start_time)

