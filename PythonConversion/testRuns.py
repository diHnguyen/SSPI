#Imports for main 
import numpy as np
import pandas as pd
import importlib
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