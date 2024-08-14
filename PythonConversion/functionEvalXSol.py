import numpy as np
import networkx as nx;
import gurobipy as gp;
from gurobipy import GRB;
def evalXSol(scens, xvals, G,b,origin,destination):
    model = gp.Model()
    num_cases = len(scens)
    spValues = []
    for k in range(num_cases):
        # multi-cut version
        # update edge cost per scenario
        for e in G.edges:
            if xvals[e] > 1e-5:
                G.edges[e]['tempCost'] = scens[k][e] + G.edges[e]['interEffect'];
            else:
                G.edges[e]['tempCost'] = scens[k][e];
        # obtain the shortest path and its length
        spValue = nx.shortest_path_length(G, source=origin, target=destination, weight='tempCost', method='dijkstra')
        spValues.append(spValue)
    print(xvals)
    print(spValues)
    # Create variables
    
    objVal = sum(spValues)/num_cases
    
    return objVal