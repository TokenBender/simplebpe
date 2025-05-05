import json
import time
import logging
import tempfile
from typing import Dict, List, Tuple, Set, Optional, Union, ByteString
from collections import Counter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BPETokenizer:
    """
    A monolithic implementation of the Byte Pair Encoding (BPE) tokenizer.
    """
    
    def __init__(self, vocab_size=256, debug=False):
        """
        Initialize the BPE tokenizer.
        
        Args:
            vocab_size: Target vocabulary size (minimum 256 for bytes)
            debug: Whether to print debug information
        """
        self.debug = debug
        self.vocab_size = max(256, vocab_size)  # We need at least 256 tokens for bytes
        
        # Start with the basic byte vocabulary (0-255)
        # Maps token IDs to their byte sequences
        self.id_to_token = {i: bytes([i]) for i in range(256)}
        
        # Maps byte sequences to their token IDs
        self.token_to_id = {bytes([i]): i for i in range(256)}
        
        # Stores merges as (token1, token2) -> new_token
        self.merges = {}
        
        # Tracks the next available token ID
        self.next_token_id = 256
        
        # Mapping of token pairs to their merge IDs
        self.pair_to_merge_id = {}
        
        if self.debug:
            logger.info(f"Initialized BPETokenizer with target vocab size {self.vocab_size}")
    
    # --- Byte-Level Tokenization ---
    
    def text_to_bytes(self, text):
        """Convert text to a list of byte values."""
        if not isinstance(text, str):
            raise TypeError("Input must be a string")
            
        # Convert to bytes using UTF-8 encoding
        byte_array = list(text.encode('utf-8'))
        
        if self.debug:
            logger.info(f"Converted text to bytes: '{text}' -> {byte_array}")
        
        return byte_array
    
    def bytes_to_text(self, byte_list):
        """Convert a list of byte values back to text."""
        if not isinstance(byte_list, list):
            raise TypeError("Input must be a list of integers")
        
        if not all(isinstance(b, int) and 0 <= b <= 255 for b in byte_list):
            raise ValueError("All bytes must be integers in range 0-255")
            
        # Convert byte list to bytearray and then to string
        try:
            # Convert to bytearray first
            byte_array = bytearray(byte_list)
            
            # Then decode to string using UTF-8
            text = byte_array.decode('utf-8')
            
            if self.debug:
                logger.info(f"Converted bytes to text: {byte_list} -> '{text}'")
                
            return text
        except UnicodeDecodeError as e:
            # Handle invalid UTF-8 sequences
            logger.error(f"Failed to decode bytes: {e}")
            raise ValueError(f"Invalid UTF-8 byte sequence: {e}")
    
    # --- Pair Frequency Counter ---
    
    def count_token_pairs(self, tokens):
        """
        Count occurrences of adjacent token pairs in a sequence.
        
        Args:
            tokens: List of token byte sequences
            
        Returns:
            Counter of token pairs with their frequencies
        """
        if not tokens:
            return Counter()
            
        # Count pairs of adjacent tokens
        pairs = Counter()
        for i in range(len(tokens) - 1):
            pair = (tokens[i], tokens[i + 1])
            pairs[pair] += 1
            
        if self.debug:
            logger.info(f"Found {len(pairs)} unique token pairs")
            if len(pairs) < 10:  # Only log details for small inputs
                logger.info(f"Pair counts: {pairs}")
                
        return pairs

    def get_most_frequent_pair(self, pairs):
        """
        Find the most frequent token pair.
        
        Args:
            pairs: Counter of token pairs with their frequencies
            
        Returns:
            Tuple of (token1, token2) representing the most frequent pair
        """
        if not pairs:
            return None
            
        # Find the pair with the highest count
        most_common_pair = pairs.most_common(1)[0][0]
        
        if self.debug:
            count = pairs[most_common_pair]
            t1, t2 = most_common_pair
            logger.info(f"Most frequent pair: ({t1}, {t2}) with count {count}")
            
        return most_common_pair
    
    # --- Merge Operations ---
    
    def merge_pair(self, tokens, pair):
        """
        Replace all occurrences of a token pair with a new merged token.
        
        Args:
            tokens: List of token byte sequences
            pair: Tuple of (token1, token2) to merge
            
        Returns:
            Updated list of tokens after merging
        """
        if not tokens or pair is None:
            return tokens
            
        t1, t2 = pair
        result = []
        i = 0
        
        # Create a new merged token by concatenating the pair
        merged_token = t1 + t2
        
        # Update vocabulary with the new token
        if merged_token not in self.token_to_id:
            self.id_to_token[self.next_token_id] = merged_token
            self.token_to_id[merged_token] = self.next_token_id
            self.next_token_id += 1
            
            # Record this merge in our merges dictionary
            self.merges[pair] = merged_token
            self.pair_to_merge_id[pair] = self.next_token_id - 1
            
            if self.debug:
                logger.info(f"Created new token {list(merged_token)} with ID {self.next_token_id - 1}")
        
        # Scan through tokens and perform merges
        while i < len(tokens):
            # If we're at the last token, just add it
            if i == len(tokens) - 1:
                result.append(tokens[i])
                break
                
            # Check if current pair matches the target pair
            if tokens[i] == t1 and tokens[i + 1] == t2:
                # Add the merged token and skip both original tokens
                result.append(merged_token)
                i += 2
            else:
                # Add the current token and move to the next
                result.append(tokens[i])
                i += 1
                
        if self.debug:
            logger.info(f"Merged {pair} -> {list(merged_token)}")
            logger.info(f"Tokens before: {len(tokens)}, after: {len(result)}")
            
        return result

    def train_step(self, tokens):
        """
        Perform a single training step: find most frequent pair and merge it.
        
        Args:
            tokens: List of token byte sequences
            
        Returns:
            (updated tokens, was_merge_performed)
        """
        # Count pairs
        pairs = self.count_token_pairs(tokens)
        
        # If no pairs, no merges to perform
        if not pairs:
            return tokens, False
            
        # Find most frequent pair
        pair = self.get_most_frequent_pair(pairs)
        
        # Merge the most frequent pair
        new_tokens = self.merge_pair(tokens, pair)
        
        # Return the new tokens and whether a merge was performed
        return new_tokens, len(new_tokens) < len(tokens)
    
    # --- Vocabulary Management ---
    
    def train(self, text, max_tokens=None, verbose=False):
        """
        Train the tokenizer on a text corpus.
        
        Args:
            text: The training text
            max_tokens: Maximum vocabulary size (if None, uses self.vocab_size)
            verbose: Whether to print progress information
            
        Returns:
            Number of merge operations performed
        """
        if max_tokens is None:
            max_tokens = self.vocab_size
            
        # Start with byte-level tokens
        byte_values = self.text_to_bytes(text)
        tokens = [bytes([b]) for b in byte_values]
        
        if verbose:
            logger.info(f"Initial tokens: {len(tokens)}")
            logger.info(f"Starting vocabulary size: {len(self.token_to_id)}")
            
        # Keep track of operations
        operations = 0
        
        # Perform merges until we reach the target vocabulary size or can't merge anymore
        while len(self.token_to_id) < max_tokens:
            # Perform a training step
            tokens, merged = self.train_step(tokens)
            
            # If no merge was performed, we're done
            if not merged:
                if verbose:
                    logger.info("No more merges possible.")
                break
                
            operations += 1
            
            if verbose and operations % 10 == 0:
                logger.info(f"Completed {operations} merges. Vocab size: {len(self.token_to_id)}")
                
        if verbose:
            logger.info(f"Training complete. Final vocabulary size: {len(self.token_to_id)}")
            logger.info(f"Performed {operations} merge operations")
            
        return operations

    def save_vocabulary(self, file_path):
        """
        Save the vocabulary to a file.
        
        Args:
            file_path: Path to save the vocabulary
        """
        # Store token pairs as strings with a separator that won't appear in the data
        merges_dict = {}
        for (t1, t2), v in self.merges.items():
            key = f"{list(t1)}|{list(t2)}"  # Use | as separator instead of comma
            merges_dict[key] = list(v)
        
        vocabulary = {
            'id_to_token': {k: list(v) for k, v in self.id_to_token.items()},
            'merges': merges_dict,
            'vocab_size': self.vocab_size,
            'next_token_id': self.next_token_id
        }
        
        with open(file_path, 'w') as f:
            json.dump(vocabulary, f, indent=2)
            
        if self.debug:
            logger.info(f"Saved vocabulary to {file_path}")
            
    def load_vocabulary(self, file_path):
        """
        Load the vocabulary from a file.
        
        Args:
            file_path: Path to load the vocabulary from
        """
        with open(file_path, 'r') as f:
            vocabulary = json.load(f)
            
        # Reset the current vocabulary
        self.id_to_token = {int(k): bytes(v) for k, v in vocabulary['id_to_token'].items()}
        self.token_to_id = {bytes(v): int(k) for k, v in vocabulary['id_to_token'].items()}
        
        # Parse the merges
        self.merges = {}
        for merge_str, merged in vocabulary['merges'].items():
            parts = merge_str.split('|')  # Split by the | separator
            if len(parts) == 2:
                t1_str, t2_str = parts
                try:
                    t1 = bytes(eval(t1_str))
                    t2 = bytes(eval(t2_str))
                    self.merges[(t1, t2)] = bytes(merged)
                except Exception as e:
                    logger.error(f"Error parsing merge: {merge_str} - {e}")
        
        # Load other attributes
        self.vocab_size = vocabulary['vocab_size']
        self.next_token_id = vocabulary['next_token_id']
        
        if self.debug:
            logger.info(f"Loaded vocabulary from {file_path}")
            logger.info(f"Vocabulary size: {len(self.token_to_id)}")
            
    def get_vocabulary_stats(self):
        """
        Get statistics about the current vocabulary.
        
        Returns:
            Dictionary with vocabulary statistics
        """
        # Count token lengths
        token_lengths = [len(token) for token in self.token_to_id.keys()]
        
        return {
            'vocab_size': len(self.token_to_id),
            'min_token_length': min(token_lengths) if token_lengths else 0,
            'max_token_length': max(token_lengths) if token_lengths else 0,
            'avg_token_length': sum(token_lengths) / len(token_lengths) if token_lengths else 0,
            'tokens_by_length': Counter(token_lengths),
            'bytes_covered': sum(token_lengths),
            'single_byte_tokens': sum(1 for l in token_lengths if l == 1),
            'multi_byte_tokens': sum(1 for l in token_lengths if l > 1)
        }


def test_vocabulary_serialization():
    """Test if the vocabulary serialization works correctly."""
    print("\n=== Testing Vocabulary Serialization ===\n")
    
    # Create a sample training text
    training_text = """
    The Byte Pair Encoding (BPE) algorithm is a data compression technique
    that iteratively replaces the most frequent pair of consecutive bytes
    in a sequence with a single, unused byte. In NLP, BPE operates on 
    characters or subwords rather than bytes, making it effective for 
    tokenization tasks in language models.
    """ * 3  # Repeat to ensure we have enough repeated patterns
    
    # Create a tokenizer for testing
    vocab_size = 300
    tokenizer = BPETokenizer(vocab_size=vocab_size, debug=True)
    
    # Train the tokenizer
    print("Training tokenizer...")
    tokenizer.train(training_text, verbose=True)
    
    # Show vocabulary stats
    stats = tokenizer.get_vocabulary_stats()
    print("\n--- Vocabulary Statistics ---")
    print(f"Vocabulary size: {stats['vocab_size']}")
    print(f"Min token length: {stats['min_token_length']}")
    print(f"Max token length: {stats['max_token_length']}")
    print(f"Average token length: {stats['avg_token_length']:.2f}")
    print(f"Single-byte tokens: {stats['single_byte_tokens']}")
    print(f"Multi-byte tokens: {stats['multi_byte_tokens']}")
    
    # Create a temporary file for testing
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp:
        vocab_file = temp.name
    
    # Test saving
    print(f"\nSaving vocabulary to: {vocab_file}")
    tokenizer.save_vocabulary(vocab_file)
    
    # Test loading with a new tokenizer
    print("\nLoading vocabulary into a new tokenizer instance...")
    new_tokenizer = BPETokenizer(debug=True)
    
    try:
        # This is the part that was failing before our fix
        new_tokenizer.load_vocabulary(vocab_file)
        
        # Verify the loaded vocabulary
        print("\n--- Verification ---")
        orig_stats = tokenizer.get_vocabulary_stats()
        new_stats = new_tokenizer.get_vocabulary_stats()
        
        print(f"Original vocabulary size: {orig_stats['vocab_size']}")
        print(f"Loaded vocabulary size: {new_stats['vocab_size']}")
        print(f"Vocabularies match: {orig_stats['vocab_size'] == new_stats['vocab_size']}")
        
        # Check a sample of tokens
        token_ids_to_check = [97, 256, tokenizer.next_token_id - 1]  # 'a', first learned token, last token
        print("\nVerifying specific tokens:")
        all_match = True
        
        for token_id in token_ids_to_check:
            if token_id in tokenizer.id_to_token and token_id in new_tokenizer.id_to_token:
                orig_token = tokenizer.id_to_token[token_id]
                new_token = new_tokenizer.id_to_token[token_id]
                match = orig_token == new_token
                print(f"  Token ID {token_id}: {list(orig_token)} vs {list(new_token)} - Match: {match}")
                if not match:
                    all_match = False
            else:
                print(f"  Token ID {token_id} not found in one of the tokenizers")
                all_match = False
        
        # Final verdict
        if all_match:
            print("\n✅ SUCCESS: The bug is fixed! Vocabulary serialization works correctly.")
        else:
            print("\n❌ ERROR: There are still issues with vocabulary serialization.")
            
    except Exception as e:
        print(f"\n❌ ERROR: Failed to load vocabulary: {e}")
        raise

if __name__ == "__main__":
    test_vocabulary_serialization()