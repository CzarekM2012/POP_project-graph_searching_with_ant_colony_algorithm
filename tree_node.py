class TreeNode:
    network = None
    start_node = None
    end_node = None

    min_dist = None
    min_cost = None

    weight_common = 1000000000
    weight_length = 1
    weight_cost = 1
    scale_cost = 1

    """
    Node of A* partial solution tree.\n
Each node represents a partial solution through a list of integers, one for each edge in the network\n
A node consists of a partial solution and references to its parent and sons
    """
    def __init__(self, solution, parent, head, phase) -> None:
        
        # Create new list to aviod copying only reference
        self.solution = []
        for edge in solution:
            self.solution.append(edge)

        self.parent = parent
        self.children = None

        # Although not exactly necessary, this makes neighbourhood calculation much faster
        self.head = head
        self.phase = phase
    
    def create_children_nodes(self):
        self.children = []
        for link_id in self.head.links:
            link = TreeNode.network.links[link_id]
            edge_type = self.solution[link_id]

            new_solution = []
            for edge in self.solution:
                new_solution.append(edge)

            # Phase 1 = looking for the end
            if self.phase == 1:
                if new_solution[link_id] == 0:
                    new_solution[link_id] = 1
                    target_node = TreeNode.network.nodes[link.get_other_end(self.head.id)]
                    if not self.is_visited_in_this_phase(target_node):
                        phase = self.phase
                        if target_node == TreeNode.end_node:
                            phase = 2    
                        self.children.append(TreeNode(new_solution, self, target_node, phase))
            
            # Phase 2 = going back to start
            if self.phase == 2:
                if new_solution[link_id] < 2:
                    new_solution[link_id] += 2
                    target_node = TreeNode.network.nodes[link.get_other_end(self.head.id)]
                    if not self.is_visited_in_this_phase(target_node):
                        phase = self.phase
                        if target_node == TreeNode.start_node:
                            phase = 3    
                        self.children.append(TreeNode(new_solution, self, target_node, phase))
            
            # Phase 3 = arrived at the start -> no more can be added

    def is_visited_in_this_phase(self, node):
        for link_id in node.links:
            if self.solution[link_id] >= self.phase:
                return True
        return False

    def get_score(self):
        return self.get_heuristic() + self.get_goal_function()

    
    # Doesn't check validity
    def get_goal_function(self):
        result = 0
        for edge, value in enumerate(self.solution):
            
            if value == 1 or value == 3:
                result += TreeNode.weight_length

            if value == 2 or value == 3:
                result += TreeNode.weight_cost * TreeNode.network.links[edge].get_a_star_cost()
            
            if value == 3:
                result += TreeNode.weight_common

        return result
    

    
    def get_heuristic(self):
        if self.phase == 1:
            return TreeNode.weight_length * TreeNode.min_dist[self.head.id][TreeNode.end_node.id] + TreeNode.weight_cost * TreeNode.scale_cost * TreeNode.min_cost[self.head.id][self.end_node.id] + TreeNode.weight_length * TreeNode.min_dist[self.end_node.id][TreeNode.start_node.id] + TreeNode.weight_cost * TreeNode.scale_cost * TreeNode.min_cost[self.end_node.id][self.start_node.id]
        elif self.phase == 2:
            return TreeNode.weight_length * TreeNode.min_dist[self.head.id][TreeNode.start_node.id] + TreeNode.weight_cost * TreeNode.scale_cost * TreeNode.min_cost[self.head.id][self.start_node.id]
        else:
            return 0

    def __lt__(self, other):
        #print(f"Comparing: {self.get_score()} and {other.get_score()}") #": {self.solution} {other.solution}")
        self.get_score() < other.get_score()

    
    def __str__(self):
        #node_ids = [TreeNode.start_node.id]
        node_ids = []

        head = self
        while head != None:
            node_ids.append(head.head.id)
            head = head.parent

#        phase = 1
#        added = True
#        while added and phase < 3:
#            added = False
#            for edge, value in enumerate(self.solution):
#                if phase == 1 and value != 1:
#                    continue
#                
#                if phase == 2 and value < 2:
#                    continue
#
#                link = TreeNode.network.links[edge]
#                
#                if link.ends[0] in node_ids and link.ends[1] not in node_ids:
#                    node_ids.append(link.ends[1])
#                    added = True
#
#                    if phase == 1 and link.ends[1] == TreeNode.end_node.id:
#                        phase = 2
#                    if phase == 2 and link.ends[1] == TreeNode.start_node.id:
#                        phase = 3
#                
#                if link.ends[0] not in node_ids and link.ends[1] in node_ids:
#                    node_ids.append(link.ends[0])
#                    added = True
#                    
#                    if phase == 1 and link.ends[0] == TreeNode.end_node.id:
#                        phase = 2
#                    if phase == 2 and link.ends[0] == TreeNode.start_node.id:
#                        phase = 3
        
        node_names = []
        for id in node_ids:
            node_names.append(TreeNode.network.nodes_ids_map[id])

        return "Path: " + str(node_names)