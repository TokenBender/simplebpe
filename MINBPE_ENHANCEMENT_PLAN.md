# minbpe Enhancement Plan

This document outlines a concrete plan to enhance our minbpe.ipynb implementation to align more closely with Karpathy's original implementation while maintaining our monolithic educational approach.

## 1. RegexTokenizer Enhancements

### Current Limitations
- Basic pattern `r'(\s+|[a-zA-Z]+|[0-9]+|\S)'` lacks sophistication
- No configurable pattern in constructor
- Missing compatibility with GPT patterns

### Implementation Plan
1. Update RegexTokenizer to accept pattern in constructor
2. Add GPT2 and GPT4 patterns as constants:
   ```python
   GPT2_SPLIT_PATTERN = r"""'(?:[sdmt]|ll|ve|re)| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""
   GPT4_SPLIT_PATTERN = r"""'(?i:[sdmt]|ll|ve|re)|[^\r\n\p{L}\p{N}]?+\p{L}+|\p{N}{1,3}| ?[^\s\p{L}\p{N}]++[\r\n]*|\s*[\r\n]|\s+(?!\S)|\s+"""
   ```
3. Improve encoding/decoding with regex pattern splitting

## 2. Special Token Handling

### Current Limitations
- Special token handling is basic
- Lacks `allowed_special` parameter options
- No explicit error handling for special tokens

### Implementation Plan
1. Update SpecialTokensTokenizer with better API:
   ```python
   def register_special_tokens(self, special_tokens_dict):
       # Update token_to_id and id_to_token with special tokens
   ```
2. Enhance encode method with allowed_special parameter:
   ```python
   def encode(self, text, allowed_special="none_raise"):
       # Support "all", "none", "none_raise", or a set of tokens
   ```
3. Add clear error handling for special tokens

## 3. GPT4Tokenizer Implementation

### Current Limitations
- No equivalent to Karpathy's GPT4Tokenizer
- Missing byte shuffling mechanism
- No tiktoken compatibility

### Implementation Plan
1. Add GPT4Tokenizer class that inherits from RegexTokenizer:
   ```python
   class GPT4Tokenizer(RegexTokenizer):
       def __init__(self):
           super().__init__(pattern=GPT4_SPLIT_PATTERN)
           # Add byte shuffling setup
   ```
2. Implement byte shuffling mechanism:
   ```python
   # In encode
   def _encode_chunk(self, text_bytes):
       # Apply byte shuffle before encoding
       
   # In decode
   def decode(self, ids):
       # Apply inverse byte shuffle after decoding
   ```
3. Add method to recover merges from tiktoken (optional)

## 4. Save/Load Functionality

### Current Limitations
- Different format from Karpathy's implementation
- Not compatible with his model/vocab file structure

### Implementation Plan
1. Update save method to create .model and .vocab files:
   ```python
   def save(self, file_prefix):
       # Write model file with headers and merges
       # Write vocab file for human inspection
   ```
2. Update load method to read from .model file:
   ```python
   def load(self, model_file):
       # Parse headers and reconstruct tokenizer
   ```

## 5. Testing and Validation

### Necessary Tests
1. Test regex tokenization with GPT patterns
2. Validate special token handling in various scenarios
3. Compare outputs with tiktoken for identical inputs
4. Verify save/load functionality

### Implementation Plan
1. Add test cells for each component
2. Add comparison with tiktoken (if available):
   ```python
   import tiktoken
   enc = tiktoken.get_encoding("cl100k_base")
   tiktoken_tokens = enc.encode("test string with emoji 😊")
   our_tokens = gpt4_tokenizer.encode("test string with emoji 😊")
   print(f"Match: {tiktoken_tokens == our_tokens}")
   ```

## 6. Documentation Updates

### Implementation Plan
1. Add detailed explanation of regex patterns
2. Document special token handling
3. Add GPT4 compatibility notes
4. Update visualization to show regex boundaries

## 7. Timeline

1. RegexTokenizer Enhancements - Day 1
2. Special Token Handling - Day 1
3. GPT4Tokenizer Implementation - Day 2
4. Save/Load Functionality - Day 2
5. Testing and Validation - Day 3
6. Documentation Updates - Day 3

## 8. Success Criteria

- All core functionality matches Karpathy's implementation
- GPT4Tokenizer produces identical output to tiktoken for test cases
- Save/load functionality is compatible with Karpathy's format
- Enhanced documentation explains all implementations clearly
- All tests pass validating functionality