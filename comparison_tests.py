from network import Network, parse_xml
from a_star import *
from os import path
import time
import random
from ant import *

ALG_A_STAR = 1
ALG_ANT_COLONY = 2
REPEAT = 100

# Test params, will be changed later for the next test
# A simple test to check correctness
# Optimal paths: Path: [S->c->d->K, S->a->b->K] or [2, 1, 2, 0, 2, 1, 1] edge-wise
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

def rate_solution_A_star(solution):
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
            result += WEIGHT_DIST + WEIGHT_COST
    
    result += WEIGHT_DIST + WEIGHT_COST
    result -= WEIGHT_DIST / dist_sum
    result -= WEIGHT_COST * cost_prod
    return result

def rate_solution_ant_colony(paths, network):
    link_paths = [[network.get_link_by_id(link_id) for link_id in paths[0]], [network.get_link_by_id(link_id) for link_id in paths[1]]]
    return cost_func(link_paths, len(network.links), WEIGHT_DIST, WEIGHT_COST)

def test(algorithm, start_node_id, end_node_id):
    solution = None
    score = 0
    time_prep = time.time()
    min_dist = None
    min_cost = None
    test_network = None

    if algorithm == ALG_A_STAR:
        min_dist = calculate_min_dist(network)
        min_cost = calculate_min_cost(network)

    if algorithm == ALG_ANT_COLONY:
        # Ant colony algorithm has its own network that needs conversion to
        test_network = RivalAntsAlgorithmNetwork(network.get_node_id_str_list(), network.get_link_data_list(), 2)

        for index, link in enumerate(test_network.links):
            if network.links[index].load == 0:
                link.load = 0.01
            else:
                link.load = network.links[index].load

    time_prep = time.time() - time_prep

    time_run = time.time()
    if algorithm == ALG_A_STAR:
        root = prepare_solution_tree(
            network, 
            network.nodes[start_node_id],
            network.nodes[end_node_id],
            min_cost, min_dist, WEIGHT_DIST, WEIGHT_COST
        )

        solution_node = a_star(root)
        
        time_run = time.time() - time_run

        #print(f"A* found {solution_node}")
        solution = solution_node.solution

        if not is_solution_valid(solution, start_node_id, end_node_id):
            print(f"Found an invalid solution: {solution}")
            return solution, float("-inf"), time_prep, time_run

        score = rate_solution_A_star(solution)

    elif algorithm == ALG_ANT_COLONY:

        paths = test_network.rival_ants_algorithm(
            network.nodes_ids_map[start_node_id], network.nodes_ids_map[end_node_id],
            [ (RivalDistanceAnt((1, -0.9), 1, 0.5)),
            (RivalCapacityAnt((-0.9, 1), 1, 3)) ],
            cost_func, generations_number=10
        )
        
        time_run = time.time() - time_run

        #for i in range(len(test_network.pheromones_amounts[0])):
        #    print(f'{test_network.links_ids_map[i]}: {test_network.pheromones_amounts[0][i]}, {test_network.pheromones_amounts[1][i]}')

        #print(f'shortest distance path {len(paths[0])} edges: {paths[0]}')
        #print(f'lowest load path {len(paths[1])} edges: {paths[1]}')
        #print(f'common edges count {len(set(paths[0]) & set(paths[1]))}')

        score = rate_solution_ant_colony(paths, test_network)
        solution = paths
#(paths: list[list[net.Link]], all_links_count: int,
#              distance_weight: float = 2, capacity_weight: float = 2) -> None:

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
        
        solution, score, time_prep, time_run = test(ALG_ANT_COLONY, start_id, end_id)
        score_sum[1] += score
        time_prep_sum[1] += time_prep
        time_run_sum[1] += time_run

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

def reset_network_load():
    for link in network.links:
        link.load = 0

def get_network_load():
    load = []
    for link in network.links:
        load.append(link.load)
    return load

def set_network_load(load_tab):
    for index, link in enumerate(network.links):
        link.load = load_tab[index]


def apply_load(solution, load):
    """
    Increases network load on links used in given solution.
    Limits added load to the lowest remaining capacity of paths used in solution
    Retruns how much load was added
    """
    # Check maximum possible load
    for edge, value in enumerate(solution):
        gap = network.links[edge].capacity - network.links[edge].load
        if value == 1 or value == 2:
            if load > gap:
                load = gap

        elif value == 3:
            if load > gap/2:
                load = gap/2

    # Apply the load to every node
    for edge, value in enumerate(solution):
        if value == 1 or value == 3:
            network.links[edge].load = min(network.links[edge].load + load, network.links[edge].capacity - 0.0001) # -0.0001 to prevent remaining space from reaching 0, which prevents calculating logarithms

        if value == 2 or value == 3:
            network.links[edge].load = min(network.links[edge].load + load, network.links[edge].capacity - 0.0001)
    
    return load

def get_network_to_fit(load):
    """
    Returns a sub-network consisting only of links that can bear given load (have enough capacity left)
    """
    node_list = network.get_node_id_str_list()
    link_list = network.get_link_data_list()

    removed = True
    while removed:
        removed = False
        for i in range(len(link_list)):
            link_id = network.links_ids_map.index(link_list[i][0])
            if network.links[link_id].capacity - network.links[link_id].load < load: # Link's capacity too low
                link_list.pop(i)
                print(f"Removed link: {link_list[i]}")
                removed = True
                break
    
    new_network = Network(node_list, link_list)
    for index, link in enumerate(new_network.links):
        link.load = network.links[network.links_ids_map.index(new_network.links_ids_map[index])].load
    
    return new_network

def test_cumulative_network_load(task_load_min, task_load_max):
    global network

    # Both algorithms receive same, randomized tasks
    task_list = []
    for i in range(REPEAT):
        start_id = random.randrange(len(network.nodes))
        end_id = random.randrange(len(network.nodes))
        if start_id == end_id:
            continue

        load = random.uniform(task_load_min, task_load_max)

        task_list.append((start_id, end_id, load))

    score_sum = [0, 0]
    time_prep_sum = [0, 0]
    time_run_sum = [0, 0]

    # Backup state, to load it before running second algorithm
    network_backup = network.get_network_copy()

    for task in task_list:
        start_id = task[0]
        end_id = task[1]
        load = task[2]
        #print(f"{network.nodes_ids_map[start_id]} {network.nodes_ids_map[end_id]}")

        #network = get_network_to_fit(load)

        solution, score, time_prep, time_run = test(ALG_A_STAR, start_id, end_id)

        apply_load(solution, load)

        score_sum[0] += score
        time_prep_sum[0] += time_prep
        time_run_sum[0] += time_run

    network = network_backup.get_network_copy()

    for task in task_list:
        start_id = task[0]
        end_id = task[1]
        load = task[2]
        #print(f"{network.nodes_ids_map[start_id]} {network.nodes_ids_map[end_id]}")

        solution, score, time_prep, time_run = test(ALG_ANT_COLONY, start_id, end_id)

        apply_load(solution, load)
        
        score_sum[1] += score
        time_prep_sum[1] += time_prep
        time_run_sum[1] += time_run

    score_avg = [score_sum[0]/REPEAT, score_sum[1]/REPEAT]
    time_prep_avg = [time_prep_sum[0]/REPEAT, time_prep_sum[1]/REPEAT]
    time_run_avg = [time_run_sum[0]/REPEAT, time_run_sum[1]/REPEAT]

    network = network_backup.get_network_copy()

    print(f"Algorithms: A*, Ant colony\n Score: {score_avg}, prep time: {time_prep_avg}, run time: {time_run_avg}")

# First case is so simple, that time differences hard to measure accurately
# It is run only to check correctness and score
solution, score, time_prep, time_run = test(ALG_A_STAR, network.nodes_ids_map.index("S"), network.nodes_ids_map.index("K"))
print(f"A* found solution: {solution}")
solution, score, time_prep, time_run = test(ALG_ANT_COLONY, network.nodes_ids_map.index("S"), network.nodes_ids_map.index("K"))
print(f"Ant colony found solution: {solution}")

# A simple test to check single path predictions in a completly free network (germany-50)
WEIGHT_COST = 1
WEIGHT_DIST = 1
nodes_ids, links_data = parse_xml(path.normpath(path.join('data', 'network_structure.xml')))
network = Network(nodes_ids, links_data)

print("Minimal load:")
randomize_network_load(network, 0.1, 0.2)
test_random_pair()

print("Average load:")
randomize_network_load(network, 0.4, 0.6)
test_random_pair()

print("Almost full:")
randomize_network_load(network, 0.8, 0.9)
test_random_pair()

# A more complicated test that accumulates load (but doesn't remove full links)
print("Cumulative load:")
randomize_network_load(network, 0.4, 0.6)
test_cumulative_network_load(1, 5)

# A test to show A* unacceptable computing times when forced to include a common link in a solution
for link_data in links_data:
    if link_data[0] == "L85":
        links_data.remove(link_data)
        break

network = Network(nodes_ids, links_data)

test(ALG_A_STAR, network.nodes_ids_map.index("Passau"), network.nodes_ids_map.index("Aachen"))
print("A* colony finished common edge test. Never actually going to happen")
