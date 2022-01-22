import network as net
from os import name, path
import math
import random
import numpy
import timeit

# TODO: Adding weight vector to RivalAnts controling impact of specific pheromones on probability of choosing a link
# TODO: Rescaling of criterion in both RivalAnts variants in the way that will make values of pheromone and criterion influences comparable


class RivalAnt:
    """
Abstract class representing ant in ant colony optimization algorithm with rivalizing ants.\n
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
        pass

    def choose_link(self, links: list[net.Link],
                    pheromones_amounts: list[float])\
            -> net.Link:
        thresholds = self.calc_links_attractiveness(links, pheromones_amounts)
        max_roll = sum(thresholds)
        roll = random.uniform(0, max_roll)
        walking_sum = 0
        for i in range(len(thresholds)):
            walking_sum += thresholds[i]
            if roll <= walking_sum:
                self.path.append(links[i])
                return links[i]

    def allot_pheromone(self) -> list[tuple[net.Link, float]]:
        return [(link, self.pheromone_amount/len(path))
                for link in self.path]


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
            links_attractiveness.append(math.pow(pheromones_value,
                                                 self.pheromone_influence) *
                                        math.pow(1/link.cost,
                                                 self.criterion_influence))
        return links_attractiveness


class RivalCapacityAnt(RivalAnt):

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
            links_attractiveness.append(math.pow(pheromones_value,
                                                 self.pheromone_influence) *
                                        math.pow(link.capacity,
                                                 self.criterion_influence))
        return links_attractiveness


class RivalAntsAlgorithmNetwork(net.Network):
    def __init__(self, nodes_ids: list[str],
                 links_data: list[tuple[str, str, str, float, float]],
                 ant_types_count: int,
                 pheromone_evaporation_coefficient: float = 0.1) -> None:
        super().__init__(nodes_ids, links_data)
        self.pheromones_amounts =\
            tuple([tuple([0.0] * ant_types_count)] * len(self.links))
        self.pheromone_evaporation_coefficient =\
            pheromone_evaporation_coefficient

    def rival_ants_algorithm(self, start_id: str, destination_id: str,
                             ants_types_data: list[tuple[type[RivalAnt],
                                                         list[float]]],
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
        for type, weights in ants_types_data:
            if len(weights) != self. len(ants_types_data):
                raise ValueError(f'weights list associated with {type} has wrong \
length')
        start = self.nodes[self.nodes_ids_map.index(start_id)]
        destination = self.nodes[self.nodes_ids_map.index(destination_id)]
        pheromones_change =\
            tuple([tuple([0.0] * len(self.pheromones_amounts[0]))] *
                  len(self.pheromones_amounts))
        for _ in range(generations_number):
            for i in range(len(ants_types_data)):
                ant_type, weights = ants_types_data[i]
                for _ in range(ants_per_generation):
                    ant = ant_type(pheromones_weights=weights)
                    current = start
                    while current != destination:
                        link = ant.choose_link([self.links[link_id]
                                               for link_id in current.links],
                                               self.pheromones_amounts)
                        current = link.get_other_end(current.id)
                    ant_pheromone_spread = ant.allot_pheromone()
                    for link, pheromone_amount in ant_pheromone_spread:
                        pheromones_change[link.id][i] += pheromone_amount
            for i in range(len(pheromones_change)):
                for j in range(len(pheromones_change[0])):
                    self.pheromones_amounts[i][j] =\
                        self.pheromones_amounts[i][j] *\
                        (1-self.pheromone_evaporation_coefficient) +\
                        pheromones_change[i][j]
