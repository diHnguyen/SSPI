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


using DataFrames

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

# K = [1.0]

# println(zeros(Int,3))

df_xCuts = DataFrame(NUM = Int[], X = Array[])
push!(df_xCuts,(1, [1, 2, 42, 66, 160, 202, 229]))
push!(df_xCuts,(2, [3, 81, 93, 138, 160, 202, 229]))
println(df_xCuts.X)
println(findall(x->x == [2, 81, 93, 138, 160, 202, 229], df_xCuts.X))


# println(findall(df_xCuts.X .==[1, 2, 42, 66, 160, 202, 229]))