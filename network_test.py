from unittest.case import expectedFailure
import network as net
from os.path import normpath, join
import unittest


class TestXMLParser(unittest.TestCase):

    def test_parse_xml(self):
        nodes_data, links_data =\
            net.parse_xml(normpath(join('test_data',
                                        'test_network_structure.xml')))
        expected_nodes_data = ['Aachen', 'Augsburg', 'Bayreuth', 'Berlin']
        expected_links_data = [('L1', 'Aachen', 'Augsburg', 40.0, 3290.0),
                               ('L2', 'Berlin', 'Augsburg', 50.0, 2290.0),
                               ('L3', 'Berlin', 'Bayreuth', 45.0, 4000.0),
                               ('L4', 'Aachen', 'Bayreuth', 60.0, 1290.0),
                               ('L5', 'Aachen', 'Berlin', 50.0, 4500.0)]
        self.assertListEqual(nodes_data, expected_nodes_data)
        self.assertListEqual(links_data, expected_links_data)


class TestNode(unittest.TestCase):

    def test_add_new_link(self):
        test_node = net.Node(0)

        self.assertListEqual(test_node.links, [])

        test_node.add_link(0)
        test_node.add_link(1)
        test_node.add_link(2)

        self.assertListEqual(test_node.links, [0, 1, 2])

    def test_add_existing_link(self):
        test_node = net.Node(0)

        self.assertListEqual(test_node.links, [])

        test_node.add_link(0)
        test_node.add_link(1)
        test_node.add_link(0)
        test_node.add_link(2)
        test_node.add_link(1)
        test_node.add_link(0)

        self.assertListEqual(test_node.links, [0, 1, 2])

    def test___eq___the_same(self):
        test_node = net.Node(0)

        test_node.add_link(0)
        test_node.add_link(1)
        test_node.add_link(2)

        self.assertEqual(test_node, test_node)

    @expectedFailure
    def test___ne___the_same(self):
        test_node = net.Node(0)

        test_node.add_link(0)
        test_node.add_link(1)
        test_node.add_link(2)

        self.assertNotEqual(test_node, test_node)

    def test___eq___equal_links_the_same_content_different_order(self):
        test_node1 = net.Node(0)
        test_node2 = net.Node(0)

        test_node1.add_link(0)
        test_node1.add_link(1)
        test_node1.add_link(2)

        test_node2.add_link(0)
        test_node2.add_link(2)
        test_node2.add_link(1)

        self.assertEqual(test_node1, test_node2)

    @expectedFailure
    def test___ne___equal_links_the_same_content_different_order(self):
        test_node1 = net.Node(0)
        test_node2 = net.Node(0)

        test_node1.add_link(0)
        test_node1.add_link(1)
        test_node1.add_link(2)

        test_node2.add_link(0)
        test_node2.add_link(2)
        test_node2.add_link(1)

        self.assertNotEqual(test_node1, test_node2)

    @expectedFailure
    def test___eq___not_equal_different_ids(self):
        test_node1 = net.Node(0)
        test_node2 = net.Node(1)

        test_node1.add_link(0)
        test_node1.add_link(1)
        test_node1.add_link(2)

        test_node2.add_link(0)
        test_node2.add_link(1)
        test_node2.add_link(2)

        self.assertEqual(test_node1, test_node2)

    def test___ne___not_equal_different_ids(self):
        test_node1 = net.Node(0)
        test_node2 = net.Node(1)

        test_node1.add_link(0)
        test_node1.add_link(1)
        test_node1.add_link(2)

        test_node2.add_link(0)
        test_node2.add_link(1)
        test_node2.add_link(2)

        self.assertNotEqual(test_node1, test_node2)

    @expectedFailure
    def test___eq___not_equal_links_different_contents(self):
        test_node1 = net.Node(0)
        test_node2 = net.Node(0)

        test_node1.add_link(0)
        test_node1.add_link(1)
        test_node1.add_link(2)

        test_node2.add_link(0)
        test_node2.add_link(1)

        self.assertEqual(test_node1, test_node2)

    def test___ne___not_equal_links_different_contents(self):
        test_node1 = net.Node(0)
        test_node2 = net.Node(0)

        test_node1.add_link(0)
        test_node1.add_link(1)
        test_node1.add_link(2)

        test_node2.add_link(0)
        test_node2.add_link(1)

        self.assertNotEqual(test_node1, test_node2)


class TestLink(unittest.TestCase):

    def test_get_other_end_has_given_end(self):
        test_link = net.Link(0, 0, 1, 0, 0)
        self.assertEqual(test_link.get_other_end(test_link.ends[0]),
                         test_link.ends[1])
        self.assertEqual(test_link.get_other_end(test_link.ends[1]),
                         test_link.ends[0])

    def test_get_other_end_does_not_have_given_end(self):
        test_link = net.Link(0, 0, 1, 0, 0)
        with self.assertRaises(ValueError):
            test_link.get_other_end(2)

    def test___eq___the_same(self):
        test_link = net.Link(0, 0, 1, 0, 0)
        self.assertEqual(test_link, test_link)

    @expectedFailure
    def test___ne___the_same(self):
        test_link = net.Link(0, 0, 1, 0, 0)
        self.assertNotEqual(test_link, test_link)

    def test___eq___equal_switched_ends(self):
        test_link1 = net.Link(0, 0, 1, 0, 0)
        test_link2 = net.Link(0, 1, 0, 0, 0)
        self.assertEqual(test_link1, test_link2)

    @expectedFailure
    def test___ne___equal_switched_ends(self):
        test_link1 = net.Link(0, 0, 1, 0, 0)
        test_link2 = net.Link(0, 1, 0, 0, 0)
        self.assertNotEqual(test_link1, test_link2)

    @expectedFailure
    def test___eq___not_equal_different_ids(self):
        test_link1 = net.Link(0, 0, 1, 0, 0)
        test_link2 = net.Link(1, 0, 1, 0, 0)
        self.assertEqual(test_link1, test_link2)

    def test___ne___not_equal_different_ids(self):
        test_link1 = net.Link(0, 0, 1, 0, 0)
        test_link2 = net.Link(1, 0, 1, 0, 0)
        self.assertNotEqual(test_link1, test_link2)

    @expectedFailure
    def test___eq___not_equal_different_costs(self):
        test_link1 = net.Link(0, 0, 1, 0, 0)
        test_link2 = net.Link(0, 0, 1, 0, 1)
        self.assertEqual(test_link1, test_link2)

    def test___ne___not_equal_different_costs(self):
        test_link1 = net.Link(0, 0, 1, 0, 0)
        test_link2 = net.Link(0, 0, 1, 0, 1)
        self.assertNotEqual(test_link1, test_link2)

    @expectedFailure
    def test___eq___not_equal_different_capacities(self):
        test_link1 = net.Link(0, 0, 1, 0, 0)
        test_link2 = net.Link(0, 0, 1, 1, 0)
        self.assertEqual(test_link1, test_link2)

    def test___ne___not_equal_different_capacities(self):
        test_link1 = net.Link(0, 0, 1, 0, 0)
        test_link2 = net.Link(0, 0, 1, 1, 0)
        self.assertNotEqual(test_link1, test_link2)

    @expectedFailure
    def test___eq___not_equal_different_ends(self):
        test_link1 = net.Link(0, 0, 1, 0, 0)
        test_link2 = net.Link(0, 0, 2, 0, 0)
        test_link3 = net.Link(0, 2, 1, 0, 0)
        test_link4 = net.Link(0, 2, 3, 0, 0)
        self.assertEqual(test_link1, test_link2)
        self.assertEqual(test_link1, test_link3)
        self.assertEqual(test_link1, test_link4)

    def test___ne___not_equal_different_ends(self):
        test_link1 = net.Link(0, 0, 1, 0, 0)
        test_link2 = net.Link(0, 0, 2, 0, 0)
        test_link3 = net.Link(0, 2, 1, 0, 0)
        test_link4 = net.Link(0, 2, 3, 0, 0)
        self.assertNotEqual(test_link1, test_link2)
        self.assertNotEqual(test_link1, test_link3)
        self.assertNotEqual(test_link1, test_link4)


class TestNetwork(unittest.TestCase):

    def test___init__(self):
        nodes_data = ['Aachen', 'Augsburg', 'Bayreuth', 'Berlin']
        links_data = [('L1', 'Aachen', 'Augsburg', 40.0, 3290.0),
                      ('L2', 'Berlin', 'Augsburg', 50.0, 2290.0),
                      ('L3', 'Berlin', 'Bayreuth', 45.0, 4000.0),
                      ('L4', 'Aachen', 'Bayreuth', 60.0, 1290.0),
                      ('L5', 'Aachen', 'Berlin', 50.0, 4500.0)]
        test_network = net.Network(nodes_data, links_data)

        # lengths
        self.assertEqual(len(nodes_data), len(test_network.nodes),
                         'Number of nodes in the test_network is not the same as in \
the nodes_data')
        self.assertEqual(len(links_data), len(test_network.links),
                         'Number of links in the test_network is not the same as in \
the links_data')

        # contents and order
        self.assertListEqual(nodes_data, [test_network.nodes_ids_map[node.id]
                                          for node in test_network.nodes],
                             'list of nodes data in the test_network is not the same as in \
the nodes_data')
        self.assertListEqual(links_data,
                             [(test_network.links_ids_map[link.id],
                               test_network.nodes_ids_map[link.ends[0]],
                               test_network.nodes_ids_map[link.ends[1]],
                               link.capacity, link.cost) for link
                              in test_network.links],
                             'list of links data in the test_network is not the same as in \
the links_data')

        # contents of individual nodes (depends on order of nodes and links)
        self.assertCountEqual(test_network.nodes[0].links,
                              [test_network.links[0].id,
                               test_network.links[3].id,
                               test_network.links[4].id])
        self.assertCountEqual(test_network.nodes[1].links,
                              [test_network.links[0].id,
                               test_network.links[1].id])
        self.assertCountEqual(test_network.nodes[2].links,
                              [test_network.links[2].id,
                               test_network.links[3].id])
        self.assertCountEqual(test_network.nodes[3].links,
                              [test_network.links[1].id,
                               test_network.links[2].id,
                               test_network.links[4].id])
