class MutantNode:
    def __init__(self, name):
        self.name = str(name)
        self.children = []
        self.parents = []
        self.tests = set()  # Use a set for easier comparison
        self.unique_tests = set()
        self.size = 1

    def add_child(self, child_node):
        if child_node not in self.children:
           self.children.append(child_node)

    def add_parent(self, parent_node):
        self.parents.append(parent_node)
        if parent_node not in self.parents:
            parent_node.children.append(self)

    def add_tests(self, tests):
        self.tests.update(tests)  # Add tests to the set

    def is_indistinguishable(self, other_node):
        return self.tests == other_node.tests

    def merge_with(self, other_node):
        """Merge another node into this one, combining their names and relationships."""
        self.name += f"-{other_node.name}"
        self.size += other_node.size
        for child in other_node.children:
            if child not in self.children:
                self.add_child(child)
        for parent in other_node.parents:
            if parent not in self.parents:
                parent.add_child(self)
        other_node.children = []
        other_node.parents = []

    def __repr__(self):
        return f"{self.name}"
