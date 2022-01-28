from network import Network, parse_xml
from a_star import *
from os import path
import time
import random

ALG_A_STAR = 1
ALG_ANT_COLONY = 2
REPEAT = 1000

# Test params, will be changed later for the next test
# A simple test to check correctness
# Optimal paths: Path: [S->c->d->K, S->a->b->K] or [2, 1, 2, 0, 2, 1, 1] edge-wise
WEIGHT_COMMON = 1000000000
WEIGHT_COST = 1
WEIGHT_DIST = 1
nodes_ids = ['S', 'K', 'a', 'b', 'c', 'd']
links_data = [ # Load will be set to 0 everywhere, except specified nodes: 
    ('L1', 'S', 'a', 1, 1),
    ('L2', 'S', 'c', 1, 1),
    ('L3', 'a', 'b', 1, 1), # Load = 0.1
    ('L4', 'a', 'K', 1, 1), # Load = 0.5
    ('L5', 'b', 'K', 1, 1), # Load = 0.1
    ('L6', 'c', 'd', 1, 1), # Load = 0.9
    ('L7', 'd', 'K', 1, 1)
]
network = Network(nodes_ids, links_data)
network.links[2].load = 0.1
network.links[3].load = 0.5
network.links[4].load = 0.1
network.links[5].load = 0.9

def is_solution_valid(solution, start_node_id, end_node_id):
    """
    Returns True if given solution is valid in set network, False otherwise.
    Is a bit too strict; Considers solutions with cycles (in a sigle path) invalid,
    as they are always worse and should not be output by any of the algorithms
    """
    visited = [[], [], []] # Separate for both phases, first one is for padding
    visited_edges = [[], [], []]

    start_node = network.nodes[start_node_id]
    end_node = network.nodes[end_node_id]
    head = start_node
    last_link_id = -1

    phase = 1
    added = True
    while added and phase < 3:
        added = False
        for link_id in head.links:
            if link_id == last_link_id:
                continue
            value = solution[link_id]
            #print(solution)
            #print(network.nodes_ids_map[head.id])
            #print(network.links[link_id])
            #print(value)
            if value != phase and value != 3:
                continue

            
            link = network.links[link_id]
            other_end_id = link.get_other_end(head.id)
            
            if other_end_id in visited[phase]: # A cycle
                return False 
            
            head = network.nodes[other_end_id]
            last_link_id = link_id
            visited[phase].append(other_end_id)
            visited_edges[phase].append(link_id)
            added = True

            if phase == 1 and other_end_id == end_node.id:
                phase = 2
                visited[phase].append(other_end_id) # Add the first one
                last_link_id = -1                   # To allow backing out if last link was a 3
            if phase == 2 and other_end_id == start_node.id:
                # Check if all links were used
                for edge, v in enumerate(solution):
                    if v == 1 and edge not in visited_edges[1]:
                        return False
                    if v == 2 and edge not in visited_edges[2]:
                        return False
                    if v == 3 and (edge not in visited_edges[1] or edge not in visited_edges[2]):
                        return False
                return True
            break # Break the for loop, which would otherwise iterate over other links from last head
    return False

def rate_solution(solution):
    """
    Returns a score for the solution in given network according to global weights 
    """
    result = 0
    dist_sum = 0
    cost_prod = 1
    for edge, value in enumerate(solution):
        if value == 1 or value == 3:
            dist_sum += 1
        if value == 2 or value == 3:
            capacity = network.links[edge].capacity
            load = network.links[edge].load
            cost_prod *= (capacity - load) / capacity
        
        if value == 3:
            result += WEIGHT_COMMON
    result -= WEIGHT_DIST / dist_sum
    result -= WEIGHT_COST * cost_prod
    return result

def test(algorithm, start_node_id, end_node_id):
    solution = None
    time_prep = time.time()
    min_cost = calculate_min_cost(network)
    min_dist = calculate_min_dist(network)

    time_prep = time.time() - time_prep

    time_run = time.time()
    if algorithm == ALG_A_STAR:
        root = prepare_solution_tree(
            network, 
            network.nodes[start_node_id],
            network.nodes[end_node_id],
            min_cost, min_dist,
            WEIGHT_COMMON, WEIGHT_DIST, WEIGHT_COST
        )

        solution_node = a_star(root)
        #print(f"A* found {solution_node}")
        solution = solution_node.solution
    
    elif algorithm == ALG_ANT_COLONY:
        solution = [0] * len(network.links)

    time_run = time.time() - time_run
    
    if not is_solution_valid(solution, start_node_id, end_node_id):
        print(f"Found an invalid solution: {solution}")
        return solution, float("-inf"), time_prep, time_run


    score = rate_solution(solution)
    return solution, score, time_prep, time_run


def test_random_pair():
    # Both algorithms receive same, randomized tasks
    score_sum = [0, 0]
    time_prep_sum = [0, 0]
    time_run_sum = [0, 0]
    for i in range(REPEAT):
        start_id = random.randrange(len(network.nodes))
        end_id = random.randrange(len(network.nodes))
        if start_id == end_id:
            continue

        #print(f"{network.nodes_ids_map[start_id]} {network.nodes_ids_map[end_id]}")

        solution, score, time_prep, time_run = test(ALG_A_STAR, start_id, end_id)
        score_sum[0] += score
        time_prep_sum[0] += time_prep
        time_run_sum[0] += time_run
        #solution, score, time_prep, time_run = test(ALG_ANT_COLONY, start_id, end_id)
        #score_sum[1] += score
        #time_prep_sum[1] += time_prep
        #time_run_sum[1] += time_run

    score_avg = [score_sum[0]/REPEAT, score_sum[1]/REPEAT]
    time_prep_avg = [time_prep_sum[0]/REPEAT, time_prep_sum[1]/REPEAT]
    time_run_avg = [time_run_sum[0]/REPEAT, time_run_sum[1]/REPEAT] 

    print(f"Algorithms: A*, Ant colony\n Score: {score_avg}, prep time: {time_prep_avg}, run time: {time_run_avg}")

def randomize_network_load(network, capacity_min, capacity_max):
    """
    Randomizes load on links uniformly between given values (fraction of link's capacity)
    """
    for link in network.links:
        link.load = random.uniform(capacity_min, capacity_max * link.capacity)


# First case is so simple, that time differences hard to measure accurately
# It is run only to check correctness and score
solution, score, time_prep, time_run = test(ALG_A_STAR, network.nodes_ids_map.index("S"), network.nodes_ids_map.index("K"))
print(f"A* found solution: {solution}")
solution, score, time_prep, time_run = test(ALG_ANT_COLONY, network.nodes_ids_map.index("S"), network.nodes_ids_map.index("K"))
print(f"Ant colony found solution: {solution}")

# A simple test to check single path predictions in a completly free network (germany-50)
WEIGHT_COMMON = 1000000000
WEIGHT_COST = 1
WEIGHT_DIST = 1
nodes_ids, links_data = parse_xml(path.normpath(path.join('data', 'network_structure.xml')))
network = Network(nodes_ids, links_data)

#test_random_pair()


# A simple test to check single path predictions in a randomly filled network (germany-50)

randomize_network_load(network, 0.4, 0.6)
test_random_pair()
#test_cumulative_network_load()

