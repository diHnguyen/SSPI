function hx_bound(c_L, c_U, d, x_now)
    # println("Here -1")
    global gurobi_env
    # println("Here 0")
    c = (c_L + c_U)/2
    #println(f,"Current CELL's LB = ", c_L)
    #println(f,"Current CELL's UB = ", c_U)
    #println(f,"Current interdiction x = ", x_now)
    M = c_U - c_L
    h2 = Model(() -> Gurobi.Optimizer(gurobi_env))
    # println("Here 1")
    @variable(h2, 1 >= y2[1:Len]>=0)
    # y2 = h2[:y2y2]
    @variable(h2, q[1:Len]>=0)
    
    #Setting constraints for remaining none-sink/start nodes
    outgoing = findall(edge[:,1].== 1)
    @constraint(h2, sum(y2[k] for k in outgoing) == 1)
    for i in all_nodes
        global outgoing
        if i != destination && i != origin
            incoming = findall(edge[:,2].== i)
            outgoing = findall(edge[:,1].== i)
            @constraint(h2, sum(-y2[k] for k in outgoing) + sum(y2[k] for k in incoming) == 0)
        end
    end
    
    for i = 1:Len
        @constraint(h2, q[i] >= c[i] - c_L[:,1][i] - M[i]*(1-y2[i])) #_h[i]))
    end

    @objective(h2, Min, sum((c_L[i]+d[i]*x_now[i])*y2[i] + q[i] for i=1:Len))
#     println(h2)
#     print(h2)
    # set_optimizer(h2, ()-> Gurobi.Optimizer(gurobi_env))
    optimize!(h2)
#     println("h2 is fine")
    hx = JuMP.objective_value.(h2)
    
    return JuMP.value.(y2), hx
end

