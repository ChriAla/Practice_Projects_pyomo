from tkinter import *
from tkinter import messagebox
import pyomo.environ as pe
import pyomo.opt as po

# Συνάρτηση για την επίλυση του Facility Location Problem
def solve_facility_location():
    try:
        # Ανάγνωση δεδομένων από το GUI
        num_facilities = int(entry_num_facilities.get())
        num_clients = int(entry_num_clients.get())
        facility_costs_input = text_facility_costs.get("1.0", END).strip()
        transport_costs_input = text_transport_costs.get("1.0", END).strip()

        # Μετατροπή δεδομένων
        facility_costs = list(map(float, facility_costs_input.split()))
        transport_costs = [
            list(map(float, row.split()))
            for row in transport_costs_input.split("\n") if row.strip()
        ]

        # Έλεγχος για ορθότητα δεδομένων
        if len(facility_costs) != num_facilities:
            raise ValueError("The number of facility costs must match the number of facilities.")
        if len(transport_costs) != num_facilities or any(len(row) != num_clients for row in transport_costs):
            raise ValueError("The transport cost table is not configured correctly.")
        
        # Δημιουργία μοντέλου Pyomo
        model = pe.ConcreteModel()

        # Σετ εγκαταστάσεων και πελατών
        model.facilities = pe.Set(initialize=range(num_facilities))
        model.clients = pe.Set(initialize=range(num_clients))

        # Μεταβλητές απόφασης
        model.y = pe.Var(model.facilities, domain=pe.Binary)  # Εγκατάσταση (1 αν ανοίξει η εγκατάσταση)
        model.x = pe.Var(model.facilities, model.clients, domain=pe.Binary)  # Αντιστοίχιση πελατών σε εγκαταστάσεις

        # Συνάρτηση στόχου: Ελαχιστοποίηση κόστους
        def objective_rule(model):
            facility_cost = sum(model.y[f] * facility_costs[f] for f in model.facilities)
            transport_cost = sum(model.x[f, c] * transport_costs[f][c] for f in model.facilities for c in model.clients)
            return facility_cost + transport_cost
        
        model.obj = pe.Objective(rule=objective_rule, sense=pe.minimize)

        # Περιορισμός: Κάθε πελάτης εξυπηρετείται από μία εγκατάσταση
        def client_constraint_rule(model, c):
            return sum(model.x[f, c] for f in model.facilities) == 1
        
        model.client_constraints = pe.Constraint(model.clients, rule=client_constraint_rule)

        # Περιορισμός: Ένας πελάτης μπορεί να εξυπηρετηθεί μόνο από ανοιχτή εγκατάσταση
        def facility_constraint_rule(model, f, c):
            return model.x[f, c] <= model.y[f]
        
        model.facility_constraints = pe.Constraint(model.facilities, model.clients, rule=facility_constraint_rule)

        # Επίλυση
        solver = po.SolverFactory('glpk')
        result = solver.solve(model, tee=True)

        # Ανάγνωση αποτελεσμάτων
        opened_facilities = []
        client_assignments = []
        total_cost = pe.value(model.obj)

        for f in model.facilities:
            if pe.value(model.y[f]) == 1:
                opened_facilities.append(f"Facility {f+1}")

        for c in model.clients:
            for f in model.facilities:
                if pe.value(model.x[f, c]) == 1:
                    client_assignments.append(f"Client {c+1} -> Facility {f+1}")

        # Εμφάνιση αποτελεσμάτων
        result_text = f"Total Cost: {total_cost}\n\nOpened Facilities:\n" + "\n".join(opened_facilities) + \
                      "\n\nClient Assignments:\n" + "\n".join(client_assignments)
        messagebox.showinfo("Results", result_text)

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Δημιουργία GUI με Tkinter
root = Tk()
root.title("Facility Location Problem Solver")

# Ετικέτες και πεδία εισόδου
Label(root, text="Number of Facilities:").grid(row=0, column=0, sticky="w")
entry_num_facilities = Entry(root)
entry_num_facilities.grid(row=0, column=1)

Label(root, text="Number of Clients:").grid(row=1, column=0, sticky="w")
entry_num_clients = Entry(root)
entry_num_clients.grid(row=1, column=1)

Label(root, text="Facility Opening Costs (space-separated):").grid(row=2, column=0, sticky="nw")
text_facility_costs = Text(root, height=5, width=40)
text_facility_costs.grid(row=2, column=1)

Label(root, text="Transport Costs (space-separated rows):").grid(row=3, column=0, sticky="nw")
text_transport_costs = Text(root, height=10, width=40)
text_transport_costs.grid(row=3, column=1)

# Κουμπί επίλυσης
solve_button = Button(root, text="Solve the problem", command=solve_facility_location)
solve_button.grid(row=4, column=0, columnspan=2)

# Εκκίνηση του Tkinter loop
root.mainloop()
