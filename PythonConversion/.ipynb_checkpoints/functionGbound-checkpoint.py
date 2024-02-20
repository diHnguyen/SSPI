import networkx as nx
import numpy as np

def gx_bound(c, c_g, edge,origin,destination):
    G = nx.DiGraph()
    for _e in range(len(c)):
        # print("\t", edge[_e])
        G.add_edge(edge[_e,0],edge[_e,1], weight=c_g[_e])
    # distmx = np.full((no_node, no_node), np.inf)
    # Find the shortest paths and lengths from the source node to all other nodes
    shortest_paths_lengths = nx.single_source_dijkstra_path_length(G, source=origin, weight='weight')
    # print(G)
#     # Get the list of predecessors for each node
#     predecessors = nx.predecessor(G, source=origin)

#     # Print the results
#     for node, predecessor_list in predecessors.items():
#         print(f"Node {node}: Predecessors {predecessor_list}")
    # print(start_node)
    # print(end_node)
    # print(distmx)
    # print(c_g)
    # print(no_link)
    # Adding links to the graph
    # Print the results
    # print(shortest_paths_lengths[1])
    label = list(shortest_paths_lengths.values())
    # print("label ", label)
    # print(f"Shortest paths from node {origin} to all other nodes:")
    # for node, path_length in shortest_paths_lengths.items():
    #     print(f"To node {node}: Length = {path_length}, Path = {nx.shortest_path(G, source=origin, target=node, weight='weight')}")
    
    
    y = np.zeros(len(G.edges))
    shortest_path=nx.shortest_path(G, source=origin, target=destination, weight='weight')
    # print("shortest_path ", shortest_path)
    for i in range(len(shortest_path) - 1):
        start_node = shortest_path[i]
        end_node = shortest_path[i + 1]
        # print("\t", start_node, "\t", end_node)
        # print(list(G.edges))
        # edge_index = list(G.edges).index((start_node, end_node)) #this rearranges the elements - don't do this
        a = np.array([start_node, end_node])
        edge_index = np.where((edge==a).all(1))[0]
        # print("\t edge_index ", edge_index)
        y[edge_index] = 1
    # print("y = ", y)
    gx = np.sum(np.array(c_g) * y)
    SP = np.sum(np.array(c) * y)
    
    # T = [1 if pred[edge[i, 1]] == edge[i, 0] else 0 for i in range(no_link)]

    return y, gx, SP, label, shortest_path
