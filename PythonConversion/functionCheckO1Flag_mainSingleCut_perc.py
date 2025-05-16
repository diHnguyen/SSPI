#Same as fuctionCheckO1Flag but uses delta1 as percentage instead
import numpy as np
import importlib
import pandas as pd

importlib.import_module("functionGetCellInfo")
from functionGetCellInfo import getCellInfo
importlib.import_module("functionGbound")
from functionGbound import gx_bound

def checkO1Flag(m,x,z,Len,O1Flag,delta1,newCell,edge,origin,destination,last_x,x_now,d, k,z_now,df_cell):
    if not np.array_equal(last_x, x_now):
        K_bar = list(range(newCell+1))
        # print("checkO1Flag/ K_bar = ", K_bar)
        last_x = x_now
        # print("Running O1Flag", K_bar)
    coef_x = [0]*Len
    constant_SP = 0
    p = df_cell['PROB']
    for k in K_bar:
        c_L, c_U, M, c, c_g, Y_k = getCellInfo(k, x_now, "c_g", d,  df_cell)
        y, gx, SP, label, path = gx_bound(c, c_g, edge,origin,destination)
        coef_x = coef_x + p[k]*np.array([a*b for a,b in zip(y,d)])
        constant_SP = constant_SP +  p[k]*sum(c[i]*y[i] for i in range(Len))
        
        df_cell.at[k, 'g'] = gx
        df_cell.at[k,'Y'] = y
        df_cell.at[k, 'PI'] = label

    if z_now > sum(coef_x[i]*x_now[i] for i in range(Len))+ constant_SP + 10**(-4):
        m.addConstr(z <= sum(coef_x[i]*x[i] for i in range(Len)) + constant_SP)
        # found_cut = True
        O1Flag = False
                
            # if z_now[k] - gx > delta1*gx: #Used to be z_now[k] - gx > delta1
            #     dtypes = {
            #         'CELL': int,
            #         'Y': object,
            #         'SP': object#,  # Assuming 'Y' contains arrays
            #         # 'con': object
            #     }
                
            #     new_row_data = {
            #                     'CELL': [k],
            #                     'Y': [y],
            #                     'SP': [SP]#, #SP = newcell_RHS
            #                     # 'con': m.addConstr(z[k] <= sum(d[i] * x[i] * y[i] for i in range(Len)) + SP)
            #                 }
            #     # con = m.addConstr(z[k] <= sum(d[i] * x[i] * y[i] for i in range(Len)) + SP)
            #     # print(type(con))
            #     df_new_row = pd.DataFrame(new_row_data, columns=dtypes.keys()).astype(dtypes)
            #     # df_constraints.loc[con_num - 1] = [con_num, newCell, Y_k.tolist(), newCell_RHS]
            #     # df_constraints = df_constraints.append(new_row_data, ignore_index=True)
                
            #     df_constraints = pd.concat([df_constraints,df_new_row], axis=0, ignore_index=True)
            #     # df_constraints.loc[con_num] = [con_num, k, y.tolist(), SP]
            #     #Example: m.addConstr(z[1] <= SP_init + sum(yy[i]*x[i]*d[i] for i in range(Len)))
            #     # constr[con_num] = m.addConstr(m, z[k] <= sum(d[i] * y[i] * x[i] for i in range(1, Len + 1)) + SP)
            #     # print("Len ", Len)
            #     # print("d ", len(d))
            #     O1Flag = False
                
            # print("After Concat - if any")
            # for index, row in df_constraints[(df_constraints.CELL == k)].iterrows():
            #     print(k, "; ", np.where(row['Y']>0)[0], "; ",row['SP'] )
                # m.addConstr(z[k] <= sum(d[i] * y[i] * x[i] for i in range(Len)) + SP)
                
            # print(k, "After Concat")
            # for index, row in df_constraints[(df_constraints.CELL == k)].iterrows():
            #     print(k, "; ", np.where(np.array(row['Y'])>0)[0], "; ",row['SP'] )
    return O1Flag, K_bar #, df_cell , df_constraints