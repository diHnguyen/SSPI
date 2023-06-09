function my_callback_function(cb_data, cb_where::Cint)
    push!(cb_calls, cb_where)
    lazy_called = true
    
    status = callback_node_status(cb_data, m)
    if cb_where == GRB_CB_MIPNODE
        objbst = Ref{Cdouble}()
        GRBcbget(cb_data, cb_where, GRB_CB_MIPNODE_OBJBST, objbst)
        objbnd = Ref{Cdouble}()
        GRBcbget(cb_data, cb_where, GRB_CB_MIPNODE_OBJBND, objbnd)    
        println("Best Obj ", objbst[])
        println("Best Bound ", objbnd[])
        push!(data, (time() - start, objbst[], objbnd[]))
    end
    # println("cb_data ", cb_data)
    if cb_where != GRB_CB_MIPSOL #&& cb_where != GRB_CB_MIPNODE #status != MOI.CALLBACK_NODE_STATUS_INTEGER
    #     println(" - Solution is integer feasible!")
        return
    end
    # println("\nCallback? ", lazy_called)
    # println("cb_where ", cb_where)
    # if cb_where == GRB_CB_MIPNODE
    #     resultP = Ref{Cint}()
    #     GRBcbget(cb_data, cb_where, GRB_CB_MIPNODE_STATUS, resultP)
    #     println("resultP ", resultP[])
    #     if resultP[] != GRB_OPTIMAL
    #         return  # Solution is something other than optimal.
    #     end
    # end
    
    global α, β, iter, total_time, K_bar, K_newly_added, K_removed, LB, MP_obj, con_num, newCell , nu_U, nu_L, LB_w, numConv, p
    global x_sol, z_sol, α_sol, last_x, x_now,α_now,z_now, terminate_cond
    global start
    
    
    iter = iter + 1
    println("-----------------------")
    println("Iter ", iter )
    println("-----------------------")
    Gurobi.load_callback_variable_primal(cb_data, cb_where)
    x_now = callback_value.(Ref(cb_data), x)
    # println("0")
    z_now = callback_value.(Ref(cb_data), z)
    # println("1")
    MP_obj = callback_value.(Ref(cb_data), z)
    # println("Called from (x, y) = ($x_now, $z_now)")
    println("z_now ", z_now, " # cells ", newCell)
    
    # if status == MOI.CALLBACK_NODE_STATUS_FRACTIONAL
    #     println(" - Solution is integer infeasible!")
    # elseif status == MOI.CALLBACK_NODE_STATUS_INTEGER
    #     println(" - Solution is integer feasible!")
    # else
    #     @assert status == MOI.CALLBACK_NODE_STATUS_UNKNOWN
    #     println(" - Don't know if the solution is integer feasible")
    # end
    
    # println("status ", status)
#     while isempty(K_bar) == false #length(K_bar) > K
#         iter = iter + 1
        
#         optimize!(m) 
       # println("\nIter : ", iter," ; LB = ", LB)
#         println(m)
#         println("", df_cell)
#         K = vcat(K, K_newly_added)
        
        
        # if termination_status(m) == MOI.OPTIMAL
        #     MP_obj = JuMP.objective_value.(m)
        #     x_now = JuMP.value.(x)
        #     # α_now = JuMP.value.(α)
        #     z_now = JuMP.value.(z)
        #     println("\nIter : ", iter," ; MP_obj = ", MP_obj, " ; time ", time()-start,"; ", length(K_bar),"/", newCell)
        #     # println("length K_bar ", length(K_bar))
        #     # if newCell > 500
        #     #     println(iter, " : ", length(K_bar),"/", newCell, " - ", time()-start)
        #     # end
        #     println("x = ", findall(x_now.>0))
        # end
        
        
        # if termination_status(m) != MOI.OPTIMAL || MP_obj <= LB
        #     terminate_cond = true
        #     K_bar = []
        # else
        println(status)
    # if status == MOI.CALLBACK_NODE_STATUS_INTEGER
    # if isempty(K_bar) == false
    if cb_where == GRB_CB_MIPSOL
        # objbst = Ref{Cdouble}()
        # GRBcbget(cb_data, cb_where, GRB_CB_MIP_OBJBST, objbst)
        # objbnd = Ref{Cdouble}()
        # GRBcbget(cb_data, cb_where, GRB_CB_MIP_OBJBND, objbnd)    
        # println("Best Obj ", objbst[])
        # println("Best Bound ", objbnd[])
        O1Flag = true
        if last_x != x_now
            println("x_now = ", findall(x_now .>0.5))
            K_bar = collect(1:newCell)
            # println("K_bar ", K_bar)
            last_x = x_now
        
        # println("K_bar ", K_bar)
            ##Put back the set of constraints as set of shortest paths seen before
            # for k in K_bar #_partition  
            #     c_L = df_cell[k,:LB]#[row] 
            #     c_U = df_cell[k,:UB]#[row] 
            #     c = (c_U + c_L)/2
            #     M = c_U - c_L
            #     c_g = c + d.*x_now
            #     y, gx, SP = gx_bound(c, c_g, edge)
            #     if y != df_cell[k,:Y]
            #         O1Flag = false
            #     end
            #     df_cell[k,:g] = gx
            #     df_cell[k,:Y] = y
            # end
            # println("O1Flag ", O1Flag)
            # println("K_bar = ", K_bar)
            # if O1Flag == false

            #CHECK IS Z_NOW IS LESS THAN THE NEW CUT BEFORE ADDING [LINES 187--190]
            #For each cell k, the shortest-path cost is found by gx_bound
            #written as: g_k = sum(c_{ij} + d_{ij} x_now_{ij} for (i,j) in Y)
            #We must have z <= sum(z_k over all k), otherwise, add constraint on z
            coef_x = zeros(Len)
            constant_SP = 0
            for k = 1:newCell  # # in K_bar
                c_L = df_cell[k,:LB]#[row] 
                c_U = df_cell[k,:UB]#[row] 
                c = (c_U + c_L)/2
                M = c_U - c_L
                c_g = c + d.*x_now
                # if last_x != x_now
                # if k in K_bar 
                #Check this -- if x_last == x_now then we don't check OC1
                # if x_last != x_now then we have to recalculate g
                Y_k, gx, SP = gx_bound(c, c_g, edge)
                df_cell[k,:g] = gx
                df_cell[k,:Y] = Y_k
                # end
                # end
                Y_k = df_cell[k,:Y]
                coef_x = coef_x .+ p[k]*(Y_k.*d)
                constant_SP = constant_SP +  p[k]*sum(c[i]*Y_k[i] for i = 1:Len)
                # println("coef_x = ", coef_x)
            end


                # push!(df_constraints, (con_num, k, y, SP))
                # constr[con_num] = @constraint(m, z <= 
                            # sum(p[k]*(sum(d[i]*x[i]*Y_k[i] for i = 1:Len) + newCell_RHS) for k = 1:newCell))
            # constr[con_num] = @constraint(m, z <= sum(coef_x[i]*x[i] for i = 1:Len)+ constant_SP)
            println("z_now ", z_now, "; RHS ", sum(coef_x[i]*x_now[i] for i = 1:Len)+ constant_SP)
            if z_now > sum(coef_x[i]*x_now[i] for i = 1:Len)+ constant_SP + 10^(-4) #plus tolerance
                con_num = con_num + 1 
                con = @build_constraint(z <= sum(coef_x[i]*x[i] for i = 1:Len)+ constant_SP)
                # println(con)
                MOI.submit(m, MOI.LazyConstraint(cb_data), con)
                O1Flag = false
            end
        end

        if O1Flag == true #&& isempty(K_bar)
            println("Pass OC1")
            #Verify against OC2
#                 println("K_bar = ", K_bar)
            #####Regular partition#####
            # a = rand()
            # if a < 0.5
            #     agressivePartition = true
            # else
            #     agressivePartition = false
            # end

            local partitionCounter
            # agressivePartition = false
            # # println("agressivePartition? ", agressivePartition)
            # if agressivePartition == true
            #     partitionCounter = 2
            # else
                partitionCounter = 1
            # end
            myCounter = 0

            while myCounter < partitionCounter
                println("Partition")
                myCounter = myCounter + 1
                # println(myCounter, ". K_bar = ", K_bar)
                for k in K_bar
                    # c_L = df_cell[k,:LB]
                    # c_U = df_cell[k,:UB]
                    # M = c_U - c_L
                    # c = (c_U + c_L)/2
                    # c_g_L = c_L + d.*x_now
                    # yK = df_cell[k,:Y]
                    c_L, c_U, M, c, c_g_L, yK = getCellInfo(k, x_now)

                    #Solving for g(\hat{x}, c^{L,k})
                    yL, gL, SPL = gx_bound(c, c_g_L, edge)
                    df_cell[k,:Y_Lk] = yL
                    df_cell[k,:gL] = gL


                    local y_h
                    y_h, hx = hx_bound(c_L, c_U, d, x_now)
                    p_k = df_cell[k,:PROB]
                    df_cell[k,:h] = hx
                    gx = df_cell[k,:g] 

                    # println("Cell ", k, ". gx = ", gx, "; hx = ", hx)
                    #Verify against OC3
                    if gx - hx <= delta2
                        push!(K_removed,k)
                    else
                        # println("Partitioning cell ", k)
                        newCell = newCell + 1 #nrow(df_cell)+1
                        Δ, arc_split, yL, yU, gL, gU, SP_L, SP_U = Partition(x_now, newCell, k, p_k, c_L, c_U, M, df_cell[k,:Y])
                    end
                end #END OF k in K_bar
                # println("0")
                p = df_cell.PROB #[!,:PROB]

                # println("newCell ", newCell)
                # println("p ", p)
                # println("Len ", Len)

                coef_x = zeros(Len)
                constant_SP = 0
                for k = 1:newCell
                    c_L = df_cell[k,:LB]#[row] 
                    c_U = df_cell[k,:UB]#[row] 
                    c = (c_U + c_L)/2
                    Y_k = df_cell[k,:Y]
                    # println(c[Y_k.==1])

                    coef_x = coef_x .+ p[k]*(Y_k.*d)
                    constant_SP = constant_SP + p[k]*sum(c[i]*Y_k[i] for i = 1:Len)
                    # println("coef_x = ", coef_x)
                end
                # println("1")
                con_num = con_num + 1 
                    # push!(df_constraints, (con_num, k, y, SP))
                    # constr[con_num] = @constraint(m, z <= 
                                # sum(p[k]*(sum(d[i]*x[i]*Y_k[i] for i = 1:Len) + newCell_RHS) for k = 1:newCell))
                # constr[con_num] = @constraint(m, z <= sum(coef_x[i]*x[i] for i = 1:Len)+ constant_SP)
                # println("z_now ", z_now)
                # println(sum(coef_x[i]*x_now[i] for i = 1:Len)+ constant_SP)
                if z_now > sum(coef_x[i]*x_now[i] for i = 1:Len)+ constant_SP + 10^(-4)
                    con = @build_constraint(z <= sum(coef_x[i]*x[i] for i = 1:Len)+ constant_SP)
                    MOI.submit(m, MOI.LazyConstraint(cb_data), con)
                    # println(con)
                end
                # println("K_bar = ", K_bar)
                # println("K_removed = ", K_removed)
                # println("K_newly_added = ", K_newly_added)
                setdiff!(K_bar,K_removed)
                
                K_bar = vcat(K_bar, K_newly_added)
                # println("updated K_bar = ", K_bar)
                K_newly_added = []
                K_removed = []
                if length(K_bar) == 0
                    myCounter = partitionCounter
                    terminate_cond = true
                end
            end
        end #If O1Flag == true
            # end #If Feasible
        # end #isempty(K_bar) == false
    end
end
# end
println("Here 6")
MOI.set(m, MOI.RawParameter("LazyConstraints"), 1)

MOI.set(m, Gurobi.CallbackFunction(), my_callback_function)
# MOI.set(m, MOI.LazyConstraintCallback(), my_callback_function)
optimize!(m) 