import network as net
import math
import random
import numpy as np
from copy import deepcopy


class RivalAnt:
    MIN_PHEROMONE_VALUE = 0.01
    """
Abstract class representing ant in ant colony optimization algorithm with
rivalizing ants.\n
    """
    def __init__(self, pheromones_weights: tuple[float],
                 pheromone_influence: float = 1.0,
                 criterion_influence: float = 1.0) -> None:
        self.pheromones_weights = pheromones_weights
        self.pheromone_influence = pheromone_influence
        self.criterion_influence = criterion_influence
        self.path = list[net.Link]()

    def calc_links_attractiveness(self) -> None:
        raise NotImplementedError('This is an instance of an abstract class \
that does and will not have this method implemented')

    def choose_link(self, links_data:
                    list[tuple[net.Link, float, list[float]]]) -> net.Link:
        links, results_min_distances_to_dest, pheromones_amounts = [], [], []
        for record in links_data:
            link, result_min_dist, pheromones_amount = record
            if len(self.path) > 0 and link == self.path[-1]:
                continue
            links.append(link)
            results_min_distances_to_dest.append(result_min_dist)
            pheromones_amounts.append(pheromones_amount)
        thresholds =\
            self.calc_links_attractiveness(links, pheromones_amounts,
                                           results_min_distances_to_dest)
        max_roll = sum(thresholds)
        roll = random.uniform(0, max_roll)
        walking_sum = 0
        for i in range(len(thresholds)):
            walking_sum += thresholds[i]
            if roll <= walking_sum:
                self.path.append(links[i])
                return links[i]


class RivalDistanceAnt(RivalAnt):
    def calc_links_attractiveness(self, links: list[net.Link],
                                  pheromones_amounts: list[tuple[float]],
                                  target_nodes_min_dest_dist: list[float])\
            -> list[float]:
        links_attractiveness = []
        for i in range(len(links)):
            link = links[i]
            link_pheromones = pheromones_amounts[i]
            distance_heuristic = target_nodes_min_dest_dist[i]
            pheromones_value = 0.0
            for j in range(len(self.pheromones_weights)):
                pheromones_value +=\
                    link_pheromones[j] * self.pheromones_weights[j]
            pheromones_value = max(self.MIN_PHEROMONE_VALUE, pheromones_value)
            pheromones_impact =\
                math.pow(pheromones_value, self.pheromone_influence)
            criterion_impact =\
                math.pow(1/(link.cost + distance_heuristic),
                         self.criterion_influence)
            links_attractiveness.append(pheromones_impact * criterion_impact)
        return links_attractiveness


class RivalCapacityAnt(RivalAnt):
    def __init__(self, pheromones_weights: tuple[float],
                 pheromone_influence: float = 1.0,
                 criterion_influence: float = 1.0) -> None:
        super().__init__(pheromones_weights, pheromone_influence,
                         criterion_influence)
        self.path_avg_length = 0
        self.path_avg_capacity = 0
        self.path_avg_load = 0
        self.path_edges_count = 0

    def choose_link(self, links_data:
                    list[tuple[net.Link, float, list[float]]]) -> net.Link:
        link = super().choose_link(links_data)
        self.path_avg_length =\
            (link.cost + self.path_avg_length * self.path_edges_count) / (self.path_edges_count + 1)
        self.path_avg_capacity =\
            (link.capacity + self.path_avg_capacity * self.path_edges_count) / (self.path_edges_count + 1)
        self.path_avg_load =\
            (link.load + self.path_avg_load * self.path_edges_count) / (self.path_edges_count + 1)
        return link

    def calc_links_attractiveness(self, links: list[net.Link],
                                  pheromones_amounts: list[tuple[float]],
                                  target_nodes_min_dest_dist: list[float])\
            -> list[float]:
        links_attractiveness = []
        for i in range(len(links)):
            link = links[i]
            link_pheromones = pheromones_amounts[i]
            distance_heuristic = target_nodes_min_dest_dist[i]
            pheromones_value = 0.0
            for j in range(len(self.pheromones_weights)):
                pheromones_value +=\
                    link_pheromones[j] * self.pheromones_weights[j]
            pheromones_value = max(self.MIN_PHEROMONE_VALUE, pheromones_value)
            pheromones_impact =\
                math.pow(pheromones_value, self.pheromone_influence)
            new_path_link_avg_length =\
                (link.cost + self.path_avg_length * self.path_edges_count) / (self.path_edges_count + 1)
            new_path_link_avg_capacity =\
                (link.capacity + self.path_avg_capacity * self.path_edges_count) / (self.path_edges_count + 1)
            new_path_link_avg_load =\
                (link.load + self.path_avg_load * self.path_edges_count) / (self.path_edges_count + 1)
            links_left_approximation = round(distance_heuristic/new_path_link_avg_length)
            free_capacity = (link.capacity - link.load)/link.capacity
            new_path_link_avg_free_capacity =\
                (new_path_link_avg_capacity - new_path_link_avg_load)/new_path_link_avg_capacity
            criterion_impact =\
                math.pow(free_capacity * math.pow(new_path_link_avg_free_capacity, links_left_approximation),
                         self.criterion_influence)
            links_attractiveness.append(pheromones_impact * criterion_impact)
        return links_attractiveness


class RivalAntsAlgorithmNetwork(net.Network):
    def __init__(self, nodes_ids: list[str],
                 links_data: list[tuple[str, str, str, float, float]],
                 ant_types_count: int,
                 pheromone_evaporation_coefficient: float = 0.5) -> None:
        super().__init__(nodes_ids, links_data)
        min_link_cost = min([link.cost for link in self.links])
        max_link_capacity = max([link.capacity for link in self.links])
        for i in range(len(self.links)):
            self.links[i].cost /= min_link_cost
            self.links[i].capacity /= max_link_capacity
            self.links[i].load = 0.01 * self.links[i].capacity
        self.pheromones_amounts =\
            np.ones((ant_types_count, len(self.links)))
        self.pheromone_evaporation_coefficient =\
            pheromone_evaporation_coefficient
        self.minimal_nodes_distances = np.asarray(self.nodes_min_distance())

    def rival_ants_algorithm(self, start_id: str, destination_id: str,
                             ants_originals: list[RivalAnt],
                             cost_func,
                             ants_per_generation: int = 10,
                             generations_number: int = 100)\
            -> tuple[list[net.Link, net.Link]]:
        """
`ants_per_generation` copies of each `RivalAnt` in `ants_originals`,
will be sent to explore graph and leave pheromone, in each of
`generation_number` generations.\n
After that one copy of each `RivalAnt` in `ants_originals`
will be sent and their paths will be returned.\n
All paths are returned in order corresponding to `RivalAnts`
in `ants_originals`.\n
`cost_func` needs to be a callable with arguments of types
`list[list[network.Link]]` - paths generated by ants; and `int` - number of all
links in network; calculating cost of each set of paths assuming that their
order in list argument corresponds to order of `RivalAnts` in `ants_originals`
        """
        self.reset_pheromones()
        start = self.get_node_by_id(start_id)
        destination = self.get_node_by_id(destination_id)
        self.explore(start, destination, ants_originals, cost_func,
                     ants_per_generation, generations_number)
        paths = self.get_paths(start, destination, ants_originals)
        return paths

    def get_node_by_id(self, id: str):
        try:
            return self.nodes[self.nodes_ids_map.index(id)]
        except ValueError as err:
            raise ValueError(f'there is no node with {id} id') from err

    def get_link_by_id(self, id: str):
        try:
            return self.links[self.links_ids_map.index(id)]
        except ValueError as err:
            raise ValueError(f'there is no link with {id} id') from err

    def reset_pheromones(self) -> None:
        self.pheromones_amounts = np.ones_like(self.pheromones_amounts)

    def explore(self, start: net.Node, destination: net.Node,
                ants_originals: list[RivalAnt], cost_func,
                ants_per_generation: int = 5,
                generations_number: int = 100) -> None:
        """
`ants_per_generation` copies of each `RivalAnt` in `ants_originals`,
will be sent to explore graph and leave pheromone, in each of
`generation_number` generations.
        """
        added_pheromones = np.zeros(self.pheromones_amounts.shape)
        for _ in range(generations_number):
            for _ in range(ants_per_generation):
                paths = []
                for ant in ants_originals:
                    new_ant = deepcopy(ant)
                    paths.append(self.send_ant(new_ant, start, destination))
                alloted_pheromones = self.allot_pheromones(paths, cost_func)
                np.add(added_pheromones, alloted_pheromones,
                       out=added_pheromones)
            np.add(self.pheromones_amounts, added_pheromones,
                   out=self.pheromones_amounts)

    def get_paths(self, start: net.Node, destination: net.Node,
                  ants_originals: list[RivalAnt]) -> list[list[str]]:
        """
One copy of each `RivalAnt` in `ants_originals` will be sent and their paths
will be returned.
        """
        paths = []
        for ant in ants_originals:
            new_ant = deepcopy(ant)
            path = self.send_ant(new_ant, start, destination)
            path = [self.links_ids_map[link.id] for link in path]
            paths.append(path)
        return paths

    def send_ant(self, ant: RivalAnt, start_node: net.Node,
                 destination_node: net.Node) -> list[net.Link]:
        current_node = start_node
        while current_node != destination_node:
            # links_data =\
            #   [(link available from current_node, min distance between node
            #     at the other end of this link and destination_node,
            #     pheromone amounts for all ant types on this link)]
            links_data = []
            for link_id in current_node.links:
                available_link = self.links[link_id]
                other_end_id = available_link.get_other_end(current_node.id)
                other_end_destination_min_distance =\
                    self.minimal_nodes_distances[destination_node.id][other_end_id]
                pheromones_amounts = self.pheromones_amounts[:, link_id]
                links_data.append((available_link,
                                   other_end_destination_min_distance,
                                   pheromones_amounts))
            link = ant.choose_link(links_data)
            current_node = self.nodes[link.get_other_end(current_node.id)]
        return ant.path

    def allot_pheromones(self, paths: list[list[net.Link]],
                         cost_func) -> list[list[float]]:
        alloted_pheromone = np.zeros_like(self.pheromones_amounts)
        cost = cost_func(paths, len(self.links))
        for i in range(len(paths)):
            for link in paths[i]:
                alloted_pheromone[i][link.id] = 1/cost
        return alloted_pheromone


def cost_func(paths: list[list[net.Link]], all_links_count: int,
              distance_weight: float = 5, capacity_weight: float = 5) -> float:
    present_in_paths = []
    for _ in range(all_links_count):
        present_in_paths.append([False] * len(paths))

    distance_path_cost = 0.0
    capacity_path_cost = 1
    for link in paths[0]:
        present_in_paths[link.id][0] = True
        distance_path_cost += link.cost
    for link in paths[1]:
        present_in_paths[link.id][1] = True
        capacity_path_cost *= (link.capacity - link.load)/link.capacity
    common_edges_count = present_in_paths.count([True, True])

    return (capacity_weight + distance_weight) * (common_edges_count + 1) -\
        (distance_weight / distance_path_cost) -\
        (capacity_weight * capacity_path_cost)



nodes_data, links_data = net.parse_xml('data/network_structure.xml')
test_network = RivalAntsAlgorithmNetwork(nodes_data, links_data, 2)
paths =\
    test_network.rival_ants_algorithm('Aachen', 'Passau',
                                      [(RivalDistanceAnt((1, -0.9), 1, 0.5)),
                                       (RivalCapacityAnt((-0.9, 1), 1, 3))],
                                      cost_func)
for i in range(len(test_network.pheromones_amounts[0])):
    print(f'{test_network.links_ids_map[i]}: {test_network.pheromones_amounts[0][i]}, {test_network.pheromones_amounts[1][i]}')

print(f'shortest distance path {len(paths[0])} edges: {paths[0]}')
print(f'lowest load path {len(paths[1])} edges: {paths[1]}')
print(f'common edges count {len(set(paths[0]) & set(paths[1]))}')
