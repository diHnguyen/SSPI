import numpy as np

def getPathCost(P_set,x_now,c,d,k):#,origin,destination
    Pk = []
    Pk_cost = 10e6
    c_g = c + np.array(d)*np.array(x_now)
    print("Inside getpathcost")
    for P in P_set:
        P_arcs = np.where(P > 0.5)[0]
        print("P_arcs = ", P_arcs, " costs ", sum(c_g[a] for a in P_arcs))
        if sum(c_g[a] for a in P_arcs) < Pk_cost:
            Pk = P
            Pk_cost = sum(c_g[a] for a in P_arcs)
    Pk_arcs = np.where(Pk > 0.5)[0]
    SP = sum(c[a] for a in Pk_arcs)     
    
#     u = origin
#     v = destination
#     label = 
#     while Pk_arcs.size != 0:
#         for arc in Pk_arcs:
#             if u == edge[arc][0]:
                
                
#                 c = np.setdiff1d(a,b)
    
    
    
    return Pk, Pk_cost, SP
        
    
    