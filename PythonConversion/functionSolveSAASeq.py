import numpy as np
import networkx as nx;
import gurobipy as gp;
from gurobipy import GRB;
def solveSAASeq(num_cases, G,b,origin,destination):
    scens=[];
    for k in range(num_cases):
        scen = {};
        for e in G.edges:
            scen[e] = np.random.uniform(G.edges[e]['costLB'],G.edges[e]['costUB']);
        scens.append(scen);
        
    model = gp.Model()
    def lazy(model, where):
        if where == GRB.Callback.MIPSOL:
            xvals = model.cbGetSolution(model._x)
            thetavals = model.cbGetSolution(model._theta);
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


    # In[10]:


    master.modelSense = GRB.MAXIMIZE
    master.Params.LazyConstraints = 1
    master.optimize(lazy)

    xvals = master.getAttr('X', x)
    print('Optimal objval: %g' % master.ObjVal)
        # print(scen_set)
        # x_sol = np.empty((0), int)
        # for e in G.edges:
        #     if xvals[e] > 1e-5:
        #         edge_index = np.where((edge==e).all(1))[0]
        #         print(edge_index)
        #         x_sol = np.concatenate((x_sol, edge_index), axis=0)
        #         print(x_sol);
    return xvals, master.ObjVal