def checkO1Flag():
    if not np.array_equal(last_x, x_now):
        K_bar = list(range(1, newCell + 1))
        last_x = x_now
        for k in K_bar:
            c_L, c_U, M, c, c_g = getCellInfo(k, x_now, "c_g")
            y, gx, SP, T, pred, label, path = gx_bound(c, c_g, edge)
            df_cell.at[k, 'g'] = gx
            df_cell.at[k, 'Y'] = y
            df_cell.at[k, 'PI'] = label
            if z_now[k - 1] - gx > delta1:
                con_num += 1
                df_constraints.loc[con_num] = [con_num, k, y.tolist(), SP]
                constr[con_num] = @constraint(m, z[k] <= sum(d[i] * y[i] * x[i] for i in range(1, Len + 1)) + SP)
                O1Flag = False
    return O1Flag