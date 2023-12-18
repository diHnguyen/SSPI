import numpy as np
def getCellInfo(k, x_now, c_or_cL, d, df_cell):
    print("Cell ", k)
    print(df_cell.loc[df_cell.CELL==k,"LB"])
    c_L = np.array(df_cell.loc[df_cell.CELL==k,"LB"][0])
    c_U = np.array(df_cell.loc[df_cell.CELL==k,"UB"][0])
    print(df_cell)
    print("c_L ", c_L)
    print("c_U ", c_U)
    # print("c_L[0] ",c_L[1])
    M = c_U - c_L
    c = (c_U + c_L)/2  
    print("M ", M)
    if c_or_cL == "c_g":
        c_with_x = c + np.array(d)*np.array(x_now)
    elif c_or_cL == "c_g_L":
        # c_g_L 
        c_with_x= c_L + np.array(d)*np.array(x_now)

    yK = np.array(df_cell.loc[df_cell.CELL==k,"Y"])
    
    return c_L, c_U, M, c, c_with_x, yK