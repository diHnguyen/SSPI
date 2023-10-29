import gurobipy as gp
import networkx as nx
import pandas as pd
from datetime import datetime

myRun = datetime.now().strftime("%H:%M:%S")
gurobi_env = gp.Env()

# Define your global variables as needed
edge = None
cL_orig = None
cU_orig = None
Len = None
c_orig = None
yy = None
SP_init = None
p = None
g = None
h = None
origin = None
destination = None
last_node = None
all_nodes = None
M_orig = None
delta1 = None
delta2 = None
b = None
last_node = None

numNodes = str(ARGS[1])  # Replace ARGS[1] with your desired argument values
density = str(ARGS[2])
Ins = str(ARGS[3])
dataSet = "N" + numNodes + "_d" + density

myFile = "./PrelimTestInstances/" + dataSet + "/" + dataSet + "_Ins_" + Ins + ".jl"
print("Ins", dataSet, "_", Ins, " Running...", myRun)

# Include your Julia files as needed
# You can translate the include statements into Python scripts as required.

epsilon = 1e-4
gurobi_env.setParam("OutputFlag", 0)
