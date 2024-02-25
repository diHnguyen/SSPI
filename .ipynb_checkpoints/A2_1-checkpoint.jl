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
            println("\nIter : ", iter," ; MP_obj = ", MP_obj, " ; time ", time()-start,"; ", length(K_bar),"/", newCell)
            # println("length K_bar ", length(K_bar))
            # if newCell > 500
            #     println(iter, " : ", length(K_bar),"/", newCell, " - ", time()-start)
            # end
            println("x = ", findall(x_now.>0))
        end

        #If x-sol changes from last iter, then we solve g(.) model again for all cells in K
        #(by resetting K_bar = K)
        O1Flag = true #Set to false if a new constraint is added to MP
        if last_x != x_now
            K_bar = collect(1:newCell)
            last_x = x_now
            for k in K_bar #_partition  
                c_L, c_U, M, c, c_g = getCellInfo(k, x_now, "c_g")
                y, gx, SP, T, pred, label, path = gx_bound(c, c_g, edge)
                df_cell[k,:g] = gx
                df_cell[k,:Y] = y
                df_cell[k,:PI] = label
                if z_now[k] - gx > delta1
                    con_num = con_num + 1 
                    push!(df_constraints, (con_num, k, y, SP))
                    constr[con_num] = @constraint(m, z[k] <= sum(d[i]*y[i]*x[i] for i = 1:Len) + SP)
                    O1Flag = false
                end
            end
        end

        if O1Flag == true 
            local partitionCounter = 1 #Set the number of partitions made per cell. 
            myCounter = 0
            while myCounter < partitionCounter
                myCounter = myCounter + 1
                # println(myCounter, ". K_bar = ", K_bar)
                for k in K_bar
                    c_L, c_U, M, c, c_g_L, yK = getCellInfo(k, x_now, "c_g_L")
                    #Solving for g(\hat{x}, c^{L,k})
                    yL, gL, SPL = gx_bound(c, c_g_L, edge)
                    df_cell[k,:Y_Lk] = yL
                    df_cell[k,:gL] = gL

                    local y_h
                    y_h, hx = hx_bound(c_L, c_U, d, x_now)
                    p_k = df_cell[k,:PROB]
                    df_cell[k,:h] = hx
                    gx = df_cell[k,:g] 

                    println("Cell ", k, ". gx = ", gx, "; hx = ", hx)
                    #Check to see if cell k needs to be partitioned
                    if gx - hx <= delta2
                        push!(K_removed,k)
                    else
                        # println("Partitioning cell ", k,". gx = ", gx, "; hx = ", hx)
                        newCell = newCell + 1 #nrow(df_cell)+1
                        
                        #Partition cell k -> k & newCell
                        #_L is for k; _U is for newCell
                        ΔL, ΔU, arc_split, yL, yU, gL, gU, SP_L, SP_U = Partition(x_now, newCell, k, p_k, c_L, c_U, M, df_cell[k,:Y])
                        # println("arc_split ", arc_split, " ", ΔL, " ", ΔU, " -- ", M[arc_split])
                        #Updating constraints in MP:
                        #Query rows from df_constraints that satisfy:
                        #(a) CELL column = k, and
                        #(b) Y column uses path that has arc # =  arc_split 
                        df_temp_k = df_constraints |> 
                        @filter(_.CELL == k)|> DataFrame
                        add_yL = true #Turns false if path yL found earlier is in cell k's existing constraints -> so don't need to add yL found earlier to P-set
                        add_yU = true #Turns false if path yU found earlier is in cell k's existing constraints -> so don't need to add yU found earlier to P-set

                        #LOOP THRU ALL ROWS IN DF ASSOCIATED WITH k
                        #Rule: all paths in a parent cell will be inherited by child cells
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
                            # & revise corresponding constraint that exists for cell k in Gurobi
                            # println(arc_split)
                            if Y_k[arc_split] == 1 
                                conRef = dfRow.NUM #Get constraint ref number wrt Gurobi of Y in df row
                                newCell_RHS = newCell_RHS + ΔU #Get RHS value of newCell
                                dfRow.SP = dfRow.SP - ΔL #Get RHS value of revised k
                                df_constraints[conRef,:SP] = dfRow.SP #Update df that tracks only constraints
                                set_normalized_rhs(constr[conRef], dfRow.SP) #Update k's constraint in Gurobi model
                            end

                            #Whether an arc is split or not, COPY PATH Y_k FROM k to NEWCELL = |K|+1
                            con_num = con_num + 1 
                            constr[con_num] = @constraint(m, z[newCell] <= 
                                        sum(d[i]*x[i]*Y_k[i] for i = 1:Len) + newCell_RHS)
                            push!(df_constraints, (con_num,newCell, Y_k, newCell_RHS)) #ADD DF INFORMATION OF CELL |K|+1
                        end

                        if add_yL == true #yL is a new path not in P-set for k then we need to add to P^k
                            con_num = con_num + 1
                            constr[con_num] = @constraint(m, z[k] <= 
                                        sum(d[i]*x[i]*yL[i] for i = 1:Len) + SP_L)
                            push!(df_constraints, (con_num,k, yL, SP_L))
                        end
                        if add_yU == true #yU is a new path not  in P-set for k so we add yU to P^{|K|+1}
                            con_num = con_num + 1
                            constr[con_num] = @constraint(m, z[newCell] <= 
                                        sum(d[i]*x[i]*yU[i] for i = 1:Len) + SP_U)
                            push!(df_constraints, (con_num, newCell, yU, SP_U))
                        end
                    end
                end #END OF for k = 1:myLength
                #Update obj function
                p = df_cell.PROB #[!,:PROB]
                # println("p = ", p)
                @objective(m, Max, sum(p[i]*z[i] for i = 1:length(p)))
                
                #K_bar = set of cells that haven't satisfied g-h<=delta2 at the beginning of the loop (for current x)
                #K_removed = set of cells we verified to have satisfied g-h<=delta2
                setdiff!(K_bar,K_removed)
                K_bar = vcat(K_bar, K_newly_added) #K_newly_added = the set of "new" child cells from partition
                # println("K_bar = ", K_bar)
                K_newly_added = []
                K_removed = []
                if length(K_bar) == 0 #Additional condition to terminate the while loop if no more cell needs partition
                    myCounter = partitionCounter
                    terminate_cond = true
                end
            end
        end #If O1Flag == true
        # end #If Feasibles
    end #While K_partition is non-empty
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
    # println("con_num = ", con_num)
end