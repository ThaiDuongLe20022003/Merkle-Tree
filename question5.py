import hashlib
from math import ceil, log2
# import networkx as nx
# import matplotlib.pyplot as plt

class MerkleTree:
    def __init__(self, data_list):
        # Initialize the leaves by hashing each data item
        self.leaves = [self._hash_data(data) for data in data_list]
        # Build the Merkle tree from the leaves up to the root
        self.tree = self._build_tree(self.leaves)

    def _hash_data(self, data):
        """Creates a SHA-256 hash of the input data."""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hashlib.sha256(data).hexdigest()

    def _build_tree(self, leaves):
        """Constructs the Merkle tree and returns the tree as a list of lists."""
        # Initialize the tree with the leaves at the bottom level
        tree = [leaves]
        current_level = leaves
        
        # Build the tree level by level until there is only one hash left (the root)
        while len(current_level) > 1:
            next_level = []
            # Iterate over pairs of nodes at the current level
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                # Handle cases where there is an odd number of nodes by duplicating the last node
                right = current_level[i + 1] if i + 1 < len(current_level) else left
                # Hash the combination of the left and right nodes to create the parent node
                combined = left + right
                next_level.append(self._hash_data(combined))
            # Add the new level to the tree
            tree.append(next_level)
            # Move up to the next level
            current_level = next_level

        return tree

    def get_root(self):
        """Returns the Merkle root."""
        return self.tree[-1][0] if self.tree else None

    def get_tree_height(self):
        """Calculates and returns the height of the tree."""
        return len(self.tree)

    def visualize_tree(self):
        """Prints the tree structure level by level."""
        for level_index, level in enumerate(self.tree):
            print(f"Level {level_index}:")
            print("  " + "  ".join(level))
            print()

    def get_proof(self, index):
        """Generates a Merkle proof for a leaf at a given index."""
        if index < 0 or index >= len(self.leaves):
            raise IndexError("Index out of bounds")

        proof = []
        for level in range(len(self.tree) - 1):
            sibling_index = index ^ 1  # XOR with 1 toggles the last bit
            if sibling_index < len(self.tree[level]):
                position = 'left' if sibling_index < index else 'right'
                proof.append({'hash': self.tree[level][sibling_index], 'position': position})
            index //= 2
        return proof

    def verify_proof(self, leaf, proof, root):
        """Verifies a Merkle proof for a given leaf and root."""
        current_hash = self._hash_data(leaf)
        for sibling in proof:
            if sibling['position'] == 'left':
                current_hash = self._hash_data(sibling['hash'] + current_hash)
            elif sibling['position'] == 'right':
                current_hash = self._hash_data(current_hash + sibling['hash'])
        return current_hash == root
    
    def update_leaf(self, index, new_value):
        """Update a leaf node and rebuild the tree from that node upwards."""
        if index < 0 or index >= len(self.leaves):
            raise IndexError("Index out of bounds")
        
        # Update the leaf node
        self.leaves[index] = self._hash_data(new_value)
        
        # Rebuild the tree from the leaf upwards
        self.tree = self._build_tree(self.leaves)
    
    def test_immutability(self, index, new_value):
        """Tests if the root changes when a leaf node is modified."""
        # Get the original root
        original_root = self.get_root()
        
        # Update the leaf node at the specified index
        self.update_leaf(index, new_value)
        
        # Get the updated root
        updated_root = self.get_root()
        
        # Compare the roots before and after the modification
        # print("Original Root:", original_root)
        # print("Updated Root:", updated_root)
        print("Roots match after modification:", original_root == updated_root)

if __name__ == "__main__":
    # Example data to create the Merkle tree
    data = ['a', 'b', 'c', 'd']

    # Initialize the Merkle tree with the data
    merkle_tree = MerkleTree(data)
    
    # Test immutability by modifying the third node (index 2)
    merkle_tree.test_immutability(2, 'z')