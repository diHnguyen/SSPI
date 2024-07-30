using JuMP, Gurobi
model = direct_model(Gurobi.Optimizer())
N = 30
@variable(model, x[1:N], Bin)
@constraint(model, rand(N)' * x  <= 10)
@objective(model, Max, rand(N)' * x)
data = Any[]
start_time = 0.0
function my_callback_function(cb_data, cb_where::Cint)
    @show cb_where
    if cb_where == GRB_CB_MIPSOL
        objbst = Ref{Cdouble}()
        GRBcbget(cb_data, cb_where, GRB_CB_MIP_OBJBST, objbst)
        objbnd = Ref{Cdouble}()
        GRBcbget(cb_data, cb_where, GRB_CB_MIP_OBJBND, objbnd)    
        println("Best Obj ", objbst[])
        println("Best Bound ", objbnd[])
        push!(data, (time() - start_time, objbst[], objbnd[]))
    end
    return
end
MOI.set(model, Gurobi.CallbackFunction(), my_callback_function)
start_time = time()
optimize!(model)
open("data.csv", "w") do io
    for x in data
        println(io, join(x, ", "))
    end
end