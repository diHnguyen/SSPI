import numpy as np
import pandas as pd
import gurobipy as gp
import importlib
from gurobipy import GRB
import time
from time import strftime, localtime

importlib.import_module("functionGetCellInfo")
from functionGetCellInfo import getCellInfo
importlib.import_module("functionCheckO1Flag_lazy_perc") #functionCheckO1Flag_lazy_perc is correct for main_w_lazy
from functionCheckO1Flag_lazy_perc import checkO1Flag
importlib.import_module("functionGbound")
from functionGbound import gx_bound
importlib.import_module("functionHbound")
from functionHbound import hx_bound
importlib.import_module("functionPartition")
from functionPartition import Partition

def lazy_for_main(MIP_GAP, A1, A3, Len, delta1, delta2, newCell, total_time, start, K_bar, edge, origin,destination,last_x, d, b,x_now, P_set, df_cell, terminate_cond):
    #Solve MP given K cells
    # Create a new Gurobi model
    MP_obj = 0.0
    # zNum = 200000
    cRefNum = len #2000000
    K_newly_added = []
    K_removed = []
    print("terminate_cond ", terminate_cond)
    def lazy(m, where):
    # while not terminate_cond:
        if where == GRB.Callback.MIPSOL:
            # m._iter += 1
            
            # last_x = m._last_x
            # x_now = m._x_now
            df_cell = m._df_cell
            # df_lazy = m._df_lazy
            # K_removed = m._K_removed
            K_bar = m._K_bar
            K_removed = []
            
            K_newly_added = []
            # K_newly_added = m._K_newly_added
            p = m._p
            LB = m._LB
            P_set = m._P_set
            newCell = m._newCell
            terminate_cond = m._terminate_cond
            # con_num = m._con_num
            # print("m._con_num " , m._con_num)
            MP_obj = m.cbGet(gp.GRB.Callback.MIPSOL_OBJBST) #m.ObjVal
            MP_bnd = m.cbGet(gp.GRB.Callback.MIPSOL_OBJBND) #m.cbGet(GRB.Callback.MIPSOL_OBJBST)
            MP_cur = m.cbGet(gp.GRB.Callback.MIPSOL_OBJ)
            x_now = np.array(list(m.cbGetSolution(m._x).values()))
            z_now = np.array(list(m.cbGetSolution(m._z).values()))
            # x_now = np.empty(Len)
            # for i in range(Len):
            #     x_now[i] = x[i].X
                
            # z_now = np.empty(newCell+1)
            # for i in range(newCell+1):
            #     z_now[i] = z[i].X
            cur_time = time.time() - start
            # print("\n==========================================================")
            # print("Iter : ", iter, " ; MP_bnd = ", MP_bnd, " ; time ", cur_time, "; ", len(m._K_bar), "/", m._newCell+1)
            # print("==========================================================")
            print("MP_obj ", MP_obj)
            print("MP_bnd ", MP_bnd)
            print("MP_cur ", MP_cur)
            print("z_now " , z_now)
    
            print("x = ", np.where(x_now > 0.5)[0])
            x_index = np.where(x_now > 0)[0]
            # print("p = ", p)
            print("newCell = ", newCell)
                        
            O1Flag = True
            # last_x = np.array(last_x)
            # last_x_arc = np.where(last_x > 0.5)[0]
            x_now_arc = np.where(x_now > 0.5)[0]
            
            
            print("\nO1Flag Check")
            # print("x_now = ", np.where(x_now > 0.5)[0])
            K_bar = np.arange(newCell+1) #collect(1:newCell)
            # print("K_bar ", K_bar)
            last_x = x_now
    
            O1Flag = True
            # prev_last_row = len(df_constraints)
            
            O1Flag, df_constraints_added = checkO1Flag(m,x,z,Len,O1Flag,delta1,newCell,edge,origin,destination,x_now,d, z_now,df_cell)
            print("len ", len(df_constraints_added))
            if len(df_constraints_added) > 0:
                for i in range(len(df_constraints_added)):
                    k = df_constraints_added.at[i,'CELL']
                    SP = df_constraints_added.at[i,'SP']
                    y = df_constraints_added.at[i, 'Y']
                    print("Outside y ", y)
                    m.cbLazy(z[k] <= sum(d[i] * m._x[i] * y[i] for i in range(Len)) + SP)
            # df_constraints = pd.concat([df_constraints,df_constraints_added], axis=0, ignore_index=True)
    
            if O1Flag:
                print("O1Flag: Passed\n")
                terminate_cond = False

                while terminate_cond == False:
                    partitionCounter = 1
                    myCounter = 0
                    # print("Before Counter: numCells = ", newCell)
                    # print("HERE")
                    # print("myCounter ", myCounter)
                    # print("z = ", z_now, " vs RHS = ", RHS)
                    while myCounter < partitionCounter:
                        myCounter += 1
                        # print("====myCounter ", myCounter, " vs ", partitionCounter)
                        # print("K_bar = ", K_bar)
                        # print("Cells failing O2Flag")
                        
                        for k in K_bar:
                            
                            # print("\nCell ", k)
                            # if k > 3:
                            #     sys.exit()
                            c_L, c_U, M, c, c_g, yK = getCellInfo(k, x_now, "c_g", d, df_cell)
                            # c_L, c_U, M, c, c_g_L, yK = getCellInfo(k, x_now, "c_g_L", d, df_cell)
                            # print("yK = ", edge[np.where(yK > 0.5)[0]])
                            print(k, "yK = ", yK)
                            # if k==10:
                            #     print("yK ", np.where(yK > 0)[0])
                            #     y_,g_,SP_ = getPathCost(P_set,x_now, c,d, k)
                            
                            yL, gL, SPL,_,_, = gx_bound(c, c_g_L, edge,origin,destination)
                            
    
                            
                            df_cell.at[k, 'Y_Lk'] = yL
                            df_cell.at[k, 'gL'] = gL
    
                            y_h, hx = hx_bound(c_L, c_U, d, x_now,edge,origin,destination)
                            
                            
                            p_k = df_cell.at[k, 'PROB']
                            # print("Before update hx")
                            # print(df_cell)
                            df_cell.at[k, 'h'] = hx
                            gx = df_cell.at[k, 'g']
                            # print(k, " gx ", gx, " hx ", hx)
                            h_val = df_cell['h']
                            if gx - hx <= delta2*gx:
                                # print("Remove ", k, ": ", delta2*gx)
                            # if gx - hx <= delta2:
                                K_removed.append(k)
                            
    
                        print("Bounds before Partition")
                        p_val = df_cell['PROB']
                        g_val = df_cell['g']
                        UB = sum(g_val[k] * p_val[k] for k in range(newCell+1))
                        LB = sum(h_val[k] * p_val[k] for k in range(newCell+1))
                        if (UB - LB)/UB <= MIP_GAP:
                            K_bar = []
                            terminate_cond = True
                        if terminate_cond == False:
                            for k in K_bar:
                            # else:
                                # print("k ", k)
                                newCell += 1
                                ΔL, ΔU, arc_split, yL, yU, gL, gU, SP_L, SP_U,df_cell,newCell = Partition(x_now, newCell, k, p_k, c_L, c_U, M, yK, d,edge,origin,destination,Len,A1,A3,df_cell, K_newly_added)
                                
                        
                                
                        K_bar = list(set(K_bar) - set(K_removed))
                        K_bar.extend(K_newly_added)
                        K_newly_added = []
                        K_removed = []
    
                        
                        
                        if len(K_bar)==0:
                            myCounter = partitionCounter
                            terminate_cond = True
                        
                    
            total_time = time.time() - start
            
            m._last_x = last_x #Weird Gurobi behavior if move these updates to mid of the lazy call -- Don't do it
            # print("End m._last_x ", m._last_x)
            m._df_cell = df_cell
            # m._df_lazy = df_lazy
            m._K_removed = K_removed
            m._K_bar = K_bar
            # print("END : ", K_bar)
            m._K_newly_added = K_newly_added
            m._p = p
            m._LB = LB
            m._newCell = newCell
            m._terminate_cond = terminate_cond
            # m._con_num = con_num
            # x_now = np.array(m.cbGetSolution(m._x).values())
            # z_now = m.cbGetSolution(m._z)
            # m._MP_obj = MP_obj #m.cbGet(GRB.Callback.MIP_OBJBST) #m.ObjVal
            # m._MP_bnd = MP_bnd #m.cbGet(GRB.Callback.MIPSOL_OBJBST)
            m._cur_time = cur_time
            m._P_set = P_set
            m.update()
        # m.write("out.mst")

    m = gp.Model()
    m.setParam(GRB.Param.OutputFlag, 0)
    # m.setParam(GRB.Param.MIPGap, 0.01)
    # m.setParam(GRB.Param.Threads,1)
    x = m.addVars(range(Len), vtype=GRB.BINARY, name="x")
    z = m.addVars(range(newCell+1), lb=0, ub=1e6, name="z")
    print("newCell ", newCell)
    m.addConstr(x.sum() == b, "sum_x_equals_b") 
    
    # Optimize model
    p = df_cell['PROB']
    m.setObjective(sum(p[k]*z[k] for k in range(newCell+1)), sense=GRB.MAXIMIZE)
    
    m._x = x
    m._z = z
    m._best = 0
    m.Params.LazyConstraints = 1
    m._newCell = newCell
    m._df_cell = df_cell
    # m._df_lazy = df_lazy
    m._P_set = P_set
    # print("p = ",p)
    
    # Objective: Maximize sum(p[i]*z[i])
    
    # Initialize global variables
    # m._x_sol=x_sol
    # m._z_sol=z_sol
    # m._x_now=x_now
    # α_now
    # m._z_now=z_now
    # m._last_x=last_x #np.array(last_x)
    # m._con_num=con_num
    # m._cur_time = cur_time
    m._total_time=total_time
    m._iter=iter
    m._K_bar=K_bar
    m._LB=None
    m._MP_obj=None
    m._MP_bnd=None
    m._K_newly_added=K_newly_added
    m._K_removed=K_removed
    m._p = p
    m._start = start
    m._terminate_cond = terminate_cond
    # m._newCell = newCell
    # m._terminate_cond = terminate_cond
    m.update()
    # print(z <= SP_init + sum(yy[i]*x[i]*d[i] for i in range(Len)))
    m.optimize(lazy)
    x_now = np.empty(Len)
    for i in range(Len):
        x_now[i] = x[i].X
    z_now = np.empty(Len)
    for i in range(newCell+1):
        z_now[i] = z[i].X
    cur_time = time.time() - start
    # z_now = z.Z
    x_index = np.where(x_now > 0)[0]
    print('x = ', x_index)        
    print('Final optimal obj: %g' % m.ObjVal)
    print("z_now ", z_now)  
    # print("bound ", m.ObjBound)
    return x_now, m.ObjVal, newCell, terminate_cond
    