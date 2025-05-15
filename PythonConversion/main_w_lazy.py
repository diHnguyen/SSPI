# This version only solves the shortest-path problem if we cannot find a violating (aggr) cut
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
from time import strftime, localtime
import gurobipy as gp
from gurobipy import GRB
import sys
import math
# from itertools import combinations

# exec(open('./testInstance.py').read())
runningTest = False
printIters = True #if True, will write output to file.
importlib.import_module("functionProcessInputFile")
from functionProcessInputFile import processInputFile
print(strftime('%Y-%m-%d %H:%M:%S', localtime(time.time())))
testSet = "N"+sys.argv[1]
ins = int(sys.argv[2])
density = sys.argv[3]
directory = "./"
# directory = "./Output/INOC2024/"
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
delta1 = 0.5/100 #Old: 1.0
delta2 = 1/100 #Old: 2.0
tol = 1e-4 #replace delta1
# b = 7
b=10
print(d)
# print(edge)
# exec(open('./testInstance.py').read())

# print("M_orig ", M_orig)
# y,gx,SP = gx_bound(c_L, c_U, c, c_g, x_now, edge)

# sys.exit()
# exec(open('./functionProcessInputFile.py'.read())
# Getting args from command line: int(sys.argv[1])
#h-bound model: 
importlib.import_module("functionGbound")
from functionGbound import gx_bound
importlib.import_module("functionHbound")
from functionHbound import hx_bound
importlib.import_module("functionSelectArc_DelaySP")
from functionSelectArc_DelaySP import selectArc_DelaySP
importlib.import_module("functionArcSplit")
from functionArcSplit import arcSplit
importlib.import_module("functionPartition")
from functionPartition import Partition
# importlib.import_module("functionCheckO1Flag_lazy")
# from functionCheckO1Flag import checkO1Flag
importlib.import_module("functionCheckO1Flag_lazy_perc") #This is correct for main_w_lazy
from functionCheckO1Flag_lazy_perc import checkO1Flag
importlib.import_module("functionGetCellInfo")
from functionGetCellInfo import getCellInfo
importlib.import_module("functionGetPathCost")
from functionGetPathCost import getPathCost
importlib.import_module("functionLazyforMain")
from functionLazyforMain import lazy_for_main
#python main.py -> #f1 #a23 as parameters
# c_L = cL_orig
# c_U = cU_orig
# M = M_orig
# y = [0,1,0,0,1]
# x_now = np.zeros(Len)
# newCell = 2
k=1
A1=0 #A1 = 0: Choose arc using worst cost. Else: Choose arc w largest M
A3=1 #A3 = 0: Split a selected using SA if possible. Else: Split using mean base cost.
###!!!Do not use A3=0 when running LazyConstraintModel_DelayedPartition

# Calculate c values
c = (cU_orig + cL_orig) / 2

# Call the gx_bound function (assuming you have it defined elsewhere)
yy, SP_init, SP_init, label, path = gx_bound(c, c, edge, origin,destination)
# print("Init yy = ", np.where(yy > 0.5)[0])

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

# dtypes_lazy = {
#     'coef': object,
#     'cons': float
# }
# new_row = {
#     'coef': [np.zeros(len(d))],
#     'cons': 1e6
# }
# print("len(d) ", len(d))
# # df_cell = pd.DataFrame(new_row)
# df_lazy = pd.DataFrame(new_row, columns=dtypes_lazy.keys()).astype(dtypes_lazy)


# constraints_dict["1"] = {"info":cell1_info, "cons":cell1_constraints}
# m.addConstr(z[1] <= SP_init + x.prod(yy[i] * d[i] for i in range(1, Len + 1)), "z_constraint_1")
newCell = 0
# print("p = ",p)

# Objective: Maximize sum(p[i]*z[i])


# Initialize global variables
# print("Len = ", Len)
P_set = np.empty((0,Len), int)
new_path =np.array([yy])
# print("P_set ", P_set)
# print("yy = ", new_path)
# print(np.shape(new_path))
P_set = np.concatenate((P_set, new_path), axis=0)

x_sol = []
α_sol = 0
z_sol = []
x_now = [0]*Len
α_now = 0
z_now = []
last_x = []
con_num = 1
cur_time = None
total_time = 0.0
iter = 0
K_bar = [0]
LB = 0
LB_w = 0
MP_obj = 1e6
K_newly_added = []
K_removed = []

start = time.time()
terminate_cond = False
MIP_GAP = 1/100
# print("df_cell")
# print(df_cell.g)

# while terminate_cond == False:
while not terminate_cond:
    iter = iter + 1
    cur_time = time.time() - start
    print("\n==========================================================")
    print("Iter : ", iter, " ; MP_obj = ", MP_obj, " ; time ", cur_time, "; ", len(K_bar), "/", newCell+1)
    print("==========================================================")
    print("MP_obj ", MP_obj)
    print("x_now ", x_now)
    x_now, MP_obj, newCell, terminate_cond = lazy_for_main(MIP_GAP, A1, A3, Len, delta1, delta2, newCell, total_time, start, K_bar, edge, origin,destination,last_x, d, b,x_now, P_set, df_cell, terminate_cond)
    
    
    # print("MP_bnd ", MP_bnd)
    # print("MP_cur ", MP_cur)
    # print("z_now " , z_now)
    

    # print("x = ", np.where(x_now > 0.5)[0])
    x_index = np.where(x_now > 0.5)[0]
    print("x = ", x_index)
    # print("p = ", p)
    print("newCell = ", newCell)

        # if iter > 1:
        #     sys.exit()
    if runningTest == False:
        if printIters == True:
            with open(directory+'Dec2024_Output/Iter/lazyDelay_'+density+'_'+testSet+'_'+sys.argv[2]+'.txt','a') as the_file:
                the_file.write("I;"+str(iter)+";"+str(cur_time)+';'+str(b)+";"+str(MP_obj)+";"+str(LB)+";"+str(z_now)+";"+str(x_index)+";"+str(len(K_bar))+";"+str(newCell+1)+"\n")
                    
        last_x = np.array(last_x)
        last_x_arc = np.where(last_x > 0.5)[0]
        x_now_arc = np.where(x_now > 0.5)[0]
        
        # print("?", np.array_equal(last_x_arc,x_now_arc)) #Provide a 3rd arg if there's a possibility of NaN
        if np.array_equal(last_x_arc,x_now_arc)==False: #last_x_arc != x_now_arc:
            print("\nO1Flag Check")
            # print("x_now = ", np.where(x_now > 0.5)[0])
            K_bar = np.arange(newCell+1) #collect(1:newCell)
            # print("K_bar ", K_bar)
            last_x = x_now
            # print("Mid m._last_x ", last_x)
                    
cur_time = time.time() - start
    

if runningTest == True:
    with open(directory+'./Dec2024_Output/test_mainwlazy_'+density+'_'+testSet+'_'+sys.argv[2]+'.txt','a') as the_file:
        the_file.write("C;"+str(iter)+";"+str(cur_time)+';'+str(b)+";"+str(MP_obj)+";"+str(LB)+";"+str(z_now)+";"+str(x_index)+";"+str(len(K_bar))+";"+str(newCell+1)+"\n")
else:
    with open(directory+'./Dec2024_Output/mainwlazy_'+density+'_'+testSet+'_'+sys.argv[2]+'.txt','a') as the_file:
        the_file.write("C;"+str(iter)+";"+str(cur_time)+';'+str(b)+";"+str(MP_obj)+";"+str(LB)+";"+str(z_now)+";"+str(x_index)+";"+str(len(K_bar))+";"+str(newCell+1)+"\n")
#
