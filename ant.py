import load_network as ln
from os import path
import math
import random

# TODO: Adding weight vector to RivalAnts controling impact of specific pheromones on probability of choosing a link
# TODO: Rescaling of criterion in both RivalAnts variants in the way that will make values of pheromone and criterion influences comparable


class RivalAntsAlgorithmNetwork(ln.Network):
    def __init__(self, nodes_ids: list[str],
                 links_data: list[tuple[str, str, str, float, float]],
                 ant_species_amount: int = 2) -> None:
        super().__init__(nodes_ids, links_data)
        self.pheromone_amounts =\
            [tuple([0.0] * ant_species_amount)] * len(self.nodes)


class Ant:
    """
Abstract class representing ant in ant colony optimization algorithm.\n
    """
    def __init__(self, network: RivalAntsAlgorithmNetwork,
                 pheromone_weight: float = 1.0, criterion_weight: float = 1.0,
                 pheromone_amount: float = 1.0) -> None:
        self.network = network
        self.pheromone_weight = pheromone_weight
        self.criterion_weight = criterion_weight
        self.pheromone_amount = pheromone_amount
        self.path = list[ln.Link]()

    def calc_links_attractiveness(self, node: ln.Node) -> list[float]:
        pass

    def choose_link(self, node: ln.Node) -> ln.Link:
        thresholds = self.calc_links_attractiveness(node)
        max_roll = sum(thresholds)
        roll = random.uniform(0, max_roll)
        walking_sum = 0
        for i in range(len(thresholds)):
            walking_sum += thresholds[i]
            if roll <= walking_sum:
                return node.links[i]

    def travel(self, start: int, destination: int) -> None:
        current = start
        while current != destination:
            link = self.choose_link(current)
            current = link.get_other_end(current)
            self.path.append(link)

    def allot_pheromone(self) -> list[tuple[str, float]]:
        return [(link.id, self.pheromone_amount/len(path))
                for link in self.path]


class RivalDistanceAnt(Ant):
    def __init__(self, network: RivalAntsAlgorithmNetwork,
                 pheromone_weight: float, criterion_weight: float,
                 pheromone_amount: float = 1.0) -> None:
        super().__init__(network, pheromone_weight,
                         criterion_weight, pheromone_amount)

    def calc_links_attractiveness(self, node: ln.Node) -> ln.Link:
        return [math.pow(self.network.pheromone_amounts[link.id],
                         self.pheromone_weight) *
                math.pow(1/link.cost,
                         self.criterion_weight)
                for link in node.links]


class RivalCapacityAnt(Ant):
    def __init__(self, network: RivalAntsAlgorithmNetwork,
                 pheromone_weight: float, criterion_weight: float,
                 pheromone_amount: float = 1.0) -> None:
        super().__init__(network, pheromone_weight,
                         criterion_weight, pheromone_amount)

    def calc_links_attractiveness(self, node: ln.Node) -> list[float]:
        return [math.pow(self.network.pheromone_amounts[link.id],
                         self.pheromone_weight) *
                math.pow(link.capacity,
                         self.criterion_weight)
                for link in node.links]


def rival_ants_algorithm(network: ln.Network,
                         start_id: str, destination_id: str,
                         ants_per_generation: int = 10,
                         generations_number: int = 100)\
                         -> tuple[list[ln.Link, ln.Link]]:
    pass


nodes_ids, links_data =\
    ln.parse_xml(path.normpath(path.join('data', 'network_structure.xml')))
network = RivalAntsAlgorithmNetwork(nodes_ids, links_data)
