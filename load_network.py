from xml.etree import ElementTree as ET
from os import path


class Node:
    """
Node of a network.\n
Contains `id` and a dict `links` indexed by ids of neighbour nodes,
consisting of tuples in the form of (capacity_of_link, cost_of_link)
    """
    def __init__(self, id) -> None:
        self.id = id
        self.links = {}

    def add_neighbour(self, neighbour_id, link_capacity, link_cost) -> None:
        self.links[neighbour_id] = (link_capacity, link_cost)


class Link:
    """
Link between nodes of a network.\n
Consists of tuple `ends` containing references to both ends of the link,
`capacity` and `cost`
    """
    def __init__(self, end1: Node, end2: Node, capacity: float, cost: float)\
            -> None:
        self.ends = (end1, end2)
        self.capacity = capacity
        self.cost = cost


class Network:
    """
Network of nodes connected by symmetrical links\n
Consists of a `nodes` dict containing all nodes of the network, indexed with
their ids and `links` list containing all links in the network.\n
Uniqueness of nodes is maintained based on their ids, links - nodes on their
ends.
    """
    def __init__(self, nodes_ids: list[str],
                 links_data: list[tuple[str, str, float, float]]) -> None:
        self.nodes = {}
        for id in nodes_ids:
            self.nodes[id] = Node(id)
        self.links = []
        for end1, end2, capacity, cost in links_data:
            self.links.append(Link(end1, end2, capacity, cost))
            self.nodes[end1].add_neighbour(end2, capacity, cost)
            self.nodes[end2].add_neighbour(end1, capacity, cost)


def parse_xml(path: str)\
        -> tuple[list[str], list[tuple[str, str, float, float]]]:
    """
Returns a tuple of 2 lists. First list contains list of ids of nodes in the
network, second - tuple of id_of_node_on_one_end, id_of_node_on_the_other_end,
capacity_of_link, cost_of_link
    """
    tree = ET.parse(path)
    root = tree.getroot()
    structure = root.find('./{http://sndlib.zib.de/network}networkStructure')
    nodes = structure.find('./{http://sndlib.zib.de/network}nodes')
    links = structure.find('./{http://sndlib.zib.de/network}links')
    nodes_data = [child.get('id') for child in nodes]
    links_data = []
    for link in links:
        source = link.find('.//{http://sndlib.zib.de/network}source')
        target = link.find('.//{http://sndlib.zib.de/network}target')
        capacity = link.find('.//{http://sndlib.zib.de/network}capacity')
        cost = link.find('.//{http://sndlib.zib.de/network}cost')
        links_data.append((source.text, target.text,
                           float(capacity.text), float(cost.text)))
    return(nodes_data, links_data)


nodes_ids, links_data =\
    parse_xml(path.normpath(path.join('data', 'network_structure.xml')))
network = Network(nodes_ids, links_data)
print(network.nodes['Dortmund'].links)
