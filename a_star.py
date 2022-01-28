from network import Network, parse_xml
from os import path
import math
from queue import PriorityQueue, SimpleQueue
from tree_node import TreeNode
from heapq import *

INF_INT = 1000000000

def calculate_min_dist(network):
    min_dist = []
    for i in range(len(network.nodes)):
        min_dist.append([INF_INT] * len(network.nodes))

    for node in network.nodes:
        min_dist[node.id][node.id] = 0

    # BFS for each node
    for start_node in network.nodes:
        q = SimpleQueue()
        q.put(start_node)
        while not q.empty():
            node = q.get()
    
            for link_id in node.links:
                link = network.links[link_id]
                new_dist = min_dist[start_node.id][node.id] + 1

                for end in link.ends:
                    if min_dist[start_node.id][end] > new_dist:
                        q.put(network.nodes[end])
                        min_dist[start_node.id][end] = new_dist
    
    return min_dist


def calculate_min_cost(network):
    min_cost = []
    for i in range(len(network.nodes)):
        min_cost.append([float("inf")] * len(network.nodes))
        
    for node in network.nodes:
        min_cost[node.id][node.id] = 0
    
    # Dijkstra for each node
    for start_node in network.nodes:
        
        for node in network.nodes:
            node.comp = float("inf")
        start_node.comp = 0

        q = PriorityQueue()
        q.put(start_node)
        while not q.empty():
            node = q.get()

            for link_id in node.links:
                link = network.links[link_id]
                new_cost = min_cost[start_node.id][node.id] + link.get_a_star_cost()

                for end in link.ends:
                    if min_cost[start_node.id][end] > new_cost:
                        network.nodes[end].comp = new_cost
                        q.put(network.nodes[end])
                        min_cost[start_node.id][end] = new_cost

    return min_cost

#for link_id in network.nodes[network.nodes_ids_map.index("Berlin")].links:
#    if network.nodes_ids_map[network.links[link_id].ends[0]] == "Leipzig":
#        network.links[link_id].cost *= 10
def get_scale(cost_tab, dist_tab):
    sum_dist = 0
    sum_cost = 0
    for i in range(len(cost_tab)):
        for j in range(len(cost_tab[0])):
            sum_dist += dist_tab[i][j]
            sum_cost += cost_tab[i][j]

    avg_dist = sum_dist/len(cost_tab)
    avg_cost = sum_cost/len(cost_tab)
    return avg_dist/avg_cost


def prepare_solution_tree(network, start_node, end_node, min_cost_tab, min_dist_tab, weight_common, weight_length, weight_cost):

    #start_node = network.nodes[network.nodes_ids_map.index("Norden")]
    #end_node = network.nodes[network.nodes_ids_map.index("Passau")]

    # Every node could have had a separate copy of those params, but it would be highly inefficient
    TreeNode.network = network
    TreeNode.start_node = start_node
    TreeNode.end_node = end_node
    
    TreeNode.min_cost = min_cost_tab
    TreeNode.min_dist = min_dist_tab

    TreeNode.weight_common = weight_common
    TreeNode.weight_length = weight_length
    TreeNode.weight_cost = weight_cost
    return TreeNode([0] * len(network.links), None, start_node, 1)


# A*
def a_star(root):
    # Using heapq, which should be much faster than standard PriorityQueue implementation
    q = [(0, root)]
    visited_count = 0
    #q = PriorityQueue()
    #q.put(root)
    end = False
    while not end and not len(q) < 1:
        visited_count += 1
        score, tree_node = heappop(q)
        #print(tree_node)
        #print(f"Current score: {tree_node.get_score()} = {tree_node.get_goal_function()} + {tree_node.get_heuristic()}")

        if tree_node.phase == 3:
            #print(f"Visited {visited_count} solutions")
            return tree_node

        tree_node.create_children_nodes()

        for child in tree_node.children:
            #print(child.solution)
            heappush(q, (child.get_score(), child))
    
    return None


# Usage example
if __name__ == "__main__":
    nodes_ids, links_data =\
        parse_xml(path.normpath(path.join('data', 'network_structure.xml')))

    network = Network(nodes_ids, links_data)

    for link_id in range(len(network.links)):
        network.links[link_id].load = network.links[link_id].capacity/2
    
    print(nodes_ids)
    print(links_data)
    
    min_cost = calculate_min_cost(network)
    min_dist = calculate_min_dist(network)
    
    print(min_cost)

    root = prepare_solution_tree(
        network, 
        network.nodes[network.nodes_ids_map.index("Norden")],
        network.nodes[network.nodes_ids_map.index("Passau")],
        min_cost, min_dist,
        1000000000, 1, 1
    )
    print(f"Found: {a_star(root)}")
