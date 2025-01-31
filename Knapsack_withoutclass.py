from tkinter import * 
from tkinter import messagebox
import pyomo.environ as pe
import pyomo.opt as po

# Συνάρτηση για την επίλυση του Knapsack Problem
def solve_knapsack():
    try:
        # Ανάγνωση δεδομένων από το GUI
        capacity = float(entry_capacity.get())
        values_input = text_values.get("1.0", END).strip()
        weights_input = text_weights.get("1.0", END).strip()

        # Μετατροπή αξιών και βαρών από είσοδο σε λίστες
        values = list(map(float, values_input.split()))
        weights = list(map(float, weights_input.split()))

        # Έλεγχος αν ο αριθμός των αντικειμένων είναι ίδιος
        if len(values) != len(weights):
            raise ValueError("The number of values and weights must be the same.")
        
        num_items = len(values)

        # Δημιουργία μοντέλου Pyomo
        model = pe.ConcreteModel()

        # Σετ αντικειμένων
        model.items = pe.Set(initialize=range(num_items))

        # Μεταβλητές απόφασης (binary): Αν το αντικείμενο i μπει στο σακίδιο
        model.x = pe.Var(model.items, domain=pe.Binary)

        # Συνάρτηση στόχου: Μέγιστη συνολική αξία
        def objective_rule(model):
            return sum(model.x[i] * values[i] for i in model.items)
        
        model.obj = pe.Objective(rule=objective_rule, sense=pe.maximize)

        # Περιορισμός: Το συνολικό βάρος να μην υπερβαίνει τη χωρητικότητα
        def weight_constraint_rule(model):
            return sum(model.x[i] * weights[i] for i in model.items) <= capacity
        
        model.weight_constraint = pe.Constraint(rule=weight_constraint_rule)

        # Επίλυση
        solver = po.SolverFactory('glpk')
        result = solver.solve(model, tee=True)

        # Ανάγνωση αποτελεσμάτων
        selected_items = []
        total_value = pe.value(model.obj)
        for i in model.items:
            if pe.value(model.x[i]) == 1:
                selected_items.append(f"Item {i+1} (Value: {values[i]}, Weight: {weights[i]})")

        # Εμφάνιση αποτελεσμάτων
        result_text = f"Total Value: {total_value}\nSelected Items:\n" + "\n".join(selected_items)
        messagebox.showinfo("Results", result_text)

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Δημιουργία GUI με Tkinter
root = Tk()
root.title("Knapsack Problem Solver")

# Ετικέτες και πεδία εισόδου
Label(root, text="Knapsack Capacity:").grid(row=0, column=0, sticky="w")
entry_capacity = Entry(root)
entry_capacity.grid(row=0, column=1)

Label(root, text="Values (space-separated):").grid(row=1, column=0, sticky="nw")
text_values = Text(root, height=5, width=40)
text_values.grid(row=1, column=1)

Label(root, text="Weights (space-separated):").grid(row=2, column=0, sticky="nw")
text_weights = Text(root, height=5, width=40)
text_weights.grid(row=2, column=1)

# Κουμπί επίλυσης
solve_button = Button(root, text="Solve the problem", command=solve_knapsack)
solve_button.grid(row=3, column=0, columnspan=2)

# Εκκίνηση του Tkinter loop
root.mainloop()
