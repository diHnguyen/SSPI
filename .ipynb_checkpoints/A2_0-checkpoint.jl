while terminate_cond == false 
    global α, iter, total_time, K_bar, K_newly_added, K_removed, LB, MP_obj, con_num, newCell , LB_w, p
    global x_sol, z_sol, α_sol, last_x, x_now, α_now,z_now, terminate_cond
    global start
    while isempty(K_bar) == false #length(K_bar) > K
        iter = iter + 1
        optimize!(m) 
       # println("\nIter : ", iter," ; LB = ", LB)
#         println(m)
#         println("", df_cell)
#         K = vcat(K, K_newly_added)

        if termination_status(m) == MOI.OPTIMAL
            MP_obj = JuMP.objective_value.(m)
            x_now = JuMP.value.(x)
            # α_now = JuMP.value.(α)
            z_now = JuMP.value.(z)
            println("\nIter : ", iter," ; MP_obj = ", MP_obj, " ; ", newCell, " time ", time()-start)
            # println("length K_bar ", length(K_bar))
            # println("K_bar : ", K_bar)
            # if newCell > 500
            #     println(iter, " : ", length(K_bar),"/", newCell, " - ", time()-start)
            # end
            println("x = ", findall(x_now.>0))
        end
        # if iter > 7
        #     terminate_cond = true
        #     K_bar = []
        # end
        # if termination_status(m) != MOI.OPTIMAL || MP_obj <= LB
        #     terminate_cond = true
        #     K_bar = []
        # else
        O1Flag = true
        if last_x != x_now
            # consec_x = 1
            K_bar = collect(1:newCell)
            last_x = x_now
            for k in K_bar #_partition  
                c_L, c_U, M, c, c_g = getCellInfo(k, x_now, "c_g")
                y, gx, SP = gx_bound(c, c_g, edge) #áy, gx, SP, T, pred, label, path
                df_cell[k,:g] = gx
                df_cell[k,:Y] = y
                if z_now[k] - gx > delta1
                    con_num = con_num + 1 
                    push!(df_constraints, (con_num, k, y, SP))
                    constr[con_num] = @constraint(m, z[k] <= sum(d[i]*y[i]*x[i] for i = 1:Len) + SP) 
                    O1Flag = false
                end
            end
        else 
            # consec_x = consec_x + 1
        end
        
        myCounter = 0
        if O1Flag == true 
            for k_1 in K_bar
                # global partitionCounter, myCounter
                # println("\tOuter K_bar Cell k_1 = ", k_1)
                myCounter = 0
                # partitionCounter = 1
                K_k = [k_1]
                continuePartition = true
                y_parent_k1 = df_cell[k_1, :Y]
                # println("\t****Begin Inner Partition***")
                while continuePartition == true #myCounter < partitionCounter 
                    # myCounter
                    myCounter = myCounter + 1
                    # println("\t", myCounter,"-split") #, " for K_k = ", K_k)
                    # if myCounter > 2
                    #     continuePartition = false
                    # end
                    # if isempty(K_k) == true
                    #    continuePartition = false 
                    # end
                    for k in K_k
                        # println("counter", myCounter, " K_k = ", K_k)
                        # global partitionCounter, myCounter
                        c_L, c_U, M, c, c_g_L, yK = getCellInfo(k, x_now, "c_g_L")
                        #Solving for g(\hat{x}, c^{L,k})
                        yL, gL, SPL = gx_bound(c, c_g_L, edge) #y, gx, SP, T, pred, label, path
                        df_cell[k,:Y_Lk] = yL
                        df_cell[k,:gL] = gL

                        #Verify against OC2
                        local y_h
                        y_h, hx = hx_bound(c_L, c_U, d, x_now)
                        p_k = df_cell[k,:PROB]
                        df_cell[k,:h] = hx
                        gx = df_cell[k,:g] 

                        # println("\tInner Cell ", k, ". gx = ", gx, "; hx = ", hx)
                        #Verify against OC3
                        if gx - hx <= delta2
                            push!(K_removed,k)
                            # continutePartition = false
                            # println("\tInner Cell ", k, ". gx = ", gx, "; hx = ", hx)
                        else
                            
                            # global partitionCounter, myCounter
                            # if myCounter == 1
                            #     partitionCounter = max(1, trunc(Int, log2((gx-hx)))) #delta2=2
                            # end
                            # local partitionCounter
                            newCell = newCell + 1 #nrow(df_cell)+1
                            # println("\tInner Cell ", k, " (-->", newCell,") . gx = ", gx, "; hx = ", hx)
                            # println("\t --   Cell ", k," becomes: ", k, ", ", newCell) 
                            ΔL, ΔU, arc_split, yL, yU, gL, gU, SP_L, SP_U = Partition(x_now, newCell, k, p_k, c_L, c_U, M, df_cell[k,:Y])
                            # if myCounter > 1
                            # println("\t...childCells y: ", y_parent_k1 != yL, " ",y_parent_k1 != yU)
                            if y_parent_k1 != yL || y_parent_k1 != yU
                               continuePartition = false 
                            end
                            # end
                            #Updating constraints in MP:

                            #Query rows from df_constraints that satisfy:
                            #(a) CELL column = k, and
                            #(b) Y column uses path that has arc # =  arc_split 
                            df_temp_k = df_constraints |> 
                            @filter(_.CELL == k)|> DataFrame ##Only copy `active' paths
                            add_yL = true #Turns false if path yL is in cell k's existing constraints
                            add_yU = true #Turns false if path yU is in cell k's existing constraints
                            existingPath = false

                            #LOOP THRU ALL ROWS IN DF ASSOCIATED WITH k
                            #Update RHS of affected constraints in k
                            #Copy each constraint in k to |K|+1

                            for dfRow in eachrow(df_temp_k) #constr_of_k 
                                Y_k = dfRow.Y
                                if Y_k == yL #Found yL in the current P-set
                                    add_yL = false
                                end
                                if Y_k == yU #Found yU in the current P-set
                                    add_yU = false
                                end

                                newCell_RHS = dfRow.SP

                                #ONLY UPDATE RHS IF ARC SPLIT IS ON THAT PATH  
                                if Y_k[arc_split] == 1
                                    conRef = dfRow.NUM
                                    newCell_RHS = newCell_RHS + ΔU #gap #FIND NEW RHS OF NEWCELL
                                    dfRow.SP = dfRow.SP - ΔL

                                    df_constraints[conRef,:SP] = dfRow.SP
                                    set_normalized_rhs(constr[conRef], dfRow.SP)
                                    # if dfRow.STAT == 0
                                    #     dfRow.STAT = 1
                                    # end
                                end
                            end
                            
                            
                            
                            

                            
                            if add_yL == true #yL is a new path not in P^k
                                con_num = con_num + 1
                                constr[con_num] = @constraint(m, z[k] <= 
                                            sum(d[i]*x[i]*yL[i] for i = 1:Len) + SP_L )
                                push!(df_constraints, (con_num,k, yL, SP_L))
                            end
                            # if add_yU == true #yU is a new path not in P^{|K|+1}
                            con_num = con_num + 1
                            constr[con_num] = @constraint(m, z[newCell] <= 
                                        sum(d[i]*x[i]*yU[i] for i = 1:Len) + SP_U )
                            push!(df_constraints, (con_num, newCell, yU, SP_U))
                            # end
                            #COPY PATH yK (parent Y) FROM k to NEWCELL = |K|+1
                            if yK != yU
                                con_num = con_num + 1 
                                SPk = sum(c[i]*yK[i] for i = 1:Len)
                                constr[con_num] = @constraint(m, z[newCell] <= 
                                            sum(d[i]*x[i]*yK[i] for i = 1:Len) + SPk)
                                push!(df_constraints, (con_num,newCell, yK, SPk)) #ADD DF INFORMATION OF CELL |K|+1
                            end
                        end
                        # println("K_newly_added = ",K_newly_added)
                    end
                    # println("Pre K_k ", K_k)
                    # println("K_removed = ", K_removed)
                    # println("K_newly_added = ", K_newly_added)
                    # setdiff!(K_k,K_removed)
                    # println("a = ", a)
                    setdiff!(K_k,K_removed)
                    K_k = unique(vcat(K_k, K_newly_added))
                    # println("Post K_k = ", K_k)
                    # println("myCounter = ", myCounter, " vs partitionCounter = ", partitionCounter)
                    K_newly_added = []
                    if isempty(K_k) == true 
                        continuePartition = false
                    end
                    # end #END OF for k = 1:myLength
                end
                K_bar = unique(vcat(K_bar, K_k))
                # println("K_bar = ", K_bar)
            end
            
            # println("Done partitioning")
            p = df_cell.PROB #[!,:PROB]
            # println("p = ", p)
            @objective(m, Max, sum(p[i]*z[i] for i = 1:length(p)))
            
            setdiff!(K_bar,K_removed)
            # println("\n***K_bar = ", K_bar)
            # K_bar = unique(vcat(K_bar, K_k)) #K_newly_added)
            # println("K_bar = ", K_bar)
            # K_newly_added = []
            K_removed = []
            # if iter > 12
            #     terminate_cond = true
            #     K_bar = []
            # end
            if length(K_bar) == 0
                myCounter = 1 #partitionCounter
                terminate_cond = true
            end
        end #If O1Flag == true
        # end #If Feasible
    end #While K_partition is non-empty
    # println("con_num = ", con_num)
#    println("Convolve x_now = ", findall(x_now.>0))
#     if terminate_cond == false
#         numConv = numConv+1
#         #Convolution
# #         println("Begin Convolution")
#         df_cellPoly = convolveEachCell()
#         #FindCVaR
#         CVaR, weight = FindCVaR(α_now, nu_L, nu_U, df_cellPoly)
#         K_bar = collect(1:nrow(df_cell))
#         @constraint(m, sum(x_now[i]*x[i] for i = 1:Len) <= b-1)
#         #println("ADD X-CONSTRAINT TO MP: ", t_con, "\n")
# #        println("CVaR = ", CVaR)
#         if LB < CVaR
#             LB_w = weight
#             LB = CVaR
#             x_sol, α_sol, z_sol = x_now, α_now, z_now
#         end
# #         println("wth Incumbent solution:")
# #         println("x = ", findall(x_sol.==1))
# #         println("α_sol = ", α_sol)
# #         println("z_sol = ", z_sol)
#     end
end