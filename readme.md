# Routing Algorithm

## Prerequisites

A random undirected graph should be generated prior to running the routing algorithm program

> Assumptions
>
> -   Every node in the graph is connected to another node with an undirected edge
> -   There does not exist self-loop edges
> -   Every edge has cost of only positive value (float)

### Environment

MacOS

### Installation

Use the package manager `pip` to install the following packages.

```bash
pip install networkx
pip install matplotlib
```

If module not found error occurs like this,

```
John-Doe:ROOT-DIRECTORY johndoe$ python3 generate_graph.py
Traceback (most recent call last):
  File "/Users/johndoe/folder/generate_graph.py", line 3, in <module>
    import networkx as nx
ModuleNotFoundError: No module named 'networkx'
```

Please try the instructions below.

Open terminal, and enter `which python`.
Then, it will print the path of python in your machine like this.

```
/usr/bin/python
```

Copy the path, and try the command below in the terminal

```
/usr/bin/python -m pip install <package>
```

### Usage

The graph generating program named `generate_graph.py` accepts `2` system arguments: `number of nodes`, `number of edges` in this order.
If you run the program, it generates a random undirected graph and creates a directory `graph` (if not exists) then creates `config.txt` file in the directory for each `node` that includes `number of neighbouring nodes`, `ID of neighbour`, `cost to neighbour`, `listening port of neighbour`.

> (Optional) For better understanding of the topology of the graph, the visualisation of the graph (png format) is also generated.

```bash
python3 generate_graph.py 10 15
```

### Output Example

Directory structure

```
Root directory
│   main.py
│   generate_graph.py
│   readme.md
│   graph_visualisation.png
└───graph
│   │   Aconfig.txt
│   │   Bconfig.txt
│   │   Cconfig.txt
│   │   Dconfig.txt
│   │       ...
│   │   Jconfig.txt
```

Aconfig.txt

```
2
B 1.3 6001
E 5.7 6004
```

The line 1 represents the number of neighbouring nodes, the lines below represent neighbour ID, cost, port respectively.

## Getting Started (main program)

First and foremost, install any missing packages required to run our program if necessary, which are

-   sys
-   socket
-   json
-   time
-   threading
-   heapq
    Also, make sure your python version is at least 3.7 as our code is likely to be dependent on new implementation of dictionary from python version 3.7 and above where dictionaries started keeping track of order of inserted items.

Open up N many terminals where you can run each of your node and give it commands through their own CLI. If you are to test our program on graph having 10 nodes, you should open up 10 separate terminal tabs.

On each terminal tab, run the following command
`python3 Routing.py <NODE-ID> <PORT-NO> <Config-File>`
eg. `python3 Routing.py A 6000 graph/Aconfig.txt`

If you think this is too much work, and is happy to give up control on some or most of the nodes, you may opt to execute some or most nodes in background: `python3 Routing.py <NODE-ID> <PORT-NO> <Config-File> &`. However, this is not recommeded by us as you need to manually kill background processes when testing is done.

### Command Line Interface (CLI)

When you run the program, you will be greeted with instructions on how to use CLI, also attached below.

1. **exit**: ends the program and clean up children threads
2. **status**: prints the node's current preception of Graph and other auxiiliary information
3. **route**: calculates shortest path to all other nodes in the graph
4. **update-link <neighbour-node> <new-cost>**: updates the link cost of edge connecting to neighbour node
5. **mark-down**: sets node as down (no broadcasting / listening)
6. **mark-up**: sets node as up again

To end the program, you can enter exit in the CLI, or give it kill signal through ctrl+C. Allow some time to terminate, as it can take up to 10 seconds cleaning up sleeping child threads. Note that some commands 2 (status) and 3 (route) are there to help you debug / investigate into the inner workings of program more effectively, and was not specified in assessment spec.
