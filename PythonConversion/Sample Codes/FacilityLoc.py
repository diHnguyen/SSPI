import gurobipy as gp
from gurobipy import GRB

def create_model():
    # Create a Gurobi model
    model = gp.Model("example_model")

    # Create decision variables
    x = model.addVar(name="x", lb=0.0)
    y = model.addVar(name="y", lb=0.0)

    # Set objective function: Maximize 3x + 2y
    model.setObjective(3 * x + 2 * y, sense=GRB.MAXIMIZE)

    # Add constraints
    constraint1 = model.addConstr(2 * x + y <= 20, "constraint1")
    model.addConstr(4 * x - 5 * y >= -10, "constraint2")

    return model, x, y, constraint1

def modify_and_reoptimize(model, constraint1):
    # Modify constraint1 (e.g., change RHS)
    constraint1.setAttr(GRB.Attr.RHS, 25)

    # Reoptimize the model
    model.optimize()

    # Check optimization status after modification and reoptimization
    if model.status == GRB.OPTIMAL:
        optimal_x = model.getVarByName("x").x
        optimal_y = model.getVarByName("y").x

        print("Optimal solution after modification:")
        print(f"x = {optimal_x}, y = {optimal_y}")
        print(f"Optimal objective value: {model.objVal}")
    else:
        print("Optimization did not converge after modification")

def optimize_and_print(model, x, y, constraint1):
    # Optimize the model
    model.optimize()

    # Check optimization status
    if model.status == GRB.OPTIMAL:
        optimal_x = x.x
        optimal_y = y.x

        print("Optimal solution found before modification:")
        print(f"x = {optimal_x}, y = {optimal_y}")
        print(f"Optimal objective value: {model.objVal}")

        # Call the function to modify and reoptimize
        modify_and_reoptimize(model, constraint1)

# Main part of the code
my_model, my_x, my_y, my_constraint1 = create_model()  # Create the model and get variables

# Pass the model, variables, and constraint to a function for optimization
optimize_and_print(my_model, my_x, my_y, my_constraint1)

# Dispose of the model when you're done
my_model.dispose()
