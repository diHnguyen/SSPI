import numpy as np
import networkx as nx;
import gurobipy as gp;
from gurobipy import GRB;
import importlib
from scipy import stats
importlib.import_module("functionGbound")
from functionGbound import gx_bound

def getSAABounds(x_now, MP_obj, c_L, c_U,d,edge,origin,destination, delta2):
    # scens=[];
    # for k in range(num_cases):
    #     scen = {};
    #     for e in G.edges:
    #         scen[e] = np.random.uniform(G.edges[e]['costLB'],G.edges[e]['costUB']);
    #     scens.append(scen);

    ###############################
    #Set Margin of Error = 1/10 of delta2 wrt ObjVal
    # MOE = (delta2)/2 #/MP_obj
    
    
    ###############################
    #This part is used to find stdev
    n = 5000
    # c_L,c_U,_,_,_,_ = getCellInfo(k, x_now, "c_g", d,  df_cell) #M, c, c_g, Y_k
    SP_costs = np.zeros(n)
    for i in range(n):
        c = np.random.uniform(c_L,c_U)
        c_g = c + np.array(d)*np.array(x_now)
        y, gx, SP, label, path = gx_bound(c, c_g, edge,origin,destination)
        # print("\ty ", np.where(y > 0.5)[0])
        # print("\tc_L ", c_L[np.where(y > 0.5)[0]])
        # print("\tc_U ", c_U[np.where(y > 0.5)[0]])
        SP_costs[i] = gx

    #Check .std make sure it's for sample
    # print("SP_costs ", SP_costs)
    SP_stdev = np.std(SP_costs, ddof=1) 

    # # if SP_stdev > 0:
    #     ###############################
    #     #Find number of samples needed
    # z_score = 2.5758293035489004 #99%, alpha = 0.01
    # print("MOE = ", MOE)
    # print("SP_stdev = ", SP_stdev)
    # n = int(np.ceil((z_score*SP_stdev/MOE)**2))
    # print("Calc sample size ", n)
    # SP_costs = np.zeros(n)
    # for i in range(n):
    #     c = np.random.uniform(c_L,c_U)
    #     c_g = c + np.array(d)*np.array(x_now)
    #     y, gx, SP, label, path = gx_bound(c, c_g, edge,origin,destination)
    #     SP_costs[i] = gx
    SP_mean = SP_costs.mean()
    # SP_stdev = SP_costs.mean()

    t_score = stats.t.ppf(1-0.01/2, n)
    one_sided_CI = t_score*(SP_stdev/np.sqrt(n))
    # else:
    # [SP_mean - one_sided_CI, gx]
        
    
    return SP_mean, one_sided_CI