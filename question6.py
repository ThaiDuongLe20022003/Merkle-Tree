import hashlib
import json

class MerkleTree:
    def __init__(self, data_list):
        # Initialize the Merkle tree by hashing the given data and building the tree
        self.leaves = [self._hash_data(data) for data in data_list]
        self.tree = self._build_tree(self.leaves)

    def _hash_data(self, data):
        """Creates a SHA-256 hash of the input data, handling both strings and dictionaries."""
        # If the data is a dictionary, convert it to a JSON string
        if isinstance(data, dict):
            data = json.dumps(data, sort_keys=True).encode('utf-8')
        elif isinstance(data, str):
            data = data.encode('utf-8')
        return hashlib.sha256(data).hexdigest()

    def _build_tree(self, leaves):
        """Constructs the Merkle tree and returns the tree as a list of lists."""
        tree = [leaves]
        current_level = leaves
        
        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left
                combined = left + right
                next_level.append(self._hash_data(combined))
            tree.append(next_level)
            current_level = next_level

        return tree

    def get_root(self):
        """Returns the Merkle root."""
        return self.tree[-1][0] if self.tree else None

    def get_tree_height(self):
        """Calculates and returns the height of the tree."""
        return len(self.tree)
    
    def visualize_tree(self):
        """Prints the tree structure level by level with hash truncation."""
        for level_index, level in enumerate(self.tree):
            print(f"Level {level_index}:")
            truncated_hashes = [hash[:6] for hash in level]
            print("  " + "  ".join(truncated_hashes))
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

    def test_immutability(self, index, new_value):
        """Tests if the root changes when a leaf node is modified."""
        original_root = self.get_root()
        self.update_leaf(index, new_value)
        updated_root = self.get_root()
        #print("Original Root:", original_root)
        #print("Updated Root:", updated_root)
        print("Roots match after modification:", original_root == updated_root)

    def update_leaf(self, index, new_value):
        """Update a leaf node and rebuild the tree from that node upwards."""
        if index < 0 or index >= len(self.leaves):
            raise IndexError("Index out of bounds")
        
        # Update the leaf node
        self.leaves[index] = self._hash_data(new_value)
        
        # Rebuild the tree from the leaf upwards
        self.tree = self._build_tree(self.leaves)

# Example usage
if __name__ == "__main__":
    # Sample records (dictionaries)
    records = [
        {"id": 1, "name": "Alice", "balance": 100.50},
        {"id": 2, "name": "Bob", "balance": 200.00},
        {"id": 3, "name": "Charlie", "balance": 150.75}
    ]
    
    # Create Merkle tree from records
    merkle_tree = MerkleTree(records)
    
    # Get the Merkle root
    root = merkle_tree.get_root()
    print("Merkle Root:", root)
    
    # Generate a proof for a record at index 1 (Bob)
    proof = merkle_tree.get_proof(1)
    
    # Verify the proof for the record at index 1 (Bob)
    is_valid = merkle_tree.verify_proof(records[1], proof, root)
    print("\nProof is valid:", is_valid)
    
    # Visualize the Merkle tree with truncated hashes
    print("\nVisualized Tree:")
    merkle_tree.visualize_tree()
    
    # Test immutability by modifying the second record (Bob)
    print("Testing Immutability:")
    merkle_tree.test_immutability(1, {"id": 2, "name": "Bob", "balance": 250.00})
