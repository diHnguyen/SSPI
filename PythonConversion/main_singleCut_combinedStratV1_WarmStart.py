#This version implements delta1 and delta2 as percentage
#See orig branch 33 for delta1=1 delta2=2
#This also uses the new convention for marking termination
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

# test = "True"
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
# d = [0]*Len
print(d)

# Getting args from command line: int(sys.argv[1])
#h-bound model: 
importlib.import_module("functionGbound")
from functionGbound import gx_bound
importlib.import_module("functionHbound")
from functionHbound import hx_bound
importlib.import_module("functionSelectArc")
from functionSelectArc import selectArc
importlib.import_module("functionArcSplit_SA_WarmStart") #Use the one specific for SA & WarmStart
from functionArcSplit_SA_WarmStart import arcSplit
importlib.import_module("functionPartition_SA_WarmStart")
from functionPartition_SA_WarmStart import Partition
importlib.import_module("functionCheckO1Flag_mainSingleCut_perc")
from functionCheckO1Flag_mainSingleCut_perc import checkO1Flag
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
A1=0 #A1 = 0: Choose arc using worst cost. Else: Choose arc w largest M
A3=0 #A3 = 0: Split a selected using SA if possible. Else: Split using mean base cost.

# Calculate c values
c = (cU_orig + cL_orig) / 2

# Call the gx_bound function (assuming you have it defined elsewhere)
yy, SP_init, SP_init, label, path = gx_bound(c, c, edge, origin,destination)
# print("yy = ", np.where(yy > 0.5)[0])
# print("SP_init = ", SP_init)
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


# data = {"cell":1, 
#         "rhs": SP_init, 
#         "SP": yy, 
#         "con":
#     m.addConstr(z[1] <= SP_init + sum(yy[i]*x[i]*d[i] for i in range(Len)))}

# # df = pd.DataFrame(data)
# constraints_dict = pd.DataFrame(data)
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
m.setParam(GRB.Param.OutputFlag, 0)
x = m.addVars(range(Len), vtype=GRB.BINARY, name="x")
# z = m.addVars(range(zNum), lb=0, ub=1e6, name="z")
z = m.addVar(lb=0,ub=1e6,name="z")

# # Create a dictionary to store constraints - for constraints related to cells
# constraints_dict = {}


# new_row = {
#     'CELL': [0],
#     'Y': [yy],
#     'SP': [SP_init]#,
#     # "con":
#     # [m.addConstr(z <= SP_init + sum(yy[i]*x[i]*d[i] for i in range(Len)))]
# }
# # Define data types for each column
# dtypes = {
#     'CELL': int,
#     'Y': object,  # Assuming 'Y' contains arrays
#     'SP': float#,
#     # 'con': object
# }

# print("yy ", yy)
# global df_constraints 
# df_constraints = pd.DataFrame(new_row, columns=dtypes.keys()).astype(dtypes)
# print(type(df_constraints.loc[0, 'con']))
# print("df_constraints")
# print(df_constraints)
# Constraint: Sum of x[i] equals b
m.addConstr(x.sum() == b, "sum_x_equals_b")
# m.addConstr(x[4]==1)
# m.addConstr(x[20]==1)


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
# m.setObjective(sum(p[i] * z[i] for i in range(newCell+1)),sense=GRB.MAXIMIZE)
m.setObjective(z,sense=GRB.MAXIMIZE)
m.update()
# print(m)


# Initialize global variables
x_sol = []
α_sol = 0
z_sol = []
x_now = []
α_now = 0
z_now = []
last_x = np.zeros(Len)
con_num = 1

total_time = 0.0
iter = 0
K_bar = [0]
LB = 0
LB_w = 0
MP_obj = 1e6
K_newly_added = []
K_removed = []
cur_time = None
start = time.time()
terminate_cond = False
MIP_GAP = 1/100 #Terminate if MIP gap, i.e., weighted UB- weighted LB, is within 1%
LB_global = 0
recalc_h = True
# print("df_cell")
# print(df_cell.g)
# print(df_cell)
calls_SASplit = 0
actual_SASplit = 0
SA_time = 0

fname = "./xSol_SAA_5000_"+density+"_"+testSet+".csv"
print(fname)
df_xSol = pd.read_csv(fname)
print("N ", testSet)
print("ins ", ins)
# print(df_xSol[(df_xSol.N == int(sys.argv[1]))&(df_xSol.Ins == int(ins))])
warmStart_X = df_xSol.loc[(df_xSol.N == int(sys.argv[1]))&(df_xSol.Ins == int(ins)), 'x_sol'].values[0]
print("warmStart ", type(warmStart_X))

# x_init = np.zeros(Len)

string_array_cleaned = warmStart_X.strip("[]")  # Remove brackets
string_list = string_array_cleaned.split()
x_init = np.array(list(map(int, string_list)))
print("x_init = ", x_init)
# sys.out()
# print(x_int, type(x_int))
# for a in x_int:
#     # print(a)
#     x_init[a] = 1
# print(x_init)
# sys.exit()
isWarmStart = False
while not terminate_cond:
    # α, iter, total_time, K_bar, K_newly_added, K_removed, LB, MP_obj, con_num, newCell, LB_w, p, \
    # x_sol, z_sol, α_sol, last_x, x_now, α_now, z_now, terminate_cond, start, set, Ins, density, dataset = \
    #     (global variable values here)
    # print("HERE")
    # print("terminate_cond ", terminate_cond)
    while (len(K_bar)>0):
        # print("len K_bar ", len(K_bar))
        # print("\n\n@@@@@DF_CELL@@@@@@")
        # for k in K_bar:
        #     print(k, ": ", np.where(df_cell.loc[k,'Y']>0)[0])
        # print("\n\n@@@@@DF_CONSTRAINTS@@@@@@")
        # for k in K_bar:
        #     print(k, ": ", df_constraints.loc[k,'con'])
        iter += 1
        # m.write("checkModel.lp")
        m.update()
        m.optimize()
        # K_bar = []#Remove when done debug 
        # print("STATUS ", m.status)
        # if termination_status(m) == MOI.OPTIMAL:
        if m.status == 2:
            MP_obj = m.ObjVal
            x_now = np.empty(Len) #[0.0]*Len
            # z_now = np.empty(zNum)
            
            for i in range(Len):
                x_now[i] = x[i].X #m.getAttr('x', x[i].X) #m.getAttr('X', vars)
            # for i in range(zNum):
            z_now = z.X
            cur_time = time.time() - start
            print("\n==========================================================")
            print("Iter : ", iter, " ; MP_obj = ", MP_obj, " ; time ", cur_time, "; ", len(K_bar), "/", newCell+1)
            print("==========================================================")
            x_index = np.where(x_now > 0)[0]
            print("x = ", x_index)
            print("z = ", z_now)
            print("x_init = ", x_init)
            print(set(x_index) == set(x_init))
            if set(x_index) == set(x_init):
                isWarmStart = True
            # if iter > 20:
            #     sys.out()
            if runningTest == False:
                if printIters == True:
                    with open(directory+'Dec2024_Output/Iter/main_singleCut_combinedStratV1_WarmStart_'+density+'_'+testSet+'_'+sys.argv[2]+'.txt','a') as the_file:
                        the_file.write("I;"+str(iter)+";"+str(cur_time)+';'+str(b)+";"+str(MP_obj)+";"+str(LB_global)+";"+str(x_index)+";"+str(len(K_bar))+";"+str(newCell+1)+";"+str(calls_SASplit)+";"+str(actual_SASplit)+";"+str(SA_time)+"\n")

        O1Flag = True
        O1Flag, K_bar = checkO1Flag(m,x,z,Len,O1Flag,delta1,newCell,edge,origin,destination,last_x,x_now,d, k,z_now,df_cell, K_bar)

        print("O1Flag ", O1Flag)

        # if iter > 50:
        #     sys.out()
        # else: 
        #     print("SP k = 1 ", np.where(np.array(df_cell.at[0, 'Y'])>0.5)[0])
        
        # if (O1Flag == False) or (not np.array_equal(last_x, x_now)):
        if (not np.array_equal(last_x, x_now)): #Only this condition is needed in singleCut - Except for the first time partition occurs, the Partition function generates new shortest paths after splitting cells, so the only case where O1Flag is false, i.e., new SPs are still being discovered, is if x-sol changes. Before that, shortest paths are continuously found with different x-solutions until all shortest-paths are found for cell k=1.
            recalc_h = True

        # df_parent = df_parent.drop(columns=['ParentY'])
        # df_parent.loc[:,'ParentCell'] = -1
        # df_parent = 
        # df_parent = df_cell[['CELL','Y']]
        # df_parent['Parent'] = df_parent['CELL']
        df_parent = pd.DataFrame({
            'CELL': df_cell.CELL,
            'Y': df_cell.Y,  # Assuming 'Y' contains arrays
            'Parent': df_cell.CELL
        })
        
        # print("0. recalc_h ", recalc_h)
        # print("O1Flag ", O1Flag)
        # print("K_bar ", K_bar)
        h = np.array(df_cell.h)
        # print(h)
        if O1Flag:
            print("\tO1Flag: Passed ", len(K_bar), "/", newCell+1)
            partitionCounter = 1
            myCounter = 0
            # print("HERE")
            # print("myCounter ", myCounter)
            
            # print("LB = ", h)
            while myCounter < partitionCounter:
                # myCounter += 1 #We're doing Aggro Split in this combined strat -- so no increment yet
                # print("K_bar = ", K_bar)
                # print("Cells failing O2Flag")
                for k in K_bar:
                    # print("Cell ", k)
                    c_L, c_U, M, c, c_g, yK = getCellInfo(k, x_now, "c_g", d, df_cell)
                    # y_h, hx = hx_bound(c_L, c_U, d, x_now,edge,origin,destination)
                    # print("y_h = ", y_h)
                    # print("hx = ", hx)
                    # h[k] = hx
                    p_k = df_cell.at[k, 'PROB']
                    # print("1. recalc_h ", recalc_h)
                    if recalc_h == True:
                    # if not np.array_equal(last_x, x_now):
                        # print("0.")
                        y_h, hx = hx_bound(c_L, c_U, d, x_now,edge,origin,destination)
                        # print("y_h = ", y_h)
                        # print("hx = ", hx)
                        # h[k] = hx

                        # print("Before update hx")
                        # print(df_cell)
                        df_cell.at[k, 'h'] = hx
                    else:
                        # print("1.")
                        hx = df_cell.at[k, 'h']
                    # y_test, h_test = hx_bound(c_L, c_U, d, x_now,edge,origin,destination)
                    # print("Before update hx")
                    # print(df_cell)
                    gx = df_cell.at[k, 'g']
                    
                    # print(k, "\tgx ", gx, " \thx ", hx, " \t_test ", h_test, "\t", gx - hx, " vs ", delta2*gx)
                    if gx - hx <= delta2*gx: #Used to be gx - hx <= delta2:
                        # print("O2Flag: Passed")
                        K_removed.append(k)
                    else:
                        # print(k, end=": ")
                        newCell += 1
                        # print("Partitioned, now have ", newCell+1, " cells")
                        ΔL, ΔU, arc_split, yL, yU, gL, gU, SP_L, SP_U,df_cell,calls_SASplit,actual_SASplit, SA_time = Partition(x_now, newCell, k, p_k, c_L, c_U, M, yK, d,edge,origin,destination,Len,A1,A3,df_cell, K_newly_added,calls_SASplit,actual_SASplit, SA_time,isWarmStart)

                        #Calculate h-bound for partitioned cells:
                        yk, hk = calcHBoundAfterPartition(k, x_now, d, df_cell,edge,origin,destination)
                        df_cell.at[k,'h'] = hk
        
                        ynewCell, hnewCell = calcHBoundAfterPartition(newCell, x_now, d, df_cell,edge,origin,destination)
                        df_cell.at[newCell,'h'] = hnewCell

                        # df_parent columns: 'CELL','Y','Parent'
                        # This takes the original parent - not just one level up
                        newCell_parent = df_parent.loc[k,'Parent']
                        newCell_parent_Y = df_parent.loc[newCell_parent,'Y']

                        df_parent.loc[len(df_parent)] = [newCell,newCell_parent_Y,newCell_parent] #Order: cell number, parent SP, parent cell

                        
                        if np.array_equal(newCell_parent_Y, yL) == False:
                            myCounter = partitionCounter
                            # print("!!!!!!! FOUND NEW PATH !!!!!!!")
                        if isWarmStart == False:
                            myCounter = partitionCounter

                        if k == K_bar[-1]:
                            recalc_h = False
                coef_x = [0]*Len
                constant_SP = 0
                p = df_cell['PROB']
                
                for k in range(newCell+1):
                    c_L, c_U, M, c, c_g, Y_k = getCellInfo(k, x_now, "c_g", d,  df_cell)
                    # y, gx, SP, label, path = gx_bound(c, c_g, edge,origin,destination)
                    coef_x = coef_x + p[k]*np.array([a*b for a,b in zip(Y_k,d)])
                    constant_SP = constant_SP +  p[k]*sum(c[i]*Y_k[i] for i in range(Len))
                    
            
                if z_now > sum(coef_x[i]*x_now[i] for i in range(Len))+ constant_SP + 10**(-4):
                    m.addConstr(z <= sum(coef_x[i]*x[i] for i in range(Len)) + constant_SP)

                # p = df_cell['PROB'].tolist()
                
                # @objective(m, Max, sum(p[i] * z[i] for i in range(1, len(p) + 1)))
                
                # m.setObjective(sum(p[i] * z[i] for i in range(1, len(p) + 1)), sense=GRB.MAXIMIZE)
                # m.setObjective(z,sense=GRB.MAXIMIZE)
                m.update()
                # print("K_removed ", K_removed)
                # print("K_bar ", K_bar)
                K_bar = list(set(K_bar) - set(K_removed))
                K_bar.extend(K_newly_added)
                K_newly_added = []
                K_removed = []
                
                if not K_bar:
                    myCounter = partitionCounter
                    terminate_cond = True

        total_time = time.time() - start
        h_val = df_cell['h']
        
        # print("h_val ", h.tolist())
        p_val = df_cell['PROB']
        # print(len(h))
        # print(newCell+1)
        # print("p = ", p.tolist())
        # print("LB after Partition")
        # LB = sum(h[k] * p_val[k] for k in range(newCell+1))
        # for k in range(newCell + 1):
        #     print(h_val[k], " ",p_val[k], " ", h_val[k] * p_val[k])
        # print("len_h ", len(h), " vs ", newCell)
        print("MP_obj = ", MP_obj, " LB (current h) ", sum(h_val[k] * p_val[k] for k in range(len(h)))) 
        LB = sum(h_val[k] * p_val[k] for k in range(newCell+1))
        if LB_global < LB:
            LB_global = LB
        print("MIP_GAP = ", MIP_GAP)
        print("MP_obj = ", MP_obj, " LB ", LB,":", (MP_obj - LB)/MP_obj)
        print("LB_global = ", LB_global,":",  (MP_obj - LB_global)/MP_obj)
        
        # if iter == 8:
        #     sys.exit()
        #Difference compared to Branch 32: Added MIP_GAP
        # print("MIP_GAP = ", MIP_GAP)
        # print("MIP GAP ", MP_obj, " ", LB,":", (MP_obj - LB)/MP_obj)
        if (MP_obj - LB_global)/MP_obj <= MIP_GAP:
            terminate_cond = True
            K_bar = []
        last_x = x_now
        # print("terminate_cond ", terminate_cond)
        # print("UB ", MP_obj, "; LB ", LB)
        # print("h_val ", h_val)
        # print(df_constraints)
        # oeFile = open(f"./PrelimOutputFile/OEFiles/OE_Alg_{set}_{dataSet}_{Ins}.txt", "a")
        # print(oeFile, f"{dataSet}; Ins {Ins}; Time {total_time}; MP_obj {MP_obj}; LB {LB}; x_now {np.where(x_now == 1)[0]}; Cells {len(K_bar)}/{newCell}; Iter {iter}")
        # oeFile.close()
#Remove when done fixing bug
    # terminate_cond=True

    # print("terminate_cond ", terminate_cond)
    
# Optimize the model
m.optimize()
if runningTest == True:
    print("End of test - Not Printing")
    # with open(directory+'./Dec2024_Output/test_main_d20_'+testSet+'_'+sys.argv[2]+'.txt','a') as the_file:
        # the_file.write("-1;"+str(cur_time)+';'+str(b)+";"+str(MP_obj)+";"+str(x_index)+";"+str(newCell+1)+"\n")
else:
    with open(directory+'./Dec2024_Output/'+'main_singleCut_combinedStratV1_WarmStart_'+density+'_'+testSet+'_'+sys.argv[2]+'.txt','a') as the_file:
        # the_file.write("-1;"+str(total_time)+';'+str(b)+";"+str(MP_obj)+";"+str(x_index)+";"+str(newCell+1)+"\n")
        the_file.write("C;"+str(iter)+";"+str(total_time)+';'+str(b)+";"+str(MP_obj)+";"+str(LB_global)+";"+str(x_index)+";"+str(len(K_bar))+";"+str(newCell+1)+";"+str(calls_SASplit)+";"+str(actual_SASplit)+";"+str(SA_time)+"\n")
    with open(directory+'Dec2024_Output/Iter/main_singleCut_combinedStratV1_WarmStart_'+density+'_'+testSet+'_'+sys.argv[2]+'.txt','a') as the_file:
                        the_file.write("C;"+str(iter)+";"+str(total_time)+';'+str(b)+";"+str(MP_obj)+";"+str(LB_global)+";"+str(x_index)+";"+str(len(K_bar))+";"+str(newCell+1)+";"+str(calls_SASplit)+";"+str(actual_SASplit)+";"+str(SA_time)+"\n")
# print("UB ", sum(df_cell.at[i,'g']*df_cell.at[i,'PROB'] for i in range(newCell+1)), "; LB ", sum(df_cell.at[i, 'h']*df_cell.at[i, 'PROB'] for i in range(newCell+1)))

# for i in range(newCell+1):
#     print(p[i], "\t", df_cell.at[i,'PROB'])
# print(np.array(df_cell['g']))
# print(np.array(df_cell['h']))

# # print(df_cell)
# K_newly_added = [1]
# ΔL, ΔU, arc_split, yL, yU, gL, gU, SP_L, SP_U,df_cell = Partition(x_now, newCell, k, p, c_L, c_U, M, y,d,edge,origin,destination,Len,A1,A3,df_cell,K_newly_added)
# ########functionArcSplit.py########
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