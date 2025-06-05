import importlib
importlib.import_module("functionGbound")
from functionGbound import gx_bound
import numpy as np
def arcSplit(x_now, arc_split, k, c_L, c_U, M, y, label,edge,origin,destination,d,Len,A3,calls_SASplit,actual_SASplit):
    # global A1, A2, A3, A4, A5, edge, destination, d
    # global K_bar, K_newly_added, d, df_cell
    # print("c_L ", c_L)
    # sp = np.where(y > 0.1)[0]
    # print("\nshortest path = ",sp)
    # print("edges ", edge[sp,:])
    # print("labels ", df_label, " " , len(df_label))
    # print("sp labels ", label[label.node.isin(edge[sp,1])]['label'])

    # for i in label.node:
    #     print(label[label.node==i])
    # print(edge[sp,:])
    c = (c_L + c_U) / 2
    # print("costs ", c[sp])
    # c_g = c + d*x_now
    # print("c_g[sp] = ", c_g[sp])
    mean_split = True
    i = edge[arc_split][0]
    j = edge[arc_split][1]
    # print("selected arc ", arc_split, "; c_L ", c_L[arc_split], "; c_U ", c_U[arc_split])
    # print("Arc (i,j) = (", i,  ", " ,j,")")
    label_i = np.array(label[label.node==i]['label'])[0]
    label_j = np.array(label[label.node==j]['label'])[0]
    # print("label[i] ", label_i, "; label[j] ", label_j)
    # print()
    # print("label[3] ", label[3])
    # d_x = np.array([x*y for x,y in zip(d,x_now)])
    # print("d[sp] ", d_x[sp])
    # print("d[arc_split] * x_now[arc_split]", d[arc_split] * x_now[arc_split])
    if A3 == 0:  # 0=Split using SA if possible
        calls_SASplit = calls_SASplit+1
        into_j = [index for index, edge in enumerate(edge) if edge[1] == j and edge[0] != i]
        # print("into_j ", into_j)
        # print(edge[into_j])
        temp_min = 1e6
        to_compare_arc = 0
        if y[arc_split] > 0.9:  # arc_split in y -- looking for labels/costs to replace (i, j)
            for arc_index in into_j:
                # print("considering arc ", edge[arc_index])
                out_k = edge[arc_index][0]
                # print("out_k ", out_k)
                if len(np.array(label[label.node==out_k]['label'])) > 0:
                    label_k = np.array(label[label.node==out_k]['label'])[0]
                else:
                    label_k = 1e6
                # print("label_k ", label_k)
                # print("c[arc_index] ", c[arc_index])
                temp_c = (c[arc_index] + d[arc_index] * x_now[arc_index]) + label_k#label[out_k]
                # print("temp_c ", temp_c)
                # print("to_compare_arc ", to_compare_arc)
                # print("d[arc_index] * x_now[arc_index] ", d[arc_index] * x_now[arc_index])
                if temp_min > temp_c:
                    temp_min = temp_c
                    to_compare_arc = arc_index
            
            
            max_current_label = (c_U[arc_split] + d[arc_split] * x_now[arc_split]) + label_i #label[i]
            # print("max_current_label ", max_current_label)
            if temp_min < max_current_label - 0.0001:
                ΔU = max_current_label - temp_min
                ΔL = M[arc_split] - ΔU
                mean_split = False
        
        else:  # arc_split not in y -- check directly with labels to see when (i, j) is on the shortest path
            c2 = c.copy()
            c2[arc_split] = c_L[arc_split]
            c2_g = [c2[i] + d[i] * x_now[i] for i in range(Len)]
            # y2, g2, SP2, T2, pred2, label2, path2 = gx_bound(c2, c2_g, edge, origin,destination)
            y2, g2, SP2, label2, path2 = gx_bound(c2, c2_g, edge, origin,destination)
            y_index = [i for i, val in enumerate(y) if val > 0.9]
            y2_index = [i for i, val in enumerate(y2) if val > 0.9]
            y_cost_c2 = sum(y[i] * (c2[i] + d[i] * x_now[i]) for i in range(Len))
            y2_cost_c2 = sum(y2[i] * (c2[i] + d[i] * x_now[i]) for i in range(Len))
            # print(y_index, "y_cost_c2 ", y_cost_c2)
            # print(y2_index,"y2_cost_c2 ", y2_cost_c2)
            ΔL = y_cost_c2 - y2_cost_c2
            # print("ΔL ", ΔL)
            if (ΔL > 0.0001) and (ΔL < M[arc_split] - 0.0001):
                mean_split = False
                ΔU = M[arc_split] - ΔL
    if mean_split == False:
        actual_SASplit = actual_SASplit+1
    if A3 == 1 or mean_split == True:  # 1=Split at mean base cost - we can always do so
        # print(M[arc_split])
        ΔL = M[arc_split] / 2
        ΔU = ΔL
    # print(k, "cL ", c_L[arc_split], "; cU ", c_U[arc_split])
    # print(k, "ΔL ",ΔL,"; ΔU ", ΔU)
    return ΔL, ΔU,calls_SASplit,actual_SASplit