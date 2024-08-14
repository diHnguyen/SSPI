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
import ast

importlib.import_module("functionProcessInputFile")
from functionProcessInputFile import processInputFile
from functionEvalXSol import evalXSol
# directory = "./PythonConversion/Output/INOC2024/"
directory = "./Output/INOC2024/"

generateScens = True

N = sys.argv[1]
testSet = "N"+str(N)
ins = int(sys.argv[2])
Len, origin, destination, edge,d,cL_orig, cU_orig = processInputFile(testSet, ins)

# x_lazyDelay_b2 = []
# x_lazyDelay_b20 = []

x_lazyDelay_dict = {
    (10, 1, 2): [2, 30],
    (10, 1, 20): [0, 1, 2, 6, 7, 9, 11, 12, 14, 17, 18, 20, 21, 22, 24, 26, 27, 28, 29, 30],
    (10, 2, 2): [0, 18],
    (10, 2, 20): [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 14, 15, 18, 19, 22, 23, 24, 25],
    (10, 3, 2): [4, 20],
    (10, 3, 20): [0, 1, 2, 3, 4, 5, 7, 9, 11, 12, 13, 14, 15, 16, 17, 18, 20, 21, 22, 23],
    (10, 4, 2): [4, 21],
    (10, 4, 20): [4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
    (10, 5, 2): [0, 18],
    (10, 5, 20): [0, 1, 2, 3, 4, 5, 6, 8, 9, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20, 22],
    (100, 1, 2): [23, 2247],
    (100, 1, 20): [0, 1, 2, 23, 157, 159, 173, 177, 842, 1002, 1321, 1515, 1598, 1600, 1659, 1707, 1777, 2247, 2431, 2955],
    (100, 2, 2): [0, 2890],
    (100, 2, 20): [0, 1, 6, 115, 462, 538, 595, 814, 862, 1319, 1416, 1446, 1545, 1706, 1749, 1951, 2115, 2462, 2641, 2890],
    (100, 3, 2): [0, 3012],
    (100, 3, 20): [0, 1, 3, 5, 209, 224, 280, 444, 751, 843, 1009, 1322, 1441, 1471, 1739, 2342, 2580, 2979, 2984, 3012],
    (100, 4, 2): [0, 1685],
    (100, 4, 20): [0, 1, 2, 3, 4, 5, 6, 38, 58, 112, 226, 662, 786, 966, 1467, 1770, 2547, 2698, 2915, 2916],
    (100, 5, 2): [0, 1],
    (100, 5, 20): [1, 2, 3, 4, 6, 7, 9, 10, 12, 57, 79, 92, 468, 768, 834, 971, 1008, 1147, 1873, 2941]
}

    

# print(x_lazyDelay_dict[(10,1,2)])
# In[2]:


# networkCSV = 'TestInstances/CSV_TestInstances/N100/' + 'N100_22.csv';
# N = 1000; #sample size
# budget = 5;
# numpy.random.seed(2024);

# networkCSV = './NewCSVFeb24/N10_1.csv'
num_cases = 10 #int(sys.argv[3]) #1000
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




if generateScens == True:
    scens = [];
    for k in range(num_cases):
        scen = {};
        for e in G.edges:
            scen[e] = np.random.uniform(G.edges[e]['costLB'],G.edges[e]['costUB']);
        scens.append(scen);
    with open(directory+'scens_N'+str(N)+'_'+str(ins)+'.txt', 'w') as the_file:
        the_file.write(str(scens))
    print(scens)
    print(type(scens))
else:
    fileName = directory+"scens_N"+str(10)+"_"+str(ins)+".txt"
    scens = []
    with open(fileName, newline='\n') as csvfile:
        spamreader = csv.reader(csvfile, delimiter='\t')
        for row in spamreader:
            scens = ast.literal_eval(row[0])
            print(type(row[0]))
            
            
    xSol = x_lazyDelay_dict[(int(N),ins, b)]
    x = {};
    for e in G.edges:
        for i in range(Len): 
            if i in xSol:
                x[(edge[i][0], edge[i][1])]= 1
            else:
                x[(edge[i][0], edge[i][1])]= 0

    start = time.time()
    obj_val_sol= evalXSol(scens, x, G,b,origin,destination)
    total_time = time.time()-start
    with open(directory+'evalLazyDelay.txt', 'a') as the_file:
        the_file.write(str(N)+":"+str(ins)+";"+str(b)+";"+str(num_cases)+";"+str(total_time)+";"+str(obj_val_sol)+";"+str(xSol)+"\n")
    print(str(N)+":"+str(ins)+";"+str(b)+";"+str(num_cases)+";"+str(total_time)+";"+str(obj_val_sol)+";"+str(xSol)+"\n")