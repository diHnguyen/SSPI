#!/usr/bin/env python
# coding: utf-8

# In[1]:

import importlib
import pandas as pd
import networkx as nx;
import pandas as pd;
# import gurobipy as gp;
# # options = {
# # "WLSACCESSID":"a96dc558-310a-4610-92c3-ec8081776782",
# # "WLSSECRET":"7278b0d5-d07f-4a01-92bf-ab59fb8e284d",
# # "LICENSEID":2820704,
# # } 
# from gurobipy import GRB;
import csv;
import sys;
import numpy as np
import time

importlib.import_module("functionProcessInputFile")
from functionProcessInputFile import processInputFile

directory = "./"

testSet = "N"+sys.argv[1]
ins = int(sys.argv[2])
density = sys.argv[3]
Len, origin, destination, edge,d,cL_orig, cU_orig = processInputFile(testSet, ins, density)

# In[2]:


# networkCSV = 'TestInstances/CSV_TestInstances/N100/' + 'N100_22.csv';
# N = 1000; #sample size
# budget = 5;
# numpy.random.seed(2024);

# networkCSV = './NewCSVFeb24/N10_1.csv'
num_cases = int(sys.argv[4]) #1000
b = 10
seed = int(sys.argv[5])
np.random.seed(seed)


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
# df_scens = pd.DataFrame(columns=['scene','edge','cost'])
df_scens = pd.DataFrame({
    'scene': pd.Series(dtype='int'),
    'edge': pd.Series(dtype='object'),
    'cost': pd.Series(dtype='object')
})

df_scens['scene'] = range(num_cases)
print(df_scens.head(5))
# print(G.edges)
edges_list = [] 
cost_list = []
for k in range(num_cases):
    scen = {};
    edges_perscen_list = []
    cost_perscen_list = []
    for e in G.edges:
        scen[e] = np.random.uniform(G.edges[e]['costLB'],G.edges[e]['costUB']);
        if G.edges[e]['costLB'] < G.edges[e]['costUB']-0.0001:
            edges_perscen_list.append(e)
            cost_perscen_list.append(scen[e])
    df_scens.at[k, 'edge']= [edges_perscen_list]
    df_scens.at[k, 'cost']= [cost_perscen_list]
    # edges_list.append(edges_perscen_list)
    # cost_list.append(cost_perscen_list)
    scens.append(scen);
# print(edges_perscen_list)
# print(cost_perscen_list)
# print(edges_list)
# print(cost_list)
print(df_scens.head(5))
df_scens.to_csv('./ScenariosData/Scenario_SAA_'+testSet+'_'+sys.argv[2]+'_n'+sys.argv[4]+'_seed'+sys.argv[5]+'.csv', index= False)
