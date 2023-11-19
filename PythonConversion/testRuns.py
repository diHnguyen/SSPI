#Imports for main 
import numpy as np
import pandas as pd
import importlib
import gurobipy as gp
from gurobipy import GRB

exec(open('testInstance.py').read())
importlib.import_module("functionGbound")
from functionGbound import gx_bound
importlib.import_module("functionHbound")
from functionHbound import hx_bound
importlib.import_module("functionSelectArc")
from functionSelectArc import selectArc
importlib.import_module("functionArcSplit")
from functionArcSplit import arcSplit
importlib.import_module("functionPartition")
from functionPartition import Partition

#python main.py -> #f1 #a23 as parameters

c_L = cL_orig
c_U = cU_orig
M = M_orig
y = [0,1,0,0,1]
x_now = np.zeros(Len)
newCell = 2
k=1
A1=1
A3=1

# df_constraints = pd.DataFrame({
#     'NUM': [],
#     'CELL': [],
#     'Y': [],
#     'SP': []
# })

# df_cell = pd.DataFrame({
#     'CELL': [],
#     'Y': [],
#     'Y_Lk': [],
#     'g': [],
#     'h': [],
#     'gL': [],
#     'LB': [],
#     'UB': [],
#     'PROB': [],
#     'PI': []
# })
# Calculate c values
c = (cU_orig + cL_orig) / 2

# Call the gx_bound function (assuming you have it defined elsewhere)
yy, SP_init, SP_init, T, pred, label, path = gx_bound(c, c, edge, origin,destination)


# Create and append rows to the DataFrames
new_row = {
    'CELL': [1],
    'Y': [[yy]],
    'Y_Lk': [[yy]],
    'g': [SP_init],
    'h': [0],
    'gL': [0],
    'LB': [[cL_orig]],
    'UB': [[cU_orig]],
    'PROB': [1],
    'PI': [[label]]
}
df_cell = pd.DataFrame(new_row)
new_row = {
    'NUM': [1],
    'CELL': [1],
    'Y': [[yy]],
    'SP': [SP_init]
}
df_constraints = pd.DataFrame(new_row)
# df_cell = pd.concat([df_cell, pd.Series({
#     'CELL': 1,
#     'Y': [yy],
#     'Y_Lk': [yy],
#     'g': SP_init,
#     'h': 0,
#     'gL': 0,
#     'LB': [cL_orig],
#     'UB': [cU_orig],
#     'PROB': 1,
#     'PI': [label]
# })], axis=0)

# df_constraints = df_constraints.append({
#     'NUM': 1,
#     'CELL': 1,
#     'Y': [yy],
#     'SP': SP_init
# }, ignore_index=True)

# Create a new Gurobi model
MP_obj = 0.0
zNum = 200000
cRefNum = 2000000

m = gp.Model()
x = m.addVars(range(Len), vtype=GRB.BINARY, name="x")
z = m.addVars(range(zNum), lb=0, ub=1e6, name="z")

# Constraint: Sum of x[i] equals b
m.addConstr(x.sum() == b, "sum_x_equals_b")

# Constraint: z[1] <= SP_init + sum(yy[i]*x[i]*d[i] for i in range(1, Len + 1))
m.addConstr(z[1] <= SP_init + sum(yy[i]*x[i]*d[i] for i in range(Len)))
# m.addConstr(z[1] <= SP_init + x.prod(yy[i] * d[i] for i in range(1, Len + 1)), "z_constraint_1")

# Objective: Maximize sum(p[i]*z[i])
m.setObjective(z.prod(p), GRB.MAXIMIZE)

import numpy as np

# Initialize global variables
x_sol = []
α_sol = 0
z_sol = []
x_now = []
α_now = 0
z_now = []
last_x = np.zeros(Len)
con_num = 1
newCell = 1
total_time = 0.0
iter = 0
K_bar = [1]
LB = 0
LB_w = 0
MP_obj = 1e6
K_newly_added = []
K_removed = []

start = time()
terminate_cond = False

while not terminate_cond:
    # α, iter, total_time, K_bar, K_newly_added, K_removed, LB, MP_obj, con_num, newCell, LB_w, p, \
    # x_sol, z_sol, α_sol, last_x, x_now, α_now, z_now, terminate_cond, start, set, Ins, density, dataset = \
    #     (global variable values here)

    while K_bar:
        iter += 1
        m.optimize()
        
        if termination_status(m) == MOI.OPTIMAL:
            MP_obj = m.ObjVal
            x_now = m.getAttr('x', vars)
            z_now = m.getAttr('z', vars)
            print("\nIter : ", iter, " ; MP_obj = ", MP_obj, " ; time ", time() - start, "; ", len(K_bar), "/", newCell)
            print("x = ", np.where(x_now > 0)[0])

        O1Flag = True
        O1Flag, K_bar,constr = checkO1Flag(O1Flag,last_x,x_now,k,z_now,constr)

        if O1Flag:
            partitionCounter = 1
            myCounter = 0
            while myCounter < partitionCounter:
                myCounter += 1
                for k in K_bar:
                    c_L, c_U, M, c, c_g_L, yK = getCellInfo(k, x_now, "c_g_L")
                    yL, gL, SPL = gx_bound(c, c_g_L, edge)
                    df_cell.at[k, 'Y_Lk'] = yL
                    df_cell.at[k, 'gL'] = gL

                    y_h, hx = hx_bound(c_L, c_U, d, x_now)
                    p_k = df_cell.at[k, 'PROB']
                    df_cell.at[k, 'h'] = hx
                    gx = df_cell.at[k, 'g']

                    if gx - hx <= delta2:
                        K_removed.append(k)
                    else:
                        newCell += 1
                        ΔL, ΔU, arc_split, yL, yU, gL, gU, SP_L, SP_U = Partition(x_now, newCell, k, p_k, c_L, c_U, M, df_cell.at[k, 'Y'])
                        df_temp_k = df_constraints[df_constraints['CELL'] == k]
                        add_yL = True
                        add_yU = True

                        for _, dfRow in df_temp_k.iterrows():
                            Y_k = np.array(dfRow['Y'])
                            if np.array_equal(Y_k, yL):
                                add_yL = False
                            if np.array_equal(Y_k, yU):
                                add_yU = False

                            newCell_RHS = dfRow['SP']

                            if Y_k[arc_split - 1] == 1:
                                conRef = dfRow['NUM']
                                newCell_RHS = newCell_RHS + ΔU
                                dfRow['SP'] = dfRow['SP'] - ΔL
                                df_constraints.at[conRef - 1, 'SP'] = dfRow['SP']
                                set_normalized_rhs(constr[conRef], dfRow['SP'])

                            con_num += 1
                            m.addConstr(z[newCell] <= sum(d[i] * x[i] * Y_k[i - 1] for i in range(Len)) + newCell_RHS)
                            # constr[con_num] = @constraint(m, z[newCell] <= sum(d[i] * x[i] * Y_k[i - 1] for i in range(1, Len + 1)) + newCell_RHS)
                            df_constraints.loc[con_num - 1] = [con_num, newCell, Y_k.tolist(), newCell_RHS]

                        if add_yL:
                            con_num += 1
                            m.addConstr(z[k] <= sum(d[i] * x[i] * YL[i] for i in range(Len)) + SP_L)
                            # constr[con_num] = @constraint(m, z[k] <= sum(d[i] * x[i] * yL[i - 1] for i in range(1, Len + 1)) + SP_L)
                            df_constraints.loc[con_num - 1] = [con_num, k, yL.tolist(), SP_L]
                        if add_yU:
                            con_num += 1
                            m.addConstr(z[newCell] <= sum(d[i] * x[i] * YU[i] for i in range(Len)) + SP_U)
                            # constr[con_num] = @constraint(m, z[newCell] <= sum(d[i] * x[i] * yU[i - 1] for i in range(1, Len + 1)) + SP_U)
                            df_constraints.loc[con_num - 1] = [con_num, newCell, yU.tolist(), SP_U]

                p = df_cell['PROB'].tolist()
                @objective(m, Max, sum(p[i] * z[i] for i in range(1, len(p) + 1)))

                K_bar = list(set(K_bar) - set(K_removed))
                K_bar.extend(K_newly_added)
                K_newly_added = []
                K_removed = []

                if not K_bar:
                    myCounter = partitionCounter
                    terminate_cond = True

        total_time = time() - start
        h_val = df_cell['h']
        p_val = df_cell['PROB']
        LB = sum(h_val[k] * p_val[k] for k in range(1, newCell + 1))

        oeFile = open(f"./PrelimOutputFile/OEFiles/OE_Alg_{set}_{dataSet}_{Ins}.txt", "a")
        print(oeFile, f"{dataSet}; Ins {Ins}; Time {total_time}; MP_obj {MP_obj}; LB {LB}; x_now {np.where(x_now == 1)[0]}; Cells {len(K_bar)}/{newCell}; Iter {iter}")
        oeFile.close()

# Optimize the model
m.optimize()

print(df_cell)
K_newly_added = [1]
ΔL, ΔU, arc_split, yL, yU, gL, gU, SP_L, SP_U = Partition(x_now, newCell, k, p, c_L, c_U, M, y,d,edge,origin,destination,Len,A1,A3,df_cell,K_newly_added)
########functionArcSplit.py########
# c_L = cL_orig
# c_U = cU_orig
# M = M_orig
# y = [0,1,0,0,1]
# x_now = np.zeros(Len)
# k=1
# label = [ 0., 10., 11., 12.,  0.]
# A3=0
# arc_split = 3
# ΔL, ΔU = arcSplit(x_now, arc_split, k, c_L, c_U, M, y, label,edge,origin,destination,d,Len,A3)
# print(ΔL," ", ΔU)
########################################
########functionSelectArc.py########
# c_L = cL_orig
# c_U = cU_orig
# M = M_orig
# y = [0,1,0,0,1]
# x_now = np.zeros(Len)
# A1 = 0
# arc_split = selectArc(x_now, c_L, c_U, M, y,d,edge,origin,destination,A1)
# print(arc_split)
################################
########functionHbound.py########
# c_L = cL_orig
# c_U = cU_orig
# x_now = np.zeros(Len)
# y2_values, hx = hx_bound(c_L, c_U, d, x_now, edge,origin,destination)
# print("hx = ", hx)
# print("y2 = ", y2_values)
########functionGbound.py########

########functionGbound.py########
# y, gx, SP, T, pred, label, path = gx_bound(c_orig, c_orig, edge, origin,destination)
# print("y = ", y)
# print("gx = ", gx)
# print("SP = ", SP)
# print("T = ", T)
# print("pred = ", pred)
# print("label = ", label)
# print("path = ", path)
################################