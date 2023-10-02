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
global A2 = 1 # 1=Partition once per cell , 0=Partition multiple per cell
global A3 = 1# 1=Split at mean base cost , 0=Split using SA if possible
global A4 = 1 # 1=Frequent solve MP
#If running A5 = 0, do not use this file, use LazyAlg.jl instead
#FIXED IN THIS FILE
global A5 = 1 # 1=Regular opt model
global set = string(A1)*string(A2)*string(A3)*string(A4)*string(A5)
include("functionLoadSharedFiles.jl")


#Setting constraint for start node
# outgoing = findall(edge[:,1].== origin)

# If we want to add # in Gurobi, then we have to turn of Gurobi's own Cuts 
# h1 = Model(() -> Gurobi.Optimizer(gurobi_env))
# h1.setParam("OutputFlag", 0)
# set_optimizer_attribute(h1, "OutputFlag", 0)

# @variable(h1, 1 >= y_h[1:Len]>=0)
#@variable(h, q[1:Len]>=0)

#Setting constraints for remaining none-sink/start nodes
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
# if A2==1 #Partition once per cell
df_constraints = DataFrame(NUM = Int[], CELL = Int[], Y = Array[], SP = Float64[])
df_cell = DataFrame(CELL = Int[], Y = Array[], Y_Lk = Array[], g = Float64[], h = Float64[], gL = Float64[], LB = Array[], UB = Array[], PROB = Float64[], PI = Array[])

# M = cU_orig - cL_orig
c = (cU_orig + cL_orig)/2  
yy, SP_init, SP_init, T, pred, label, path = gx_bound(c, c, edge) #y, gx, SP, T, pred, label, path
# print("label ", label)
push!(df_cell, (1, yy,yy, SP_init, 0, 0, cL_orig, cU_orig, 1,label))
push!(df_constraints, (1, 1,yy,SP_init))
# else #Partition multiple per cell
#     df_constraints = DataFrame(NUM = Int[], CELL = Int[], Y = Array[], SP = Float64[], STAT= Int[])
# df_cell = DataFrame(CELL = Int[], Y = Array[], Y_Lk = Array[], g = Float64[], h = Float64[], gL = Float64[], LB = Array[], UB = Array[], PROB = Float64[])
#     push!(df_cell, (1, yy,yy, SP_init, 0, 0, cL_orig, cU_orig, 1))
#     push!(df_constraints, (1, 1,yy,SP_init,1))
# end



##println(f,"MASTER PROBLEM==========================================================================================")

MP_obj = 0.0
zNum = 200000
cRefNum = 2000000
if A1==1
    zNum = 2000000
    cRefNum = 20000000
end
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
if A2 == 1
    if A4 == 1 #1=Frequent solve MP
        include("A2_1.jl") #Partition once per cell
    else
        println("A4_0")
        include("A4_0.jl")
    end
else
    include("A2_0.jl") #Partition multiple per cell
end
# println("con_num " , con_num)
# println("constr ", constr[1:con_num])
# println("z_now ", z_now[1:newCell])
total_time = time() - start

println("Alg_"*set*"_"*dataSet, "; Ins ", Ins, "; Time ", total_time, "; MP_obj ", MP_obj, "; x_now ", findall(x_now.==1),"; Cells ", nrow(df_cell), "; Iter ", iter)#, "; W ", LB_w, "; Cuts ", numConv)
h_val = df_cell.h
p_val = df_cell.PROB

println("LB = ", sum(h_val[k]*p_val[k] for k=1:newCell))

timesFile = open("./PrelimOutputFile/Alg_"*set*"_"*dataSet*".txt", "a")
println(timesFile, dataSet, "; Ins ", Ins, "; Time ", total_time, "; MP_obj ", MP_obj, "; x_now ", findall(x_now.==1),"; Cells ", nrow(df_cell), "; Iter ", iter)#, "; W ", LB_w, "; Cuts ", numConv)
close(timesFile)
# println(LB_w + β)
# println("\007")
