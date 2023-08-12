using JuMP, Gurobi
model = Model(Gurobi.Optimizer)
@variable(model, 0 <= x[i=1:3, j=i+1:3] <= 2.5, Int)
function my_callback_function(cb_data)
    x_val = callback_value.(Ref(cb_data), x)
    display(x_val)
    for i=1:3, j=i+1:3
        con = @build_constraint(x[i, j] <= floor(Int, x_val[i, j]))
        MOI.submit(model, MOI.LazyConstraint(cb_data), con)
    end
end
MOI.set(model, MOI.LazyConstraintCallback(), my_callback_function)
optimize!(model)