from operator import ne
from network import Network, parse_xml
from os import link, path
import math
from queue import PriorityQueue, SimpleQueue

INF_INT = 1000000000

def get_link_cost(link):
    return 1/link.capacity
    #return link.cost

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
            new_cost = min_cost[start_node.id][node.id] + get_link_cost(link)

            for end in link.ends:
                if min_cost[start_node.id][end] > new_cost:
                    network.nodes[end].comp = new_cost
                    q.put(network.nodes[end])
                    min_cost[start_node.id][end] = new_cost

#print(min_dist)
#print(min_cost)

#print(min_cost[network.nodes_ids_map.index("Bayreuth")][network.nodes_ids_map.index("Berlin")])




