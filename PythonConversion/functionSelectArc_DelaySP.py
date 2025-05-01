import numpy as np
import importlib
importlib.import_module("functionGbound")
from functionGbound import gx_bound
def selectArc_DelaySP(x_now, c_L, c_U, M, y,d,edge,origin,destination,A1):
    # global A1, A2, A3, A4, A5
    # print("A1 ", A1)
    # print("M ", M)
    if A1 == 1:
        # print("M ", M)
        S_k_W = np.where(M == np.max(M))[0]
        # print("S_k_W ", S_k_W)
        arc_split = S_k_W[0]
    else:
        arcs = np.where(y>0)[0]
        # print("\nMULTIPLY")
        # print("arcs ", arcs)
        # print(c_L[arcs])
        
        cW = c_L + M * y
        # print(cW[arcs])
        c_g_W = cW + d * x_now

        # Applying Lemma 2
        yW, gW, SPW, _, _ = gx_bound(cW,c_g_W,edge,origin,destination)
        # print(
        # print("gW ", gW)
        # print("yW ", np.where(yW > 0.5)[0])
        # print("y ", np.where(y > 0.5)[0])
        M_path = np.abs(y - yW) * M
        
        # print("c_U = ", c_U)
        # print("c_L = ", c_L)
        # print("M_path = ", M_path)
        S_k_W = np.where((M_path == np.max(M_path)) & (M_path > 0))[0]
        # print("S_k_W ", S_k_W)
        if len(S_k_W) == 0: 
            arc_split = -1
        else:
            arc_split = S_k_W[0]
        # print("S_k_W ", S_k_W, " ", M[arc_split])
    return arc_split
