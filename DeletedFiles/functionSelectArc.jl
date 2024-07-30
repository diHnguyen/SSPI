function selectArc(x_now, c_L, c_U, M, y)
    global A1, A2, A3, A4, A5
    if A1 == 1
        S_k_W = findall(M.==maximum(M))
        arc_split = S_k_W[1]
    else
        cW = c_L + M.*y
        c_g_W = cW + d.*x_now
        #Applying Lemma 2
        yW, gW, SPW = gx_bound(cW, c_g_W, edge)
        # println("yW = ", findall(yW.>0.9))
        M_path = broadcast(abs,y-yW).*M
        S_k_W = findall((M_path.==maximum(M_path)) .& (M_path.>0))
        # println("S_k_W = ", S_k_W)
        arc_split = S_k_W[1]
    end
    return arc_split
end