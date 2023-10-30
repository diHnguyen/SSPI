def selectArc(x_now, c_L, c_U, M, y):
    global A1, A2, A3, A4, A5

    if A1 == 1:
        S_k_W = np.where(M == np.max(M))[0]
        arc_split = S_k_W[0]
    else:
        cW = c_L + M * y
        c_g_W = cW + d * x_now

        # Applying Lemma 2
        yW, gW, SPW, _, _, _, _ = gx_bound(cW, c_g_W, edge)
        M_path = np.abs(y - yW) * M
        S_k_W = np.where((M_path == np.max(M_path)) & (M_path > 0))[0]
        arc_split = S_k_W[0]

    return arc_split
