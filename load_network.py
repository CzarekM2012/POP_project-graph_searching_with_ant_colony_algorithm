from xml.etree import ElementTree as ET


class Node:
    """
Node of a network.\n
Contains `id` and a list `links` containing ids of links it belongs to.\n
Two nodes are equal if their `id`s are equal and
their `links` contain the same ids
    """
    def __init__(self, id: int) -> None:
        self.id = id
        self.links = []

    def add_link(self, link_id: int) -> None:
        if link_id not in self.links:
            self.links.append(link_id)

    def __eq__(self, other: 'Node') -> bool:
        if len(self.links) != len(other.links):
            return False

        for link_id in self.links:
            if link_id not in other.links:
                return False

        return self.id == other.id

    def __ne__(self, other: 'Node') -> bool:
        return not self == other


class Link:
    """
Link between nodes of a network.\n
Consists of tuple `ends` containing ids of nodes
on both ends of the link, `capacity` and `cost`\n
Two links are equal if values of their `id`, `capacity` and `cost` are equal, and
their `ends` contain the same ids.
    """
    def __init__(self, self_id: int, end1_id: int, end2_id: int,
                 capacity: float, cost: float)\
            -> None:
        self.id = self_id
        self.ends = (end1_id, end2_id)
        self.capacity = capacity
        self.cost = cost

    def get_other_end(self, end: int) -> int:
        if end == self.ends[0]:
            return self.ends[1]
        elif end == self.ends[1]:
            return self.ends[0]
        raise ValueError('given end is not one of the ends of this link')

    def __eq__(self, other: 'Link') -> bool:
        return ((self.ends[0] == other.ends[0] and
                 self.ends[1] == other.ends[1]) or
                (self.ends[0] == other.ends[1] and
                 self.ends[1] == other.ends[0])) and\
               self.capacity == other.capacity and\
               self.cost == other.cost and\
               self.id == other.id

    def __ne__(self, other: 'Link') -> bool:
        return not self == other


class Network:
    """
Network of nodes connected by symmetrical links\n
Contains `nodes` and `links` lists containing all
nodes and links of the network.\n
Contains `nodes_ids_map` and `links_ids_map` lists, allowing
to return from internal, numerical ids to original string ids.
    """
    def __init__(self, nodes_ids: list[str],
                 links_data: list[tuple[str, str, str, float, float]]) -> None:
        node_id = 0
        link_id = 0
        node_id_str_to_int = dict[str, int]()
        self.nodes_ids_map = []
        self.links_ids_map = []

        self.nodes = list[Node]()
        for id in nodes_ids:
            if id not in self.nodes_ids_map:
                self.nodes_ids_map.append(id)
                self.nodes.append(Node(node_id))
                node_id_str_to_int[id] = node_id
                node_id += 1

        self.links = list[Link]()
        for id, end1, end2, capacity, cost in links_data:
            if id not in self.links_ids_map:
                end1 = node_id_str_to_int[end1]
                end2 = node_id_str_to_int[end2]
                self.links_ids_map.append(id)
                self.links.append(Link(link_id, end1, end2, capacity, cost))
                self.nodes[end1].add_link(end2)
                self.nodes[end2].add_link(end1)


def parse_xml(path: str)\
        -> tuple[list[str], list[tuple[str, str, str, float, float]]]:
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
        links_data.append((link.get('id'), source.text, target.text,
                           float(capacity.text), float(cost.text)))
    return(nodes_data, links_data)
