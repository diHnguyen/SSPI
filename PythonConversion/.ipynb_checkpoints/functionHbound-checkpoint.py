import gurobipy as gp

def hx_bound(c_L, c_U, d, x_now,edge,origin,destination):
    c = (c_L + c_U) / 2
    M = c_U - c_L
    
    env = gp.Env(empty=True)
    env.setParam("OutputFlag", 0)
    env.start()
    h2 = gp.Model(env=env)
    
    Len = len(c_L)
    all_nodes = list(range(1, Len + 1))
    outgoing = [i for i, node in enumerate(edge) if node[0] == 1]
    
    y2 = h2.addVars(Len, vtype=gp.GRB.CONTINUOUS, name="y2")
    q = h2.addVars(Len, vtype=gp.GRB.CONTINUOUS, name="q")
    
    # Setting constraints for remaining non-sink/start nodes
    h2.addConstr(gp.quicksum(y2[k] for k in outgoing) == 1)
    
    for i in all_nodes:
        if i != destination and i != origin:
            incoming = [k for k, node in enumerate(edge) if node[1] == i]
            outgoing = [k for k, node in enumerate(edge) if node[0] == i]
            h2.addConstr(gp.quicksum(-y2[k] for k in outgoing) + gp.quicksum(y2[k] for k in incoming) == 0)
    
    for i in range(Len):
        h2.addConstr(q[i] >= c[i] - c_L[i] - M[i] * (1 - y2[i]))

    h2.setObjective(gp.quicksum((c_L[i] + d[i] * x_now[i]) * y2[i] + q[i] for i in range(Len)), sense=gp.GRB.MINIMIZE)

    h2.optimize()
    
    y2_values = [y2[i].X for i in range(Len)]
    hx = h2.ObjVal

    return y2_values, hx
