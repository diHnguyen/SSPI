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
import math
from copy import deepcopy

importlib.import_module("functionProcessInputFile")
from functionProcessInputFile import processInputFile
from functionSolveSAASeq import solveSAASeq
directory = "./PythonConversion/Output/INOC2024/"
print("LN e : ", math.exp(1))
testSet = "N"+sys.argv[1]
ins = int(sys.argv[2])
Len, origin, destination, edge,d,cL_orig, cU_orig = processInputFile(testSet, ins)

# x-sequence for N10_4:
# 1. [4]
# 2. [4]
# 3. [0 4]
# 4. [4 6]
# 5 and more. [4 21]
# print(edge[0])
x_pool = np.array([[4], [0, 4], [4, 6], [4, 21]], dtype=object) 
#[
# [(1, 10)], 
# [(1, 2), (1, 10)], 
# [(1, 10), (2, 7)], 
# [(1, 10), (7, 8)]]
x_candidates = []
for x_sol in x_pool:
    # print("\n",x_sol)
    print("\n")
    x_temp = []
    for e in x_sol:
        # print(edge[e])
        x_temp.append((edge[e][0],edge[e][1]))
    print(x_temp)
    x_candidates.append(x_temp)
print(x_candidates)
# In[2]:


# networkCSV = 'TestInstances/CSV_TestInstances/N100/' + 'N100_22.csv';
# N = 1000; #sample size
# budget = 5;
# numpy.random.seed(2024);

# networkCSV = './NewCSVFeb24/N10_1.csv'
iter = 1
p = 1.91e-1 #1 #same as paper

#These h-values correspond to an initial sample size n1 = 50.
h = 0.425 #2
h_prime = 0.015 #1  

epsilon = 2e-7#2
epsilon_prime = 1e-7#1
alpha = 0.1 #same as paper.
c_p = 8.14491246025 #8.14491246025 for setup in Bayrak's #4.3786 for alpha = 0.1, p=1
k_f = 1e6 #resampling frequency
num_cases = int(np.ceil(((1/(h-h_prime))**2)*(c_p+2*p*((np.log(iter))**2))))#int(sys.argv[3]) #1000

para = str(h)+","+str(h_prime)+","+str(epsilon)+","+str(epsilon_prime)+","+str(alpha)+","+str(c_p)+","+str(k_f)

print("Num scens for k=1 ", num_cases)
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





# In[6]:


# break 
# print("scens[0] = ", scens[0])
# sys. exit()

# In[8]:


# Callback - use lazy constraints
def lazy(model, where):
    if where == GRB.Callback.MIPSOL:
        xvals = model.cbGetSolution(model._x)
        thetavals = model.cbGetSolution(model._theta);
        # print("thetavals ", thetavals)
        iter = model._iter
        h = model._h
        h_prime = model._h_prime
        p = model._p
        epsilon = model._epsilon 
        epsilon_prime = model._epsilon_prime
        alpha = model._alpha
        c_p = model._c_p #= 4.3786 #for alpha = 0.1, p=1
        opt_gap = model._opt_gap
        var = model._var
        
        
        print("\n\nIter ", iter)
        print("c_p ", c_p)
        
        # if iter <4:
        #Obtain num_scens n_k:
        # print(
        num_scens = int(np.ceil(((1/(h-h_prime))**2)*(c_p+2*p*(np.log(iter)**2))))
        # print((1/(h-h_prime))**2)
        # print((c_p))
        # print(2*p*(np.log(iter)**2))
        # print("h-h_prime ",h-h_prime)
        # print("c_p ", c_p, "; p ", p, "; log(iter) ", iter)
        print("iter ", iter, " num_scens n_k ", num_scens)
        
        #Using m_k = 2n_k similar to paper
        m_k = 2*num_scens
        x_candidate, obj_val = solveSAASeq(m_k, G,b,origin,destination)
        print("obj_val ", obj_val)
        print("m_k ", m_k, " samples")
        # print(candidate_x)
        
        # solveSAASeq(m_k,

        cur_SP_cost_all_scens = []
        
        # print("opt_gap = ", opt_gap, " h_prime*np.sqrt(var)+epsilon_prime " , h_prime*np.sqrt(var)+epsilon_prime)
        scens = [];
        for k in range(num_cases):
            scen = {};
            for e in G.edges:
                scen[e] = np.random.uniform(G.edges[e]['costLB'],G.edges[e]['costUB']);
            scens.append(scen);
        for k in range(len(scens)):
            # print(scens)
            # multi-cut version
            # update edge cost per scenario
            for e in model._G.edges:
                if xvals[e] > 1e-5:
                    model._G.edges[e]['tempCost'] = scens[k][e] + model._G.edges[e]['interEffect'];
                else:
                    model._G.edges[e]['tempCost'] = scens[k][e];
            # obtain the shortest path and its length
            spValue = nx.shortest_path_length(model._G, source=model._origin, target=model._destination, weight='tempCost', method='dijkstra')
            cur_SP_cost_all_scens.append(spValue)
            
            if (spValue < thetavals[k]-(1e-5)) & (opt_gap > h_prime*np.sqrt(var)+epsilon_prime):
                # print("add constraint!!!")
                # add lazy constraints
                spPath = nx.shortest_path(model._G, source=model._origin, target=model._destination, weight='tempCost', method='dijkstra')
                constrCoefList = [1];
                constrVarList = [model._theta[k]];
                rhs = 0
                # print("spPath ", spPath)
                for i in range(len(spPath)-1):
                    rhs += scens[k][(spPath[i],spPath[i+1])];
                    constrCoefList.append(-model._G.edges[(spPath[i],spPath[i+1])]['interEffect']);
                    # print("constrCoefList " , constrCoefList)
                    constrVarList.append(model._x[(spPath[i],spPath[i+1])]);
                expr = gp.LinExpr();
                expr.addTerms(constrCoefList, constrVarList);
                model.cbLazy(expr <= rhs);

        #Obtain optimality gap:
        SP_cost_all_scens_candidate = []
        
        # temp_x = x_pool[iter]
        # x_candidate = deepcopy(xvals)#[0] * len(xvals)
        # if iter >=4:
        #     x_candidate = x_candidates[3]
        # else:
        #     x_candidate = x_candidates[iter-1]
        
        # print("x_candidate ", x_candidate)
        # print("xvals ", xvals)
        # for e in model._G.edges:
        #     if xvals[e] > 1e-5:
        #         print(xvals[e], end=" ")
        # print("\n")
        # print("xvals ", xvals[xvals>0.5])#[numpy.array(a) for a in [[0,1,2,3], [2,3,4]]]
        # for e in temp_x:
        #     x_candidate[e] = 1

        for k in range(len(scens)):
            # multi-cut version
            # update edge cost per scenario
            for e in model._G.edges:

                if e in x_candidate:#[e] > 1e-5:
                    # print("scen", k, "e = ", e, "\t", e in x_candidate)
                    model._G.edges[e]['tempCost'] = scens[k][e] + model._G.edges[e]['interEffect'];
                else:
                    model._G.edges[e]['tempCost'] = scens[k][e];
            # obtain the shortest path and its length
            spValue = nx.shortest_path_length(model._G, source=model._origin, target=model._destination, weight='tempCost', method='dijkstra')
            # break
            SP_cost_all_scens_candidate.append(spValue)
        temp_arr = -(np.array(cur_SP_cost_all_scens)-np.array(SP_cost_all_scens_candidate)) #Since we're maximizing
        opt_gap = sum(temp_arr/len(cur_SP_cost_all_scens))
        print("Opt Gap ", opt_gap)
        var = 0
        for i in range(len(temp_arr)):
            var = var+ (temp_arr[i]-opt_gap)**2
        var = var/(len(temp_arr)-1)
        print("var ", var)
        print("one-sided CI [0, ", h*np.sqrt(var)+epsilon,"]")
        # print(xxx)
        #Terminating condition:
        # print(h_prime*s_k +epsilon_prime)
        iter = iter+1
        model._iter = iter
        model._opt_gap = opt_gap
        model._var = var


# In[9]:
#Parameters for sequential sampling



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
# master._scens = scens

master._opt_gap = 1e6
master._var = 1e6
        
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
print('Final Optimal objval: %g' % master.ObjVal)
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
print("Time taken ", total_time)
print("para ", para)
with open(directory+'SAA_'+testSet+'_'+sys.argv[2]+'.txt', 'a') as the_file:
    the_file.write(str(num_cases)+";"+str(total_time)+";"+str(b)+";"+str(master.ObjVal)+";"+str(x_sol)+";"+para+"\n")
# print(str(num_cases)+";"+str(total_time)+";"+str(b)+";"+str(master.ObjVal)+";"+str(x_sol)+";"+para+"\n")