# function Partition(x_now, newCell, k, p, c_L, c_U, M, y, yL)
function Partition(x_now, newCell, k, p, c_L, c_U, M, y)
    global K_bar, K_newly_added, d, df_cell
    # println("Cells ", k," and ", newCell)
    #################################
    #c_bar: vector of mean base cost
    #c_bar_g: vector of mean base cost given interdiction x_now
    c_bar = (c_L+c_U)/2 
    c_bar_g = c_bar + d.*x_now
    ################################
    
    #Find set of M^k_{ij} s.t. (i,j) is in either paths but not both
#     M_path = broadcast(abs,y-yL).*M 
#     println("y = ", findall(y.==1), ": ", sum(c_g.*y))
#     println("yL = ", findall(yL.==1), ": ", sum(c_L.*yL))
    
    #Return arcs indices using Lemma 1
#     S_k = findall((M_path.==maximum(M_path)) .& (M_path.>0))
#     arc_split = 0
#     println("S_k = ", S_k)
#     if isempty(S_k) == false
#         arc_split = S_k[1]
#     else
    
    ##############################
    #cW = worst-case cost with respect to y, i.e., cost of every arc in path y takes max value cU_{ij}; other arcs take min value
    #y = shortest path given mean base cost c_bar
    #c_g_Q = worst-case cost cW (wrt y) plus interdiction cost given x_now
    cW = c_L + M.*y
    c_g_W = cW + d.*x_now
    ##############################
    #APPLYING LEMMA 2: find the set of arcs in A that are in: 
    #  either y (shortest path given mean base cost c-bar, x_now) or y-worst (y-worst wrt y)
    #Get info on path y-worst
    yW, gW, SPW, TW, predW, labelW = gx_bound(cW, c_g_W, edge) #y, gx, SP, T, pred, label, path
    
    #Get info on path y
    y, g, SP, T, pred, label = gx_bound(c_bar, c_bar_g, edge)
    Y = findall(y.> 0.9)
    println("pred ", pred)
    println("label ", label)
    println("Y ", Y)
    M_temp = deepcopy(M)
    found_arc = false
    while found_arc == false
        S_k = findall((M_temp.==maximum(M_temp)) .& (M_temp.>0))
        for arc_index in S_k
            i = edge[arc_index, 1] 
            j = edge[arc_index, 2] 
            if arc_index in Y
                
            else
                #if label j - label i > cL_ij then we can partition 
            end
        end
    
#         println("yW = ", findall(yW.>0))
    #Return set of arcs that are in y-k or y-worst but not both
    #This set should form cycles
    S_k = broadcast(abs,y-yW)
    
    # println(S_k)
    
    
    #Arcs that are in y-k but not y-
    S_k_y = findall((S_k.==1) .& (y.==1))
    S_k_yW = findall((S_k.==1) .& (yW.==1))
    # println("Sky ", S_k_y)
    # println("SkyW ", S_k_yW)
    N_k = []
    for arc in S_k_y
        push!(N_k, edge[arc,1])
        push!(N_k, edge[arc,2])
    end 
    N_kW = []
    for arc in S_k_yW
        push!(N_kW, edge[arc,1])
        push!(N_kW, edge[arc,2])
    end 
    unique!(N_k)
    unique!(N_kW)
    # println("N_k ", N_k)
    # println("N_kW ", N_kW)
    
    s_C_set = intersect(N_k, N_kW)
    # println("s_C_set ", s_C_set)
    # println("Cy ", edge[S_k_y, :])
    # println("CyW ", edge[S_k_yW, :])
    M_path = broadcast(abs,y-yW).*M
    S_k = findall(M_path.>0) #Set of arcs in either yk or yw but not both, and M-val > 0
    S_k_W = findall((M_path.==maximum(M_path)) .& (M_path.>0)) #Find set of candidate arcs, i.e., using Lemma 2 and has largest M-vals
    # println("S_k = ", S_k)
    # println("S_k_W = ", S_k_W)
    
    # println("N_k ", N_k)
    # println("predW_Sk ", predW[N_k])
    # println("labelW_Sk ", labelW[N_k])
    

    arc_split = S_k_W[1]
    # println("arc_split ", arc_split)
    
    n_i = edge[arc_split, 1]
    n_j = edge[arc_split, 2]
    # println("i ", n_i, " u_i ", labelW[n_i])
    # println("j ", n_j, " u_j ", labelW[n_j])
    # println("cL_ij ", c_L[arc_split], " cU_ij ", c_U[arc_split])
    # println("cW_ij ", cW[arc_split])
    s_C = n_i
    
    if arc_split in S_k_y
        # println("in yk")
        while (s_C in s_C_set) == false
        #     trace_arc = findall((edge[:, 1].==pred[s_C]) .& (edge[:, 2].==s_C))[1]
        #     cost_C_y = cost_C_y + c_g_W[trace_arc]
            s_C = pred[s_C] 
        end
    else
        # println("in yW")
        while (s_C in s_C_set) == false
        #     trace_arc = findall((edge[:, 1].==pred[s_C]) .& (edge[:, 2].==s_C))[1]
            s_C = predW[s_C]
        end
    end
    
    # calc_cost_cycle = true
    found_C_y = false
    found_C_yW = false
    cost_C_y = c_g_W[arc_split]
    cost_C_yW = c_g_W[arc_split]
    n_i = s_C
    n_i_W = s_C
    # println("s_C ", s_C)
    
    while (found_C_y == false) || (found_C_yW == false) #calc_cost_cycle
        if found_C_y == false
            for arc in S_k_y
                # println("", arc, edge[arc, :])
                if edge[arc, 1] == n_i 
                    # println("y-arc ", edge[arc, :], " - ", c_g_W[arc])
                    cost_C_y = cost_C_y + c_g_W[arc]
                    n_i = edge[arc, 2]
                    if (n_i != s_C) && (n_i in N_kW)
                        found_C_y = true
                    end
                end
            end
        end
        if found_C_yW == false
            for arc in S_k_yW
                # println("", arc, edge[arc, :])
                if edge[arc, 1] == n_i_W 
                    # println("yW-arc ", edge[arc, :], " - ", c_g_W[arc])
                    cost_C_yW = cost_C_yW + c_g_W[arc]
                    n_i_W = edge[arc, 2]
                    if (n_i_W != s_C) && (n_i_W in N_k)
                        found_C_yW = true
                    end
                end
            end
        end
        # println("cost_C_y ", cost_C_y)
        # println("cost_C_yW ", cost_C_yW)
        # break
    end
#     println("cost_C_y ", cost_C_y)
#     println("cost_C_yW ", cost_C_yW)
#     println("cost_C_y - cost_C_y ", cost_C_y - cost_C_yW, "; vs gap ", c_U[arc_split] -c_L[arc_split])
    
    # println("s_C = ", s_C)
    # println("pi_s_C = ", labelW[s_C])
    
    midSplit = true
    
    if cost_C_y - cost_C_yW < c_U[arc_split] -c_L[arc_split] - 0.05
        midSplit = false
    end
    # println("HERE")
    ΔL = 0
    ΔU = 0
    if midSplit == false
        c_L_L = deepcopy(c_L)  #Revised cell k, c_Lower Bound
        c_L_U = deepcopy(c_U) #Revised cell k, c_Upper Bound
        c_U_L = deepcopy(c_L) #New cell |K|+1, c_Lower Bound
        c_U_U = deepcopy(c_U) #New cell |K|+1, c_Upper Bound
        c_gap = cost_C_y - cost_C_yW
        # println("c_gap ", c_gap)
        # println("(c_U[arc_split] -c_L[arc_split]) ", (c_U[arc_split] -c_L[arc_split]))
        p_new = 1.0
        p_cur = 1.0
        # println("c_L_U[arc_split] ", c_L_U[arc_split])
        # println("c_L_L[arc_split] ", c_L_L[arc_split])
        # println("c_U_U[arc_split] ", c_U_U[arc_split])
        # println("c_U_L[arc_split] ", c_U_L[arc_split])
        # println("c_gap ", c_gap)
        if arc_split in S_k_y #If arc_split is in y_k
            p_new = c_gap/(c_U[arc_split] -c_L[arc_split])
            c_L_U[arc_split] = c_L_U[arc_split] - c_gap
            c_U_L[arc_split] = c_L_U[arc_split] #+ 0.0
            # println("c_L_L[arc_split] ", c_L_L[arc_split])
            # println("c_U_U[arc_split] ", c_U_U[arc_split])
            # println("p_new ", p_new)
            p_cur = 1 - p_new
        else #If arc_split is in y_kW
            p_cur = c_gap/(c_U[arc_split] -c_L[arc_split])
            c_U_L[arc_split] = c_U_L[arc_split] + c_gap
            c_L_U[arc_split] = c_U_L[arc_split] #+ 0.0
            # println("c_L_L[arc_split] ", c_L_L[arc_split])
            # println("c_U_U[arc_split] ", c_U_U[arc_split])
            # println("p_cur ", p_cur)
            p_new = 1 - p_cur
        end
        # println("HERE1")
        
        # println(p_new)
        # println(p_cur)
        p_new = p_new*p
        p_cur = p_cur*p
        cL_avg = (c_L_L + c_L_U)/2
        cU_avg = (c_U_L + c_U_U)/2
        # println("c_L_U[arc_split] ", c_L_U[arc_split])
        # println("c_L_L[arc_split] ", c_L_L[arc_split])
        # println("c_U_U[arc_split] ", c_U_U[arc_split])
        # println("c_U_L[arc_split] ", c_U_L[arc_split])
        
        ΔL = (c_L_U[arc_split] - c_L_L[arc_split])/2
        ΔU = (c_U_U[arc_split] - c_U_L[arc_split])/2
        # println("ΔL ", ΔL)
        # println("ΔU ", ΔU)
        # exit(0)
        yL, gL, SP_L = gx_bound(cL_avg, cL_avg+d.*x_now, edge)
        yU, gU, SP_U = gx_bound(cU_avg, cU_avg+d.*x_now, edge)
        push!(df_cell, (newCell, yU, yU, gU, 0, 0, c_U_L, c_U_U, p_new))
        df_cell[k,:UB] = c_L_U
        df_cell[k,:Y] = yL
        df_cell[k,:g] = gL
        df_cell[k,:h] = 0
        df_cell[k,:PROB] = p_cur
        push!(K_newly_added, newCell)
        # println("Split at ", c_L_U[arc_split], " ", c_U_L[arc_split])
    else
        # println("HERE2")
        M_ = zeros(Len)
        M_[arc_split] = M[arc_split]/2
        ΔL = M[arc_split]/4
        ΔU = ΔL
        cL_avg = (c_L+c_U-M_)/2
        cU_avg = (c_L+M_+c_U)/2
        # println("HERE3")
        yL, gL, SP_L = gx_bound(cL_avg, cL_avg+d.*x_now, edge)
        yU, gU, SP_U = gx_bound(cU_avg, cU_avg+d.*x_now, edge)
        push!(df_cell, (newCell, yU, yU, gU, 0, 0, c_L+M_, c_U, p/2))
        # println("HERE4")
        df_cell[k,:UB] = c_U-M_
        df_cell[k,:Y] = yL
        df_cell[k,:g] = gL
        df_cell[k,:h] = 0
        df_cell[k,:PROB] = p/2
        push!(K_newly_added, newCell)
        # println("Split at ", c_U[arc_split]-M_[arc_split])
    end
    # println("DONE")
    return ΔL, ΔU, arc_split, yL, yU, gL, gU, SP_L, SP_U
end
