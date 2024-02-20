function getCellInfo(k, x_now, c_or_cL)
    c_L = df_cell[k,:LB]
    c_U = df_cell[k,:UB]
    M = c_U - c_L
    c = (c_U + c_L)/2  
    # print("c_L = ", c_L)
    if c_or_cL == "c_g"
        c_with_x = c + d.*x_now
    elseif c_or_cL == "c_g_L"
        # c_g_L 
        c_with_x= c_L + d.*x_now
    end
    yK = df_cell[k,:Y]
    
    return c_L, c_U, M, c, c_with_x, yK
end
