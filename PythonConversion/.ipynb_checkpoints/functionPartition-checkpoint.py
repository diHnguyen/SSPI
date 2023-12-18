import numpy as np
import importlib
importlib.import_module("functionSelectArc")
from functionSelectArc import selectArc
importlib.import_module("functionArcSplit")
from functionArcSplit import arcSplit
importlib.import_module("functionGbound")
from functionGbound import gx_bound

def Partition(x_now, newCell, k, p, c_L, c_U, M, y,d,edge,origin,destination,Len,A1,A3,df_cell, K_newly_added):
    # global K_bar, K_newly_added, d, df_cell
    # global A1, A2, A3, A4, A5

    # Selecting the arc to split
    arc_split = selectArc(x_now, c_L, c_U, M, y,d,edge,origin,destination,A1)

    label = df_cell.loc[k-1, "PI"][0]
    
    # Calculate ΔL and ΔU
    ΔL, ΔU = arcSplit(x_now, arc_split, k, c_L, c_U, M, y, label,edge,origin,destination,d,Len,A3)

    # Create info for the new cell K+1
    cL_newCell = np.copy(c_L)
    cL_newCell[arc_split] += ΔL
    cU_k = np.copy(c_U)
    cU_k[arc_split] -= ΔU

    cL_avg = (c_L + cU_k) / 2
    cU_avg = (cL_newCell + c_U) / 2
    yL, gL, SP_L, T_L, pred_L, label_L, path_L = gx_bound(cL_avg, cL_avg + d * x_now, edge, origin,destination)
    print("yL = ", yL)
    print("cL_avg = ", cL_avg)
    print("cL_avg + d * x_now = ", cL_avg + d * x_now)
    yU, gU, SP_U, T_U, pred_U, label_U, path_U = gx_bound(cU_avg, cU_avg + d * x_now, edge, origin,destination)
    print("label_L ",label_L)
    
    current_p = df_cell.loc[k-1, "PROB"]
    # Add information for the new cell K+1
    df_cell = df_cell.append({'CELL':newCell, 'Y': [yU], 'Y_Lk':[yU], 'g':gU, 'h':0, 'gL':0, 'LB':[cL_newCell], 'UB':[c_U], 'PROB':current_p * (ΔU / M[arc_split]), 'PI':[label_U]},ignore_index=True)
    
    print(df_cell)
    print("k = ", k)
    # print(df_cell.loc[k-1,:])
    print("cU_k = ", cU_k)
    # Updating information for the revised cell k
    # print("replace ", df_cell.loc[df_cell.CELL == k,'UB'])
    # print("with ", np.array([cU_k]))
    # print("g ", gL, "; h ", 0, "PROB ", current_p * (ΔL / M[arc_split]))
    df_cell.loc[df_cell.CELL == k,'UB'][0] = [cU_k]
    
    df_cell.loc[df_cell.CELL == k,'Y'][0] = [yL]
    df_cell.loc[df_cell.CELL == k,'g'] = gL
    df_cell.loc[df_cell.CELL == k,'h'] = 0
    df_cell.loc[df_cell.CELL == k,'PROB'] = current_p * (ΔL / M[arc_split])
    df_cell.loc[df_cell.CELL == k,'PI'][0] = [label_L]
    print(df_cell)
    K_newly_added.append(newCell)

    ΔL /= 2
    ΔU /= 2

    return ΔL, ΔU, arc_split, yL, yU, gL, gU, SP_L, SP_U
