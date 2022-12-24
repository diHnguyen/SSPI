function getCellInfo(k, x_now)
    c_L = df_cell[k,:LB]
    c_U = df_cell[k,:UB]
    M = c_U - c_L
    c = (c_U + c_L)/2
    c_g_L = c_L + d.*x_now
    yK = df_cell[k,:Y]
    return c_L, c_U, M, c, c_g_L, yK
end
