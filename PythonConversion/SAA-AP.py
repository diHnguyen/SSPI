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

importlib.import_module("functionFindCluster")
from functionFindCluster import findCluster

# In[2]:


# networkCSV = 'TestInstances/CSV_TestInstances/N100/' + 'N100_22.csv';
# N = 1000; #sample size
# budget = 5;
# numpy.random.seed(2024);

# networkCSV = './NewCSVFeb24/N10_1.csv'
num_cases = int(sys.argv[3]) #1000
b = 2
option = 2; #1: conservative refinement; 2: aggressive refinement
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
        thetaval = model.cbGetSolution(model._theta);
        # Phase-1: Just using the existing partition -- coarse cuts
        partitionCosts = [];
        partitionPaths = [];
        
        totalCost = 0;
        for p in range(len(model._partition)):
            # update edge cost per partition
            #partitionEdgeCost = {};
            for e in model._G.edges:
                #edgeCost = 0;
                #for k in model._partition[p]:
                #    edgeCost += model._scens[k][e];
                #edgeCost = edgeCost*1.0/len(model._partition[p]);
                #partitionEdgeCost[e] = edgeCost;
                if xvals[e] > 1e-5:
                    model._G.edges[e]['tempCost'] = model._partition[p]["edgeCosts"][e] + model._G.edges[e]['interEffect'];
                else:
                    model._G.edges[e]['tempCost'] = model._partition[p]["edgeCosts"][e];
            # obtain the shortest path and its length
            spValue = nx.shortest_path_length(model._G, source=model._origin, target=model._destination, weight='tempCost', method='dijkstra')
            spPath = nx.shortest_path(model._G, source=model._origin, target=model._destination, weight='tempCost', method='dijkstra')
            partitionCosts.append(spValue); 
            partitionPaths.append(spPath);
            #partitionEdgeCosts.append(partitionEdgeCost);
            totalCost += spValue*len(model._partition[p]["scenList"])/num_cases;
        if totalCost < thetaval-(1e-5):
            # add lazy constraints
            constrCoefList = [1];
            constrVarList = [model._theta];
            rhs = 0;
            for p in range(len(model._partition)):
                for i in range(len(partitionPaths[p])-1):
                    rhs += model._partition[p]["edgeCosts"][(partitionPaths[p][i],partitionPaths[p][i+1])]*len(model._partition[p]["scenList"])/num_cases;
                    constrCoefList.append(-model._G.edges[(partitionPaths[p][i],partitionPaths[p][i+1])]['interEffect']*len(model._partition[p]["scenList"])/num_cases);
                    constrVarList.append(model._x[(partitionPaths[p][i],partitionPaths[p][i+1])]);
            expr = gp.LinExpr();
            expr.addTerms(constrCoefList, constrVarList);
            model.cbLazy(expr <= rhs);
        else:
            # Phase-2: Refine into semi-coarse cuts or fine cuts
            # First sort the partition list from the largest to smallest
            sortedList = sorted(range(len(model._partition)), key=lambda k: len(model._partition[k]["scenList"]), reverse = True);
            newPartition = [];
            newPartitionPaths = [];
            newPartitionEdgeCosts = [];
            # Now start refining
            flag = True;
            for p in sortedList:
                fflag = False;
                if model._option == 1:
                    # conservative refinement strategy
                    if flag and len(model._partition[p]["scenList"]) > 1:
                        fflag = True;
                if model._option == 2:
                    # aggressive refinement strategy
                    if len(model._partition[p]["scenList"]) > 1:
                        fflag = True;
                if fflag: 
                    totalCost -= partitionCosts[p]*len(model._partition[p]["scenList"])/num_cases;
                    clusters = [];
                    clusterPaths = [];
                    clusterCost = 0;
                    for k in model._partition[p]["scenList"]:
                        # update edge cost per scenario
                        for e in model._G.edges:
                            if xvals[e] > 1e-5:
                                model._G.edges[e]['tempCost'] = model._scens[k][e] + model._G.edges[e]['interEffect'];
                            else:
                                model._G.edges[e]['tempCost'] = model._scens[k][e];
                        # obtain the shortest path and its length
                        spValue = nx.shortest_path_length(model._G, source=model._origin, target=model._destination, weight='tempCost', method='dijkstra')
                        clusterCost += spValue;
                        spPath = nx.shortest_path(model._G, source=model._origin, target=model._destination, weight='tempCost', method='dijkstra');
                        clusters, clusterPaths = findCluster(spPath, k, clusters, clusterPaths);
                    totalCost += clusterCost*1.0/num_cases;
                    for k in range(len(clusters)):
                        newPartitionPaths.append(clusterPaths[k]);
                        partitionEdgeCost = {};
                        for e in model._G.edges:
                            edgeCost = 0;
                            for kk in clusters[k]:
                                edgeCost += model._scens[kk][e];
                            edgeCost = edgeCost*1.0/len(clusters[k]);
                            partitionEdgeCost[e] = edgeCost;
                        newPartition.append({"scenList": clusters[k], "edgeCosts": partitionEdgeCost});
                    if totalCost < thetaval-(1e-5):
                        flag = False;
                else:
                    newPartition.append(model._partition[p]);
                    newPartitionPaths.append(partitionPaths[p]);
            if not flag: 
                # add lazy constraints
                constrCoefList = [1];
                constrVarList = [model._theta];
                rhs = 0;
                for p in range(len(newPartition)):
                    for i in range(len(newPartitionPaths[p])-1):
                        rhs += newPartition[p]["edgeCosts"][(newPartitionPaths[p][i],newPartitionPaths[p][i+1])]*len(newPartition[p]["scenList"])/num_cases;
                        constrCoefList.append(-model._G.edges[(newPartitionPaths[p][i],newPartitionPaths[p][i+1])]['interEffect']*len(newPartition[p]["scenList"])/num_cases);
                        constrVarList.append(model._x[(newPartitionPaths[p][i],newPartitionPaths[p][i+1])]);
                expr = gp.LinExpr();
                expr.addTerms(constrCoefList, constrVarList);
                model.cbLazy(expr <= rhs);
            model._partition = newPartition;


# In[9]:

total_time = 0.0
start = time.time()
master = gp.Model()
master.setParam(GRB.Param.OutputFlag, 0)
# Create variables
x = {};
for e in G.edges:
    x[e] = master.addVar(obj=0, vtype=GRB.BINARY);
    
# theta = {};
# for k in range(num_cases):
#     theta[k] = master.addVar(obj=1.0/num_cases, vtype=GRB.CONTINUOUS, lb = 0, ub = 1e7);
theta = master.addVar(obj=1.0, vtype=GRB.CONTINUOUS, lb = 0, ub = 1e7);

# Add interdiction budget constraint
master.addConstr(gp.quicksum(x[e] for e in G.edges) <= b);

master._x = x
master._theta = theta
master._G = G
master._origin = origin
master._destination = destination
master._scens = scens
master._option = option
partitionEdgeCost = {};
for e in G.edges:
    edgeCost = 0;
    for k in range(num_cases):
        edgeCost += scens[k][e];
    edgeCost = edgeCost*1.0/num_cases;
    partitionEdgeCost[e] = edgeCost;
initial_partition = {"scenList": list(range(num_cases)), "edgeCosts": partitionEdgeCost};
master._partition = [initial_partition]; # initial partition: putting everything together
master._scens = scens


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
# with open(directory+'SAA_AP_'+testSet+'_'+sys.argv[2]+'.txt', 'a') as the_file:
#     the_file.write(str(num_cases)+";"+str(total_time)+";"+str(b)+";"+str(master.ObjVal)+";"+str(x_sol)+"\n")

print(str(num_cases)+";"+str(total_time)+";"+str(b)+";"+str(master.ObjVal)+";"+str(x_sol)+"\n")