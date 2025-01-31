from tkinter import *
from tkinter import messagebox
import pyomo.environ as pe
import pyomo.opt as po

# Συνάρτηση για την επίλυση του Scheduling Problem
def solve_scheduling():
    try:
        # Ανάγνωση δεδομένων από το GUI
        num_tasks = int(entry_num_tasks.get())
        num_machines = int(entry_num_machines.get())
        task_durations_input = text_task_durations.get("1.0", END).strip()

        # Μετατροπή δεδομένων
        task_durations = list(map(float, task_durations_input.split()))

        # Έλεγχος δεδομένων
        if len(task_durations) != num_tasks:
            raise ValueError("The number of task durations must match the number of tasks.")

        # Δημιουργία μοντέλου Pyomo
        model = pe.ConcreteModel()

        # Σετ εργασιών και μηχανών
        model.tasks = pe.Set(initialize=range(num_tasks))
        model.machines = pe.Set(initialize=range(num_machines))

        # Μεταβλητές απόφασης
        model.start_time = pe.Var(model.tasks, domain=pe.NonNegativeReals)  # Χρόνος έναρξης εργασίας
        model.machine_assignment = pe.Var(model.tasks, model.machines, domain=pe.Binary)  # Ανάθεση μηχανής

        # Μεταβλητή για το makespan (συνολικό χρόνο ολοκλήρωσης)
        model.makespan = pe.Var(domain=pe.NonNegativeReals)

        # Συνάρτηση στόχου: Ελαχιστοποίηση του makespan
        def objective_rule(model):
            return model.makespan
        
        model.obj = pe.Objective(rule=objective_rule, sense=pe.minimize)

        # Περιορισμός: Κάθε εργασία πρέπει να εκτελείται από μία μηχανή
        def task_assignment_rule(model, t):
            return sum(model.machine_assignment[t, m] for m in model.machines) == 1
        
        model.task_constraints = pe.Constraint(model.tasks, rule=task_assignment_rule)

        # Περιορισμός: Καμία εργασία δεν ξεκινά πριν να έχει εκχωρηθεί σε μηχανή
        def start_time_rule(model, t):
            return model.start_time[t] >= 0
        
        model.start_time_constraints = pe.Constraint(model.tasks, rule=start_time_rule)

        # Περιορισμός: Εργασίες που εκτελούνται στην ίδια μηχανή δεν επικαλύπτονται
        def no_overlap_rule(model, t1, t2, m):
            if t1 != t2:
                return model.start_time[t1] + task_durations[t1] * model.machine_assignment[t1, m] <= model.start_time[t2] + (1 - model.machine_assignment[t2, m]) * 1e6
            return pe.Constraint.Skip
        
        model.no_overlap_constraints = pe.Constraint(model.tasks, model.tasks, model.machines, rule=no_overlap_rule)

        # Περιορισμός: Ο makespan είναι μεγαλύτερος ή ίσος από το χρόνο ολοκλήρωσης κάθε εργασίας
        def makespan_rule(model, t):
            return model.makespan >= model.start_time[t] + sum(model.machine_assignment[t, m] * task_durations[t] for m in model.machines)
        
        model.makespan_constraints = pe.Constraint(model.tasks, rule=makespan_rule)

        # Επίλυση
        solver = po.SolverFactory('glpk')
        result = solver.solve(model, tee=True)

        # Ανάγνωση αποτελεσμάτων
        schedule = []
        total_makespan = pe.value(model.makespan)
        for t in model.tasks:
            assigned_machine = next(m for m in model.machines if pe.value(model.machine_assignment[t, m]) == 1)
            start_time = pe.value(model.start_time[t])
            schedule.append(f"Task {t+1} -> Machine {assigned_machine+1} (Start: {start_time})")

        # Εμφάνιση αποτελεσμάτων
        result_text = f"Total Makespan: {total_makespan}\n\nSchedule:\n" + "\n".join(schedule)
        messagebox.showinfo("Results", result_text)

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Δημιουργία GUI με Tkinter
root = Tk()
root.title("Scheduling Problem Solver")

# Ετικέτες και πεδία εισόδου
Label(root, text="Number of Tasks:").grid(row=0, column=0, sticky="w")
entry_num_tasks = Entry(root)
entry_num_tasks.grid(row=0, column=1)

Label(root, text="Number of Machines:").grid(row=1, column=0, sticky="w")
entry_num_machines = Entry(root)
entry_num_machines.grid(row=1, column=1)

Label(root, text="Task Durations (space-separated):").grid(row=2, column=0, sticky="nw")
text_task_durations = Text(root, height=5, width=40)
text_task_durations.grid(row=2, column=1)

# Κουμπί επίλυσης
solve_button = Button(root, text="Solve the problem", command=solve_scheduling)
solve_button.grid(row=3, column=0, columnspan=2)

# Εκκίνηση του Tkinter loop
root.mainloop()
