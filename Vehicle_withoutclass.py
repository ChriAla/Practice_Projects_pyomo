from tkinter import *
from tkinter import messagebox
import pyomo.environ as pe
import pyomo.opt as po

# Συνάρτηση για την επίλυση του VRP
def solve_vrp():
    try:
        # Ανάγνωση δεδομένων από το GUI
        num_customers = int(entry_num_customers.get())
        num_vehicles = int(entry_num_vehicles.get())
        capacity = int(entry_vehicle_capacity.get())
        demand_input = text_demand.get("1.0", END).strip()
        cost_input = text_costs.get("1.0", END).strip()

        # Μετατροπή δεδομένων
        demands = list(map(int, demand_input.split()))
        costs = [
            list(map(float, row.split()))
            for row in cost_input.split("\n") if row.strip()
        ]

        # Έλεγχος δεδομένων
        if len(demands) != num_customers or len(costs) != num_customers + 1 or any(len(row) != num_customers + 1 for row in costs):
            raise ValueError("The demand vector or cost matrix is not correctly formatted.")

        # Δημιουργία μοντέλου Pyomo
        model = pe.ConcreteModel()

        # Σετ πελατών και κόμβων (πελάτες + αποθήκη)
        model.customers = pe.Set(initialize=range(1, num_customers + 1))
        model.nodes = pe.Set(initialize=range(num_customers + 1))  # 0 = αποθήκη
        model.vehicles = pe.Set(initialize=range(num_vehicles))

        # Μεταβλητές απόφασης
        model.x = pe.Var(model.nodes, model.nodes, model.vehicles, domain=pe.Binary)  # Αν το όχημα k πάει από i σε j
        model.load = pe.Var(model.nodes, domain=pe.NonNegativeReals)  # Φορτίο που μεταφέρει το όχημα στο κόμβο i

        # Συνάρτηση στόχου: Ελαχιστοποίηση κόστους
        def objective_rule(model):
            return sum(model.x[i, j, k] * costs[i][j] for i in model.nodes for j in model.nodes for k in model.vehicles if i != j)

        model.obj = pe.Objective(rule=objective_rule, sense=pe.minimize)

        # Περιορισμός: Κάθε πελάτης εξυπηρετείται ακριβώς μία φορά
        def visit_customer_rule(model, j):
            return sum(model.x[i, j, k] for i in model.nodes if i != j for k in model.vehicles) == 1

        model.visit_constraints = pe.Constraint(model.customers, rule=visit_customer_rule)

        # Περιορισμός: Ροή οχημάτων (αρχή και τέλος στην αποθήκη)
        def flow_balance_rule(model, i, k):
            if i == 0:  # Αποθήκη
                return sum(model.x[0, j, k] for j in model.customers) == 1
            elif i in model.customers:
                return sum(model.x[i, j, k] for j in model.nodes if i != j) == sum(
                    model.x[j, i, k] for j in model.nodes if i != j
                )
            else:
                return pe.Constraint.Skip

        model.flow_constraints = pe.Constraint(model.nodes, model.vehicles, rule=flow_balance_rule)

        # Περιορισμός: Χωρητικότητα οχημάτων
        def capacity_rule(model, j, k):
            return model.load[j] >= demands[j - 1] if j > 0 else pe.Constraint.Skip

        model.capacity_constraints = pe.Constraint(model.nodes, model.vehicles, rule=capacity_rule)

        # Επίλυση
        solver = po.SolverFactory('glpk')
        result = solver.solve(model, tee=True)

        # Ανάγνωση αποτελεσμάτων
        routes = []
        total_cost = pe.value(model.obj)
        for k in model.vehicles:
            route = []
            for i in model.nodes:
                for j in model.nodes:
                    if i != j and pe.value(model.x[i, j, k]) == 1:
                        route.append((i, j))
            if route:
                routes.append(f"Vehicle {k+1}: " + " -> ".join(f"{i}->{j}" for i, j in route))

        # Εμφάνιση αποτελεσμάτων
        result_text = f"Total Cost: {total_cost}\n\nRoutes:\n" + "\n".join(routes)
        messagebox.showinfo("Results", result_text)

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Δημιουργία GUI με Tkinter
root = Tk()
root.title("Vehicle Routing Problem Solver")

# Ετικέτες και πεδία εισόδου
Label(root, text="Number of Customers:").grid(row=0, column=0, sticky="w")
entry_num_customers = Entry(root)
entry_num_customers.grid(row=0, column=1)

Label(root, text="Number of Vehicles:").grid(row=1, column=0, sticky="w")
entry_num_vehicles = Entry(root)
entry_num_vehicles.grid(row=1, column=1)

Label(root, text="Vehicle Capacity:").grid(row=2, column=0, sticky="w")
entry_vehicle_capacity = Entry(root)
entry_vehicle_capacity.grid(row=2, column=1)

Label(root, text="Demand per Customer (space-separated):").grid(row=3, column=0, sticky="nw")
text_demand = Text(root, height=5, width=40)
text_demand.grid(row=3, column=1)

Label(root, text="Cost Matrix (space-separated rows):").grid(row=4, column=0, sticky="nw")
text_costs = Text(root, height=10, width=40)
text_costs.grid(row=4, column=1)

# Κουμπί επίλυσης
solve_button = Button(root, text="Solve the problem", command=solve_vrp)
solve_button.grid(row=5, column=0, columnspan=2)

# Εκκίνηση του Tkinter loop
root.mainloop()
