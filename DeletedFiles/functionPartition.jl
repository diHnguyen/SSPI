# function Partition(x_now, newCell, k, p, c_L, c_U, M, y, yL)
function Partition(x_now, newCell, k, p, c_L, c_U, M, y)
    global K_bar, K_newly_added, d, df_cell
    global A1, A2, A3, A4, A5
        # #Applying Lemma 2
        # yW, gW, SPW = gx_bound(cW, c_g_W, edge)
        # # println("yW = ", findall(yW.>0.9))
        # M_path = broadcast(abs,y-yW).*M
        # S_k_W = findall((M_path.==maximum(M_path)) .& (M_path.>0))
        # # println("S_k_W = ", S_k_W)
    arc_split = selectArc(x_now, c_L, c_U, M, y) #S_k_W[1]
    # println("\nk=", k," ; ",arc_split)
    # println("c_orig = [", c_L[arc_split], " \t", c_U[arc_split],"]")
    
#     end
    
    label = df_cell[k,:PI]
    #ΔL=M-gap of arc_split for revised k 
    #ΔU=M-gap of arc_split for new cell k+1
    #ΔL+ΔL = original k's M-gap of arc_split 
    ΔL, ΔU = ArcSplit(x_now,arc_split,k,c_L, c_U, M,y, label)
    
    #Create info for new cell |K|+1
    cL_newCell = deepcopy(c_L)
    cL_newCell[arc_split] = cL_newCell[arc_split] + ΔL 
    cU_k = deepcopy(c_U)
    cU_k[arc_split] = cU_k[arc_split] - ΔU 
    # M_ = zeros(Len)
    # println("\t k: ", c_L[arc_split], " \t", cU_k[arc_split])
    # println("\t |K|+1: ", cL_newCell[arc_split], " \t", c_U[arc_split])
    
    
    cL_avg = (c_L+cU_k)/2
    cU_avg = (cL_newCell+c_U)/2
    yL, gL, SP_L, T_L, pred_L, label_L, path_L = gx_bound(cL_avg, cL_avg+d.*x_now, edge)
    yU, gU, SP_U, T_U, pred_U, label_U, path_U = gx_bound(cU_avg, cU_avg+d.*x_now, edge)

    current_p = df_cell[k,:PROB]
    #Add to df info for new cell K+1
    push!(df_cell, (newCell, yU, yU, gU, 0, 0, cL_newCell, c_U, current_p*(ΔU/M[arc_split]), label_U))
    # println(df_cell[newCell,:])
    #Updating Info for revised cell k
    df_cell[k,:UB] = cU_k
    df_cell[k,:Y] = yL
    df_cell[k,:g] = gL
    df_cell[k,:h] = 0
    df_cell[k,:PROB] = current_p*(ΔL/M[arc_split]) #p/2
    df_cell[k,:PI] = label_L
    # println(df_cell[k,:])
    push!(K_newly_added, newCell)

    # break
    # exit()
    ΔL = ΔL/2
    ΔU = ΔU/2
    return ΔL, ΔU, arc_split, yL, yU, gL, gU, SP_L, SP_U
end
