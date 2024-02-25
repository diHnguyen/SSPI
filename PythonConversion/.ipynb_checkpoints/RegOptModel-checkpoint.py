from itertools import product
from math import sqrt

import gurobipy as gp
from gurobipy import GRB

# tested with Gurobi v9.1.0 and Python 3.7.0

# Parameters
customers = [(0,1.5), (2.5,1.2)]
facilities = [(0,0), (0,1), (0,2), (1,0), (1,1), (1,2), (2,0), (2,1), (2,2)]
setup_cost = [3,2,3,1,3,3,4,3,2]
cost_per_mile = 1

# This function determines the Euclidean distance between a facility and customer sites.

def compute_distance(loc1, loc2):
    dx = loc1[0] - loc2[0]
    dy = loc1[1] - loc2[1]
    return sqrt(dx*dx + dy*dy)

# Compute key parameters of MIP model formulation

num_facilities = len(facilities)
num_customers = len(customers)
cartesian_prod = list(product(range(num_customers), range(num_facilities)))

# Compute shipping costs

shipping_cost = {(c,f): cost_per_mile*compute_distance(customers[c], facilities[f]) for c, f in cartesian_prod}

# MIP  model formulation

m = gp.Model('facility_location')

select = m.addVars(num_facilities, vtype=GRB.BINARY, name='Select')
assign = m.addVars(cartesian_prod, ub=1, vtype=GRB.CONTINUOUS, name='Assign')

Setup2ship = {}
for c,f in cartesian_prod:
    Setup2ship[c,f] = m.addConstr(assign[(c,f)] <= select[f])

Demand = {}
for c in range(num_customers):
    Demand[c] = m.addConstr(gp.quicksum(assign[(c,f)] for f in range(num_facilities)) == 1)

m.setObjective(select.prod(setup_cost)+assign.prod(shipping_cost), GRB.MINIMIZE)

# c0 = m.getConstrByName('Setup2ship')
# row = m.getRow(c0)
# for i in range(row.size()):
#     print("variable %s, coefficient=%f" % (row.getVar(i).VarName, row.getCoeff(i)))

# Demand[1].rhs = 10
def test1(Demand):
    Demand[1].setAttr(GRB.Attr.RHS, 10)
    
test1
#Check Setup2ship.add
# Setup2ship[2,0] = m.addConstr(assign[0,0] + assign[0,1] <= 10, name='Setup2ship')

# Setup2ship[0,0].rhs = 2
print("Demand ", Demand)
m.optimize()

print (m.display())

# m.write("out.mst")
# m.write("out.sol")

# Dispose of the model to free resources
m.dispose()