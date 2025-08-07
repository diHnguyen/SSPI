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
delta1 = 1/10000 #0.5/100 #Old: 1.0
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
importlib.import_module("functionPartition_SA")
from functionPartition_SA import Partition
importlib.import_module("functionCheckO1Flag_perc")
from functionCheckO1Flag_perc import checkO1Flag
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
z = m.addVars(range(zNum), lb=0, ub=1e6, name="z")


# # Create a dictionary to store constraints - for constraints related to cells
# constraints_dict = {}


new_row = {
    'CELL': [0],
    'Y': [yy],
    'SP': [SP_init],
    "con":
    [m.addConstr(z[0] <= SP_init + sum(yy[i]*x[i]*d[i] for i in range(Len)))]
}
# Define data types for each column
dtypes = {
    'CELL': int,
    'Y': object,  # Assuming 'Y' contains arrays
    'SP': float,
    'con': object
}

# print("yy ", yy)
global df_constraints 
df_constraints = pd.DataFrame(new_row, columns=dtypes.keys()).astype(dtypes)
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
m.setObjective(sum(p[i] * z[i] for i in range(newCell+1)),sense=GRB.MAXIMIZE)
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
last_O1Flag = None
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
# print("df_cell")
# print(df_cell.g)
# print(df_cell)
calls_SASplit = 0
actual_SASplit = 0
SA_time = 0

while not terminate_cond:
    # α, iter, total_time, K_bar, K_newly_added, K_removed, LB, MP_obj, con_num, newCell, LB_w, p, \
    # x_sol, z_sol, α_sol, last_x, x_now, α_now, z_now, terminate_cond, start, set, Ins, density, dataset = \
    #     (global variable values here)
    # print("HERE")
    
    while (len(K_bar)>0):
        
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
            z_now = np.empty(zNum)
            
            for i in range(Len):
                x_now[i] = x[i].X #m.getAttr('x', x[i].X) #m.getAttr('X', vars)
            for i in range(zNum):
                z_now[i] = z[i].X
            
            # print(m)
            cur_time = time.time() - start
            print("\n==========================================================")
            print("Iter : ", iter, " ; MP_obj = ", MP_obj, " ; time ", cur_time, "; ", len(K_bar), "/", newCell+1)
            print("==========================================================")
            x_index = np.where(x_now > 0)[0]
            print("x = ", x_index)
            # print("z_now ", z_now[0:2])
            if runningTest == False:
                if printIters == True:
                    with open(directory+'Dec2024_Output/Iter/main_A3_0_'+density+'_'+testSet+'_'+sys.argv[2]+'.txt','a') as the_file:
                        the_file.write("I;"+str(iter)+";"+str(cur_time)+';'+str(b)+";"+str(MP_obj)+";"+str(LB_global)+";"+str(x_index)+";"+str(len(K_bar))+";"+str(newCell+1)+str(calls_SASplit)+";"+str(actual_SASplit)+";"+str(SA_time)+"\n")

            # print("df_constraints")
            # for i in range(len(df_constraints)):
            #     # print(df_constraints.loc[i,:])
            #     print("Constraint ", i)
            #     mcell = df_constraints['CELL'][i]
            #     print("Cell ", mcell)
            #     c_L, c_U, M, c, c_g, Y_k = getCellInfo(mcell, x_now, "c_g", d,  df_cell)
            #     marc =np.where(np.array(df_constraints['Y'][i])>0)[0]
            #     print("Y ", marc)
            #     print("SP ", df_constraints['SP'][i])
            #     cost = sum(c[a] + d[a]*x_now[a] for a in marc)
            #     print("\t",cost)
            
                    
            # print(df_cell)
            # print("z = ", z_now[0:(newCell+1)])
            # print("p = ", p)
            # print("newCell = ", newCell)
            # print("g = ", df_cell.loc[:,'g'])
            # print("h = ", df_cell.loc[:,'h'])
            # if iter == 6:
            #     print("HERE")
            #     # print (m.display())
            #     m.write("mainModel.lp")
            #     m.write("mainModel.rlp")
            #     m.write("mainModel.mps")
            

        O1Flag = True
        O1Flag, K_bar, df_cell, df_constraints = checkO1Flag(m,x,z,Len,O1Flag,delta1,newCell,edge,origin,destination,last_x,x_now,d, k,z_now,df_cell,df_constraints, K_bar)
        
        
        print("O1Flag ", O1Flag)
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
                myCounter += 1
                # print("K_bar = ", K_bar)
                # print("Cells failing O2Flag")
                for k in K_bar:
                    # print("Cell ", k)
                    c_L, c_U, M, c, c_g, yK = getCellInfo(k, x_now, "c_g", d, df_cell)
                    # yL, gL, SPL,_,_, = gx_bound(c, c_g_L, edge,origin,destination)
                    # df_cell.at[k, 'Y_Lk'] = yL
                    # df_cell.at[k, 'gL'] = gL
                    
                    # if iter == 5:
                    #     with open('test.csv','a') as the_file:
                    #         the_file.write('\n')
                    #         the_file.write(str(c_L))
                    #         the_file.write(c_L)
                    #         the_file.write(c_L)
                    #         the_file.write(c_L)
                            
                    p_k = df_cell.at[k, 'PROB']
                    if (not np.array_equal(last_x, x_now)) or (last_O1Flag == False):
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
                    # print("After update hx")
                    # print(df_cell)
                    gx = df_cell.at[k, 'g']

                    
                    # print("hx = ", hx)
                    
                    if gx - hx <= delta2*gx: #Used to be gx - hx <= delta2:
                        # print("O2Flag: Passed")
                        K_removed.append(k)
                    else:
                        # print(k, end=": ")
                        newCell += 1
                        # print("2. After update hx")
                        # print(df_cell)
                        # if k == 44:
                        #     print(k, "gx = ", gx,"; hx = ", hx)
                        #     y_h, hx = hx_bound(c_L, c_U, d, x_now,edge,origin,destination)
                        #     y, gx, SP, label, path = gx_bound(c, c_g, edge,origin,destination)
                        #     print(k, "gx = ", gx,"; hx = ", hx)
                        ΔL, ΔU, arc_split, yL, yU, gL, gU, SP_L, SP_U,df_cell,calls_SASplit,actual_SASplit, SA_time = Partition(x_now, newCell, k, p_k, c_L, c_U, M, yK, d,edge,origin,destination,Len,A1,A3,df_cell, K_newly_added,calls_SASplit,actual_SASplit, SA_time)
                        
                        #Calculate h-bound for partitioned cells:
                        yk, hk = calcHBoundAfterPartition(k, x_now, d, df_cell,edge,origin,destination)
                        df_cell.at[k,'h'] = hk
                        
                        ynewCell, hnewCell = calcHBoundAfterPartition(newCell, x_now, d, df_cell,edge,origin,destination)
                        df_cell.at[newCell,'h'] = hnewCell
                        
                        
                        
                        # print("arc_split ", arc_split)
                        # print(k, ": Added a new cell")
                        # print(df_cell)
                        
                        # df_temp_k = df_constraints[df_constraints.CELL == k]
                        #constraints associated with cell k
                        # print("Constraints of ", k)
                        indices = df_constraints.index[df_constraints.CELL == k].tolist()
                        add_yL = True
                        add_yU = True
                        # print("arc_split = ", arc_split)
                        _, _, _, c, _, _ = getCellInfo(k, x_now, "c_g", d,  df_cell)
                        _, _, _, c_newCell, _, _ = getCellInfo(newCell, x_now, "c_g", d,  df_cell)
                        #Iterate over constraints related to k
                        for r in indices: #_, dfRow in df_temp_k.iterrows():
                            # Y_k = np.array(dfRow['Y'])
                            # print(np.where(df_constraints.at[r,'Y']>0)[0])
                            # print("Checking constraint ", r, " cell ", k)
                            Y_k = np.array(df_constraints.at[r,'Y'])
                            # print("Y_k ", Y_k)
                            if np.array_equal(Y_k, yL):
                                add_yL = False
                            if np.array_equal(Y_k, yU):
                                add_yU = False

                            # newCell_RHS = dfRow['SP']
                            newCell_RHS = df_constraints.at[r, 'SP']
                            # print("arc_split ", arc_split)
                            # print("Y_k ", Y_k)
                            #If current constraint (correspond to row)
                            # print("Y_k ", np.where(Y_k>0)[0])
                            marc = np.where(Y_k >0)[0]
                            if Y_k[arc_split] == 1:
                                # conRef = dfRow['NUM']
                                # constr_to_update = dfRow['con'] 
                                constr_to_update = df_constraints.at[r,'con'] 
                                # print(constr_to_update)
                                #constraints_dict.loc[constraints_dict.cell ==k, 'cell']
                                
                                # print("ΔU = ", ΔU,"; ΔL = ", ΔL)
                                    
                                # newCell_RHS = newCell_RHS + ΔU 
                                newCell_RHS = sum(c_newCell[a] for a in marc)
                                # print(k, "Before update SP ", df_constraints.loc[r,'SP'])
                                # dfRow['SP'] = dfRow['SP'] - ΔL
                                # print(df_constraints.loc[r,:])
                                # print("ΔU " ,ΔU, "; ΔL " , ΔL)
                                # print("0.df_constraints.at[r,'SP'] ", df_constraints.at[r,'SP'])
                                curCell_RHS = sum(c[a] for a in marc)
                                df_constraints.at[r,'SP'] = curCell_RHS
                                # df_constraints.at[r,'SP'] = df_constraints.at[r,'SP'] - ΔL
                                # print("1.df_constraints.at[r,'SP'] ", df_constraints.at[r,'SP'])
                                # print("newCell_RHS " , newCell_RHS)
                                # print("current Cell RHS ", df_constraints.at[r,'SP'])

                           
                                # for a in np.where(Y_k >0)[0]:
                                #     print(d[a], " " , x_now[a], " ", c[a])
                                # print(k, "After update SP ", df_constraints.loc[r,'SP'])
                                # print(newCell, "After update SP ", newCell_RHS)
                                # df_constraints.at[conRef - 1, 'SP'] = dfRow['SP']
                                # set_normalized_rhs(constr[conRef], dfRow['SP'])
                                constr_to_update.setAttr(GRB.Attr.RHS, df_constraints.loc[r,'SP'])

                                
                                
                            # con_num += 1
                            
                            # constr[con_num] = @constraint(m, z[newCell] <= sum(d[i] * x[i] * Y_k[i - 1] for i in range(1, Len + 1)) + newCell_RHS)
                            
                            new_con = {
                                'CELL': [newCell],
                                'Y': [Y_k],
                                'SP':[newCell_RHS],
                                'con': [m.addConstr(z[newCell] <= sum(d[i] * x[i] * Y_k[i] for i in range(Len)) + newCell_RHS)]
                            }
                            
                            # print(z[newCell] <= sum(d[i] * x[i] * Y_k[i] for i in range(Len)) + newCell_RHS)
                            dtypes = {
                                'CELL': int,
                                'Y': object,  # Assuming 'Y' contains arrays
                                'SP': float,
                                'con': object
                            }
                            # print("yy ", yy)
                            # df_constraints.loc[con_num - 1] = [con_num, newCell, Y_k.tolist(), newCell_RHS]
#                             df_constraints = df_constraints.append(new_row_data, ignore_index=True)
                            
                            df_new_con = pd.DataFrame(new_con, columns=dtypes.keys()).astype(dtypes)
                            df_constraints = pd.concat([df_constraints,df_new_con], axis=0, ignore_index=True)
                            # print("Y_k ", np.array(Y_k))
                            # print(df_constraints)
                        if add_yL:
                            # con_num += 1
                            new_con = {
                                'CELL': [k],
                                'Y': [yL],
                                'SP':[SP_L],
                                'con': [m.addConstr(z[k] <= sum(d[i] * x[i] * yL[i] for i in range(Len)) + SP_L)]
                            }
                            # print("k = ", k)
                            # print(np.where(yL >0)[0])
                            # for a in np.where(yL >0)[0]:
                            #     print(d[a], " " , x_now[a], " ", c[a])
                            dtypes = {
                                'CELL': int,
                                'Y': object,  # Assuming 'Y' contains arrays
                                'SP': float,
                                'con': object
                            }
                            # print("yy ", yy)
                            # df_constraints.loc[con_num - 1] = [con_num, newCell, Y_k.tolist(), newCell_RHS]
#                             df_constraints = df_constraints.append(new_row_data, ignore_index=True)
                            
                            df_new_con = pd.DataFrame(new_con, columns=dtypes.keys()).astype(dtypes)
                            df_constraints = pd.concat([df_constraints,df_new_con], axis=0, ignore_index=True)
                            # m.addConstr(z[k] <= sum(d[i] * x[i] * YL[i] for i in range(Len)) + SP_L)
                            # constr[con_num] = @constraint(m, z[k] <= sum(d[i] * x[i] * yL[i - 1] for i in range(1, Len + 1)) + SP_L)
                            # df_constraints.loc[con_num - 1] = [con_num, k, yL.tolist(), SP_L]
#                             df_constraints = df_constraints.append(new_row_data, ignore_index=True)
                        if add_yU:
                            # con_num += 1
                            
                            # m.addConstr(z[newCell] <= sum(d[i] * x[i] * YU[i] for i in range(Len)) + SP_U)
                            # constr[con_num] = @constraint(m, z[newCell] <= sum(d[i] * x[i] * yU[i - 1] for i in range(1, Len + 1)) + SP_U)
                            # df_constraints.loc[con_num - 1] = [con_num, newCell, yU.tolist(), SP_U]
#                             new_row_data = {
#                                 'CELL': newCell,
#                                 'Y': yU,
#                                 'SP':SP_U,
#                                 'con': m.addConstr(z[newCell] <= sum(d[i] * x[i] * yU[i] for i in range(Len)) + SP_U)
#                             }
#                             df_constraints = df_constraints.append(new_row_data, ignore_index=True)
                            new_con = {
                                'CELL': [newCell],
                                'Y': [yU],
                                'SP':[SP_U],
                                'con': [m.addConstr(z[newCell] <= sum(d[i] * x[i] * yU[i] for i in range(Len)) + SP_U)]
                            }

                            dtypes = {
                                'CELL': int,
                                'Y': object,  # Assuming 'Y' contains arrays
                                'SP': float,
                                'con': object
                            }
                            # print("yy ", yy)
                            # df_constraints.loc[con_num - 1] = [con_num, newCell, Y_k.tolist(), newCell_RHS]
#                             df_constraints = df_constraints.append(new_row_data, ignore_index=True)
                            
                            df_new_con = pd.DataFrame(new_con, columns=dtypes.keys()).astype(dtypes)
                            df_constraints = pd.concat([df_constraints,df_new_con], axis=0, ignore_index=True)
                # print("newCell ", newCell)
                p = df_cell['PROB'].tolist()
                
                # @objective(m, Max, sum(p[i] * z[i] for i in range(1, len(p) + 1)))
                
                # m.setObjective(sum(p[i] * z[i] for i in range(1, len(p) + 1)), sense=GRB.MAXIMIZE)
                # print("",sum(p[i] * z[i] for i in range(newCell+1)))
                m.setObjective(sum(p[i] * z[i] for i in range(newCell+1)),sense=GRB.MAXIMIZE)
                m.update()
                
                K_bar = list(set(K_bar) - set(K_removed))
                K_bar.extend(K_newly_added)
                K_newly_added = []
                K_removed = []
                # print("0. K_bar ", K_bar)
                if not K_bar:
                    myCounter = partitionCounter
                    terminate_cond = True

        total_time = time.time() - start
        h_val = df_cell['h']
        
        # print("h_val ", h_val[0])
        p_val = df_cell['PROB']
        # print(len(h))
        # print(newCell+1)
        # print("LB before Partition")
        LB = sum(h_val[k] * p_val[k] for k in range(newCell+1))
        if LB_global < LB:
            LB_global = LB
        print("MIP_GAP = ", MIP_GAP)
        print("MP_obj = ", MP_obj, " LB ", LB,":", (MP_obj - LB)/MP_obj)
        print("LB_global = ", LB_global,":",  (MP_obj - LB_global)/MP_obj)

        #Difference compared to Branch 32: Added MIP_GAP
        
        # print("MIP GAP ", MP_obj, " ", LB,":", (MP_obj - LB)/MP_obj)
        if (MP_obj - LB_global)/MP_obj <= MIP_GAP:
            # print("1.")
            terminate_cond = True
            K_bar = []
        print("terminate_cond ", terminate_cond)
        # print("K_bar ", K_bar)
        last_x = x_now
        last_O1Flag = O1Flag
        # print("UB ", MP_obj, "; LB ", LB)
        # print("h_val ", h_val)
        # print(df_constraints)
        # oeFile = open(f"./PrelimOutputFile/OEFiles/OE_Alg_{set}_{dataSet}_{Ins}.txt", "a")
        # print(oeFile, f"{dataSet}; Ins {Ins}; Time {total_time}; MP_obj {MP_obj}; LB {LB}; x_now {np.where(x_now == 1)[0]}; Cells {len(K_bar)}/{newCell}; Iter {iter}")
        # oeFile.close()
#Remove when done fixing bug
    terminate_cond=True
    
# Optimize the model
m.optimize()
if runningTest == True:
    print("End of test - Not Printing")
    # with open(directory+'./Dec2024_Output/test_main_d20_'+testSet+'_'+sys.argv[2]+'.txt','a') as the_file:
        # the_file.write("-1;"+str(cur_time)+';'+str(b)+";"+str(MP_obj)+";"+str(x_index)+";"+str(newCell+1)+"\n")
else:
    with open(directory+'./Dec2024_Output/'+'main_A3_0_'+density+'_'+testSet+'_'+sys.argv[2]+'.txt','a') as the_file:
        # the_file.write("-1;"+str(total_time)+';'+str(b)+";"+str(MP_obj)+";"+str(x_index)+";"+str(newCell+1)+"\n")
        the_file.write("C;"+str(iter)+";"+str(total_time)+';'+str(b)+";"+str(MP_obj)+";"+str(LB_global)+";"+str(x_index)+";"+str(len(K_bar))+";"+str(newCell+1)+";"+str(newCell+1)+str(calls_SASplit)+";"+str(actual_SASplit)+";"+str(SA_time)+"\n")
    with open(directory+'Dec2024_Output/Iter/main_A3_0_'+density+'_'+testSet+'_'+sys.argv[2]+'.txt','a') as the_file:
                        the_file.write("C;"+str(iter)+";"+str(total_time)+';'+str(b)+";"+str(MP_obj)+";"+str(LB_global)+";"+str(x_index)+";"+str(len(K_bar))+";"+str(newCell+1)+";"+str(newCell+1)+str(calls_SASplit)+";"+str(actual_SASplit)+";"+str(SA_time)+"\n")
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