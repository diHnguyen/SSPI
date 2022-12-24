# function Partition(x_now, newCell, k, p, c_L, c_U, M, y, yL)
function Partition(x_now, newCell, k, p, c_L, c_U, M, y)
    global K_bar, K_newly_added, d, df_cell
    
#     c_g = (c_L+c_U) + d.*x_now
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
        cW = c_L + M.*y
        c_g_W = cW + d.*x_now
        
        #Applying Lemma 2
        yW, gW, SPW = gx_bound(cW, c_g_W, edge)
#         println("yW = ", findall(yW.>0))
        M_path = broadcast(abs,y-yW).*M
        S_k_W = findall((M_path.==maximum(M_path)) .& (M_path.>0))
#         println("S_k_W = ", S_k_W)
        arc_split = S_k_W[1]
#     end
    
#     println("arc_split = ", arc_split)
#     println("M[arc_split] = ", M[arc_split])
    M_ = zeros(Len)
    M_[arc_split] = M[arc_split]/2
    Δ = M[arc_split]/4
#         println("cU = ", cU)
#         println("c+ = ", cL+M_)
#         println("c- = ", cU-M_)
#         println("cL = ", cL)
#         println("arc_split = ", arc_split)
#     println("Split cell ", k, " on arc ", arc_split, " at ", c_L[arc_split],"--",c_L[arc_split]+M_[arc_split], "--", c_U[arc_split])
    cL_avg = (c_L+c_U-M_)/2
    cU_avg = (c_L+M_+c_U)/2
    yL, gL, SP_L = gx_bound(cL_avg, cL_avg+d.*x_now, edge)
    yU, gU, SP_U = gx_bound(cU_avg, cU_avg+d.*x_now, edge)
#     println(k,". ", gL, "yL = ", findall(yL.>0))
#     println(newCell,". ", gU, "yU = ", findall(yU.>0))
#     println()
#         println("g revised k = ", gL)
#         println("g  = ", gU)
#     println(df_cell)
    push!(df_cell, (newCell, yU, yU, gU, 0, 0, c_L+M_, c_U, p/2))
#     println("Here")
    df_cell[k,:UB] = c_U-M_
    df_cell[k,:Y] = yL
    df_cell[k,:g] = gL
    df_cell[k,:h] = 0
    df_cell[k,:PROB] = p/2
    push!(K_newly_added, newCell)
    
#         println("Done.")
#     end
#     println("Inside partition")
#     println("Δ = ", Δ)
#     push!(K_partition, newCell)
    return Δ, arc_split, yL, yU, gL, gU, SP_L, SP_U
end
