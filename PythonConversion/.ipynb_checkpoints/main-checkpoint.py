#Flow:
import gurobipy as gp

# #Load instance given parameters
# A1 = 0  # 1=Select arc having the largest uncertainty , 0=Select arc using Lemma2
# A2 = 1  # 1=Partition once per cell , 0=Partition multiple per cell
# A3 = 1  # 1=Split at mean base cost , 0=Split using SA if possible
# A4 = 1  # 1=Frequent solve MP
# # If running A5 = 0, do not use this file, use LazyAlg.jl instead
# # FIXED IN THIS FILE
A5 = 1  # 1=Regular opt model
# set_var = str(A1) + str(A2) + str(A3) + str(A4) + str(A5)
# # Assuming you have a file "functionLoadSharedFiles.py" with the required functions
# exec(open("functionLoadSharedFiles.py").read())

if A5==1: #Solve a regular optimization model
    exec(open("RegOptModel.py").read())
else: #Solve a lazy model
    exec(open("LazyConstraintModel.py").read())


# Create a new Gurobi model
model = gp.Model()

# Parameters
supply = [20, 30, 25]  # Supply at each source
demand = [10, 15, 25]  # Demand at each destination
cost = [[2, 4, 5],    # Cost to transport from source i to destination j
        [3, 2, 6],
        [7, 8, 3]]

# Variables
num_sources = len(supply)
num_destinations = len(demand)
x = {}
for i in range(num_sources):
    for j in range(num_destinations):
        x[i, j] = model.addVar(vtype=gp.GRB.INTEGER, name=f'x_{i}_{j}')

# Objective function
model.setObjective(gp.quicksum(cost[i][j] * x[i, j] for i in range(num_sources) for j in range(num_destinations)), sense=gp.GRB.MINIMIZE)

# Supply constraints
for i in range(num_sources):
    model.addConstr(gp.quicksum(x[i, j] for j in range(num_destinations)) == supply[i], name=f'supply_{i}')

# Demand constraints
for j in range(num_destinations):
    model.addConstr(gp.quicksum(x[i, j] for i in range(num_sources)) == demand[j], name=f'demand_{j}')

# Solve the model
model.optimize()

if model.status == gp.GRB.OPTIMAL:
    print("Optimal solution found!")
    for i in range(num_sources):
        for j in range(num_destinations):
            print(f"x_{i}_{j} = {x[i, j].x}")
    print(f"Total cost: {model.objVal}")
else:
    print("No solution found")

# Dispose of the model to free resources
model.dispose()