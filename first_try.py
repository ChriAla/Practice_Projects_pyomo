import pyomo.environ as pe
import pyomo.opt as po

solver = po.SolverFactory('gurobi') # GNU Linear Programming Kit

model = pe.ConcreteModel()# Create the model

# Variables
model.x1 = pe.Var(domain = pe.Binary)
model.x2 = pe.Var(domain = pe.Binary)
model.x3 = pe.Var(domain = pe.Binary)
model.x4 = pe.Var(domain = pe.Binary)
model.x5 = pe.Var(domain = pe.Binary)

# Objective
obj_expr = 3 * model.x1 + 4 * model.x2 + 5 * model.x3 + 8 * model.x4 + 9 * model.x5 
model.obj = pe.Objective(sense = pe.maximize, expr = obj_expr)

# Constrain
con_expr = 2 * model.x1 + 3 * model.x2 + 4 * model.x3 + 5 * model.x4 + 9 * model.x5 <= 20
model.con = pe.Constraint(expr = con_expr)

result = solver.solve(model, tee=True)

print(pe.value(model.x1))
print(pe.value(model.x2))
print(pe.value(model.x3))
print(pe.value(model.x4))
print(pe.value(model.x5))
print(pe.value(model.obj))