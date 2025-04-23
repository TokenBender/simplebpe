#!/usr/bin/env python3
"""
Byte Pair Encoding (BPE) implementation
"""

import re
from collections import Counter
from typing import Dict, List, Tuple, Set


class BPETokenizer:
    """
    A simple implementation of the Byte Pair Encoding algorithm for tokenization.
    """

    def __init__(self, vocab_size: int = 1000):
        """
        Initialize the BPE tokenizer.
        
        Args:
            vocab_size: The maximum size of the vocabulary to generate.
        """
        self.vocab_size = vocab_size
        self.merges: List[Tuple[str, str]] = []
        self.vocab: Dict[str, int] = {}
        self.inverse_vocab: Dict[int, str] = {}
        
    def _get_stats(self, words: List[List[str]]) -> Counter:
        """
        Count frequency of pairs of adjacent symbols.
        
        Args:
            words: List of tokenized words (each word is a list of characters/tokens).
            
        Returns:
            Counter with pairs and their frequencies.
        """
        pairs = Counter()
        for word in words:
            for i in range(len(word) - 1):
                pairs[(word[i], word[i + 1])] += 1
        return pairs
    
    def _merge_pair(self, pair: Tuple[str, str], words: List[List[str]]) -> List[List[str]]:
        """
        Merge all occurrences of the given pair in the list of words.
        
        Args:
            pair: The pair of tokens to merge.
            words: List of tokenized words.
            
        Returns:
            Updated list of words with the pair merged.
        """
        first, second = pair
        new_token = first + second
        new_words = []
        
        for word in words:
            i = 0
            new_word = []
            while i < len(word):
                if i < len(word) - 1 and word[i] == first and word[i + 1] == second:
                    new_word.append(new_token)
                    i += 2
                else:
                    new_word.append(word[i])
                    i += 1
            new_words.append(new_word)
            
        return new_words
    
    def train(self, text: str) -> None:
        """
        Train the BPE tokenizer on the given text.
        
        Args:
            text: The text to train on.
        """
        # Initialize vocabulary with individual characters
        unique_chars = set(text)
        self.vocab = {char: i for i, char in enumerate(unique_chars)}
        self.inverse_vocab = {i: char for char, i in self.vocab.items()}
        
        # Split text into words and initialize each word as a list of characters
        words = [[char for char in word] for word in text.split()]
        
        # Perform merges until we reach the desired vocabulary size
        while len(self.vocab) < self.vocab_size:
            pairs = self._get_stats(words)
            if not pairs:
                break
                
            # Find the most frequent pair
            best_pair = max(pairs, key=pairs.get)
            
            # Merge the pair in all words
            words = self._merge_pair(best_pair, words)
            
            # Add the new token to the vocabulary
            new_token = best_pair[0] + best_pair[1]
            self.vocab[new_token] = len(self.vocab)
            self.inverse_vocab[len(self.inverse_vocab)] = new_token
            
            # Record the merge operation
            self.merges.append(best_pair)
            
            # If we've reached the desired vocabulary size, stop
            if len(self.vocab) >= self.vocab_size:
                break
    
    def tokenize(self, text: str) -> List[int]:
        """
        Tokenize the given text using the trained BPE model.
        
        Args:
            text: The text to tokenize.
            
        Returns:
            List of token IDs.
        """
        # Split text into words and initialize each word as a list of characters
        words = [[char for char in word] for word in text.split()]
        
        # Apply the learned merges in order
        for pair in self.merges:
            words = self._merge_pair(pair, words)
        
        # Convert tokens to IDs
        token_ids = []
        for word in words:
            for token in word:
                if token in self.vocab:
                    token_ids.append(self.vocab[token])
                else:
                    # Handle unknown tokens (could be improved)
                    for char in token:
                        if char in self.vocab:
                            token_ids.append(self.vocab[char])
            
            # Add space between words (assuming space is in the vocabulary)
            if ' ' in self.vocab and word != words[-1]:
                token_ids.append(self.vocab[' '])
                
        return token_ids
    
    def decode(self, token_ids: List[int]) -> str:
        """
        Decode the given token IDs back to text.
        
        Args:
            token_ids: List of token IDs.
            
        Returns:
            Decoded text.
        """
        text = ''
        for token_id in token_ids:
            if token_id in self.inverse_vocab:
                text += self.inverse_vocab[token_id]
            
        return text


def main():
    # Example usage
    sample_text = """The Byte Pair Encoding algorithm is a simple data compression technique 
    that iteratively replaces the most frequent pair of bytes in a sequence with a single, 
    unused byte. It was first described by Philip Gage in 1994."""
    
    # Create and train the tokenizer
    tokenizer = BPETokenizer(vocab_size=200)
    tokenizer.train(sample_text)
    
    # Tokenize some text
    tokens = tokenizer.tokenize("The Byte Pair Encoding algorithm is simple.")
    print(f"Tokenized: {tokens}")
    
    # Decode the tokens back to text
    decoded = tokenizer.decode(tokens)
    print(f"Decoded: {decoded}")


if __name__ == "__main__":
    main()