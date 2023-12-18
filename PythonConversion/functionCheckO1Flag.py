import numpy as np
import importlib

importlib.import_module("functionGetCellInfo")
from functionGetCellInfo import getCellInfo
importlib.import_module("functionGbound")
from functionGbound import gx_bound

def checkO1Flag(m,x,z,Len,O1Flag,delta1,newCell,edge,origin,destination,last_x,x_now,d, k,z_now,df_cell,constraints_dict):
    if not np.array_equal(last_x, x_now):
        K_bar = list(range(1, newCell + 1))
        last_x = x_now
        for k in K_bar:
            c_L, c_U, M, c, c_g, y = getCellInfo(k, x_now, "c_g", d,  df_cell)
            y, gx, SP, T, pred, label, path = gx_bound(c, c_g, edge,origin,destination)
            df_cell.loc[df_cell.CELL==k, 'g'] = gx
            # t = np.array(df_cell.loc[df_cell.CELL==k, 'Y'])
            # print("Y ", np.array(df_cell.loc[df_cell.CELL==k]['Y'][0]))
            # print("y ", np.array(y))
            df_cell.loc[df_cell.CELL==k, 'Y'][0] = y
            df_cell.loc[df_cell.CELL==k, 'PI'][0] = label
            print("z_now[k-1]", z_now[k])
            print("gx ", gx)
            if z_now[k] - gx > delta1:
                # con_num += 1
                constraints_dict
                # key = current_cell k
                # Retrieve the record for the specified key
                target_key = str(k)
                target_record = constraints_dict[target_key]
                
                print(constraints_dict)
                
                # Access the constraints and values for the retrieved record
                target_cons = target_record["cons"]
                target_info = target_record["info"]

                # Print information about the retrieved record
                print(f"Record for cell: {target_key}")
                print("Constraints:")
                for constraint in target_cons:
                    print(f"  {constraint.ConstrName}")
                print("Values:")
                for key, value in target_info.items():
                    print(f"  {key}: {value}")
                # df_constraints.loc[con_num] = [con_num, k, y.tolist(), SP]
                #Example: m.addConstr(z[1] <= SP_init + sum(yy[i]*x[i]*d[i] for i in range(Len)))
                # constr[con_num] = m.addConstr(m, z[k] <= sum(d[i] * y[i] * x[i] for i in range(1, Len + 1)) + SP)
                print("Len ", Len)
                print("d ", len(d))
                m.addConstr(z[k] <= sum(d[i] * y[i] * x[i] for i in range(Len)) + SP)
                O1Flag = False
    return O1Flag, K_bar