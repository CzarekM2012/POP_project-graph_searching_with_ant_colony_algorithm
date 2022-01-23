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
                 criterion_influence: float = 1.0,
                 pheromone_amount: float = 1.0) -> None:
        self.pheromones_weights = pheromones_weights
        self.pheromone_influence = pheromone_influence
        self.criterion_influence = criterion_influence
        self.pheromone_amount = pheromone_amount
        self.path = list[net.Link]()

    def calc_links_attractiveness(self) -> None:
        raise NotImplementedError('This is an instance of an abstract class \
that does and will not have this method implemented')

    def choose_link(self, links: list[net.Link],
                    pheromones_amounts: list[float])\
            -> net.Link:
        if len(self.path) > 0:
            back_index = links.index(self.path[-1])
            links.pop(back_index)
            pheromones_amounts.pop(back_index)
        thresholds = self.calc_links_attractiveness(links, pheromones_amounts)
        max_roll = sum(thresholds)
        roll = random.uniform(0, max_roll)
        walking_sum = 0
        for i in range(len(thresholds)):
            walking_sum += thresholds[i]
            if roll <= walking_sum:
                self.path.append(links[i])
                return links[i]

    def allot_pheromone(self) -> None:
        raise NotImplementedError('This is an instance of an abstract class \
that does and will not have this method implemented')


class RivalDistanceAnt(RivalAnt):

    def calc_links_attractiveness(self, links: list[net.Link],
                                  pheromones_amounts: list[tuple[float]])\
            -> list[float]:
        links_attractiveness = []
        for i in range(len(links)):
            link = links[i]
            link_pheromones = pheromones_amounts[i]
            pheromones_value = 0.0
            for j in range(len(self.pheromones_weights)):
                pheromones_value +=\
                    link_pheromones[j] * self.pheromones_weights[j]
            pheromones_value = max(self.MIN_PHEROMONE_VALUE, pheromones_value)
            links_attractiveness.append(math.pow(pheromones_value,
                                                 self.pheromone_influence) *
                                        math.pow(1/link.cost,
                                                 self.criterion_influence))
        return links_attractiveness

    def allot_pheromone(self) -> list[tuple[net.Link, float]]:
        sum_distance = sum([link.cost for link in self.path])
        return [(link, self.pheromone_amount/sum_distance)
                for link in self.path]


class RivalCapacityAnt(RivalAnt):

    def __init__(self, pheromones_weights: tuple[float],
                 start_path_min_capacity: int = 1000000) -> None:
        super().__init__(pheromones_weights)
        self.path_min_capacity = start_path_min_capacity

    def choose_link(self, links: list[net.Link],
                    pheromones_amounts: list[float]) -> net.Link:
        link = super().choose_link(links, pheromones_amounts)
        self.path_min_capacity = min(self.path_min_capacity, link.capacity)
        return link

    def calc_links_attractiveness(self, links: list[net.Link],
                                  pheromones_amounts: list[tuple[float]])\
            -> list[float]:
        links_attractiveness = []
        for i in range(len(links)):
            link = links[i]
            link_pheromones = pheromones_amounts[i]
            pheromones_value = 0.0
            for j in range(len(self.pheromones_weights)):
                pheromones_value +=\
                    link_pheromones[j] * self.pheromones_weights[j]
            pheromones_value = max(self.MIN_PHEROMONE_VALUE, pheromones_value)
            links_attractiveness.append(math.pow(pheromones_value,
                                                 self.pheromone_influence) *
                                        math.pow(link.capacity,
                                                 self.criterion_influence))
        return links_attractiveness

    def allot_pheromone(self) -> list[tuple[net.Link, float]]:
        return [(link, self.pheromone_amount * self.path_min_capacity)
                for link in self.path]


class RivalAntsAlgorithmNetwork(net.Network):
    def __init__(self, nodes_ids: list[str],
                 links_data: list[tuple[str, str, str, float, float]],
                 ant_types_count: int,
                 pheromone_evaporation_coefficient: float = 0.6) -> None:
        super().__init__(nodes_ids, links_data)
        self.pheromones_amounts =\
            np.zeros((ant_types_count, len(self.links)))
        self.pheromone_evaporation_coefficient =\
            pheromone_evaporation_coefficient
        self.max_distance = max([link.cost for link in self.links]) # try normalizing values for ants heuristics
        self.min_distance = min([link.cost for link in self.links])
        self.max_capacity = max([link.capacity for link in self.links])

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
            for i in range(len(ants_types_data)):
                ant_type, weights = ants_types_data[i]
                for _ in range(ants_per_generation):
                    ant = ant_type(pheromones_weights=weights)
                    ant_pheromone_spread =\
                        self.send_ant(ant, start, destination)
                    for link, pheromone_amount in ant_pheromone_spread:
                        added_pheromones[i][link.id] += pheromone_amount
                print(f'{ant_type.__name__}, {len(ant_pheromone_spread)}')
            self.update_pheromones(added_pheromones)

    def send_ant(self, ant: RivalAnt, start_node: net.Node,
                 destination_node: net.Node) -> list[tuple[net.Link, float]]:
        current_node = start_node
        while current_node != destination_node:
            available_links =\
                [self.links[link_id] for link_id in current_node.links]
            available_links_pheromones = []
            for link_id in current_node.links:
                available_links_pheromones.append(
                    [self.pheromones_amounts[i][link_id] for i
                     in range(len(self.pheromones_amounts))])
            link = ant.choose_link(available_links, available_links_pheromones)
            current_node = self.nodes[link.get_other_end(current_node.id)]
        ant_pheromone_spread = ant.allot_pheromone()
        return ant_pheromone_spread

    def update_pheromones(self, added_pheromones: np.ndarray) -> None:
        for i in range(added_pheromones.shape[0]):
            normalization_divider = added_pheromones[i].max()
            for j in range(added_pheromones.shape[1]):
                self.pheromones_amounts[i][j] =\
                    self.pheromones_amounts[i][j] *\
                    (1-self.pheromone_evaporation_coefficient) +\
                    added_pheromones[i][j] / normalization_divider


nodes_data, links_data = net.parse_xml('data/network_structure.xml')
test_network = RivalAntsAlgorithmNetwork(nodes_data, links_data, 2)
paths = test_network.rival_ants_algorithm('Aachen', 'Passau',
                                          [(RivalDistanceAnt, (1, 0)),
                                           (RivalCapacityAnt, (0, 1))])
print('')
