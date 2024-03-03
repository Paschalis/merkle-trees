import hashlib
import math

from graphviz import Digraph

def hash(m: str) -> str:
    '''
    SHA256 hash of a string.
    '''
    h = hashlib.sha256()
    h.update(bytes(m, 'utf-8'))
    return str(h.digest().hex())


def verify_proof(value: str, index: int, proof: list[str], root_value: str) -> bool:
    '''
    Verify a Merkle Tree proof of inclusion.

    Indexing starts at 0.
    '''

    # Make sure index is not out of bounds.
    max_index = 2**len(proof) - 1
    if index > max_index: return False

    level = 0

    cur_hash = hash(str(level) + value)
    for elem in proof:
        level += 1
        if index % 2 == 0: # even number, so value is a left child
            cur_hash = hash(str(level) + cur_hash + elem)
        else:
            cur_hash = hash(str(level) + elem + cur_hash) 
        index = index // 2
    return cur_hash == root_value


class Node:
    '''
    Node of a (doubly linked) binary tree.
    '''
    def __init__(self, value, parent=None, left=None, right=None, level=0):
        self.value = value
        self.parent = parent
        self.left = left
        self.right = right
        self.level = level


def create_parent(left: Node, right: Node) -> Node:
    '''
    Given two Nodes, calculate, set and return their parent.
    '''
    parent = Node(value=hash(str(left.level+1) + left.value + right.value), level=left.level+1)
    left.parent = parent
    right.parent = parent
    parent.left = left
    parent.right = right
    return parent   


class MerkleTree:
    def __init__(self, values: list[str]):
        self.values = values
        # number of non-dummy values
        self.non_dummy = len(values)
        self.__create_leaves()
        self.root = self.__construct()
        self.height = self.root.level

    def __create_leaves(self) -> list[Node]:
        '''
        Create the leaves of a Merkle Tree.

        Leaf values are prepended with a "0" before being hashed.
        '''
        self.leaves = []
        for value in self.values:
            # TODO: put this into Node constructor
            self.leaves.append(Node(hash('0'+value)))

    def __construct(self) -> Node:
        '''
        Construct a Merkle Tree.
        - calculate levels
        - set root
        '''
        self.__pad()
        cur_level = self.leaves
        while len(cur_level) > 1:
            next_level = []
            for i in range(0, len(cur_level), 2):
                node_left = cur_level[i]
                node_right = cur_level[i+1]
                next_level.append(create_parent(node_left, node_right))
            cur_level = next_level
        [root] = cur_level
        return root
    
    def __pad(self):
        '''
        Make number of leaves a power of 2 by adding dummy values.
        '''
        number_of_leaves = len(self.leaves)
        log = math.log2(number_of_leaves)
        # if not a power of 2
        if math.floor(log) != log:
            closest_power_of_two = int(2 ** (math.floor(log) + 1)) # number of leaves it should have
            to_append = closest_power_of_two - number_of_leaves # number of leaves to be added (dummy values)
            self.leaves += [Node(hash('0'+'dummy')) for i in range(to_append)]
    
    def calculate_proof(self, value: str, index: int) -> list[str]:
        '''
        Calculate Merkle Tree proof.
        '''
        if (index > len(self.values) or self.values[index] != value):
            return ['']
        proof = []
        node = self.leaves[index]
        while node.parent:
            parent = node.parent
            if node == parent.left:
                proof.append(parent.right.value)
            else:
                proof.append(parent.left.value)
            node = parent
        return proof


    
    # def concat(self, other_tree) -> Node:
    #     '''
    #     Concatenate two Merkle Trees.

    #     Trees should have the same number of leaves (and be padded).

    #     Returns new root.
    #     '''
    #     left_root = self.root
    #     right_root = other_tree.root
    #     parent = create_parent(left_root, right_root)
    #     self.root = parent
    #     self.leaves += other_tree.leaves
    #     self.values += other_tree.values
    #     self.non_dummy += other_tree.non_dummy
    
    # def add_value(self, value: str):
    #     '''
    #     Add value to Merkle Tree (create new leaf).
    #     '''
    #     # if non-dummy values are already a power of 2
    #     # so tree is full
    #     if (self.non_dummy == len(self.leaves)):
    #         # construct a new merkle tree and concatenate the two
    #         new_tree = MerkleTree([value] + ['dummy' for i in range(len(self.leaves) - 1)])
    #         # concat new tree to old tree
    #         self.concat(new_tree)
    #     else:
    #         # replace a dummy value with the new value
    #         index = self.non_dummy
    #         self.leaves[index].value = hash('0'+value)
    #         self.values.append(value)
    #         self.non_dummy += 1
    #         # re-calculate hashes
    #         node = self.leaves[index]
    #         while node.parent:
    #             parent = node.parent
    #             if node == parent.left:
    #                 parent.value = hash('1' + node.value + parent.right.value)
    #             else:
    #                 parent.value = hash('1' + parent.left.value + node.value)
    #             node = node.parent

    # def update_value_at_index(self, index: int, new_value: str):
    #     '''
    #     Update the value at a given index.
    #     '''
    #     try:
    #         # update values
    #         self.values[index] = new_value
    #         # update node and path up to root
    #         node = self.leaves[index]
    #         node.value = hash('0' + new_value)
    #         while node.parent:
    #             parent = node.parent
    #             if node == parent.left:
    #                 parent.value = hash('1' + node.value + parent.right.value)
    #             else:
    #                 parent.value = hash('1' + parent.left.value + node.value)
    #             node = parent
    #     except IndexError:
    #         raise IndexError('Index out of bounds.')

    def print(self):
        '''
        Print all levels of the tree.
        '''
        cur_level = self.leaves
        to_print = []
        while cur_level:
            cur_level_vals = [node.value for node in cur_level]
            to_print.append(cur_level_vals)
            # construct next level
            next_level = []
            for i in range(0, len(cur_level), 2):
                node = cur_level[i]
                if node.parent:
                    next_level.append(node.parent)
            cur_level = next_level
        to_print.reverse()
        for level in to_print:
            print(level)








    def visualize(self, filename='merkle_tree'):
        dot = Digraph(comment='Merkle Tree')

        def add_nodes_edges(node):
            if node is None:
                return
            # Check if the node's value needs to be truncated
            label = str(node.value)[:16] + "..." if len(node.value) > 16 else str(node.value)
            # Add the current node with the updated label
            dot.node(name=str(id(node)), label=label)
            # Recursively add left child
            if node.left:
                dot.edge(str(id(node)), str(id(node.left)))
                add_nodes_edges(node.left)
            # Recursively add right child
            if node.right:
                dot.edge(str(id(node)), str(id(node.right)))
                add_nodes_edges(node.right)

        add_nodes_edges(self.root)
        dot.render(filename, format='pdf', view=False)  # Explicitly specify the format and don't open automatically
        try:
            dot.render(filename, view=false)  # Save and open the rendered graph
        except Exception as e:
            print(f"Error generating visualization: {e}")
