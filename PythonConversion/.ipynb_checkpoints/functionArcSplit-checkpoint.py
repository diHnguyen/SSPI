def arc_split(x_now, arc_split, k, c_L, c_U, M, y, label):
    global A1, A2, A3, A4, A5, edge, destination, d
    # global K_bar, K_newly_added, d, df_cell

    c = (c_L + c_U) / 2
    mean_split = True
    i = edge[arc_split][0]
    j = edge[arc_split][1]

    if A3 == 0:  # 0=Split using SA if possible
        into_j = [index for index, edge in enumerate(edge) if edge[1] == j and edge[0] != i]
        temp_min = 1e6
        to_compare_arc = 0

        if y[arc_split] > 0.9:  # arc_split in y -- looking for labels/costs to replace (i, j)
            for arc_index in into_j:
                out_k = edge[arc_index][0]
                temp_c = (c[arc_index] + d[arc_index] * x_now[arc_index]) + label[out_k]

                if temp_min > temp_c:
                    temp_min = temp_c
                    to_compare_arc = arc_index

            max_current_label = (c_U[arc_split] + d[arc_split] * x_now[arc_split]) + label[i]

            if temp_min < max_current_label - 0.0001:
                ΔU = max_current_label - temp_min
                ΔL = M[arc_split] - ΔU
                mean_split = False

        else:  # arc_split not in y -- check directly with labels to see when (i, j) is on the shortest path
            c2 = c.copy()
            c2[arc_split] = c_L[arc_split]
            c2_g = [c2[i] + d[i] * x_now[i] for i in range(len(d))]
            y2, g2, SP2, T2, pred2, label2 = gx_bound(c2, c2_g, edge)
            y_index = [i for i, val in enumerate(y) if val > 0.9]
            y2_index = [i for i, val in enumerate(y2) if val > 0.9]
            y_cost_c2 = sum(y[i] * (c2[i] + d[i] * x_now[i]) for i in range(len(d))
            y2_cost_c2 = sum(y2[i] * (c2[i] + d[i] * x_now[i]) for i in range(len(d))

            ΔL = y_cost_c2 - y2_cost_c2

            if (ΔL > 0.0001) and (ΔL < M[arc_split] - 0.0001):
                mean_split = False
                ΔU = M[arc_split] - ΔL

    if A3 == 1 or mean_split == True:  # 1=Split at mean base cost - we can always do so
        ΔL = M[arc_split] / 2
        ΔU = ΔL

    return ΔL, ΔU