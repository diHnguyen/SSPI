import networkx as nx
import numpy as np

def gx_bound(c, c_g, edge,origin,destination):
    start_node = np.array(edge)[:, 0]
    end_node = np.array(edge)[:, 1]

    no_node = max(max(start_node), max(end_node))+1
    no_link = len(start_node)

    def get_shortest_x(state, start_node, end_node, origin, destination):
        _x = np.zeros(len(start_node), dtype=int)
        _path = list(nx.shortest_path(state, source=origin, target=destination))

        for i in range(len(_path) - 1):
            _start = _path[i]
            _end = _path[i + 1]

            for j in range(len(start_node)):
                if start_node[j] == _start and end_node[j] == _end:
                    _x[j] = 1
                    break

        return _x

    graph = nx.DiGraph()
    distmx = np.full((no_node, no_node), np.inf)
    
    # print(start_node)
    # print(end_node)
    # print(distmx)
    # print(c_g)
    # print(no_link)
    # Adding links to the graph
    for i in range(no_link):
        # print("\ni ", i)
        # print("start ", start_node[i], "; end ", end_node[i])
        graph.add_edge(start_node[i], end_node[i])
        distmx[start_node[i], end_node[i]] = c_g[i]

    # Run Dijkstra's Algorithm from the origin node to all nodes
    state = nx.single_source_dijkstra_path_length(graph, source=origin, weight='weight')
    label = np.array([state[node] if node in state else np.inf for node in range(1, no_node + 1)])
    pred = state

    b_arc = ""
    for i in range(1, len(pred)):
        if pred[i] != origin:
            b_arc += f"({pred[i]}, {i})"

    # Retrieving the shortest path
    path = list(nx.shortest_path(graph, source=origin, target=destination))

    # Retrieving the 'x' variable in a 0-1 vector
    y = get_shortest_x(graph, start_node, end_node, origin, destination)

    gx = np.sum(np.array(c_g) * y)
    SP = np.sum(np.array(c) * y)

    T = [1 if pred[edge[i, 1]] == edge[i, 0] else 0 for i in range(no_link)]

    return y, gx, SP, T, pred, label, path
