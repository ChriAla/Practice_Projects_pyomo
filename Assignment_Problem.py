import pyomo.environ as pe
import pyomo.opt as po

# Δημιουργία του AbstractModel
model = pe.AbstractModel()

# Σετ
model.Workers = pe.Set()  # Σύνολο εργαζομένων
model.Tasks = pe.Set()  # Σύνολο εργασιών

# Παράμετροι
model.cost = pe.Param(model.Workers, model.Tasks)  # Κόστος ανάθεσης εργασιών

# Μεταβλητές
model.x = pe.Var(model.Workers, model.Tasks, domain=pe.Binary)  # Δυαδικές μεταβλητές ανάθεσης

# Συνάρτηση στόχου
def objective_rule(model):
    return sum(model.cost[i, j] * model.x[i, j] for i in model.Workers for j in model.Tasks)

model.obj = pe.Objective(rule=objective_rule, sense=pe.minimize)

# Περιορισμοί
def worker_assignment_rule(model, i):
    return sum(model.x[i, j] for j in model.Tasks) == 1  # Κάθε εργαζόμενος αναλαμβάνει μία εργασία

def task_assignment_rule(model, j):
    return sum(model.x[i, j] for i in model.Workers) == 1  # Κάθε εργασία εκτελείται από έναν εργαζόμενο

model.worker_assignment = pe.Constraint(model.Workers, rule=worker_assignment_rule)
model.task_assignment = pe.Constraint(model.Tasks, rule=task_assignment_rule)

# Δεδομένα
data = {
    None: {
        'Workers': [1, 2, 3, 4],
        'Tasks': [1, 2, 3, 4],
        'cost': {
            (1, 1): 9, (1, 2): 2, (1, 3): 7, (1, 4): 8,
            (2, 1): 6, (2, 2): 4, (2, 3): 3, (2, 4): 7,
            (3, 1): 5, (3, 2): 8, (3, 3): 1, (3, 4): 8,
            (4, 1): 7, (4, 2): 6, (4, 3): 9, (4, 4): 4,
        }
    }
}

# Δημιουργία και επίλυση του μοντέλου
instance = model.create_instance(data)  # Δημιουργία συγκεκριμένου instance από το AbstractModel
solver = po.SolverFactory('gurobi')  # Χρήση του Gurobi
result = solver.solve(instance, tee=True)

# Εκτύπωση αποτελεσμάτων
print("Αποτέλεσμα Ανάθεσης:")
for i in instance.Workers:
    for j in instance.Tasks:
        if pe.value(instance.x[i, j]) == 1:
            print(f"Εργαζόμενος {i} αναλαμβάνει Εργασία {j}")

print(f"Συνολικό κόστος: {pe.value(instance.obj)}")
