# Pkg.add("Graphs")
using LightGraphs
# using Graphs
# using Pkg
# Pkg.add("GraphPlot")
using GraphPlot

### Get y_0 ###
function gx_bound(c_L, c_U, c, c_g, x_now, edge)
    
    #println(f,"Current CELL's LB = ", c_L)
    #println(f,"Current CELL's UB = ", c_U)
    #println(f, "Current interdiction x = ", x_now)
    Len = length(edge[:,1])
    start_node = edge[:,1]
    end_node = edge[:,2]

    no_node = max(maximum(start_node), maximum(end_node) )
    no_link = length(start_node)


    function getShortestX(state, start_node, end_node, origin, destination)
        _x = zeros(Int, length(start_node))
        _path = enumerate_paths(state, destination)

        for i=1:length(_path)-1
            _start = _path[i]
            _end = _path[i+1]

            for j=1:length(start_node)
                if start_node[j]==_start && end_node[j]==_end
                _x[j] = 1
                break
                end
            end

        end
        _x
    end


    graph = Graph(no_node)
    distmx = Inf*ones(no_node, no_node)

    # Adding links to the graph
    for i=1:no_link
        add_edge!(graph, start_node[i], end_node[i])
        distmx[start_node[i], end_node[i]] = c_g[i]
    end

    # Run Dijkstra's Algorithm from the origin node to all nodes
    state = dijkstra_shortest_paths(graph, origin, distmx)
    label = state.dists
    pred = state.parents
    b_arc = ""
    
    for i = 1: length(state.parents)
        if state.parents[i] != 0 
            b_arc = string(b_arc, "(", state.parents[i], ",", i, ")")
        end
    end
    
    # Retrieving the shortest path
    path = enumerate_paths(state, destination)
    
    #parents = LightGraphs.DijkstraState(state, destination)

    # Retrieving the 'x' variable in a 0-1 vector
    y = getShortestX(state, start_node, end_node, origin, destination)
    #println(f,"y vector:", y)
    
    gx = sum(c_g[i]*y[i] for i = 1:no_link)    
    SP = sum(c[i]*y[i] for i = 1:length(c))
    T = Int64[]
    for i = 1:Len
        if pred[edge[i,2]] == edge[i,1]
            push!(T, 1)
        else
            push!(T, 0)
        end
    end

    y_index = findall(y .== 1)

#     println("Minimum Spanning Tree: ", T)
    #println("Shortest path y = ", y)
    #println("Indices of shortest path (edge) = ", y_index)
    #println("Nodes visited =", path)
    #println("Minimum Spanning Tree =", pred)
    #println("Node label =" ,label)

    return y, gx, SP
end


###### EDIT NETWORK PARA HERE ####################
##################################################
N = 100
target_density = 0.3
A = 0.3*(N)*(N-1)
max_A = N*(N-1)
density = 0.3*max_A/(max_A - (N-1) - (N-2))
println("density ", density)
println("max_A ",max_A)
numInstances = 20
all_Density = zeros(numInstances)
unc_arc = 0.25
myInstance = 1

origin = 1
destination = N
############################
############################


while myInstance <= numInstances
    edge = Array{Int64}(undef,(0,2))
    for i = 1:N-1
        for j = 2:N
            r = rand()
            if r <= density && i!=j
                arc = [i,j]
                edge = [edge; [i,j]']
            end
        end
    end
#     avg = avg + length(edge[:,1])/max_A
    cU_orig = zeros(length(edge[:,1]))
    cL_orig = zeros(length(edge[:,1]))
    d = zeros(length(edge[:,1]))
    origin = 1
    destination = N
#     println("",edge)
    Len = length(edge[:,1])
#     println("Len = ", length(edge[:,1]))
    for i = 1:length(edge[:,1])
         
#         prob = rand(1:10)
#         high = rand(1:40)
#         if prob <= 3
#             low = rand(1:high)
#         else
#             low = high
#         end
        diff = abs(edge[i,2]-edge[i,1])*50
        c = rand(1:diff)
        r = rand()
#         println("c = ", c)
#         println("cL_orig ", cL_orig)
        if r <= unc_arc
            unc_amt = rand(1:c)
            cL_orig[i] = c - unc_amt
            cU_orig[i] = c + unc_amt
        else
            cL_orig[i] = c 
            cU_orig[i] = c 
        end
        
        interdict = rand(1:50)
#         push!(cU_orig, high)
#         push!(cL_orig, low)
        d[i] = interdict
    end
    c_L = cL_orig
    c_U = cU_orig
    c = (c_L + c_U)/2
    c_g = c 
    x_now = zeros(Int64,length(d))
#     println("1")
    y,gx,SP = gx_bound(c_L, c_U, c, c_g, x_now, edge)
#     println(y)
    
    if sum(y[i] for i = 1:length(d)) > 0 
        println(edge[y.>0,:])
        outfile = "./Instances/N"*string(N)*"Ins_"*string(myInstance)*".jl"
        f = open(outfile, "w")
        println(f,"edge = ", edge)
        println(f,"cL_orig = ", cL_orig)
        println(f,"cU_orig = ", cU_orig)
        println(f,"d = ", d)
        Len = length(d)
#STARTING SOLUTION:
println(f, "Len = length(d)
\nyy = ",y, "
\nc_orig = 0.5*(cL_orig+cU_orig)
\nSP_init = sum(yy[i]*c_orig[i] for i = 1:Len)

\np = [1.0]
\ng = [SP_init]
\nh = [0.0]

\norigin = ",1,"
\ndestination =",N,"

last_node = maximum(edge)
all_nodes = collect(1:last_node)

M_orig = zeros(Len)

for i = 1:Len
    M_orig[i] = cU_orig[i] - cL_orig[i]
end

case = 0
delta1 = 1e-6
delta2 = ",2,"
last_node = maximum(edge)")
    close(f)
        myInstance = myInstance + 1
    end
end

# println(avg/numInstances)