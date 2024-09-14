from ortools.sat.python import cp_model

model = cp_model.CpModel()

# dictionary to store the worker, shift, and day combinations
shift_assignments = {}

# used 9 workers with 3 for each role to get quick results
num_workers = 9
shifts_per_day = 2  # assumed two shifts per day
num_days = 7  # 7 days per week

# worker roles: 1 = cook, 2 = hostess, 3 = server
worker_roles = {
    0: 1, 1: 1, 2: 2, 3: 2, 4: 3, 5: 3, 6: 3, 7: 1, 8: 2
}

# Let's assume each shift is 8 hours
shift_hours = 8

### Here's where we would build constraints into our query dynamically as things are selected in the UI
### For simplicity's sake I only have a couple constraints but you can imagine how we could add roles to workers (full-time and part-time for example) and constraints to check that, add in holidays, and so on.

# Create boolean variables for each combination of worker, day, and shift
for worker in range(num_workers):
    for day in range(num_days):
        for shift in range(shifts_per_day):
            # Create a boolean variable to represent whether a worker is assigned to a specific shift on a specific day
            shift_assignments[(worker, day, shift)] = model.NewBoolVar(f"shift_w{worker}_d{day}_s{shift}")

# Ensure at least 1 cook, 1 hostess, and 1 server must work each day
for day in range(num_days):
    for shift in range(shifts_per_day):
        # At least 1 cook
        model.Add(sum(shift_assignments[(worker, day, shift)] for worker in range(num_workers) if worker_roles[worker] == 1) >= 1)
        # At least 1 hostess
        model.Add(sum(shift_assignments[(worker, day, shift)] for worker in range(num_workers) if worker_roles[worker] == 2) >= 1)
        # At least 1 server
        model.Add(sum(shift_assignments[(worker, day, shift)] for worker in range(num_workers) if worker_roles[worker] == 3) >= 1)

# Let's limit the solution search to 5 solutions
class SolutionPrinter(cp_model.CpSolverSolutionCallback):
    def __init__(self, shift_assignments, num_workers, num_days, shifts_per_day, max_solutions=5):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self._shift_assignments = shift_assignments
        self._num_workers = num_workers
        self._num_days = num_days
        self._shifts_per_day = shifts_per_day
        self._solution_count = 0
        self._max_solutions = max_solutions

    def on_solution_callback(self):
        if self._solution_count < self._max_solutions:
            print(f"Solution {self._solution_count}")
            for day in range(self._num_days):
                print(f"Day {day}")
                for shift in range(self._shifts_per_day):
                    for worker in range(self._num_workers):
                        if self.Value(self._shift_assignments[(worker, day, shift)]):
                            role = worker_roles[worker]
                            role_str = "Cook" if role == 1 else "Hostess" if role == 2 else "Server"
                            print(f"Worker {worker} ({role_str}) works Day {day}, Shift {shift}")
            print()
            self._solution_count += 1
        if self._solution_count >= self._max_solutions:
            print(f"Stopping after {self._max_solutions} solutions.")
            self.StopSearch()

    def solution_count(self):
        return self._solution_count

# Solve the model
solver = cp_model.CpSolver()

solution_printer = SolutionPrinter(shift_assignments, num_workers, num_days, shifts_per_day, max_solutions=5)
status = solver.SearchForAllSolutions(model, solution_printer)

# Check the status
if status == cp_model.INFEASIBLE:
    print("No feasible solution found.")
else:
    print(f"Total solutions found: {solution_printer.solution_count()}")
