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


# using DataFrames

# df = DataFrame(A=1:2:1000, B=repeat(1:10, inner=50), C=1:500)
# println(df[(df.A .> 750) .& (300 .< df.C .< 400), 1])

using JuMP 
using Gurobi

global gurobi_env = Gurobi.Env()
m = Model(() -> Gurobi.Optimizer(gurobi_env)) # If we want to add # in Gurobi, then we have to turn of 

@variable(m, x[1:3], Bin)

# @constraintref constr[1:200000]
# @ConstrRef constr[1:200000]

# constr = Array{JuMP.JuMPArray{JuMP.ConstraintRef,1,Tuple{Array{Int64,1}}}}()


con = @constraint(m, x[1] + x[2] + x[3] <= 4)
con2 = @constraint(m, x[1] <= 2)
@objective(m, Max, x[1] )#w - sum(s[k] for k=1:length(s))/length(s) )
println(m)
optimize!(m) 
set_normalized_rhs(con2, GRB_INFINITY)
println(m)
optimize!(m)