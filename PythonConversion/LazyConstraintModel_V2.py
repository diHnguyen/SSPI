#This version only solves the shortest-path problem if we cannot find a violating (aggr) cut
# P = P1, P2, P3
# K = {k1, k2}
# P1 -- cost
# P2 -- cost
# P3 -- cost
# Pick smallest cost among paths -- per cell k
# E.g., k1 gets P2 as shortest path, k2 has P3 as shortest path --> Check if aggr cut btwn P1 and P2 violates z 
# If yes -- add cut (Phase 1)
# ---- Repeat Phase 1 as long as possible
# If no -- find new shortest path (Phase 2)



#Imports for main 
import numpy as np
import pandas as pd
pd.set_option('display.max_columns', 500)
import importlib
import time
import gurobipy as gp
from gurobipy import GRB
import sys
import math
# from itertools import combinations


# exec(open('./testInstance.py').read())
runningTest = False
printIters = True
# exec(open('testInstance.py').read())
# collect_output = True #if True, will write output to file.

importlib.import_module("functionProcessInputFile")
from functionProcessInputFile import processInputFile
testSet = "N"+sys.argv[1]
ins = int(sys.argv[2])
density = sys.argv[3]
directory = "./"
#directory = "./Output/INOC2024/"
Len, origin, destination, edge,d,cL_orig, cU_orig = processInputFile(testSet, ins, density)
# print("cL_orig ", cL_orig)
# print(cU_orig - cL_orig)
c_orig = 0.5*(cL_orig+cU_orig)
# last_node = maximum(edge)
# all_nodes = collect(1:last_node)
# M_orig = zeros(Len)
# for i = 1:Len
p = [1.0]
M_orig = cU_orig - cL_orig
delta1 = 1/10000#0.5/100 #Old: 1.0
delta2 = 1/100 #Old: 2.0
# b = 7
b=10
print(d)

# Getting args from command line: int(sys.argv[1])
#h-bound model: 
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
# importlib.import_module("functionCheckO1Flag_lazy")
# from functionCheckO1Flag import checkO1Flag
importlib.import_module("functionCheckO1Flag_lazy_perc_mainSingleCut")
from functionCheckO1Flag_lazy_perc_mainSingleCut import checkO1Flag
importlib.import_module("functionGetCellInfo")
from functionGetCellInfo import getCellInfo
importlib.import_module("functionCalcHBoundAfterPartition")
from functionCalcHBoundAfterPartition import calcHBoundAfterPartition

#python main.py -> #f1 #a23 as parameters
# c_L = cL_orig
# c_U = cU_orig
# M = M_orig
# y = [0,1,0,0,1]
# x_now = np.zeros(Len)
# newCell = 2
k=1
A1=0
A3=1

# Calculate c values
c = (cU_orig + cL_orig) / 2

# Call the gx_bound function (assuming you have it defined elsewhere)
yy, SP_init, SP_init, label, path = gx_bound(c, c, edge, origin,destination)

# Create and append rows to the DataFrames
new_row = {
    'CELL': [0],
    'Y': [np.array(yy)],
    'Y_Lk': [np.array(yy)],
    'g': [SP_init],
    'h': [0],
    'gL': [0],
    'LB': [cL_orig],
    'UB': [cU_orig],
    'PROB': [1],
    'PI': [np.array(label)]
}

# Define data types for each column
dtypes = {
    'CELL': int,
    'Y': object,
    'Y_Lk': object,  # Assuming 'Y' contains arrays
    'g': float,
    'h': float,
    'gL': float,
    'LB': object,
    'UB': object,
    'PROB': float,
    'PI': object
}
# df_cell = pd.DataFrame(new_row)
df_cell = pd.DataFrame(new_row, columns=dtypes.keys()).astype(dtypes)
# print(df_cell)






# Constraint: z[1] <= SP_init + sum(yy[i]*x[i]*d[i] for i in range(1, Len + 1))
# data = {
#     'ID': [1, 2, 3, 4, 5],
#     'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eva'],
#     'Age': [25, 30, 22, 35, 28],
#     'City': ['New York', 'San Francisco', 'Los Angeles', 'Chicago', 'Miami']
# }


# constraints_dict["1"] = {"info":cell1_info, "cons":cell1_constraints}
# m.addConstr(z[1] <= SP_init + x.prod(yy[i] * d[i] for i in range(1, Len + 1)), "z_constraint_1")
newCell = 0
# print("p = ",p)

# Objective: Maximize sum(p[i]*z[i])


import numpy as np

# Initialize global variables
x_sol = []
α_sol = 0
z_sol = []
x_now = []
α_now = 0
z_now = []
last_x = []
con_num = 1

total_time = 0.0
iter = 0
K_bar = [0]
LB = 0
LB_w = 0
MP_obj = 1e6
K_newly_added = []
K_removed = []
P_bar = np.array([yy])
# print(P_bar)
# P_bar = P_bar.append(yy)


# print(P_bar)
start = time.time()
terminate_cond = False
# print("df_cell")
# print(df_cell.g)

def lazy(m, where):
    # while not terminate_cond:
    # if (where == GRB.Callback.MIPNODE):
    #     print("MIPNODE_OBJBND ", m.cbGet(GRB.Callback.MIPNODE_OBJBND))
    #     print("MIPNODE_OBJBST ", m.cbGet(GRB.Callback.MIPNODE_OBJBST))
    if (where == GRB.Callback.MIP):
        print("MIP_OBJBND ", m.cbGet(GRB.Callback.MIP_OBJBND))
        print("MIP_OBJBST ", m.cbGet(GRB.Callback.MIP_OBJBST))

    if (where == GRB.Callback.MIPSOL):
        m._iter += 1
        k = m._k
        last_x = m._last_x
        df_cell = m._df_cell
        K_removed = m._K_removed
        K_bar = m._K_bar
        K_newly_added = m._K_newly_added
        p = m._p
        P_bar = m._P_bar
        newCell = m._newCell
        x_now = np.array(m.cbGetSolution(m._x).values())
        z_now = m.cbGetSolution(m._z)
        con_num = m._con_num
        # MP_obj = m.cbGet(GRB.Callback.MIP_OBJBST) #m.ObjVal
        m._best = m.cbGet(GRB.Callback.MIPSOL_OBJBST)
        print("MIPSOL_OBJBND ", m.cbGet(GRB.Callback.MIPSOL_OBJBND))
        print("MIPSOL_OBJBST ", m.cbGet(GRB.Callback.MIPSOL_OBJBST))
        
        terminate_cond = m._terminate_cond
        # α, iter, total_time, K_bar, K_newly_added, K_removed, LB, MP_obj, con_num, newCell, LB_w, p, \
        # x_sol, z_sol, α_sol, last_x, x_now, α_now, z_now, terminate_cond, start, set, Ins, density, dataset = \
        #     (global variable values here)
        # print("HERE")
        # while (len(K_bar)>0):
            
            # m.write("checkModel.lp")
            # m.optimize()
            # K_bar = []#Remove when done debug 
            # print("STATUS ", m.status)
            # if termination_status(m) == MOI.OPTIMAL:
            # if m.status == 2:
        # MP_obj = m.ObjVal
        # x_now = np.empty(Len) #[0.0]*Len
        # z_now = np.empty(zNum)

        # for i in range(Len):
        #     x_now[i] = x[i].X #m.getAttr('x', x[i].X) #m.getAttr('X', vars)
        # for i in range(zNum):
        #     z_now[i] = z[i].X
        print("\n==========================================================")
        print("Iter : ", m._iter, " ; MP_obj = ", m._MP_obj, " ; time ", time.time() - m._start, "; ", len(m._K_bar), "/", m._newCell+1)
        print("==========================================================")
        x_index = np.where(x_now > 0)[0]
        print("x = ", x_index)
        print("z = ", z_now)
        # print("x = ", np.where(x_now > 0)[0])
        # print("z = ", z_now[0:(newCell+1)])
        # print("p = ", p)
        # print("newCell = ", newCell)
        # print("P_bar = ", P_bar)
        print("g = ", list(df_cell.loc[:,'g']))
        print("h = ", list(df_cell.loc[:,'h']))


        O1Flag = True
        O1Flag, K_bar = checkO1Flag(m,x,z,Len,O1Flag,delta1,newCell,edge,origin,destination,last_x,x_now,d, k,z_now,df_cell, K_bar)

        # O1Flag, K_bar = checkO1Flag(m,x,z,Len,O1Flag,delta1,newCell,edge,origin,destination,last_x,x_now,d, k,z_now,df_cell,df_constraints)
        # print("O1Flag ", O1Flag)
        # print("K_bar ", K_bar)
        # print("last_x " , last_x)
        # print((last_x.shape))
        # print("x_now " , x_now)
        # print((x_now.shape))
        # print(last_x!=x_now)

        print("O1Flag ", O1Flag)
        if (O1Flag == False) or (not np.array_equal(last_x, x_now)):
            recalc_h = True
        h = np.array(df_cell.h)
        
        # if list(last_x) != list(x_now):
        #     print("\nO1Flag")
        #     print("x_now = ", np.where(x_now > 0.5)[0])
        #     K_bar = np.arange(newCell+1) #collect(1:newCell)
        #     print("K_bar ", K_bar)
        #     m._last_x = x_now
        
        # println("K_bar ", K_bar)
            ##Put back the set of constraints as set of shortest paths seen before
            # for k in K_bar #_partition  
            #     c_L = df_cell[k,:LB]#[row] 
            #     c_U = df_cell[k,:UB]#[row] 
            #     c = (c_U + c_L)/2
            #     M = c_U - c_L
            #     c_g = c + d.*x_now
            #     y, gx, SP = gx_bound(c, c_g, edge)
            #     if y != df_cell[k,:Y]
            #         O1Flag = false
            #     end
            #     df_cell[k,:g] = gx
            #     df_cell[k,:Y] = y
            # end
            # println("O1Flag ", O1Flag)
            # println("K_bar = ", K_bar)
            # if O1Flag == false

            #CHECK IS Z_NOW IS LESS THAN THE NEW CUT BEFORE ADDING [LINES 187--190]
            #For each cell k, the shortest-path cost is found by gx_bound
            #written as: g_k = sum(c_{ij} + d_{ij} x_now_{ij} for (i,j) in Y)
            #We must have z <= sum(z_k over all k), otherwise, add constraint on z
        
        if O1Flag:
            print("\tO1Flag: Passed")
            # terminate_cond = False
            # while terminate_cond == False:
            partitionCounter = 1
            myCounter = 0
            # print("HERE")
            # print("myCounter ", myCounter)
            while myCounter < partitionCounter:
                myCounter += 1
                # print("K_bar = ", K_bar)
                print("Cells failing O2Flag")
                for k in K_bar:
                    # print("Cell ", k)
                    c_L, c_U, M, c, c_g_L, yK = getCellInfo(k, x_now, "c_g_L", d, df_cell)
                    p_k = df_cell.at[k, 'PROB']
                    
                    # yL, gL, SPL,_,_, = gx_bound(c, c_g_L, edge,origin,destination)
                    # df_cell.at[k, 'Y_Lk'] = yL
                    # df_cell.at[k, 'gL'] = gL
                    if recalc_h ==True:
                        y_h, hx = hx_bound(c_L, c_U, d, x_now,edge,origin,destination)

                    # print("y_h = ", y_h)
                    # print("hx = ", hx)
                    
                    # print("Before update hx")
                    # print(df_cell)
                        df_cell.at[k, 'h'] = hx
                    else:
                        hx = df_cell.at[k,'h']
                    # print("After update hx")
                    # print(df_cell)
                    gx = df_cell.at[k, 'g']
                    # print("gx = ", gx)
                    # print("hx = ", hx)
                    print("h = ", list(df_cell['h']))
                    # print(df_cell.loc[k,:])
                    if gx - hx <= delta2*gx:
                        # print("O2Flag: Passed")
                        K_removed.append(k)
                    else:
                        # print(k, end=": ")
                        newCell += 1
                        # print("2. After update hx")
                        # print(df_cell)
                        ΔL, ΔU, arc_split, yL, yU, gL, gU, SP_L, SP_U,df_cell = Partition(x_now, newCell, k, p_k, c_L, c_U, M, yK, d,edge,origin,destination,Len,A1,A3,df_cell, K_newly_added)

                        #Calculate h-bound for partitioned cells:
                        yk, hk = calcHBoundAfterPartition(k, x_now, d, df_cell,edge,origin,destination)
                        df_cell.at[k,'h'] = hk
        
                        ynewCell, hnewCell = calcHBoundAfterPartition(newCell, x_now, d, df_cell,edge,origin,destination)
                        df_cell.at[newCell,'h'] = hnewCell
                        if k == K_bar[-1]:
                            recalc_h = False

                        
                        # print("yL = ", yL)
                        # print("P_bar = ", P_bar)
                        # print("yL in P_bar ", (yL in P_bar))
                        # print(k, ": Added a new cell")
                        # print("Outside Partition")
                        # print(df_cell)

                        # df_temp_k = df_constraints[df_constraints.CELL == k]
                        #constraints associated with cell k
                # print("After Partition")
                # p = df_cell.PROB.tolist()
                # # print("p = ", p)
                # coef_x = [0]*Len
                # constant_SP = 0
                coef_x = [0]*Len
                constant_SP = 0
                p = df_cell['PROB']

                for k in range(newCell+1):
                    # print("k = ", k)
                    c_L, c_U, M, c, c_g, Y_k = getCellInfo(k, x_now, "c_g", d, df_cell)
                    coef_x = coef_x + p[k]*np.array([a*b for a,b in zip(Y_k,d)])
                    constant_SP = constant_SP + p[k]*sum(c[i]*Y_k[i] for i in range(Len))



                if z_now > sum(coef_x[i]*x_now[i] for i in range(Len))+ constant_SP + 10**(-4):
                    m.cbLazy(m._z <= sum(coef_x[i]*m._x[i] for i in range(Len)) + constant_SP)
                    # print(z <= sum(coef_x[i]*m._x[i] for i in range(Len)) + constant_SP)
                m.update()
                K_bar = list(set(K_bar) - set(K_removed))
                K_bar.extend(K_newly_added)
                K_newly_added = []
                K_removed = []

                if not K_bar:
                    myCounter = partitionCounter
                    terminate_cond = True
        
        total_time = time.time() - start
        print("_end g = ", list(df_cell['g']))
        print("_end h = ", list(df_cell['h']))
        print("terminate_cond ", terminate_cond)
        # h_val = df_cell['h']
        # print(df_cell)
        # print("h_val ", h_val[0])
        # p_val = df_cell['PROB']
        # LB = sum(h_val[k] * p_val[k] for k in range(newCell+1))
        # print("UB ", MP_obj, "; LB ", LB)
        # print("h_val ", h_val)
    # terminate_cond=True
        m._last_x = last_x
        m._df_cell = df_cell
        m._K_removed = K_removed
        m._K_bar = K_bar
        m._K_newly_added = K_newly_added
        m._p = p
        m._newCell = newCell
        m._con_num = con_num
        m._P_bar = P_bar
        # x_now = np.array(m.cbGetSolution(m._x).values())
        # z_now = m.cbGetSolution(m._z)
        # MP_obj = m.cbGet(GRB.Callback.MIP_OBJBST) #m.ObjVal
        # m._best = m.cbGet(GRB.Callback.MIPSOL_OBJBST)
        # print(df_cell)
    
# Create a new Gurobi model
MP_obj = 0.0
# zNum = 200000
cRefNum = 2000000

m = gp.Model()
m.setParam(GRB.Param.OutputFlag, 0)
x = m.addVars(range(Len), vtype=GRB.BINARY, name="x")
z = m.addVar(lb=0, ub=1e6, name="z")
m.addConstr(x.sum() == b, "sum_x_equals_b") 
m.addConstr(z <= SP_init + sum(yy[i]*x[i]*d[i] for i in range(Len)))


# # Create a dictionary to store constraints - for constraints related to cells
# constraints_dict = {}
# new_row = {
#     'CELL': [0],
#     'Y': [yy],
#     'SP': [SP_init],
#     "con":
#     [m.addConstr(z[0] <= SP_init + sum(yy[i]*x[i]*d[i] for i in range(Len)))]
# }
# Define data types for each column
# dtypes = {
#     'CELL': int,
#     'Y': object,  # Assuming 'Y' contains arrays
#     'SP': float,
#     'con': object
# }
# print("yy ", yy)
# df_constraints = pd.DataFrame(new_row, columns=dtypes.keys()).astype(dtypes)
# print(type(df_constraints.loc[0, 'con']))
# print("df_constraints")
# print(df_constraints)
# Constraint: Sum of x[i] equals b
# m.addConstr(x.sum() == b, "sum_x_equals_b")

# Optimize model
m.setObjective(z, sense=GRB.MAXIMIZE)

m._iter = iter
m._x = x
m._z = z
m._best = 0
m.Params.LazyConstraints = 1
m._newCell = newCell
m._df_cell = df_cell
m._P_bar = P_bar
m._k = k
# print("p = ",p)

# Objective: Maximize sum(p[i]*z[i])

# Initialize global variables
m._x_sol=x_sol
m._z_sol=z_sol
m._x_now=x_now
# α_now
m._z_now=z_now
m._last_x=np.array(last_x)
m._con_num=con_num

m._total_time=total_time
m._iter=iter
m._K_bar=K_bar
m._LB=LB
m._MP_obj=MP_obj
m._K_newly_added=K_newly_added
m._K_removed=K_removed
m._p = p
m._start = start
m._terminate_cond = terminate_cond
m.optimize(lazy)

vals = m.getAttr('X', x)
# Optimize the model
# m.optimize()
obj = m.ObjVal
print(obj)
