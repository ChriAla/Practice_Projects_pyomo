from tkinter import * 
from tkinter import messagebox
import pyomo.environ as pe
import pyomo.opt as po

# Συνάρτηση για την επίλυση του Assignment Problem
def solve_assignment():
    try:
        # Ανάγνωση δεδομένων από το GUI
        num_workers = int(entry_num_workers.get())
        num_tasks = int(entry_num_tasks.get())
        cost_input = text_costs.get("1.0", END).strip()
        
        # Έλεγχος αν ο αριθμός εργατών και εργασιών ταιριάζει
        if num_workers != num_tasks:
            raise ValueError("The Assignment Problem requires an equal number of workers and jobs.")
        
        # Μετατροπή κόστους από είσοδο σε πίνακα
        costs = [
            list(map(float, row.split()))
            for row in cost_input.split("\n") if row.strip()
        ]
        if len(costs) != num_workers or any(len(row) != num_tasks for row in costs):
            raise ValueError("The cost table is not configured correctly.")
        
        # Δημιουργία μοντέλου Pyomo
        model = pe.ConcreteModel()

        # Σετ εργατών και εργασιών
        model.workers = pe.Set(initialize=range(num_workers))
        model.tasks = pe.Set(initialize=range(num_tasks))

        # Μεταβλητές ανάθεσης (binary)
        model.x = pe.Var(model.workers, model.tasks, domain=pe.Binary)

        # Συνάρτηση στόχου: Ελαχιστοποίηση κόστους
        def objective_rule(model):
            return sum(model.x[w, t] * costs[w][t] for w in model.workers for t in model.tasks)
        
        model.obj = pe.Objective(rule=objective_rule, sense=pe.minimize)

        # Περιορισμός: Κάθε εργάτης αναλαμβάνει ακριβώς μία εργασία
        def worker_constraint_rule(model, w):
            return sum(model.x[w, t] for t in model.tasks) == 1
        
        model.worker_constraints = pe.Constraint(model.workers, rule=worker_constraint_rule)

        # Περιορισμός: Κάθε εργασία ανατίθεται σε ακριβώς έναν εργάτη
        def task_constraint_rule(model, t):
            return sum(model.x[w, t] for w in model.workers) == 1
        
        model.task_constraints = pe.Constraint(model.tasks, rule=task_constraint_rule)

        # Επίλυση
        solver = po.SolverFactory('glpk')
        result = solver.solve(model, tee=True)

        # Ανάγνωση αποτελεσμάτων
        assignments = []
        total_cost = pe.value(model.obj)
        for w in model.workers:
            for t in model.tasks:
                if pe.value(model.x[w, t]) == 1:
                    assignments.append(f"Worker {w+1} -> Task {t+1}")

        # Εμφάνιση αποτελεσμάτων
        result_text = f"Final Cost: {total_cost}\nAssignments:\n" + "\n".join(assignments)
        messagebox.showinfo("Results", result_text)

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Δημιουργία GUI με Tkinter
root = Tk()
root.title("Assignment Problem Solver")

# Ετικέτες και πεδία εισόδου
Label(root, text="Number of Workers:").grid(row=0, column=0, sticky="w")
entry_num_workers = Entry(root)
entry_num_workers.grid(row=0, column=1)

Label(root, text="Number of Jobs:").grid(row=1, column=0, sticky="w")
entry_num_tasks = Entry(root)
entry_num_tasks.grid(row=1, column=1)

Label(root, text="Cost Table (space-separated lines):").grid(row=2, column=0, sticky="nw")
text_costs = Text(root, height=10, width=40)
text_costs.grid(row=2, column=1)

# Κουμπί επίλυσης
solve_button = Button(root, text="Solve the problem", command=solve_assignment)
solve_button.grid(row=3, column=0, columnspan=2)

# Εκκίνηση του Tkinter loop
root.mainloop()
