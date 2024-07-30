# using Pkg
# Pkg.add("JuMP")
# Pkg.add("Gurobi")
# Pkg.add("LightGraphs")
# Pkg.add("DataFrames")
# Pkg.add("Query")
# Pkg.add("CSV")
# Pkg.add("TimerOutputs")
# Pkg.add("Dates")
# Pkg.add("Polynomials")

#Ready for upload
include("functionLoadSharedFiles.jl")
include("functionPartition_BasicAlg.jl")
# #Setting constraint for start node
# outgoing = findall(edge[:,1].== origin)

# #Setting constraints for remaining none-sink/start nodes
# @constraint(h1, sum(y_h[k] for k in outgoing) == 1)
# for i in all_nodes
#     global outgoing
#     if i != destination && i != origin
#         incoming = findall(edge[:,2].== i)
#         outgoing = findall(edge[:,1].== i)
#         @constraint(h1, sum(-y_h[k] for k in outgoing) + sum(y_h[k] for k in incoming) == 0)
#     end
# end

#MAIN PROGRAM:
df_constraints = DataFrame(NUM = Int[], CELL = Int[], Y = Array[], SP = Float64[])
df_cell = DataFrame(CELL = Int[], Y = Array[], Y_Lk = Array[], g = Float64[], h = Float64[], gL = Float64[], LB = Array[], UB = Array[], PROB = Float64[])


MP_obj = 0.0

push!(df_cell, (1, yy,yy, SP_init, 0, 0, cL_orig, cU_orig, 1))
push!(df_constraints, (1, 1,yy,SP_init))
##println(f,"MASTER PROBLEM==========================================================================================")

zNum = 200000
cRefNum = 2000000
m = Model(() -> Gurobi.Optimizer(gurobi_env)) # If we want to add # in Gurobi, then we have to turn of 
# set_optimizer_attribute(m, "OutputFlag", 0)    #Gurobi's own Cuts 
# println("1")
@variable(m, x[1:Len], Bin)
# @variable(m, α)
@variable(m, 1e6 >= z[1:zNum] >= 0)
# @constraintref constr[1:200000]
# @ConstrRef constr[1:200000]

# constr = Array{JuMP.JuMPArray{JuMP.ConstraintRef,1,Tuple{Array{Int64,1}}}}()

constr = Array{JuMP.ConstraintRef}(undef, cRefNum)
@constraint(m, sum(x[i] for i=1:Len) == b) 
constr[1] = @constraint(m, z[1] <= SP_init + sum(yy[i]*x[i]*d[i] for i=1:Len) )
@objective(m, Max, sum(p[i]*z[i] for i = 1:length(p)) )#w - sum(s[k] for k=1:length(s))/length(s) )
include("functionSetGlobalVar_MP.jl")
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
            println("\nIter : ", iter," ; MP_obj = ", MP_obj)
            #println("length K_bar ", length(K_bar))
            # if newCell > 500
            #     println(iter, " : ", length(K_bar),"/", newCell, " - ", time()-start)
            # end
            println("x = ", findall(x_now.>0))
        end
        
        # if termination_status(m) != MOI.OPTIMAL || MP_obj <= LB
        #     terminate_cond = true
        #     K_bar = []
        # else
        O1Flag = true
        if last_x != x_now
            K_bar = collect(1:newCell)
            last_x = x_now
            for k in K_bar #_partition  
                c_L, c_U, M, c, c_g = getCellInfo(k, x_now, "c_g")
                y, gx, SP = gx_bound(c, c_g, edge)
                df_cell[k,:g] = gx
                df_cell[k,:Y] = y
                if z_now[k] - gx > delta1
                    con_num = con_num + 1 
                    push!(df_constraints, (con_num, k, y, SP))
                    constr[con_num] = @constraint(m, z[k] <= sum(d[i]*y[i]*x[i] for i = 1:Len) + SP)
                    O1Flag = false
                end
            end
        end

        if O1Flag == true 
            local partitionCounter = 2 #Set the number of partitions made per cell. 
            myCounter = 0
            while myCounter < partitionCounter
                myCounter = myCounter + 1
                # println(myCounter, ". K_bar = ", K_bar)
                for k in K_bar
                    c_L, c_U, M, c, c_g_L, yK = getCellInfo(k, x_now, "c_g_L")
                    #Solving for g(\hat{x}, c^{L,k})
                    
                    yL, gL, SPL = gx_bound(c, c_g_L, edge) #y, gx, SP, T, pred, label, path
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
                        newCell = newCell + 1 #nrow(df_cell)+1

                        Δ, arc_split, yL, yU, gL, gU, SP_L, SP_U = Partition(x_now, newCell, k, p_k, c_L, c_U, M, df_cell[k,:Y])

                        #Updating constraints in MP:

                        #Query rows from df_constraints that satisfy:
                        #(a) CELL column = k, and
                        #(b) Y column uses path that has arc # =  arc_split 
                        df_temp_k = df_constraints |> 
                        @filter(_.CELL == k)|> DataFrame
                        add_yL = true #Turns false if path yL is in cell k's existing constraints
                        add_yU = true #Turns false if path yU is in cell k's existing constraints

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
                                newCell_RHS = newCell_RHS + Δ #gap #FIND NEW RHS OF NEWCELL
                                dfRow.SP = dfRow.SP - Δ

                                df_constraints[conRef,:SP] = dfRow.SP
                                set_normalized_rhs(constr[conRef], dfRow.SP)
                            end

                            #COPY PATH Y_k FROM k to NEWCELL = |K|+1
                            con_num = con_num + 1 
                            constr[con_num] = @constraint(m, z[newCell] <= 
                                        sum(d[i]*x[i]*Y_k[i] for i = 1:Len) + newCell_RHS)
                            push!(df_constraints, (con_num,newCell, Y_k, newCell_RHS)) #ADD DF INFORMATION OF CELL |K|+1
                        end

                            if add_yL == true #yL is a new path not in P^k

                                con_num = con_num + 1
                                constr[con_num] = @constraint(m, z[k] <= 
                                            sum(d[i]*x[i]*yL[i] for i = 1:Len) + SP_L )
                                push!(df_constraints, (con_num,k, yL, SP_L))
                            end
                            if add_yU == true #yU is a new path not in P^{|K|+1}
                                con_num = con_num + 1
                                constr[con_num] = @constraint(m, z[newCell] <= 
                                            sum(d[i]*x[i]*yU[i] for i = 1:Len) + SP_U )
                                push!(df_constraints, (con_num, newCell, yU, SP_U))
                            end
                        end
                    # end
                end #END OF for k = 1:myLength
                p = df_cell.PROB #[!,:PROB]
                @objective(m, Max, sum(p[i]*z[i] for i = 1:length(p)))
                setdiff!(K_bar,K_removed)
                K_bar = vcat(K_bar, K_newly_added)
                # println("K_bar = ", K_bar)
                K_newly_added = []
                K_removed = []
                if length(K_bar) == 0
                    myCounter = partitionCounter
                    terminate_cond = true
                end
            end
        end #If O1Flag == true
        # end #If Feasible
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
end

total_time = time() - start

println("BasicAlg_A_"*dataSet, "; Ins ", Ins, "; Time ", total_time, "; MP_obj ", MP_obj, "; x_now ", findall(x_now.==1),"; Cells ", nrow(df_cell), "; Iter ", iter)#, "; W ", LB_w, "; Cuts ", numConv)

timesFile = open("./OutputFile/BasicAlg_A_"*dataSet*".txt", "a")
println(timesFile, dataSet, "; Ins ", Ins, "; Time ", total_time, "; MP_obj ", MP_obj, "; x_now ", findall(x_now.==1),"; Cells ", nrow(df_cell), "; Iter ", iter)#, "; W ", LB_w, "; Cuts ", numConv)
close(timesFile)
# println(LB_w + β)
# println("\007")
