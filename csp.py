import Queue

# A CSP represents an constraint satisfaction problem with a partial assignment
# this class only supports binary constraints
class BinaryCSP:
    # The n variables in the CSP are represented by the integers 0...n-1
    # domains[i] contains a list of possible values for variable i
    # values[i] contains the assigned value for variable i, or None if unassigned
    # constraints is a dictionary that maps a pair of vairables (j, k) to
    # a function that takes the values assigned to those variables and returns
    # whether the constraints between those variables are satisfied.
    def __init__(self, domains=[], values=[], constraints={},
                 use_forward_checking=False, use_arc_consistency=False):
       self.domains = domains
       self.values = values
       self.constraints = constraints
       self.use_forward_checking = use_forward_checking
       self.use_arc_consistency = use_arc_consistency

    # Return a deep copy of the problem
    def copy(self):
        return BinaryCSP([d[:] for d in self.domains], self.values[:], self.constraints,
                         self.use_forward_checking, self.use_arc_consistency)

    # Set the value of a variable and update the domain to contain only that value
    def set_var_val(self, var, val):
        if val not in self.domains[var]:
            raise Exception(str(val) + " is not in variable %d's domain" % var)
        self.values[var] = val
        self.domains[var] = [val]
        if self.use_forward_checking:
            self.forward_check(var)
        elif self.use_arc_consistency:
            self.run_arc_consistency([(tail, var) for tail in range(len(self.values)) if tail != var])


    # Return true iff the assignments var1=val1, var2=val2 violate a constraint
    # Note: this can be overridden by a subclass that wants to define conflicts
    # in a way other than an explicit dictionary of all constraints
    def conflicted(self, var1, val1, var2, val2):
        if val1 == None or val2 == None:
            return False
        if (min(var1, var2), max(var1, var2)) not in self.constraints:
            return False
        # Constraint keys and arguments take the lower-valued variable first
        # so we may need to reverse the variables
        if var1 < var2:
            constraint = self.constraints[(var1, var2)]
        else:
            original = self.constraints[(var2, var1)]
            constraint = lambda a, b: original(b, a)

        return not constraint(val1, val2)

    # Returns the number of constraints that would be violated by the assignemnt
    # var=val given the current values assigned to other variables
    def num_conflicts(self, var, val):
        return [self.conflicted(var, val, var2, self.values[var2])
                for var2 in range(len(self.values)) if var2 != var].count(True)

    # Returns the total number of constraints violated
    def total_conflicts(self):
        return sum([self.num_conflicts(var, self.values[var]) for var in range(len(self.values))])/2

    # Return true iff the assignment is complete (each variable has a value)
    def is_complete(self):
        return None not in self.values

    # Return true iff each unassigned variable has a non-empty domain
    def is_consistent(self):
        return [] not in self.domains

    # Return true iff the assignment is a solution
    def is_solution(self):
        if None in self.values:
            return False
        for var_a, var_b in self.constraints:
            constraint = self.constraints[(var_a, var_b)]
            if not constraint(self.values[var_a], self.values[var_b]):
                return False
        return True

    # Enforce arc consistency on the arc tail -> head
    # Return True if any changes were made
    def enforce_arc(self, tail, head):
        # Find the constraint.  Constraint functions take the lower-valued
        # variable as the first argument so we may need to reverse the function
        if (min(tail, head), max(tail, head)) not in self.constraints:
            return False

        # Remove values from the domain of the tail that cannot be extended
        # to a valid assignment at the head
        new_tail_domain = filter(
            lambda tail_val: False in [self.conflicted(tail, tail_val, head, head_val)
                                       for head_val in self.domains[head]],
            self.domains[tail]
            )

        domain_reduced = len(new_tail_domain) < len(self.domains[tail])
        self.domains[tail] = new_tail_domain
        return domain_reduced

    # Run forward checking for an updated variable
    def forward_check(self, var):
        if self.values[var] == None:
            raise Exception("Cannot forward check on unasigned variable %d" % var)

        for tail in [var2 for var2 in range(len(self.values)) if var2 != var]:
            self.enforce_arc(tail, var)

    # Run arc consistency given an initial list of arcs to check
    def run_arc_consistency(self, arcs):
        while len(arcs) > 0:
            tail, head = arcs[0]
            arcs = arcs[1:]
            if self.enforce_arc(tail, head):
                # tail was updated so need to re-check arcs pointing to tail
                for var in range(len(self.values)):
                    if var != tail and (var, tail) not in arcs:
                        arcs.append((var, tail))

    # Ensure arc consistency of entire problem
    def check_all_arcs(self):
        n = len(self.values)
        self.run_arc_consistency([(tail, head) for tail in range(n) for head in range(n) if head != tail])

    def display(self):
        print self.values

# An n-queens problem
# Variable i represents the ith row
# The value of variable i represents the column that the queen is in
class NQueens(BinaryCSP):
    # If domains and values are given, copy them.  Otherwise create a new
    # n-queens problem with an empty assignment and full domains
    def __init__(self, n, domains=[], values=[], constraints={},
                 use_forward_checking=False, use_arc_consistency=False):
        self.n = n
        if len(domains) == n and len(values) == n:
            BinaryCSP.__init__(self, domains, values, constraints,
                               use_forward_checking, use_arc_consistency)
        else:
            print "Initializing new %d-queens problem" % n
            self.values = [None for row in range(n)]
            self.domains = [[col for col in range(n)] for row in range(n)]
            self.constraints = {}
            for var1 in range(n - 1):
                for var2 in range(var1 + 1, n):
                    self.constraints[(var1, var2)] = NQueens.generate_constraint(var1, var2)
            self.use_forward_checking = use_forward_checking
            self.use_arc_consistency = use_arc_consistency

    def copy(self):
        return NQueens(self.n, [d[:] for d in self.domains], self.values[:],
                       self.constraints, self.use_forward_checking, self.use_arc_consistency)

    # Print a text-based representation of the board
    # If the board is too big, just print the array of variable values
    def display(self):
        if self.n > 25:
            print self.values
            return
        print ' ' + ' '.join(['_' for i in range(self.n)])
        for col in self.values:
            print '|' + '|'.join(['Q' if i == col else '_' for i in range(self.n)]) + '|'

    # Generates the constraint between two variables in an n-qeens problem
    # The values (columns) of the two variables must not be equal, and not
    # on a diagonal (differ by same value as the row numbers differ by
    # var1    |    Q
    # var1 + 1|   XXX
    # var1 + 2|  X X X
    # Assumes var1 < var2
    @staticmethod
    def generate_constraint(var1, var2):
        return lambda val1, val2: val1 != val2 and abs(val2 - val1) != var2 - var1

# A sudoku problem
# Represented by 81 variables each with domain [1...9]
# variable k represents row k/9, column k % 9
class Sudoku(BinaryCSP):
    def __init__(self, domains = [], values = [], constraints={},
                 use_forward_checking=False, use_arc_consistency=False):
        if len(domains) == 81 and len(values) == 81:
            BinaryCSP.__init__(self, domains, values, constraints,
                               use_forward_checking, use_arc_consistency)
        else:
            print "Initializing new Sudoku problem"
            self.domains = [[v+1 for v in range(9)] for var in range(81)]
            self.constraints = {}
            print "Generating constraints...",
            for var in range(81):
                self.gen_constraints(var)
            print " Done."
            self.use_forward_checking = use_forward_checking
            self.use_arc_consistency = use_arc_consistency

            if len(values) == 81:
                self.values = values
            else:
                self.values = [None for var in range(81)]



    # For a given variable, generate all constraints including that variable
    # and put them in self.constraints. Only store constraints with variables
    # larger than the given variable to avoid duplicate rules
    def gen_constraints(self, var):
        row = var / 9
        col = var % 9
        neq = lambda a, b: a != b
        # Row inequality
        for x in range(col + 1, 9):
            self.constraints[(var, 9 * row + x)] = neq
        # Column inequality
        for y in range(row + 1, 9):
            self.constraints[(var, 9 * y + col)] = neq
        # Cell inequality
        for x in range(3 * (col/3), 3 * (col/3 + 1)):
            for y in range(3 * (row/3), 3 * (row/3 + 1)):
                if 9 * y + x > var:
                    self.constraints[(var, 9 * y + x)] = neq

    # Return a deep copy of the problem
    def copy(self):
        return Sudoku([d[:] for d in self.domains], self.values[:], self.constraints,
                      self.use_forward_checking, self.use_arc_consistency)

    def display(self):
        print ' ' + ' '.join(['_' for x in range(9)])
        for y in range(9):
            row = self.values[y*9:y*9+9]
            row = [str(row[x]) if row[x]!=None else '_' for x in range(9)]
            print '|' + '|'.join(row) + '|'

# Some sample Sudoku games from websudoku.com
# "easy": Easy no. 881,854,343
# "medium": Medium no. 3,910,102,414
# "hard": Hard no. 3,131,202,773
# "evil": Evil no 8,431,342,145
def sudoku_problem(name):
    u = None
    prob = Sudoku()
    if name == "easy":
        prob.values = [u, 9, 3, 7, 8, 1, 4, u, 5,
                       8, 1, u, 4, 5, u, 6, u, 7,
                       u, u, u, u, u, u, u, 1, u,
                       3, u, u, u, 4, 7, u, u, u,
                       u, u, 1, u, u, u, 9, u, u,
                       u, u, u, 5, 9, u, u, u, 1,
                       u, 7, u, u, u, u, u, u, u,
                       9, u, 6, u, 7, 8, u, 5, 4,
                       1, u, 5, 2, 6, 4, 8, 7, u]
    elif name == "medium":
        prob.values = [u, 3, 4, 2, 7, 1, 5, 6, u,
                       u, u, u, u, u, u, 3, u, 1,
                       u, 9, 6, u, u, 8, u, 2, u,
                       u, 7, u, u, 2, 4, u, u, u,
                       u, u, u, u, u, u, u, u, u,
                       u, u, u, 1, 5, u, u, 3, u,
                       u, 4, u, 3, u, u, 6, 9, u,
                       6, u, 3, u, u, u, u, u, u,
                       u, 1, 7, 6, 8, 2, 4, 5, u]
    elif name == "hard":
        prob.values = [u, 8, u, 9, u, u, 6, u, u,
                       u, u, 1, u, u, u, 4, u, u,
                       u, 4, u, u, u, 5, u, u, 7,
                       u, u, 4, u, 9, u, u, u, 5,
                       5, 3, u, u, 2, u, u, 7, 4,
                       2, u, u, u, 8, u, 1, u, u,
                       4, u, u, 8, u, u, u, 2, u,
                       u, u, 3, u, u, u, 7, u, u,
                       u, u, 9, u, u, 1, u, 6, u]
    elif name == "evil":
        prob.values = [3, u, 6, u, 1, u, u, u, u,
                       u, u, u, 8, u, 6, u, 7, 3,
                       u, u, u, u, u, u, u, 1, u,
                       4, u, u, u, u, 1, u, u, u,
                       u, 5, 1, u, 9, u, 4, 8, u,
                       u, u, u, 2, u, u, u, u, 9,
                       u, 1, u, u, u, u, u, u, u,
                       6, 2, u, 4, u, 7, u, u, u,
                       u, u, u, u, 3, u, 8, u, 5]
    else:
        raise Exception("No known sudoku problem " + name)

    for var in range(len(prob.values)):
        if prob.values[var]:
            prob.domains[var] = [prob.values[var]]

    return prob


# Small map coloring problem for testing
class DemoProb(BinaryCSP):
    def __init__(self):
        BinaryCSP.__init__(self, [['r', 'g', 'b'] for x in range(5)], [None for x in range(5)])
        neq = lambda a, b: a != b
        self.constraints= {
            (0, 1): neq,
            (0, 2): neq,
            (0, 3): neq,
            (1, 4): neq,
            (2, 4): neq
            }
