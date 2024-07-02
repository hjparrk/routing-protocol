import os
import sys
import networkx as nx
import matplotlib.pyplot as plt
import random


def get_nodes(n):
    # return a list of n nodes labelled alphabetically
    # eg) ["A", "B", ... ,"G"]
    return [chr(i) for i in range(ord('A'), ord('A') + n)]


def get_ports(nodes):
    # return a dic of ports for each node
    # eg) A: 6000, B: 6001, C: 6002, ...
    dic = {}
    counter = 0
    for node in nodes:
        dic[node] = 6000 + counter
        counter += 1
    return dic


def generate_random_graph(nodes):
    # create an empty undirected graph
    G = nx.Graph()

    # add n number of nodes to the graph
    G.add_nodes_from(nodes)

    # ensures each node is connected to at least one of other nodes
    for i in range(len(nodes)):
        # u: current node, v: neighbour node
        u = nodes[i]
        while True:
            # randomly choose a node
            v = random.choice(list(G.nodes))
            # this will not create a self-loop edge
            if u != v:
                break
        G.add_edge(u, v, cost=round(random.uniform(0.0, 10.0), 1))

    # assign the rest edges to 2 randomly chosen nodes
    num_edges = int(sys.argv[2])
    while G.number_of_edges() < num_edges:
        # choose two different random nodes
        u, v = random.choices(list(G.nodes), k=2)
        # this will not create a self-loop edge
        if u == v:
            continue
        # add an edge if it does not exist
        if not G.has_edge(u, v):
            G.add_edge(u, v, cost=round(random.uniform(0.0, 10.0), 1))

    # return the randomly generated undirected graph with costs of positive number (float)
    return G


def generate_configs(graph, ports):
    # generate config files for each node

    # directory name
    dir_name = "graph"

    # check if the directory exists and create it if not
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    # iterate through the nodes
    for node in graph.nodes:

        # neighbours of the node
        neighbours = list(graph.neighbors(node))

        # construct the filename
        filename = os.path.join(dir_name, f"{node}config.txt")

        # open the file in write mode. this will create the file if it does not exist.
        # if the file already exists, it will be overwritten.
        with open(filename, 'w') as file:
            # Optionally, write something to the file. For example, write the element value.
            file.write(f"{len(neighbours)}\n")
            for neighbour in neighbours:
                cost = graph.get_edge_data(node, neighbour)["cost"]
                file.write(f"{neighbour} {cost} {ports[neighbour]}\n")


def generate_visualised_graph(graph):
    # visualise the graph

    # set up the figure size and resolution
    plt.figure(figsize=(20, 10), dpi=300)

    # position/general layout of the nodes in the graph
    pos = nx.circular_layout(graph)

    # draw the nodes
    nx.draw(graph, pos, with_labels=True, node_color='skyblue', node_size=2400)

    # draw the edges
    edge_labels = nx.get_edge_attributes(graph, 'cost')
    nx.draw_networkx_edge_labels(graph,
                                 pos,
                                 edge_labels=edge_labels,
                                 font_size=16)

    # save the graph as a png file into current directory
    plt.savefig('graph_visualisation.png', format='png')
    plt.close()


def run():
    # a list of n(sys.argv[1]) nodes sorted alphabetically
    nodes = get_nodes(int(sys.argv[1]))

    # a list of ports corresponding to each node
    ports = get_ports(nodes)

    while True:
        # a generated random undirected graph with link cost (float)
        graph = generate_random_graph(nodes)

        # this ensures the graph is connected
        if nx.is_connected(graph):
            break

    # generate config files for each node
    generate_configs(graph, ports)

    # optional: visualise the graph
    generate_visualised_graph(graph)


if __name__ == "__main__":
    # run the program
    run()
