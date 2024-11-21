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
    
    def find_sibling(self, index):
        """Returns the sibling hash of a given leaf node index."""
        if index < 0 or index >= len(self.leaves):
            raise IndexError("Index out of bounds")

        # Sibling index is calculated by toggling the last bit (XOR with 1)
        sibling_index = index ^ 1

        # Ensure sibling_index is within bounds for the first level (leaves level)
        if sibling_index >= len(self.tree[0]):
            return None

        # Return the sibling hash from the first level (leaves level)
        return self.tree[0][sibling_index]
        
if __name__ == "__main__":
    # Example data to create the Merkle tree
    data = ['a', 'b', 'c', 'd']

    # Initialize the Merkle tree with the data
    merkle_tree = MerkleTree(data)

    # Find the sibling of node 2
    sibling_hash = merkle_tree.find_sibling(2)
    print("Sibling of node 2:", sibling_hash)