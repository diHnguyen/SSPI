#Imports for main 
import numpy as np
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


c_L = cL_orig
c_U = cU_orig
M = M_orig
y = [0,1,0,0,1]
x_now = np.zeros(Len)
k=1
label = [ 0., 10., 11., 12.,  0.]
A3=0
arc_split = 3
ΔL, ΔU = arcSplit(x_now, arc_split, k, c_L, c_U, M, y, label,edge,origin,destination,d,Len,A3)
print(ΔL," ", ΔU)
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