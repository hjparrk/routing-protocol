from sys import argv
import socket
import json
import time
import threading
import heapq


# Main node's current preception of the graph represented in adjacency list
# Gradually syncrhonises with neighbour nodes to gain full understanding of the graph
Graph: dict[str, list[list[str, float, float]]] = dict()


def add_or_update_edge(nodeA: str, nodeB: str, cost: str, updated: str | float):
    cost = float(cost)
    updated = int(updated)
    if nodeA not in Graph:
        Graph[nodeA] = [["power", "up", updated]]
    if nodeB not in Graph:
        Graph[nodeB] = [["power", "up", updated]]

    # no negative link costs allowed (plus, it doesn't make sense, ay?)
    assert cost > 0

    for A, B in [(nodeA, nodeB), (nodeB, nodeA)]:
        seen_B = False
        for edge in Graph[A][1:]:
            if edge[0] != B:
                continue
            seen_B = True
            # *Update* edge if cost is different (therefore making the edge "new")
            # AND when the new edge-info is more up to date
            if edge[1] != cost and edge[2] < updated:
                edge[1] = cost
                edge[2] = updated
        if not seen_B:
            # *Append* edge if it didn't exists in main node's perception of the graph before
            Graph[A].append([B, cost, updated])


main_nodeID = argv[1]
main_node_port = int(argv[2])

start_time = time.time()
program_stopped = False

neighbours_info = []
# Initialise the Graph with neighbour nodes
# Record port number of neighbour nodes for main node to communicate with them
with open(argv[3], 'r') as config_file:
    neighbour_count = int(config_file.readline().strip())
    for _ in range(neighbour_count):
        nodeID, cost, n_port = config_file.readline().strip().split(' ')
        neighbours_info.append((nodeID, int(n_port)))
        add_or_update_edge(main_nodeID, nodeID, cost, time.time())


def update_node_failure(target_nodeID: str, state: str, updated: str | float, main=False):
    if target_nodeID not in Graph:
        return
    target_node = Graph[target_nodeID]
    _, power_state, recorded = target_node[0]
    updated = int(updated)
    # make update regarding to node failures if changes happend (on -> off, off -> on)
    # and when the time that change happend if more up to date than the recorded one
    if power_state != state and recorded < updated:
        target_node[0] = ["power", state, updated]


def listen():
    main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    main_socket.bind(('localhost', main_node_port))
    main_socket.listen(10)
    main_socket.settimeout(1)  # to prevent waiting indefinitely
    last_received_time = dict()

    while True:
        if program_stopped:
            break
        elif Graph[main_nodeID][0][1] == "down":
            time.sleep(0.1)
            continue
        for neighbourID, last_received in last_received_time.items():
            if time.time() - last_received > 12:  # double check
                update_node_failure(neighbourID, "down", time.time())
            else:
                update_node_failure(neighbourID, "up", time.time())
        try:
            conn, _ = main_socket.accept()
            message = conn.recv(1024).decode()
            GR = json.loads(message)  # neighbour's perception of the graph
            for node, edge_list in GR.items():
                update_node_failure(node, edge_list[0][1], edge_list[0][2])
                for other_node, cost, updated in edge_list[1:]:
                    add_or_update_edge(node, other_node, cost, updated)
            sender: str = next(iter(GR))
            # print(sender, time.time())
            last_received_time[sender] = time.time()
        except:
            continue
    main_socket.close()


def broadcast():
    while True:
        time.sleep(10)
        if program_stopped:
            break
        if Graph[main_nodeID][0][1] == "down":
            time.sleep(.1)
            continue
        for neighbourID, neighbour_port in neighbours_info:
            try:
                if Graph[neighbourID][0][1] == "down":
                    # print("skipping broadcasting to", neighbourID)
                    continue
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect(('localhost', neighbour_port))
                sock.sendall(json.dumps(Graph).encode())
                sock.close()
                # print("broadcasted to", neighbourID)
            except Exception as e:
                # print("Failed to braodcst to", neighbourID)
                pass


# Start listening for messages that represent neighbour nodes' "perception" of the graph
# Then, expand the main node's perception of the grpah by adding missing nodes hinted by incoming messages
# For every 10 seconds, broadcast main node's perception of the grpah to its neighbours
t1 = threading.Thread(target=listen)
t2 = threading.Thread(target=broadcast)
t1.start()
t2.start()


class Node:
    def __init__(self, id, cost):
        self.id = id
        self.path = main_nodeID
        self.cost = cost

    def __str__(self):
        return f"Least cost path from {main_nodeID} to {self.id}: {self.path}, link cost: {round(self.cost, 2)}"

    def __lt__(self, other: 'Node'):
        return self.cost < other.cost


def find_shortest_route():
    PQ: list['Node'] = []  # priority queue with heap data structure
    for nodeID in Graph:
        if Graph[nodeID][0][1] == "down":
            continue
        cost = 0 if nodeID == main_nodeID else float('inf')
        heapq.heappush(PQ, Node(nodeID, cost))

    while len(PQ) > 0:
        closest_node = heapq.heappop(PQ)
        for adj_nodeID, link_cost, _ in Graph[closest_node.id][1:]:
            adj_node = next((n for n in PQ if n.id == adj_nodeID), None)
            if adj_node is not None and closest_node.cost + link_cost < adj_node.cost:
                adj_node.cost = closest_node.cost + link_cost
                adj_node.path = closest_node.path + adj_node.id
                heapq.heapify(PQ)
        print(f"I am Node {main_nodeID}" if closest_node.id ==
              main_nodeID else closest_node)


def detect_update(consider_updates_from, tick):
    if tick < 60:
        # changes under 60 seconds from node start will be ignored and not trigger routing algorithm
        return False
    if tick == 60:
        # execute routing algorithm regardless of any updates at 60 seconds after node start
        return True
    for node in Graph:
        for update_info in Graph[node]:
            if update_info[2] > consider_updates_from:
                return True
    return False


def calculate_upon_change():
    # only activate routing algorithm after 60 seconds of starting the node
    # and when change is detected in the network grpah
    consider_updates_from = start_time + 60
    tick = 0
    while True:
        if program_stopped:
            break
        if Graph[main_nodeID][0][1] == "down":
            time.sleep(.1)
            continue
        if detect_update(consider_updates_from, tick):
            find_shortest_route()
            consider_updates_from = time.time()
        tick += 1
        time.sleep(1)


t3 = threading.Thread(target=calculate_upon_change)
t3.start()


def green(text):
    return f"\033[32m{text}\033[0m"


print(f'''
( Node {main_nodeID} )
How to use CLI: 
  1. {green("exit")}: ends the program and clean up children threads
  2. {green("status")}: prints the node's current preception of Graph and other auxiiliary information
  3. {green("route")}: calculates shortest path to all other nodes in the graph (run command to route apart from automatic routing thread)
  4. {green("update-link <neighbour-node> <new-cost>")}: updates the link cost of edge connecting to neighbour node
  5. {green("mark-down")}: sets node {main_nodeID} as down (no broadcasting / listening)
  6. {green("mark-up")}: sets node {main_nodeID} as up again 
''')

# IDLE main thread that serves CLI role
while True:
    try:
        cmd = input("")
        if cmd == "exit":
            break
        elif cmd == "status":
            print("Time since boot: %.1fs" % (time.time() - start_time))
            for node in Graph:
                print(node, Graph[node])
        elif cmd == "route":
            find_shortest_route()
        elif cmd.startswith("update-link"):
            cmd, neighbour, new_cost = cmd.split(" ")
            add_or_update_edge(main_nodeID, neighbour, new_cost, time.time())
        elif cmd == "mark-down":
            update_node_failure(main_nodeID, "down", time.time())
        elif cmd == "mark-up":
            update_node_failure(main_nodeID, "up", time.time())
        else:
            print("Command not recognised")
    except KeyboardInterrupt:
        break
    except Exception as e:
        print("Error occured while parsing / executing the command")
        print(e)

program_stopped = True
print("Terminating Node in few seconds... (waiting for sleeping threads)")
t1.join()
t2.join()
t3.join()
