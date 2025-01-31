import pyomo.environ as pe
import pyomo.opt as po

# Δημιουργία του AbstractModel
model = pe.AbstractModel()

# Σετ των μεταβλητών (δημιουργούμε ένα σύνολο με 5 μεταβλητές)
model.I = pe.RangeSet(1, 5)

# Παράμετροι
model.coeff = pe.Param(model.I)  # Συντελεστές για τη συνάρτηση στόχου
model.weights = pe.Param(model.I)  # Βάρη για τους περιορισμούς
model.capacity = pe.Param()  # Μέγιστη χωρητικότητα (δεξιά πλευρά του περιορισμού)

# Μεταβλητές
model.x = pe.Var(model.I, domain=pe.Binary)

# Συνάρτηση στόχου
def objective_rule(model):
    return sum(model.coeff[i] * model.x[i] for i in model.I)

model.obj = pe.Objective(rule=objective_rule, sense=pe.maximize)

# Περιορισμός
def constraint_rule(model):
    return sum(model.weights[i] * model.x[i] for i in model.I) <= model.capacity

model.con = pe.Constraint(rule=constraint_rule)

# Δεδομένα
data = {
    None: {
        'coeff': {1: 3, 2: 4, 3: 5, 4: 8, 5: 9},
        'weights': {1: 2, 2: 3, 3: 4, 4: 5, 5: 9},
        'capacity': {None: 20},
    }
}

# Δημιουργία και επίλυση του μοντέλου
instance = model.create_instance(data)  # Δημιουργία ενός Concrete instance από το AbstractModel
solver = po.SolverFactory('gurobi')
result = solver.solve(instance, tee=True)

# Εκτύπωση των αποτελεσμάτων
for i in instance.I:
    print(f"x[{i}] = {pe.value(instance.x[i])}")

print(f"Objective value: {pe.value(instance.obj)}")
