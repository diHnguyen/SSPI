function good_callback_function(cb_data)
    if callback_value(x) > 2
        con = @build_constraint(x <= 2)
        MOI.submit(model, MOI.LazyConstraint(cb_data), con)
    end
end