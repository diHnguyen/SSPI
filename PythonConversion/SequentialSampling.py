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

importlib.import_module("functionProcessInputFile")
from functionProcessInputFile import processInputFile

directory = "./PythonConversion/Output/INOC2024/"

testSet = "N"+sys.argv[1]
ins = int(sys.argv[2])
Len, origin, destination, edge,d,cL_orig, cU_orig = processInputFile(testSet, ins)

# In[2]:


# networkCSV = 'TestInstances/CSV_TestInstances/N100/' + 'N100_22.csv';
# N = 1000; #sample size
# budget = 5;
# numpy.random.seed(2024);

# networkCSV = './NewCSVFeb24/N10_1.csv'
num_cases = int(sys.argv[3]) #1000
b = 2
np.random.seed(2024)


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


# In[6]:


# print("scens[0] = ", scens[0])


# In[8]:


# Callback - use lazy constraints
def lazy(model, where):
    if where == GRB.Callback.MIPSOL:
        xvals = model.cbGetSolution(model._x)
        thetavals = model.cbGetSolution(model._theta);
        iter = model._iter
        h = model._h
        h_prime = model._h_prime
        p = model._p
        epsilon = model._epsilon 
        epsilon_prime = model._epsilon_prime
        alpha = model._alpha
        c_p = model._c_p #= 4.3786 #for alpha = 0.1, p=1
        print("c_p ", c_p)
        iter = iter+1
        
        #Obtain num_scens n_k:
        num_scens = int(np.ceil(((1/(h-h_prime))**2)*(c_p+2*p*(np.log(iter)**2))))
        print("num_scens ", num_scens)
        
        for k in range(len(model._scens)):
            # multi-cut version
            # update edge cost per scenario
            for e in model._G.edges:
                if xvals[e] > 1e-5:
                    model._G.edges[e]['tempCost'] = model._scens[k][e] + model._G.edges[e]['interEffect'];
                else:
                    model._G.edges[e]['tempCost'] = model._scens[k][e];
            # obtain the shortest path and its length
            spValue = nx.shortest_path_length(model._G, source=model._origin, target=model._destination, weight='tempCost', method='dijkstra')
            if spValue < thetavals[k]-(1e-5):
                # add lazy constraints
                spPath = nx.shortest_path(model._G, source=model._origin, target=model._destination, weight='tempCost', method='dijkstra')
                constrCoefList = [1];
                constrVarList = [model._theta[k]];
                rhs = 0
                for i in range(len(spPath)-1):
                    rhs += model._scens[k][(spPath[i],spPath[i+1])];
                    constrCoefList.append(-model._G.edges[(spPath[i],spPath[i+1])]['interEffect']);
                    constrVarList.append(model._x[(spPath[i],spPath[i+1])]);
                expr = gp.LinExpr();
                expr.addTerms(constrCoefList, constrVarList);
                model.cbLazy(expr <= rhs);
                
        #Obtain optimality gap:
        
        model._iter = iter


# In[9]:

total_time = 0.0
start = time.time()
master = gp.Model()
master.setParam(GRB.Param.OutputFlag, 0)
# Create variables
x = {};
for e in G.edges:
    x[e] = master.addVar(obj=0, vtype=GRB.BINARY);
    
theta = {};
for k in range(num_cases):
    theta[k] = master.addVar(obj=1.0/num_cases, vtype=GRB.CONTINUOUS, lb = 0, ub = 1e7);

# Add interdiction budget constraint
master.addConstr(gp.quicksum(x[e] for e in G.edges) <= b);

master._x = x
master._theta = theta
master._G = G
master._origin = origin
master._destination = destination
master._scens = scens

#Parameters for sequential sampling
iter = 1
p = 1
h = 2
h_prime = 1
epsilon = 2
epsilon_prime = 1
alpha = 0.1
c_p = 4.3786 #for alpha = 0.1, p=1
k_f = 10 #resampling frequency
        
master._iter = iter
master._p = p
master._h = h
master._h_prime = h_prime
master._epsilon = epsilon
master._epsilon_prime = epsilon_prime
master._alpha = alpha
master._c_p = c_p #for alpha = 0.1, p=1

# In[10]:


master.modelSense = GRB.MAXIMIZE
master.Params.LazyConstraints = 1
master.optimize(lazy)

xvals = master.getAttr('X', x)

print('')
print('Optimal objval: %g' % master.ObjVal)
print('')
print('Optimal xval = ')

x_sol = np.empty((0), int)
for e in G.edges:
    if xvals[e] > 1e-5:
        edge_index = np.where((edge==e).all(1))[0]
        print(edge_index)
        x_sol = np.concatenate((x_sol, edge_index), axis=0)
        print(x_sol);
        # print(" ")
# print(edge)
total_time = time.time() - start
print(total_time)
# with open(directory+'SAA_'+testSet+'_'+sys.argv[2]+'.txt', 'a') as the_file:
#     the_file.write(str(num_cases)+";"+str(total_time)+";"+str(b)+";"+str(master.ObjVal)+";"+str(x_sol)+"\n")
print(str(num_cases)+";"+str(total_time)+";"+str(b)+";"+str(master.ObjVal)+";"+str(x_sol)+"\n")