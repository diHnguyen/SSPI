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
global A1 = 0 # 1=Select arc having the largest uncertainty , 0=Select arc using Lemma2
global A2 = 0 # 1=Partition once per cell , 0=Partition multiple per cell
global A3 = 0# 1=Split at mean base cost , 0=Split using SA if possible
global A4 = 1 # 1=Frequent solve MP
global A5 = 0 # 1=Regular opt model
include("functionLoadSharedFiles.jl")

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
# df_constraints = DataFrame(NUM = Int[], CELL = Int[], Y = Array[], SP = Float64[])
df_cell = DataFrame(CELL = Int[], Y = Array[], Y_Lk = Array[], g = Float64[], h = Float64[], gL = Float64[], LB = Array[], UB = Array[], PROB = Float64[], PI = Array[])



c = (cU_orig + cL_orig)/2  
yy, SP_init, SP_init, T, pred, label, path = gx_bound(c, c, edge) #y, gx, SP, T, pred, label, path
print("label ", label)
push!(df_cell, (1, yy,yy, SP_init, 0, 0, cL_orig, cU_orig, 1,label))
# push!(df_constraints, (1, 1,yy,SP_init))
##println(f,"MASTER PROBLEM==========================================================================================")
MP_obj = 0.0
zNum = 200000
cRefNum = 2000000
gurobi_env_m = Gurobi.Env()
# Gurobi.GRBsetintparam(gurobi_env_m, "OutputFlag", 1)
# Gurobi.GRBsetintparam(gurobi_env_m, "LogToConsole", 0)
# Gurobi.GRBsetintparam(gurobi_env_m, "LogFile", "my_log_file.txt")
m = Model(() -> Gurobi.Optimizer(gurobi_env_m)) # If we want to add # in Gurobi, then we have to turn of 
# println("Here 2")
set_optimizer_attribute(m, "OutputFlag", 1)    #Gurobi's own Cuts 
# println("Here3")
set_optimizer_attribute(m, "LogToConsole", 0)
# println("Here4")
# set_optimizer_attribute(m, "LogFile", "./OutputFile/LOG_BasicAlg_CombCuts_"*dataSet*".txt")
# println("Here5")
# println("1")
@variable(m, x[1:Len], Bin)
# @variable(m, α)
@variable(m, 1e6 >= z >= 0)
# @constraintref constr[1:200000]
# @ConstrRef constr[1:200000]

# constr = Array{JuMP.JuMPArray{JuMP.ConstraintRef,1,Tuple{Array{Int64,1}}}}()

constr = Array{JuMP.ConstraintRef}(undef, cRefNum)
@constraint(m, sum(x[i] for i=1:Len) == b) 
constr[1] = @constraint(m, z <= SP_init + sum(yy[i]*x[i]*d[i] for i=1:Len) )

@objective(m, Max, z)
# @objective(m, Max, sum(p[i]*z[i] for i = 1:length(p)) )#w - sum(s[k] for k=1:length(s))/length(s) )
include("functionSetGlobalVar_MP.jl")
# global x_sol = []
# global α_sol = 0
# global z_sol = []
# global x_now = []
# global α_now = 0
# global z_now = []
# global last_x = zeros(Len)
# global con_num = 1
# global newCell = 1
# global total_time = 0.0
# global iter = 0
# # global K = Int64[1]
# global K_bar = Int64[1]
# global LB = 0
# global LB_w = 0 
# global MP_obj = 1e6
# global K_newly_added = []
# global K_removed = []
# global start = time()
# global terminate_cond = false
# while terminate_cond == false && iter <5
lazy_called = true
cb_calls = Cint[]
data = Any[]
# start_time = 0.0
function my_callback_function(cb_data)#, cb_where::Cint)
    # push!(cb_calls, cb_where)
    lazy_called = true
    
    status = callback_node_status(cb_data, m)
    # x_val = callback_value(cb_data, x)
    # y_val = callback_value(cb_data, y)
    # println("Called from (x, y) = ($x_val, $y_val)")
    
    # if cb_where == GRB_CB_MIPNODE
    #     objbst = Ref{Cdouble}()
    #     GRBcbget(cb_data, cb_where, GRB_CB_MIPNODE_OBJBST, objbst)
    #     objbnd = Ref{Cdouble}()
    #     GRBcbget(cb_data, cb_where, GRB_CB_MIPNODE_OBJBND, objbnd)    
    #     println("Best Obj ", objbst[])
    #     println("Best Bound ", objbnd[])
    #     push!(data, (time() - start, objbst[], objbnd[]))
    # end
    # # println("cb_data ", cb_data)
    if status != MOI.CALLBACK_NODE_STATUS_INTEGER #GRB_CB_MIPSOL #&& cb_where != GRB_CB_MIPNODE #status != MOI.CALLBACK_NODE_STATUS_INTEGER
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
    println("Lazy - Iter ", iter )
    println("-----------------------")
    
    # if iter > 2
    #     return
    #     # break
    # end
    # Gurobi.load_callback_variable_primal(cb_data, cb_where)
    x_now = callback_value.(Ref(cb_data), x) #Julia v1.9
    # x_now = callback_value.(Ref(cb_data), x)
    # println("0")
    z_now = callback_value.(Ref(cb_data), z) #Julia v1.9
    # z_now = callback_value.(Ref(cb_data), z)
    # println("1")
    MP_obj = callback_value.(Ref(cb_data), z) #Julia v1.9
    # MP_obj = callback_value.(Ref(cb_data), z)
    # println("Called from (x, y) = ($x_now, $z_now)")
    # println("z_now ", z_now, " # cells ", newCell)
    println("\nIter : ", iter," ; MP_obj = ", MP_obj, " ; time ", time()-start,"; ", length(K_bar),"/", newCell)
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
        println(m)
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
    if status == MOI.CALLBACK_NODE_STATUS_INTEGER #GRB_CB_MIPSOL
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
                c_L, c_U, M, c, c_g = getCellInfo(k, x_now, "c_g")
                # if last_x != x_now
                # if k in K_bar 
                #Check this -- if x_last == x_now then we don't check OC1
                # if x_last != x_now then we have to recalculate g
                Y_k, gx, SP = gx_bound(c, c_g, edge)
                df_cell[k,:g] = gx
                df_cell[k,:Y] = Y_k
                # Y_k = df_cell[k,:Y]
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

            local partitionCounter = 1
            myCounter = 0

            while myCounter < partitionCounter
                # println("Partition")
                myCounter = myCounter + 1
                # println(myCounter, ". K_bar = ", K_bar)
                for k in K_bar
                    # c_L = df_cell[k,:LB]
                    # c_U = df_cell[k,:UB]
                    # M = c_U - c_L
                    # c = (c_U + c_L)/2
                    # c_g_L = c_L + d.*x_now
                    # yK = df_cell[k,:Y]
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
                    # c_L = df_cell[k,:LB]#[row] 
                    # c_U = df_cell[k,:UB]#[row] 
                    # c = (c_U + c_L)/2
                    # Y_k = df_cell[k,:Y]
                    c_L, c_U, M, c, c_g, Y_k = getCellInfo(k, x_now, "c_g")
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
# println("Here 6")
# MOI.set(m, MOI.RawParameter("LazyConstraints"), 1)

set_attribute(m, MOI.LazyConstraintCallback(), my_callback_function) #For Julia v1.9
# MOI.set(m, Gurobi.CallbackFunction(), my_callback_function)
# MOI.set(m, MOI.LazyConstraintCallback(), my_callback_function)
optimize!(m) 
println("con_num " , con_num)
# println("constr ", constr[1:con_num])
# println("z_now ", z_now[1:newCell])
total_time = time() - start

set = string(A1)*string(A2)*string(A3)*string(A4)*string(A5)
println("Alg_"*set*"_"*dataSet, "; Ins ", Ins, "; Time ", total_time, "; MP_obj ", MP_obj, "; x_now ", findall(x_now.==1),"; Cells ", nrow(df_cell), "; Iter ", iter)#, "; W ", LB_w, "; Cuts ", numConv)
h_val = df_cell.h
p_val = df_cell.PROB

println("LB = ", sum(h_val[k]*p_val[k] for k=1:newCell))

timesFile = open(myPath*"/PrelimOutputFile/Alg_"*set*"_"*dataSet*".txt", "a")
println(timesFile, dataSet, "; Ins ", Ins, "; Time ", total_time, "; MP_obj ", MP_obj, "; x_now ", findall(x_now.==1),"; Cells ", nrow(df_cell), "; Iter ", iter)#, "; W ", LB_w, "; Cuts ", numConv)
close(timesFile)

# println("\007")
