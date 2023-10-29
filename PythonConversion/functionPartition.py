import numpy as np

def Partition(x_now, newCell, k, p, c_L, c_U, M, y):
    global K_bar, K_newly_added, d, df_cell
    global A1, A2, A3, A4, A5

    # Selecting the arc to split
    arc_split = selectArc(x_now, c_L, c_U, M, y)

    label = df_cell[k, "PI"]
    
    # Calculate ΔL and ΔU
    ΔL, ΔU, arc_split, yL, yU, gL, gU, SP_L, SP_U = ArcSplit(x_now, arc_split, k, c_L, c_U, M, y, label)

    # Create info for the new cell K+1
    cL_newCell = np.copy(c_L)
    cL_newCell[arc_split] += ΔL
    cU_k = np.copy(c_U)
    cU_k[arc_split] -= ΔU

    cL_avg = (c_L + cU_k) / 2
    cU_avg = (cL_newCell + c_U) / 2
    yL, gL, SP_L, T_L, pred_L, label_L, path_L = gx_bound(cL_avg, cL_avg + d * x_now, edge)
    yU, gU, SP_U, T_U, pred_U, label_U, path_U = gx_bound(cU_avg, cU_avg + d * x_now, edge)

    current_p = df_cell[k, "PROB"]

    # Add information for the new cell K+1
    df_cell.loc[newCell] = [newCell, yU, yU, gU, 0, 0, cL_newCell, c_U, current_p * (ΔU / M[arc_split]), label_U]

    # Updating information for the revised cell k
    df_cell.at[k, 'UB'] = cU_k
    df_cell.at[k, 'Y'] = yL
    df_cell.at[k, 'g'] = gL
    df_cell.at[k, 'h'] = 0
    df_cell.at[k, 'PROB'] = current_p * (ΔL / M[arc_split])
    df_cell.at[k, 'PI'] = label_L

    K_newly_added.append(newCell)

    ΔL /= 2
    ΔU /= 2

    return ΔL, ΔU, arc_split, yL, yU, gL, gU, SP_L, SP_U
