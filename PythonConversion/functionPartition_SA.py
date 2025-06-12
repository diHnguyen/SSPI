import numpy as np
import pandas as pd
import importlib
importlib.import_module("functionSelectArc")
from functionSelectArc import selectArc
importlib.import_module("functionArcSplit")
from functionArcSplit import arcSplit
importlib.import_module("functionGbound")
from functionGbound import gx_bound
import time

def Partition(x_now, newCell, k, p, c_L, c_U, M, y,d,edge,origin,destination,Len,A1,A3,df_cell, K_newly_added,calls_SASplit,actual_SASplit, SA_time):
    # global K_bar, K_newly_added, d, df_cell
    # global A1, A2, A3, A4, A5
    # print("\t",k,": Partitioning (inside function)")
    # print("\tNewCell = ", newCell)
    # Selecting the arc to split
    # print("M ", M)
    # print(0, " cL = ", c_L)
    # if k == 1:
        # print("2. ", df_cell['CELL'])
    now = time.time()
    # print("now ", now)
    arc_split = selectArc(x_now, c_L, c_U, M, y,d,edge,origin,destination,A1)
    # print("time ", time.time())
    SA_time = SA_time + (time.time()-now)
    # print("SA_time ", SA_time)
    # print("arc_split ", arc_split, edge[arc_split, :])
    # print("pre slit cL cU", c_L[arc_split], " ", c_U[arc_split])
    # print("df_cell.at[k, PI] ")
    # print(df_cell.at[k, "PI"])
    label = df_cell.at[k, "PI"]
    
    # Calculate ΔL and ΔU
    # c = (c_L + c_U)/2
    # c_g = c + d * x_now
    # y1, _, _, label1, path1 = gx_bound(c, c_g, edge, origin,destination)
    # print("path1 = ", path1)
    # print("labels = ", np.array(label1)[np.array(path1)])
    # sp = np.array([0, 7, 20, 2, 26, 29])
    # y1_arcs = np.where(y1 > 0.1)[0]
    # print("c[sp] = ", c[y1_arcs])
    # print("c_g[sp] = ", c_g[y1_arcs])
    # print("y1 = ", y1_arcs)
    # print("label1[26] ", label1[26])
    # print("label1[29] ", label1[29])
    # print("label1[3] ", label1[3])
    # print("edge[20] ", edge[20])
    # print("c[116] ", c[116])
    # print("c[20] ", c[20])
    # print("c_g[116] = ", c_g[116])
    # print("c_g[20] = ", c_g[20])
    # print("x[116] ", x_now[116])
    # print("x[20] ", x_now[20])
    # print("d[116] ", d[116])
    # print("d[20] ", d[20])
    ΔL, ΔU,calls_SASplit,actual_SASplit = arcSplit(x_now, arc_split, k, c_L, c_U, M, y, label,edge,origin,destination,d,Len,A3,calls_SASplit,actual_SASplit)
    
    # Create info for the new cell K+1
    cL_newCell = np.copy(c_L)
    cL_newCell[arc_split] += ΔL
    cU_k = np.copy(c_U)
    cU_k[arc_split] = cU_k[arc_split] - ΔU
    # print("post slit k+1 cL cU", cL_newCell[arc_split], " ", c_U[arc_split])
    # print("post slit k cL cU", c_L[arc_split], " ", cU_k[arc_split])
    # print("cU_k = ", cU_k)
    # print("2.2")
    # print(df_cell)
    cL_avg = (c_L + cU_k) / 2
    cU_avg = (cL_newCell + c_U) / 2
    yL, gL, SP_L, label_L, path_L = gx_bound(cL_avg, cL_avg + d * x_now, edge, origin,destination)
    
    # print("yL = ", np.where(yL>0.1)[0], " cost ", gL)
    # print("cL_avg = ", cL_avg)
    # print("cL_avg + d * x_now = ", cL_avg + d * x_now)
    yU, gU, SP_U, label_U, path_U = gx_bound(cU_avg, cU_avg + d * x_now, edge, origin,destination)
    # print("label_L ",label_L)
    # print("yU = ", np.where(yU>0.1)[0], " cost ", gU)

    current_p = df_cell.at[k, "PROB"]
    # print("current_p ", current_p)
    # print("(ΔU / M[arc_split]) ", (M[arc_split]))
    # print("TESTING")
    # print(df_cell)
    # Add information for the new cell K+1
    # print("Before update")
    # print(df_cell)
#     df_cell = df_cell.append({'CELL':newCell, 'Y': yU, 'Y_Lk':yU, 'g':gU, 'h':0, 'gL':0, 'LB':cL_newCell, 'UB':c_U, 'PROB':current_p * (ΔU / M[arc_split]), 'PI':label_U},ignore_index=True)
    dtypes = {
        'CELL': int,
        'Y': object,
        'Y_Lk': object,  # Assuming 'Y' contains arrays
        'g': float,
        'h': float,
        'gL': float,
        'LB': object,
        'UB': object,
        'PROB': float,
        'PI': object
    }
    new_row = {
    'CELL': [newCell],
    'Y': [np.array(yU)],
    'Y_Lk': [np.array(yU)],
    'g': [gU],
    'h': [0],
    'gL': [0],
    'LB': [cL_newCell],
    'UB': [c_U],
    'PROB': [current_p * (ΔU / M[arc_split])],
    'PI': [np.array(label_U)]
    }
#     new_row = {'CELL':newCell, 'Y': yU, 'Y_Lk':yU, 'g':gU, 'h':0, 'gL':0, 'LB':cL_newCell, 'UB':c_U, 'PROB':current_p * (ΔU / M[arc_split]), 'PI':label_U}
    df_new_row = pd.DataFrame(new_row, columns=dtypes.keys()).astype(dtypes)
    # print("NEW ROW")
#     print(pd.DataFrame(new_row))
    df_cell = pd.concat([df_cell,df_new_row], axis=0, ignore_index=True)
    df_cell.at[newCell, 'PI'] = label_U
    # print(df_cell)
    # print("2.3")
    # print(df_cell)
    # print("k = ", k)
    # print(df_cell.loc[k-1,:])
    # print("cU_k = ", cU_k)
    # Updating information for the revised cell k
    # print("replace ", df_cell.loc[df_cell.CELL == k,'UB'])
    # print("with ", np.array([cU_k]))
    # print("g ", gL, "; h ", 0, "PROB ", current_p * (ΔL / M[arc_split]))
    # print(    df_cell.loc[df_cell.CELL == k,'UB'])
    # print("Before update df_cell")
    # print(df_cell)
    # print(df_cell.CELL == k)
    # print("/n k = ", k)
    # print("cU_k = ", cU_k)
    # print("df_cell.loc[df_cell.CELL == k,'UB'] ", df_cell.loc[df_cell.CELL == k,'UB'])
    #Don't use .loc -- doesn't update correctly when dealing with array.
    df_cell.at[k,'UB'] = cU_k
    # print("df_cell.loc[df_cell.CELL == k,'UB'][0] ", df_cell.loc[df_cell.CELL == k,'UB'][0])
    df_cell.at[k,'Y'] = yL
    df_cell.at[k,'g'] = gL
    df_cell.at[k,'h'] = 0
    df_cell.at[k,'PROB'] = current_p * (ΔL / M[arc_split])
    df_cell.at[k,'PI'] = label_L
    # print("2. df_cell.at[k,'PI'] ")
    # print(df_cell.at[k,'PI'])
    # print("After update df_cell")
    # print(df_cell)
    K_newly_added.append(newCell)

    ΔL /= 2
    ΔU /= 2
    # print("Inside Partition")
    # print(df_cell)
    return ΔL, ΔU, arc_split, yL, yU, gL, gU, SP_L, SP_U,df_cell,calls_SASplit,actual_SASplit, SA_time
