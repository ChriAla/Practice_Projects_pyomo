import pyomo.environ as pe
import pyomo.opt as po

solver = po.SolverFactory('glpk') # GNU Linear Programming Kit

model = pe.ConcreteModel()

model.N = pe.RangeSet(1, 5)

# Parameters
c = {1: 3, 2: 4, 3: 5, 4: 8, 5: 9}
a = {1: 2, 2: 3, 3: 4, 4: 5, 5: 9}
b = 20

model.c = pe.Param(model.N, initialize = c)
model.a = pe.Param(model.N, initialize = a)
model.b = pe.Param(initialize = b)

model.x = pe.Var(model.N, domain = pe.Binary)

obj_expr = sum(model.c[i] * model.x[i] for i in model.N)
model.obj = pe.Objective(sense = pe.maximize, expr = obj_expr)

con_lhs_expr = sum(model.a[i] * model.x[i] for i in model.N)
con_rhs_expr = model.b
model.con = pe.Constraint(expr = (con_lhs_expr <= con_rhs_expr))

result = solver.solve(model)

for i in model.N:
    print(pe.value(model.x[i]))
print(pe.value(model.obj))