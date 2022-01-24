import network as net
import math
import random
import numpy as np

# TODO: Rescaling of criterion in both RivalAnts variants in the way that will make values of pheromone and criterion influences comparable


class RivalAnt:
    MIN_PHEROMONE_VALUE = 0.00000001
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
                 start_path_min_capacity: int = 1000000) -> None:
        super().__init__(pheromones_weights)
        self.path_min_capacity = start_path_min_capacity

    def choose_link(self, links_data:
                    list[tuple[net.Link, float, list[float]]]) -> net.Link:
        link = super().choose_link(links_data)
        self.path_min_capacity = min(self.path_min_capacity, link.capacity)
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
            criterion_impact =\
                math.pow(link.capacity + 0.01/(link.cost + distance_heuristic),
                         self.criterion_influence)
            links_attractiveness.append(pheromones_impact * criterion_impact)
        return links_attractiveness


class RivalAntsAlgorithmNetwork(net.Network):
    def __init__(self, nodes_ids: list[str],
                 links_data: list[tuple[str, str, str, float, float]],
                 ant_types_count: int,
                 pheromone_evaporation_coefficient: float = 0.6) -> None:
        super().__init__(nodes_ids, links_data)
        min_link_cost = min([link.cost for link in self.links])
        for i in range(len(self.links)):
            self.links[i].cost /= min_link_cost
        self.pheromones_amounts =\
            np.zeros((ant_types_count, len(self.links)))
        self.pheromone_evaporation_coefficient =\
            pheromone_evaporation_coefficient
        self.minimal_nodes_distances = np.asarray(self.nodes_min_distance())

    def rival_ants_algorithm(self, start_id: str, destination_id: str,
                             ants_types_data: list[tuple[type[RivalAnt],
                                                         tuple[float]]],
                             ants_per_generation: int = 10,
                             generations_number: int = 100)\
            -> tuple[list[net.Link, net.Link]]:
        """
tuples in `ants_types_data` should consist of subclass of Ant class
implementing calc_links_attractiveness() and list with length equal to
`ants_types_data` consisting of weights of pheromones of specific ant types
for decision-making process of associated ant type, for example:\n
`ants_types_data` = [(RivalDistanceAnt, [1, -1]), (RivalCapacityAnt, [-1, 1])]
        """
        for ant_type_data in ants_types_data:
            if len(ant_type_data[1]) != len(ants_types_data):
                raise ValueError(f'weights list associated with {type} has wrong \
length')
        start = self.nodes[self.nodes_ids_map.index(start_id)]
        destination = self.nodes[self.nodes_ids_map.index(destination_id)]
        added_pheromones = np.zeros(self.pheromones_amounts.shape)
        for _ in range(generations_number):
            for _ in range(ants_per_generation):
                paths = []
                for i in range(len(ants_types_data)):
                    ant_type, weights = ants_types_data[i]
                    ant = ant_type(pheromones_weights=weights)
                    paths.append(self.send_ant(ant, start, destination))
                alloted_pheromones = self.allot_pheromones(paths)
                for i in range(len(alloted_pheromones)):
                    for j in range(len(alloted_pheromones[i])):
                        added_pheromones[i][j] += alloted_pheromones[i][j]
            self.update_pheromones(added_pheromones)

    def send_ant(self, ant: RivalAnt, start_node: net.Node,
                 destination_node: net.Node) -> list[tuple[net.Link, float]]:
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
                pheromones_amounts =\
                    [self.pheromones_amounts[i][link_id] for i
                     in range(len(self.pheromones_amounts))]
                links_data.append((available_link,
                                   other_end_destination_min_distance,
                                   pheromones_amounts))
            link = ant.choose_link(links_data)
            current_node = self.nodes[link.get_other_end(current_node.id)]
        return ant.path

    def allot_pheromones(self, paths: list[list[net.Link]])\
            -> list[list[float]]:
        alloted_pheromone = []
        for _ in range(self.pheromones_amounts.shape[0]):
            alloted_pheromone.append([0.0] * self.pheromones_amounts.shape[1])

        DISTANCE_WEIGHT = 1
        CAPACITY_WEIGHT = 1
        present_in_paths = []
        for _ in range(len(self.links)):
            present_in_paths.append([False] * len(paths))

        distance_path_cost = 0.0
        capacity_path_cost = 1
        for link in paths[0]:
            present_in_paths[link.id][0] = True
            distance_path_cost += link.cost
        for link in paths[1]:
            present_in_paths[link.id][1] = True
            capacity_path_cost *= 1
        common_edges_count = present_in_paths.count([True, True])

        #cost = (CAPACITY_WEIGHT + DISTANCE_WEIGHT) * (common_edges_count + 1) -\
        #    DISTANCE_WEIGHT/distance_path_cost -\
        #    CAPACITY_WEIGHT/capacity_path_cost

        cost = distance_path_cost

        print(distance_path_cost)

        for i in range(len(present_in_paths)):
            for j in range(len(paths)):
                if present_in_paths[i][j]:
                    alloted_pheromone[j][i] = 1/cost

        return alloted_pheromone

    def update_pheromones(self, added_pheromones: np.ndarray) -> None:
        for i in range(added_pheromones.shape[0]):
            for j in range(added_pheromones.shape[1]):
                self.pheromones_amounts[i][j] =\
                    self.pheromones_amounts[i][j] *\
                    (1-self.pheromone_evaporation_coefficient) +\
                    added_pheromones[i][j]


nodes_data, links_data = net.parse_xml('data/network_structure.xml')
test_network = RivalAntsAlgorithmNetwork(nodes_data, links_data, 2)
paths = test_network.rival_ants_algorithm('Aachen', 'Passau',
                                          [(RivalDistanceAnt, (1, 0)),
                                           (RivalCapacityAnt, (0, 1))])
print('')
