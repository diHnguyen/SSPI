function hx_bound(c_L, c_U, d, x_now)
    
    c = (c_L + c_U)/2
    #println(f,"Current CELL's LB = ", c_L)
    #println(f,"Current CELL's UB = ", c_U)
    #println(f,"Current interdiction x = ", x_now)
    M = c_U - c_L

    h2 = copy(h1)
    y2 = h2[:y_h]
    @variable(h2, q[1:Len]>=0)
    for i = 1:Len
        @constraint(h2, q[i] >= c[i] - c_L[:,1][i] - M[i]*(1-y2[i])) #_h[i]))
    end

    @objective(h2, Min, sum((c_L[i]+d[i]*x_now[i])*y2[i] + q[i] for i=1:Len))
#     println(h2)
#     print(h2)
    set_optimizer(h2, ()-> Gurobi.Optimizer(gurobi_env))
    optimize!(h2)
#     println("h2 is fine")
    hx = JuMP.objective_value.(h2)
    
    return JuMP.value.(y2), hx
end

