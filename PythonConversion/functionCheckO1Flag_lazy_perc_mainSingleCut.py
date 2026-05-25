import numpy as np
import importlib

importlib.import_module("functionGetCellInfo")
from functionGetCellInfo import getCellInfo
importlib.import_module("functionGbound")
from functionGbound import gx_bound

def checkO1Flag(m,x,z,Len,O1Flag,delta1,newCell,edge,origin,destination,last_x,x_now,d, k,z_now,df_cell,K_bar):
    if not np.array_equal(last_x, x_now):
        K_bar = list(range(newCell+1))
    coef_x = [0]*Len
    constant_SP = 0
    
    p = df_cell['PROB']
        # print("checkO1Flag/ K_bar = ", K_bar)
    for k in range(newCell+1):
        # for k in K_bar:
        # print("\nk = ", k)
        c_L, c_U, M, c, c_g, y = getCellInfo(k, x_now, "c_g", d,  df_cell)
        if k in K_bar:
            y, gx, SP, label, path = gx_bound(c, c_g, edge,origin,destination)
            df_cell.at[k, 'g'] = gx
            df_cell.at[k,'Y'] = y
            df_cell.at[k, 'PI'] = label
        else:
            gx = df_cell.at[k, 'g']
            y = df_cell.at[k,'Y'] 
            
        y_temp = np.where(df_cell.at[k,'Y']>0)[0]
        print("y_temp ", y_temp)
        print("c_temp ", c[y_temp])
        print("d_temp ", d[y_temp])
        print("p ", list(p))
        coef_x = coef_x + p[k]*np.array([a*b for a,b in zip(y,d)])
        # print("g = ", list(df_cell['g']), " recalc")
        # for k in range(newCell+1):
            # print(np.where[df_cell.at[k,'Y'][0]>0][0])
            
            
        constant_SP = constant_SP +  p[k]*sum(c[i]*y[i] for i in range(Len))
        # print(coef_x)
        # print(x_now)
        # print(constant_SP)
    print("z = ", z_now)
    print("z > ", sum(coef_x[i]*x_now[i] for i in range(Len))+ constant_SP + 10**(-4))
    if z_now > sum(coef_x[i]*x_now[i] for i in range(Len))+ constant_SP + 10**(-4): #z_now[k] - gx > delta1*gx: #Used to be z_now[k] - gx > delta1:
            # con_num += 1
#                 constraints_dict
#                 # key = current_cell k
#                 # Retrieve the record for the specified key
#                 target_key = str(k)
#                 target_record = constraints_dict[target_key]
        m.cbLazy(m._z <= sum(coef_x[i]*m._x[i] for i in range(Len)) + constant_SP)

        temp_index = np.where(coef_x > 0)[0]
        # print(m._z <= sum(coef_x[i]*m._x[i] for i in temp_index) + constant_SP)
        O1Flag = False
#                 print(constraints_dict)
                
#                 # Access the constraints and values for the retrieved record
#                 target_cons = target_record["cons"]
#                 target_info = target_record["info"]

#                 # Print information about the retrieved record
#                 print(f"Record for cell: {target_key}")
#                 print("Constraints:")
#                 for constraint in target_cons:
#                     print(f"  {constraint.ConstrName}")
#                 print("Values:")
#                 for key, value in target_info.items():
#                     print(f"  {key}: {value}")
            # dtypes = {
            #     'CELL': int,
            #     'Y': object,
            #     'SP': object,  # Assuming 'Y' contains arrays
            #     'con': object
            # }    
            # new_row_data = {
            #                 'CELL': k,
            #                 'Y': Y_k,
            #                 'SP':newCell_RHS,
            #                 'con': [] #m.cbLazy(m._z[k] <= sum(d[i] * m._x[i] * y[i] for i in range(Len)) + SP)
            #             }
            # # model.cbLazy(gp.quicksum(model._vars[i, j] for i, j in combinations(tour, 2))<= len(tour)-1)
        
            # # df_constraints.loc[con_num - 1] = [con_num, newCell, Y_k.tolist(), newCell_RHS]
            
            # df_new_row = pd.DataFrame(new_row_data, columns=dtypes.keys()).astype(dtypes)
                # df_constraints = pd.concat([df_constraints,df_new_row], axis=0, ignore_index=True)
                # df_constraints = df_constraints.append(new_row_data, ignore_index=True)
                # df_constraints.loc[con_num] = [con_num, k, y.tolist(), SP]
                #Example: m.addConstr(z[1] <= SP_init + sum(yy[i]*x[i]*d[i] for i in range(Len)))
                # constr[con_num] = m.addConstr(m, z[k] <= sum(d[i] * y[i] * x[i] for i in range(1, Len + 1)) + SP)
                # print("Len ", Len)
                # print("d ", len(d))
                
                # m.addConstr(z[k] <= sum(d[i] * y[i] * x[i] for i in range(Len)) + SP)
                # O1Flag = False
    return O1Flag, K_bar#,df_constraints