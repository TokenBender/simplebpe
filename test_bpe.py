#!/usr/bin/env python3
"""
Tests for the BPE implementation
"""

import unittest
from bpe import BPETokenizer


class TestBPETokenizer(unittest.TestCase):
    
    def test_basic_tokenization(self):
        # Simple test case
        text = "hello world"
        tokenizer = BPETokenizer(vocab_size=20)
        tokenizer.train(text)
        
        # Tokenize the same text
        tokens = tokenizer.tokenize(text)
        
        # Decode should match the original
        decoded = tokenizer.decode(tokens)
        self.assertEqual(text, decoded)
    
    def test_merges(self):
        # Test that merges are happening
        text = "aaabdaaabac"
        tokenizer = BPETokenizer(vocab_size=15)
        tokenizer.train(text)
        
        # The pair 'aa' should be merged
        self.assertTrue(('a', 'a') in tokenizer.merges)
        
        # Vocabulary should contain 'aa'
        self.assertTrue('aa' in tokenizer.vocab)
    
    def test_unknown_tokens(self):
        # Train on one text
        train_text = "hello world"
        tokenizer = BPETokenizer(vocab_size=20)
        tokenizer.train(train_text)
        
        # Test on text with unknown characters
        test_text = "hello universe"
        tokens = tokenizer.tokenize(test_text)
        decoded = tokenizer.decode(tokens)
        
        # The known parts should be decoded correctly
        self.assertTrue("hello" in decoded)


if __name__ == "__main__":
    unittest.main()