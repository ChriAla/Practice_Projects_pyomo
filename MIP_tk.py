from tkinter import *
from tkinter import messagebox
import pyomo.environ as pe
import pyomo.opt as po


def solve_mip():
    try:
        # Ανάγνωση εισόδων από το GUI
        objective_input = text_objective.get("1.0", END).strip()
        constraints_input = text_constraints.get("1.0", END).strip()
        var_types_input = text_var_types.get("1.0", END).strip()

        # Επεξεργασία συνάρτησης στόχου
        objective = list(map(float, objective_input.split()))
        
        # Επεξεργασία περιορισμών
        constraints = []
        for line in constraints_input.split("\n"):
            if line.strip():
                parts = line.split(",")
                lhs = list(map(float, parts[0].split()))
                sense = parts[1].strip()
                rhs = float(parts[2].strip())
                constraints.append((lhs, sense, rhs))
        
        # Επεξεργασία τύπων μεταβλητών
        var_types = var_types_input.split()

        # Δημιουργία του μοντέλου Pyomo
        model = pe.ConcreteModel()

        # Δημιουργία μεταβλητών
        model.vars = pe.Var(range(len(var_types)), domain=pe.Reals)
        for i, var_type in enumerate(var_types):
            if var_type == 'binary':
                model.vars[i].domain = pe.Binary
            elif var_type == 'integer':
                model.vars[i].domain = pe.Integers

        # Προσθήκη συνάρτησης στόχου
        model.obj = pe.Objective(
            expr=sum(objective[i] * model.vars[i] for i in range(len(objective))),
            sense=pe.minimize,
        )

        # Προσθήκη περιορισμών
        model.constraints = pe.ConstraintList()
        for lhs, sense, rhs in constraints:
            if sense == '<=':
                model.constraints.add(sum(lhs[i] * model.vars[i] for i in range(len(lhs))) <= rhs)
            elif sense == '>=':
                model.constraints.add(sum(lhs[i] * model.vars[i] for i in range(len(lhs))) >= rhs)
            elif sense == '==':
                model.constraints.add(sum(lhs[i] * model.vars[i] for i in range(len(lhs))) == rhs)

        # Επίλυση
        solver = po.SolverFactory('glpk')
        result = solver.solve(model)

        # Ανάγνωση αποτελεσμάτων
        if result.solver.termination_condition == pe.TerminationCondition.optimal:
            solution = {f"x{i}": pe.value(var) for i, var in enumerate(model.vars.values())}
            total_cost = pe.value(model.obj)
            result_text = f"Optimal Solution Found!\n\nObjective Value: {total_cost}\nVariables:\n"
            result_text += "\n".join([f"{var} = {value}" for var, value in solution.items()])
            messagebox.showinfo("Results", result_text)
        else:
            messagebox.showerror("Error", "No optimal solution found.")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")


# Δημιουργία GUI με Tkinter
root = Tk()
root.title("MIP Solver")

# Ετικέτες και πεδία εισόδου
Label(root, text="Objective Function (space-separated coefficients):").grid(row=0, column=0, sticky="w")
text_objective = Text(root, height=2, width=50)
text_objective.grid(row=1, column=0, padx=10, pady=5)

Label(root, text="Constraints (one per line, format: coefficients,sense,rhs):").grid(row=2, column=0, sticky="w")
text_constraints = Text(root, height=10, width=50)
text_constraints.grid(row=3, column=0, padx=10, pady=5)

Label(root, text="Variable Types (space-separated, e.g., continuous binary integer):").grid(row=4, column=0, sticky="w")
text_var_types = Text(root, height=2, width=50)
text_var_types.grid(row=5, column=0, padx=10, pady=5)

# Κουμπί επίλυσης
solve_button = Button(root, text="Solve MIP Problem", command=solve_mip)
solve_button.grid(row=6, column=0, pady=10)

# Εκκίνηση της εφαρμογής
root.mainloop()
