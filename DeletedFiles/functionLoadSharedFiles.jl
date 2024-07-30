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
global numNodes = string(ARGS[1])
global density = string(ARGS[2])
global Ins = string(ARGS[3])
# global myPath = "/Users/dinguyen/Library/CloudStorage/GoogleDrive-di.hoai.nguyen@gmail.com/Other\ computers/My\ Laptop/Documents/GitHub/Paper5"
global dataSet = "N"*string(numNodes)*"_d"*string(density)

myFile = "./PrelimTestInstances/"*dataSet*"/"*dataSet*"_Ins_"*Ins*".jl"
println("Ins ", dataSet,"_", Ins, " Running...", myRun)
include(myFile)
include("functionGbound.jl")
# println("Before function Hbound")
include("functionHbound.jl")

include("functionGetCellInfo.jl")
include("functionSelectArc.jl")
include("functionArcSplit.jl")
include("functionPartition.jl")
global epsilon = 1e-4
Gurobi.GRBsetintparam(gurobi_env, "OutputFlag", 0)