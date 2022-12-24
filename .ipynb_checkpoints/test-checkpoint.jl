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

# K = [1]

# for a in K
    
#     println("K ", K)
#     push!(K, 2)
    
# end
            
# K = [1,1,1]
# println(K)
# replace!(K, 1 => 0)
K = [1.0]

println(zeros(Int,3))