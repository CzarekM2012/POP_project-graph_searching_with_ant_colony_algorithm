from operator import ne
from network import Network, parse_xml
from os import link, path
import math
from queue import PriorityQueue, SimpleQueue
from tree_node import TreeNode
from heapq import *

INF_INT = 1000000000

WEIGHT_DIST = 1.0
WEIGHT_COST = 1.0

nodes_ids, links_data =\
    parse_xml(path.normpath(path.join('data', 'network_structure.xml')))

#print(nodes_ids)
#print(links_data)

network = Network(nodes_ids, links_data)

min_cost = []
min_dist = []
for i in range(len(network.nodes)):
    min_cost.append([float("inf")] * len(network.nodes))
    min_dist.append([INF_INT] * len(network.nodes))

for node in network.nodes:
    min_cost[node.id][node.id] = 0
    min_dist[node.id][node.id] = 0



#for link_id in network.nodes[network.nodes_ids_map.index("Berlin")].links:
#    if network.nodes_ids_map[network.links[link_id].ends[0]] == "Leipzig":
#        network.links[link_id].cost *= 10

for start_node in network.nodes:
    # BFS
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
    # Dijkstra
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

#print(min_dist)
#print(min_cost)

sum_dist = 0
sum_cost = 0
for i in range(len(network.nodes)):
    for j in range(len(network.nodes)):
        sum_dist += min_dist[i][j]
        sum_cost += min_cost[i][j]

#print(sum_dist)
#print(sum_cost)

avg_dist = sum_dist/len(network.nodes)
avg_cost = sum_cost/len(network.nodes)

#print(avg_dist)
#print(avg_cost)

scale_cost = avg_dist/avg_cost
print(f"Cost will be additionaly multiplied by {scale_cost}")


# A*

#start_node = network.nodes[network.nodes_ids_map.index("Berlin")]
#end_node = network.nodes[network.nodes_ids_map.index("Regensburg")]

start_node = network.nodes[network.nodes_ids_map.index("Norden")]
end_node = network.nodes[network.nodes_ids_map.index("Passau")]

TreeNode.network = network
TreeNode.start_node = start_node
TreeNode.end_node = end_node
TreeNode.min_dist = min_dist
TreeNode.min_cost = min_cost
TreeNode.scale_cost = scale_cost
root = TreeNode([0] * len(network.links), None, start_node, 1)

# Using heapq, which should be much faster than standard PriorityQueue implementation
q = [(0, root)]
visited_count = 0
#q = PriorityQueue()
#q.put(root)
end = False
while not end and not len(q) < 1:
    visited_count += 1
    score, tree_node = heappop(q)
    #print(network.nodes_ids_map[tree_node.head.id])
    print(tree_node)
    print(f"Current score: {tree_node.get_score()}, \nsolution: {tree_node.solution}")

    if tree_node.phase == 3:
        print(f"Found: {tree_node}")
        end = True

    tree_node.create_children_nodes()

    for child in tree_node.children:
        #print(child.solution)
        heappush(q, (child.get_score(), child))

print(f"Visited {visited_count} solutions")
#print(min_cost[network.nodes_ids_map.index("Bayreuth")][network.nodes_ids_map.index("Berlin")])


