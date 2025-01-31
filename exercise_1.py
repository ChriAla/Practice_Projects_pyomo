import pandas as pd
import pyomo.environ as pe
import pyomo.opt as po

pinakas = [
    [0, 7, 3, 0, 0, 18, 13, 6, 0, 9],
    [12, 5, 0, 12, 4, 22, 0, 17, 13, 0],
    [18, 0, 6, 8, 10, 0, 19, 0, 8, 15]
]

workers = {'A', 'B', 'C'}

tasks = set(range(1, 11))

c = {
    ('A', 2): 7,
    ('A', 3): 3,
    ('A', 6): 18,
    ('A', 7): 13,
    ('A', 8): 6,
    ('A', 10): 9,
    ('B', 1): 12,
    ('B', 2): 5,
    ('B', 4): 12,
    ('B', 5): 4,
    ('B', 6): 22,
    ('B', 8): 17,
    ('B', 9): 13,
    ('C', 1): 18,
    ('C', 3): 6,
    ('C', 4): 8,
    ('C', 5): 10,
    ('C', 7): 19,
    ('C', 9): 8,
    ('C', 10): 15,
}

max_hours = 40

model = pe.ConcreteModel()

model.workers = pe.Set(initialize = workers)
model.tasks = pe.Set(initialize = tasks)

model.c = pe.Param(model.workers, model.tasks, initialize = c, default = 1000)
model.max_hours = pe.Param(initialize = max_hours)

model.x = pe.Var(model.workers, model.tasks, domain = pe.Reals, bounds = (0,1))

expr = sum(model.c[w, t] * model.x[w, t]
            for w in model.workers for t in model.tasks)
model.objective = pe.Objective(sense = pe.minimize, expr = expr)

model.tasks_done = pe.ConstraintList()
for t in model.tasks:
    lhs = sum(model.x[w, t] for w in model.workers)
    rhs = 1
    model.tasks_done.add(lhs == rhs)

model.hour_limit = pe.ConstraintList()
for w in model.workers:
    lhs = sum(model.c[w, t] * model.x[w, t] for t in model.tasks)
    rhs = model.max_hours
    model.hour_limit.add(lhs <= rhs)

solver = po.SolverFactory('glpk')
results = solver.solve(model, tee = True)

df = pd.DataFrame(index = pd.MultiIndex.from_tuples(model.x, names = ['w', 't']))
df['x'] = [pe.value(model.x[key]) for key in df.index]
df['c'] = [model.c[key] for key in df.index]
print((df['c'] * df['x']).unstack('t'))
print((df['c'] * df['x']).groupby('w').sum().to_frame())
print(df['x'].groupby('t').sum().to_frame().T)
