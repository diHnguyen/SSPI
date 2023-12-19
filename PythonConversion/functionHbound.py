import gurobipy as gp
import numpy as np
def hx_bound(c_L, c_U, d, x_now,edge,origin,destination):
    c = (c_L + c_U) / 2
    M = c_U - c_L
    # print("d = ", d)
    # print("c_L = ", c_L)
    # print("M = ", M)
    env = gp.Env(empty=True)
    env.setParam("OutputFlag", 0)
    env.start()
    h2 = gp.Model(env=env)
    
    Len = len(c_L)
    all_nodes = list(range(destination))
    # outgoing = [i for i, node in enumerate(edge) if node[0] == 1]
    outgoing = np.where(edge[:, 0] == origin)[0]
    # print("outgoing ", outgoing)
    # print("all_nodes ", all_nodes)
    y2 = h2.addVars(Len, vtype=gp.GRB.CONTINUOUS, name="y2")
    q = h2.addVars(Len, vtype=gp.GRB.CONTINUOUS, name="q")
    
    # Setting constraints for remaining non-sink/start nodes
    h2.addConstr(sum(y2[k] for k in outgoing) == 1)
    
    for i in all_nodes:
        # print("\nnode ", i)
        if i != destination and i != origin:
            # incoming = [k for k, node in enumerate(edge) if node[1] == i]
            # outgoing = [k for k, node in enumerate(edge) if node[0] == i]
            incoming = np.where(edge[:, 1] == i)[0]
            outgoing = np.where(edge[:, 0] == i)[0]
            # print("incoming ", incoming)
            # print("outgoing ", outgoing)
            h2.addConstr(sum(-y2[k] for k in outgoing) + sum(y2[k] for k in incoming) == 0)
    
    for i in range(Len):
        h2.addConstr(q[i] >= c[i] - c_L[i] - M[i] * (1 - y2[i]))

    h2.setObjective(sum((c_L[i] + d[i] * x_now[i]) * y2[i] + q[i] for i in range(Len)), sense=gp.GRB.MINIMIZE)

    h2.optimize()
    
    y2_values = [y2[i].X for i in range(Len)]
    # print("y2_values ", y2_values)
    hx = h2.ObjVal

    return y2_values, hx
