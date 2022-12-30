
#     println(min_gLk,", ",max_gUk)
#     println("df_cell = ")
#     println(df_cell)
#     if length(K) == length(K_removed)#isempty(K) == true
#         @constraint(m, sum(x_now[i]*x[i] for i=1:Len) <= b-1)
#         println("Check beta-CVar")
#         df_cellPoly = DataFrame(CELL = Int64[], df = Any[], NUMPOLY = Int64[], DETSHIFT = Float64[])
#         K_removed = [] 
#         println("K = ", K)
#         for k in K# 1:3 #length(df_cell)
#             cL = df_cell[k,:LB]
#             cU = df_cell[k,:UB]
#             y = df_cell[k,:Y]
#             Len = length(cL)
#             println("\nCell ", k)
#             unc_arcs = findall((y.>0) .& (cL.<cU))
#             det_arcs = findall((y.>0) .& (cL.==cU))
#             println("unc_arcs = ", unc_arcs)
#             println("det_arcs = ", det_arcs)
            
#             if isempty(det_arcs) == false
#                 det_Shift = sum(cL[i] for i in det_arcs)
#             else
#                 det_Shift = 0
#             end
#         #     det_arcs = findall((Y.>0) .& (cL.==cU))
#         #     filter!(x-> !(x in unc_arcs), det_arcs)
#         #     det_Shift = 0
#             if length(unc_arcs) > 0
                
#                 df, numPoly = Convolve(cL, cU, Len, unc_arcs)

#             #     df[:,:leftShift] = df[:,:leftShift] .+ det_Shift
#                 df.w = zeros(numPoly)
#                 println(df)
#                 push!(df_cellPoly, (k,df,numPoly, det_Shift))
#             else
#                 push!(df_cellPoly, (k,DataFrame(),-1, det_Shift))
#             end
#         end
#         println(df_cell[:,:PROB])
#         println(df_cellPoly)
# #         break
#         temp_CVaR = FindCVaR(β,α_now,min_gLk,max_gUk,df_cellPoly, df_cell[:,:PROB])
#         if LB < temp_CVaR 
#             LB = temp_CVaR    
#             x_sol = x_now
#             α_sol = α_now
#             z_sol = z_now
#         end
#     end
#     if iter > 6
#         println("Break early...")
#         terminate_cond = true
#         K_removed = copy(K)
#         break
#     end

function FindCVaR(α_now, α_L, α_U, df_cellPoly)
    global β, df_cell, LB
    pCell = df_cell.PROB
    cellNum = nrow(df_cell)
    K = df_cell.CELL
    
    eVaR = -0.1 #Changes made here
    W = -1
    V = 0
    
    #The original
    VaR = α_now
#     println("1-β = ", 1-β)
#     println("1-β - W = ", 1-β-W)
    iter = 1
    lastVaR = -0.5
    W_k = zeros(cellNum)
#     while abs(1-β - W) > tol
#     println("[α_L, α_U] = ", α_L," , ", α_U)
    while α_U - α_L > eVaR
#         println(VaR, "Range in [",α_L,",",α_U,"]")
        eVaR = 0.1 #Changes made here
        W = 0
        for k in K
            df = df_cellPoly[k,:df]
            numPoly = df_cellPoly[k,:NUMPOLY]
            det_Shift = df_cellPoly[k,:DETSHIFT]
            W_k[k] = 0
#             if k == 4
#                println("", df) 
#                 println("det_Shift = ", det_Shift)
#             end
#             println("Cell ",k)
            if numPoly == 0 #Changes made here
                if det_Shift <= VaR
                    W_k[k] = 1 #Changes made here
                end
            else
#                 W_k[k] = 0
                for i = 1:numPoly
                    r_l = df[i,:l]
                    r_u = df[i,:u]
                    rightShift = df[i,:leftShift]
                    poly = df[i,:Poly]
                    p_poly = integrate(poly)
                    w_i = 0
                    
                    if r_l + rightShift + det_Shift <= VaR  #df[i,:leftShift]
                        if (lastVaR < r_u + rightShift + det_Shift) || (VaR < r_u + rightShift+ det_Shift)
#                             println("VaR - rightShift - det_Shift = ", VaR-rightShift- det_Shift)
                            poly = df[i,:Poly]
                            p_poly = integrate(poly)  
                            
                            #One of these two is correct:
                            #1
                            u = min(VaR-rightShift-det_Shift, r_u) 
                            #2
#                             u = min(VaR-rightShift-det_Shift, r_u) 
                            
                            w_i = p_poly(u) - p_poly(r_l)
                            df[i,:w] = w_i
                           
                        else
                            w_i = df[i,:w]
                        end
                    end
                    W_k[k] = W_k[k] + w_i 
#                     println("Integrate (", poly, ") from ", r_l," to ", r_u, " yields ", W_k[k])
                end
                
            end
#             println("Cell ", k,": W_k = ", W_k[k])
            W = W + W_k[k]*pCell[k]

        end
        
#         println("\nVaR Guess = ", VaR, " in [",α_L,",",α_U,"]")
#         println("W current = ", W)
#         println("W = ", W)
        lastVaR = VaR
#         println("Update bounds on nu")
#         println("VaR = ", VaR)
#         println("Current: [",α_L,",",α_U,"]")
        if W <= 1-β #VaR > α_L && 
            α_L = VaR
        end
        if W >= 1-β #VaR < α_U && 
            α_U = VaR
        end
#         if α_U - α_L > eVaR #abs(1-β - W) > eVaR
        VaR = (α_U + α_L)/2
    end
    # HERE LASTTTTTTTT: ADDED THE FOR LOOP OVER K:
    
        W = 0
        for k in K
            df = df_cellPoly[k,:df]
            numPoly = df_cellPoly[k,:NUMPOLY]
            det_Shift = df_cellPoly[k,:DETSHIFT]
            W_k[k] = 0
#             if k == 4
#                println("", df) 
#                 println("det_Shift = ", det_Shift)
#             end
#             println("Cell ",k)
            if numPoly == 0 #Changes made here
                if det_Shift <= VaR
                    W_k[k] = 1 #Changes made here
                end
            else
#                 W_k[k] = 0
                for i = 1:numPoly
                    r_l = df[i,:l]
                    r_u = df[i,:u]
                    rightShift = df[i,:leftShift]
                    poly = df[i,:Poly]
                    p_poly = integrate(poly)
                    w_i = 0
                    
                    if r_l + rightShift + det_Shift <= VaR  #df[i,:leftShift]
                        if (lastVaR < r_u + rightShift + det_Shift) || (VaR < r_u + rightShift+ det_Shift)
#                             println("VaR - rightShift - det_Shift = ", VaR-rightShift- det_Shift)
                            poly = df[i,:Poly]
                            p_poly = integrate(poly)  
                            
                            #One of these two is correct:
                            #1
                            u = min(VaR-rightShift-det_Shift, r_u) 
                            #2
#                             u = min(VaR-rightShift-det_Shift, r_u) 
                            
                            w_i = p_poly(u) - p_poly(r_l)
                            df[i,:w] = w_i
                           
                        else
                            w_i = df[i,:w]
                        end
                    end
                    W_k[k] = W_k[k] + w_i 
                end
                
            end
            W = W + W_k[k]*pCell[k]
        end
	
#     println("Final β-VaR = ", VaR, " in [",α_L,",",α_U,"]")
#     println("1-β = ", 1-β)
#     println("Final W = ", W)
#     println("W_k = ", W_k)
    V=0
    total_p = 0
    V_k = zeros(cellNum)
    for k in K #Replace with the size of K here
        numPoly = df_cellPoly[k,:NUMPOLY] #Changes made here
        det_Shift = df_cellPoly[k,:DETSHIFT] #Changes made here
        if numPoly == 0 #Changes made here
            if det_Shift <= VaR #Changes made here
                V_k[k] = det_Shift #Changes made here
            else 
                V_k[k] = 0 #Changes made here
            end 
        else #Changes made here
            if W_k[k] > 0
                df = df_cellPoly[k,:df]
#                 numPoly = df_cellPoly[k,:NUMPOLY]
#                 det_Shift = df_cellPoly[k,:DETSHIFT]
                V = 0
                for i = 1:numPoly
                    r_l = df[i,:l]
                    r_u = df[i,:u]
                    rightShift = df[i,:leftShift]
                    poly = df[i,:Poly]
                    if r_l + rightShift + det_Shift <= VaR 
    #                     println("Assessing V, poly ", i)
                        u = min(VaR-rightShift-det_Shift, r_u) 
    #                     println(poly)
    #                     println(fromroots([-(rightShift+det_Shift)]))
                        e_poly = integrate(poly*fromroots([-(rightShift+det_Shift)]))
                        v_i = e_poly(u) - e_poly(r_l)
                        V = V + v_i 
                    end

                end
                V_k[k] = V
    #             println(k,". V_k = ", V_k[k], "; W_k = ", W_k[k], "; p_k = ", pCell[k])
            end
        end
    end
    bCVaR = sum(V_k[k]*pCell[k] for k in K)/sum(W_k[k]*pCell[k] for k in K)
    #println("W = ", W)
    if abs(W - (1-β)) > eVaR 
        bCVaR = (sum(V_k[k]*pCell[k] for k in K) - VaR*(W - 1+β))/(1-β)
        #println("Adjusted ", bCVaR, "; W = ", W)
        W = 1-β
    end
	#println("β-CVaR = ", bCVaR,"; W = ", W, " vs. LB = ", LB, "; abs = ", abs(W - 1+β)) 
    return bCVaR, W
end