function ArcSplit(x_now,arc_split,k,c_L, c_U, M,y, label)
    global A1, A2, A3, A4, A5, edge, destination,d
    # global K_bar, K_newly_added, d, df_cell
    # 
    c = (c_L+c_U)/2
    mean_split = true
    i = edge[arc_split,1]
    j = edge[arc_split,2]
    # println("y ", edge[findall(y.>0.9),:])
    # println("arc ", edge[arc_split,:], c_L[arc_split], " ", c_U[arc_split])
    # println("pi[i]=", label[i], " ; pi[j]=", label[j])
    if A3==0 #0=Split using SA if possible
        #let arc_split correspond to (i,j) 
        into_j = findall((edge[:,2].== j) .& (edge[:,1].!= i)) #return indices of arcs
        # cost_j = zeros(destination)
        temp_min = 10e6
        to_compare_arc = 0
        if y[arc_split] > 0.9 #arc_split in y -- looking for labels/costs to replace (i,j)
            # println("(i,j) in Y")
            
            for arc_index in into_j
                # println("Checking ", edge[arc_index,:])
                out_k = edge[arc_index, 1]
                # println("out_k = ", out_k)
                temp_c = (c[arc_index]+d[arc_index]*x_now[arc_index]) + label[out_k]
                # println("would-be label = ", temp_c)
                
                if temp_min > temp_c #c_L[arc_index] + label[out_k]
                    temp_min = temp_c #c_L[arc_index] + label[out_k]
                    to_compare_arc = arc_index
                end
            end
            # println("temp_min = ", temp_min)
            # println("to_compare_arc ", edge[to_compare_arc,:])
            max_current_label = (c_U[arc_split]+d[arc_split]*x_now[arc_split]) + label[i]
            # println("temp_min " , temp_min, " ; max_current_label = ", max_current_label)
            if temp_min < max_current_label - 0.0001
                ΔU = max_current_label - temp_min
                ΔL = M[arc_split] - ΔU
                # println("ΔL = ", ΔL, "; ΔU = ",ΔU )
                # ΔL = ΔL/2
                # ΔU = ΔU/2
                mean_split=false
            end
        else #arc_split not in y -- check directly with labels to see when (i,j) is on shortest path
            # println(edge[arc_split,:], " not in Y")
            # println("Checking ", edge[arc_index,:])
            # println("out_k = ", out_k)
            c2 = deepcopy(c)
            c2[arc_split] = c_L[arc_split]
            # println("arc_split cost: ", c2[
            c2_g = c2 + d.*x_now
            y2, g2, SP2, T2, pred2, label2 = gx_bound(c2, c2_g, edge)
            y_index = findall(y.>0.9)
            y2_index = findall(y2.>0.9)
            y_cost_c2 = sum(y[i]*(c2[i]+d[i]*x_now[i]) for i=1:length(d))
            y2_cost_c2 = sum(y2[i]*(c2[i]+d[i]*x_now[i]) for i=1:length(d))
            # println("cost y ", y_cost_c2)
            # println("cost y2 ", y2_cost_c2)
            # println("arc_split cost ", c2[arc_split], " ", c[arc_split])
            ΔL = y_cost_c2 - y2_cost_c2
            # println("ΔL < M[arc_split] ", ΔL < M[arc_split])
            if (ΔL > 0.0001) & (ΔL < M[arc_split] - 0.0001)
                mean_split = false
                # println("ΔL = ", ΔL, "; M[arc_split] = ", M[arc_split])
                ΔU = M[arc_split] - ΔL
                # ΔL = ΔL/2
                # ΔU = ΔU/2
                # println("mean_split ", mean_split)
            end
            
            
#             if (issubset(y_index, y2_index)==false) || (issubset(y_index, y2_index) == false)
#                 shared_arcs = intersect(y_index, y2_index)
#                 cycle = setdiff(y_index, shared_arcs)
#                 cycle2 = setdiff(y2_index, shared_arcs)
#                 println("cycle ", edge[cycle,:], "; cycle2 ", edge[cycle2,:])
                
#                 cycle_nodes_outgoing = edge[cycle,1]
#                 current_arc = deepcopy(arc_split)
#                 found_start_cycle = false
#                 start_cycle_node = 0
#                 cycleCost2 = 0
#                 while found_start_cycle == false
#                     current_node = edge[current_arc, 1] #start with i
#                     # println("current_node ", current_node, " - ", (current_node in cycle_nodes_outgoing))
#                     cycleCost2 = cycleCost2 + (c2[current_arc]+d[current_arc]*x_now[current_arc])
#                     println("cycleCost2 = ", cycleCost2)
#                     if (current_node in cycle_nodes_outgoing) == true
#                         found_start_cycle = true
#                         # println("\tfound_start_cycle ", found_start_cycle)
#                     else
#                         _i = findall(edge[cycle2,2].== current_node)[1]
#                         # println("_i ", _i)
#                         current_arc = cycle2[_i]
#                         println("next arc ", current_arc, " ", edge[current_arc, :])
#                     end    
#                     # println("found_start_cycle ", found_start_cycle)
#                     # break
#                     start_cycle_node = current_node
#                 end
#                 println("start cycle node ", start_cycle_node)
#                 println("first half cost ", cycleCost2,"\n")
                
#                 current_arc = deepcopy(arc_split)
#                 found_end_cycle = false
#                 end_cycle_node = 0
#                 cycleCost2 = cycleCost2 - c2[arc_split]
#                 cycle_nodes_incoming = edge[cycle,2]
#                 while found_end_cycle == false
#                     current_node = edge[current_arc, 2] #start with j
#                     # println("curre/nt_node ", current_node, " - ", (current_node in cycle_nodes_incoming))
#                     cycleCost2 = cycleCost2 + (c2[current_arc]+d[current_arc]*x_now[current_arc])
#                     println("cycleCost2 = ", cycleCost2)
#                     if (current_node in cycle_nodes_incoming) == true
#                         found_end_cycle = true
#                         # println("\tfound_start_cycle ", found_start_cycle)
#                     else
#                         _i = findall(edge[cycle2,1].== current_node)[1]
#                         # println("_i ", _i)
#                         current_arc = cycle2[_i]
#                         println("next arc ", current_arc, " ", edge[current_arc, :], " ", c2[current_arc])
#                     end    
#                     # println("found_end_cycle ", found_end_cycle)
#                     end_cycle_node = current_node
#                     # break
#                 end
#                 println("end cycle node ", end_cycle_node)
#                 println("all cost C2 ", cycleCost2,"\n")
                
#                 println("cycle ", edge[cycle, :])
#                 # println("findall(edge[cycle,1].== start_cycle_node)[1] ", findall(edge[cycle,1].== start_cycle_node)[1])
#                 _i = findall(edge[cycle,1].== start_cycle_node)[1]
#                 # println("current_arc ", current_arc)
#                 current_arc =cycle[_i]
#                 println("C1 current arc ", edge[current_arc,:], " current_arc ", current_arc, " ", c2[current_arc])
#                 found_end_cycle = false
#                 cycleCost = 0
#                 cycle_nodes_incoming = edge[cycle,2]
#                 while found_end_cycle == false
#                     current_node = edge[current_arc, 2] #start with j
#                     # println("1current_node ", current_node, " - ", (current_node in cycle_nodes_incoming))
#                     cycleCost = cycleCost + (c[current_arc]+d[current_arc]*x_now[current_arc])
#                     println("cycleCost = ", cycleCost)
#                     # println("current_node == end_cycle_node ", current_node == end_cycle_node)
#                     if current_node == end_cycle_node
#                         found_end_cycle = true
#                         # println("\tfound_start_cycle ", found_start_cycle)
#                     else
#                         _i = findall(edge[cycle,1].== current_node)[1]
#                         # println("1_i ", _i)
#                         current_arc = cycle[_i]
#                         println("1next arc ", current_arc, " ", edge[current_arc, :], " ", c2[current_arc])
#                     end    
#                     println("1found_end_cycle ", found_end_cycle)
#                     # break
#                 end
#                 println("1all cost C", cycleCost,"\n")
                
#                 if cycleCost2 < cycleCost
#                     #Find the gap
#                     # mean_split may be false 
#                 end
                
#                 # println("cycle_set ", edge[cycle_set,:])
#                 println("c_L[arc_split] + label[i] = ", c_L[arc_split] + label[i])
#                 if  c_L[arc_split] + label[i] < label[j] - 0.0001
#                     ΔL = label[j] - (c_L[arc_split] + label[i])
#                     ΔU = M[arc_split] - ΔL
#                     # ΔL = ΔL/2
#                     # ΔU = ΔU/2
#                     mean_split=false
#                 end
#             end
        end
    end
    if A3==1 || mean_split == true # 1=Split at mean base cost - we can always do so
        # M_ = zeros(Len)
        # M_[arc_split] = M[arc_split]/2
        # Δ =  #4 
        ΔL = M[arc_split]/2 #The second /2 happens in function Partition()
        ΔU = deepcopy(ΔL)
    end
    # println("mean split? " , mean_split)
    # println("ΔL = ", ΔL, " ; ΔU = ", ΔU)
    #     end 
    return ΔL, ΔU
end