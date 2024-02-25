using JuMP 
using Gurobi
using LightGraphs
using DataFrames, Query
using CSV
using TimerOutputs
using Dates
# using Polynomials #Be careful using Polynomials and JuMP pkg in Julia 1.9. They both have @variables so not preferred. 

myRun = Dates.format(now(), "HH:MM:SS")
global gurobi_env = Gurobi.Env()
global edge, cL_orig, cU_orig, Len, c_orig, yy, SP_init, p,g,h, origin, destination, last_node, all_nodes, M_orig, delta1, delta2, b, last_node
# global β # = rand(1:999)/1000
# gurobi_env.setParam("LogToConsole", 0)

to = TimerOutput()
numNodes = string(ARGS[1])
dataSet = "N50" #"N"*string(numNodes)
Ins = "84" #string(ARGS[2])
myFile = "./TestInstances/"*dataSet*"/"*dataSet*"_"*Ins*".jl"
println("Ins ", dataSet,"_", Ins, " Running...", myRun)
include(myFile)
include("functionGbound.jl")
# println("Before function Hbound")
include("functionHbound.jl")

include("functionGetCellInfo.jl")
include("functionSelectArc.jl")
include("functionArcSplit.jl")
include("functionPartition_MainAlg.jl")
global epsilon = 1e-4
Gurobi.GRBsetintparam(gurobi_env, "OutputFlag", 0)