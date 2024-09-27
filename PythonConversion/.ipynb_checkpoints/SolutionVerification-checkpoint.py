#!/usr/bin/env python
# coding: utf-8

# In[1]:

import importlib
import pandas as pd
import networkx as nx;
import pandas as pd;
import gurobipy as gp;
from gurobipy import GRB;
import csv;
import sys;
import numpy as np
import time
import os 

importlib.import_module("functionProcessInputFile")
from functionProcessInputFile import processInputFile

directory = "./"

N = 30
testSet = "N"+sys.argv[1]
ins = int(sys.argv[2])


#NEED TO PROCESS X-SOL HERE.

Len, origin, destination, edge,d,cL_orig, cU_orig = processInputFile(testSet, ins)

# In[2]:


# networkCSV = 'TestInstances/CSV_TestInstances/N100/' + 'N100_22.csv';
# N = 1000; #sample size
# budget = 5;
# numpy.random.seed(2024);

# networkCSV = './NewCSVFeb24/N10_1.csv'
num_cases = 1000000 #3#int(sys.argv[3]) #1000
b = 10
np.random.seed(20242024) #Use a new seed so SAA algs don't see these yet


xMain = []
xLazy = []
xSAA = []
xSAA_AP = []
xSeq = []
dir = "./Sep2024_Output/"
for filename in os.listdir(dir):
    if filename.startswith("main_N"+str(N)+"_"+str(ins)+".txt"):
        df = pd.read_csv(dir+filename, sep=';', names=['iiter','total_time','b','ObjVal','x_sol'], header=None)
        print(df)
        xMain = df['x_sol'][0]
        print(filename)
    if filename.startswith("lazyDelay_N"+str(N)+"_"+str(ins)+".txt"):
        df = pd.read_csv(dir+filename, sep=';', names=['num_cases','total_time','b','ObjVal','z','x_sol'], header=None)
        xLazy = df['x_sol'][0]
    if filename.startswith("SAA_N"+str(N)+"_"+str(ins)+".txt"):
        df = pd.read_csv(dir+filename, sep=';', names=['iiter','total_time','b','ObjVal','x_sol'], header=None)
        xSAA = df['x_sol'][0]
    if filename.startswith("SAA-AP_N"+str(N)+"_"+str(ins)+".txt"):
        df = pd.read_csv(dir+filename, sep=';', names=['iiter','total_time','b','ObjVal','x_sol'], header=None)
        xSAA_AP = df['x_sol'][0]
    if filename.startswith("SeqSampling_N"+str(N)+"_"+str(ins)+".txt"):
        df = pd.read_csv(dir+filename, sep=';', names=['iiter','total_time','b','ObjVal','x_sol'], header=None)
        xSeq = df['x_sol'][0]
print("xMain ",xMain)
print("xLazy ",xLazy)
print("xSeq ", xSeq)
print("xSAA ", xSAA)
print("xSAA_AP ", xSAA_AP)

# prefixed = [filename for filename in os.listdir('./') if filename.startswith("main_N"+str(N)+"_")]
# In[3]:


# Reading network file
# with open(networkCSV, newline='') as f:
#     reader = csv.reader(f);
#     row1 = next(reader);
#     Len = int(row1[0]);
#     row2 = next(reader);
#     origin = int(row2[0]);
#     row3 = next(reader);
#     destination = int(row3[0]);
    
G = nx.DiGraph();
# data = pd.read_csv(networkCSV, skiprows=4, header=None, sep='\s+');
# n_edge = len(data.index);

for i in range(Len): 
    # G.add_edge(data.iat[i,0], data.iat[i,1], costLB = data.iat[i,2], 
    #         costUB = data.iat[i,3], interEffect = data.iat[i,4], tempCost = 0);
    G.add_edge(edge[i][0], edge[i][1], costLB = cL_orig[i], 
            costUB = cU_orig[i], interEffect = d[i], tempCost = 0);


# In[7]:


print("Len = ", Len);
print("origin = ", origin);
print("destination = ", destination);
# print("G.nodes = ", G.nodes)
# print("G.edges = ", G.edges)
# for e in G.edges:
#     print(e)
#     print(G.edges[e])


# In[5]:


scens = [];

for k in range(num_cases):
    scen = {};
    for e in G.edges:
        scen[e] = np.random.uniform(G.edges[e]['costLB'],G.edges[e]['costUB']);
    scens.append(scen);

ObjMain = -1
ObjLazy = -1
ObjSAA = -1
ObjSAA_AP = -1
ObjSeq = -1
for x in [xMain, xLazy, xSAA, xSAA_AP]:
    xvals = [] #model.cbGetSolution(model._x)
    # print(len(edge))
    # print("x ", x)
    string_array_cleaned = x.strip("[]")  # Remove brackets
    string_list = string_array_cleaned.split()
    x_int = np.array(list(map(int, string_list)))
    for a in x_int:
        # print(a)
        xvals.append((edge[a][0], edge[a][1]))
    print(xvals)
    # thetavals = model.cbGetSolution(model._theta);
    # xSol = [0, 1, 5, 17, 106, 174, 234, 249, 292, 299]
    SP_costs = []
    for k in range(len(scens)):
        # multi-cut version
        # update edge cost per scenario
        for e in G.edges:
            if e in xvals: #xvals[e] > 1e-5:
                G.edges[e]['tempCost'] = scens[k][e] + G.edges[e]['interEffect'];
            else:
                G.edges[e]['tempCost'] = scens[k][e];
        # obtain the shortest path and its length
        spValue = nx.shortest_path_length(G, source=origin, target=destination, weight='tempCost', method='dijkstra')
        SP_costs.append(spValue)
    
    if x == xMain:
        ObjMain = sum(SP_costs)/num_cases
    if x == xLazy:
        ObjLazy = sum(SP_costs)/num_cases
    if x == xSAA:
        ObjSAA = sum(SP_costs)/num_cases
    if x == xSAA_AP:
        ObjSAA_AP = sum(SP_costs)/num_cases
    if x == xSeq:
        ObjSeq = sum(SP_costs)/num_cases
        
        
print(ObjMain)
print(ObjLazy)
print(ObjSAA)
print(ObjSAA_AP)
print(ObjSeq)
# In[6]:


# print("scens[0] = ", scens[0])


# In[8]:
# print(scens)

# x_sol = np.empty((0), int)
# for e in G.edges:
#     if xvals[e] > 1e-5:
#         edge_index = np.where((edge==e).all(1))[0]
#         print(edge_index)
#         x_sol = np.concatenate((x_sol, edge_index), axis=0)
#         print(x_sol);
#         # print(" ")
# # print(edge)
# total_time = time.time() - start
# print(total_time)
with open(directory+'Sep2024_Output/SolutionVerification.csv', 'a') as the_file:
    if ObjMain > 0:
        the_file.write(str(N)+";"+str(ins)+";"+"xMain;"+xMain+";"+str(num_cases)+";"+str(b)+";"+str(ObjMain)+"\n")
    if ObjLazy > 0:
        the_file.write(str(N)+";"+str(ins)+";"+"xLazy;"+xLazy+";"+str(num_cases)+";"+str(b)+";"+str(ObjLazy)+"\n")
    if ObjSAA > 0:
        the_file.write(str(N)+";"+str(ins)+";"+"xSAA;"+xSAA+";"+str(num_cases)+";"+str(b)+";"+str(ObjSAA)+"\n")
    if ObjSAA_AP > 0:
        the_file.write(str(N)+";"+str(ins)+";"+"xSAA_AP;"+xSAA_AP+";"+str(num_cases)+";"+str(b)+";"+str(ObjSAA_AP)+"\n")
    if ObjSeq > 0:
        the_file.write(str(N)+";"+str(ins)+";"+"xSeq;"+xSeq+";"+str(num_cases)+";"+str(b)+";"+str(ObjSeq)+"\n")
