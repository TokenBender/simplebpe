#!/usr/bin/env python
# coding: utf-8

# # minbpe: Minimal Byte Pair Encoding Tokenizer
# 
# This notebook contains a faithful implementation of Andrej Karpathy's minbpe tokenizer, emphasizing:
# - Clean, minimal code
# - Byte-level tokenization
# - Educational clarity
# 
# The implementation follows the core design philosophy of Karpathy's approach, preserving the simplicity and readability of the original.

# In[1]:


import os
import json
import time
import regex as re
from collections import Counter
from typing import List, Dict, Tuple, Optional, Set, Any, Union


# ## Base Tokenizer Implementation
# 
# We start with a basic tokenizer class that implements the core BPE algorithm without any regex-based preprocessing.

# In[2]:


class Tokenizer:
    """A minimal Byte Pair Encoding tokenizer implementation."""

    def __init__(self):
        # Initialize with the base 256 tokens (raw bytes 0-255)
        self.merges = {}  # (token1, token2) -> new_token_id 
        self.vocab = {}   # token_id -> token (bytes)
        self.vocab_size = 0
        self.special_tokens = {}

        # Pre-populate the vocabulary with the basic 256 byte tokens
        for i in range(256):
            token = bytes([i])
            self.vocab[i] = token

        self.vocab_size = 256

    def train(self, text: str, vocab_size: int, verbose: bool = False) -> None:
        """Train the tokenizer on text, extending the vocabulary to the desired size."""
        # Convert text to bytes
        text_bytes = text.encode("utf-8")
        ids = list(text_bytes)

        # Keep track of progress
        if verbose:
            print(f"Training BPE tokenizer to vocab size {vocab_size}")
            print(f"Text size: {len(text)} chars, {len(ids)} bytes")

        # Iteratively merge the most frequent pair until we reach the desired vocab size
        num_merges = vocab_size - 256
        for i in range(num_merges):
            # Count frequencies of adjacent pairs
            stats = self.get_stats(ids)
            if not stats:
                break

            # Find the most frequent pair
            pair = max(stats, key=stats.get)

            # Create a new token for this pair
            token1, token2 = pair
            new_token = self.vocab[token1] + self.vocab[token2]
            new_id = self.vocab_size

            # Add merge to our vocabulary
            self.merges[pair] = new_id
            self.vocab[new_id] = new_token
            self.vocab_size += 1

            # Apply the merge to the current token list
            ids = self.merge(ids, pair, new_id)

            # Print progress
            if verbose and i % 100 == 0:
                print(f"Merge #{i}: pair {pair} -> {new_id}, corpus now {len(ids)} tokens")

    def get_stats(self, ids: List[int]) -> Dict[Tuple[int, int], int]:
        """Count the frequencies of adjacent token pairs."""
        stats = Counter()
        for i in range(len(ids) - 1):
            pair = (ids[i], ids[i+1])
            stats[pair] += 1
        return stats

    def merge(self, ids: List[int], pair: Tuple[int, int], new_id: int) -> List[int]:
        """Replace all occurrences of a token pair with a new token ID."""
        # Create a new list for the merged result
        new_ids = []
        i = 0
        while i < len(ids):
            # If we're at the last token, just add it
            if i == len(ids) - 1:
                new_ids.append(ids[i])
                break

            # If current pair matches, merge and add the new token
            if ids[i] == pair[0] and ids[i+1] == pair[1]:
                new_ids.append(new_id)
                i += 2  # Skip both tokens
            else:
                new_ids.append(ids[i])
                i += 1  # Move to next token

        return new_ids

    def encode(self, text: str) -> List[int]:
        """Encode text to token IDs."""
        # Convert text to bytes
        text_bytes = text.encode("utf-8")
        ids = list(text_bytes)

        # Apply merges iteratively, in the order they were learned
        while len(ids) >= 2:
            # Find valid merge pairs in the current sequence
            pairs = [(ids[i], ids[i+1]) for i in range(len(ids)-1)]
            valid_pairs = [(pair, self.merges[pair]) for pair in pairs if pair in self.merges]

            # If no valid pairs, we're done
            if not valid_pairs:
                break

            # Find the pair with the lowest merge ID (first learned)
            pair, new_id = min(valid_pairs, key=lambda x: x[1])

            # Apply the merge
            ids = self.merge(ids, pair, new_id)

        return ids

    def decode(self, ids: List[int]) -> str:
        """Decode token IDs back to text."""
        # Convert token IDs to bytes
        bytes_list = []
        for token_id in ids:
            bytes_list.extend(self.vocab[token_id])

        # Convert bytes to UTF-8 text
        text = bytes(bytes_list).decode("utf-8", errors="replace")
        return text

    def save(self, file_path: str) -> None:
        """Save the tokenizer to a file."""
        # Prepare model data - convert bytes to lists for JSON serialization
        model_data = {
            "vocab_size": self.vocab_size,
            "merges": {f"{t1},{t2}": idx for (t1, t2), idx in self.merges.items()},
            "vocab": {str(i): list(t) for i, t in self.vocab.items() if i >= 256},
            "special_tokens": self.special_tokens
        }

        # Save to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(model_data, f, ensure_ascii=False, indent=2)

    def load(self, file_path: str) -> None:
        """Load a tokenizer from a file."""
        # Read the model data
        with open(file_path, 'r', encoding='utf-8') as f:
            model_data = json.load(f)

        # Reset the tokenizer
        self.__init__()

        # Load the vocabulary
        self.vocab_size = model_data["vocab_size"]

        # Add vocabulary items (skipping the base 256 bytes already initialized)
        for token_id_str, token_bytes in model_data["vocab"].items():
            token_id = int(token_id_str)
            self.vocab[token_id] = bytes(token_bytes)

        # Load merges
        for pair_str, idx in model_data["merges"].items():
            t1, t2 = map(int, pair_str.split(","))
            self.merges[(t1, t2)] = idx

        # Load special tokens
        self.special_tokens = model_data.get("special_tokens", {})

    def token_to_str(self, token_id: int) -> str:
        """Get a string representation of a token for visualization."""
        token_bytes = self.vocab[token_id]
        # Try to convert to UTF-8 string if possible
        try:
            s = token_bytes.decode('utf-8')
            # Replace newlines, tabs, etc. for display
            s = s.replace('\n', '\\n').replace('\t', '\\t')
            if len(s.strip()) == 0:
                # If it's all whitespace, show hex
                return f"[hex: {token_bytes.hex()}]"
            return s
        except UnicodeDecodeError:
            # If not a valid UTF-8 string, show hex
            return f"[hex: {token_bytes.hex()}]"

    def print_vocab(self, n=50) -> None:
        """Print the first n tokens in the vocabulary for inspection."""
        ids = sorted(self.vocab.keys())
        skipped = max(0, len(ids) - n)
        print(f"Vocabulary size: {len(ids)} tokens")
        print(f"Showing first {min(n, len(ids))} tokens:")
        for i, token_id in enumerate(ids[:n]):
            s = self.token_to_str(token_id)
            print(f"Token {token_id}: {s}")
        if skipped > 0:
            print(f"... and {skipped} more tokens")


# ## Testing the Tokenizer
# 
# Let's test our implementation with a simple example text.

# In[3]:


# Create a simple training corpus
training_text = """
Byte Pair Encoding (BPE) is a data compression technique that iteratively replaces the most frequent pair of consecutive bytes in a sequence with a single, unused byte. In NLP, it is used as a subword tokenization algorithm.

The BPE algorithm works as follows:
1. Initialize the vocabulary with individual characters/bytes
2. Count all pairs of adjacent symbols in the training corpus
3. Merge the most frequent pair and add it to the vocabulary
4. Repeat steps 2-3 until reaching the desired vocabulary size

BPE can handle out-of-vocabulary words by splitting them into known subword units, making it effective for various languages and even emoji 👍🌍.
"""

# Initialize our tokenizer
tokenizer = Tokenizer()

# Train to a vocabulary size of 500
tokenizer.train(training_text, vocab_size=500, verbose=True)

# Show some of the learned tokens
tokenizer.print_vocab(30)


# ## Encoding and Decoding
# 
# Now let's test encoding and decoding to verify the tokenizer works as expected.

# In[4]:


# Test with a new sentence
test_text = "BPE tokenization works great for natural language processing!"

# Encode the text
encoded = tokenizer.encode(test_text)
print(f"Encoded into {len(encoded)} tokens: {encoded}")

# Display each token
print("\nToken breakdown:")
for i, token_id in enumerate(encoded):
    print(f"Token {i+1}: ID {token_id} = '{tokenizer.token_to_str(token_id)}'")

# Decode the tokens back to text
decoded = tokenizer.decode(encoded)
print(f"\nDecoded text: '{decoded}'")
print(f"Round trip success: {test_text == decoded}")


# ## Measuring Tokenization Efficiency
# 
# Let's compute some metrics on the tokenization efficiency.

# In[5]:


def measure_efficiency(tokenizer, texts):
    """Measure tokenization efficiency across multiple text samples."""
    results = []
    for name, text in texts.items():
        # Tokenize and measure
        start_time = time.time()
        tokens = tokenizer.encode(text)
        encode_time = time.time() - start_time

        start_time = time.time()
        decoded = tokenizer.decode(tokens)
        decode_time = time.time() - start_time

        # Calculate metrics
        char_count = len(text)
        token_count = len(tokens)
        compression_ratio = char_count / token_count
        chars_per_second = char_count / encode_time if encode_time > 0 else 0

        # Store results
        results.append({
            "name": name,
            "chars": char_count,
            "tokens": token_count,
            "ratio": compression_ratio,
            "encode_time": encode_time,
            "decode_time": decode_time,
            "chars_per_second": chars_per_second,
            "roundtrip_success": text == decoded
        })

    # Print results table
    print(f"{'Text':<15} | {'Chars':<8} | {'Tokens':<8} | {'Ratio':<7} | {'Encode (s)':<10} | {'Decode (s)':<10} | {'Success':<7}")
    print("-" * 75)
    for r in results:
        print(f"{r['name']:<15} | {r['chars']:<8} | {r['tokens']:<8} | {r['ratio']:<7.2f} | {r['encode_time']:<10.4f} | {r['decode_time']:<10.4f} | {r['roundtrip_success']}")

    return results

# Define test texts
test_texts = {
    "English": "The quick brown fox jumps over the lazy dog.",
    "Repeated": "hello hello hello hello hello hello hello",
    "Numbers": "1234567890 1234567890 1234567890",
    "Technical": "def factorial(n): return 1 if n <= 1 else n * factorial(n-1)",
    "Emoji": "🙂 🌍 🚀 👨‍👩‍👧‍👦 🎉",
    "Mixed": "Training at 3.5x speed: 😊 快速训练！速度提高"
}

# Measure tokenization efficiency
efficiency_results = measure_efficiency(tokenizer, test_texts)


# ## Visualizing Tokenization Process
# 
# Let's create a visualization of how text gets split into tokens.

# In[6]:


def visualize_tokenization(tokenizer, text):
    """Visualize how text is tokenized by showing token boundaries."""
    # Encode the text
    ids = tokenizer.encode(text)

    # Get the bytes for each token
    token_bytes = [tokenizer.vocab[id] for id in ids]

    # Try to display each token as text
    visualized = []
    for token in token_bytes:
        try:
            token_text = token.decode('utf-8')
            # Replace whitespace for visibility
            token_text = token_text.replace(' ', '␣').replace('\n', '\\n').replace('\t', '\\t')
            visualized.append(token_text)
        except UnicodeDecodeError:
            # If not a valid UTF-8 sequence, show hex
            visualized.append(f"[{token.hex()}]")

    # Display with token boundaries
    print(f"Tokenized into {len(ids)} tokens:")
    result = ""
    for token in visualized:
        result += f"[{token}]"
    print(result)

    # Display each token with its ID
    print("\nDetailed token breakdown:")
    for i, (id, vis) in enumerate(zip(ids, visualized)):
        print(f"Token {i+1}: ID {id} = '{vis}'")

    return visualized

# Visualize tokenization for a sample text
sample_text = "Hello, world! This is a test of BPE tokenization."
tokens_visualized = visualize_tokenization(tokenizer, sample_text)


# ## Saving and Loading the Tokenizer
# 
# Let's test the serialization and deserialization of our tokenizer.

# In[7]:


# Save the tokenizer
tokenizer.save("bpe_tokenizer.json")
print(f"Saved tokenizer with {tokenizer.vocab_size} tokens")

# Create a new tokenizer and load the saved model
new_tokenizer = Tokenizer()
new_tokenizer.load("bpe_tokenizer.json")
print(f"Loaded tokenizer with {new_tokenizer.vocab_size} tokens")

# Verify the loaded tokenizer works the same
check_text = "Testing if the loaded tokenizer works correctly."
original_tokens = tokenizer.encode(check_text)
loaded_tokens = new_tokenizer.encode(check_text)

print(f"Original tokenizer: {len(original_tokens)} tokens")
print(f"Loaded tokenizer: {len(loaded_tokens)} tokens")
print(f"Tokens match: {original_tokens == loaded_tokens}")


# ## Regex-Based Tokenizer
# 
# For more efficient tokenization in natural language processing, we can implement a regex-based pre-tokenization step before applying BPE merges. This helps the tokenizer better handle natural language boundaries like words and numbers.

# In[8]:


class RegexTokenizer(Tokenizer):
    """Enhanced tokenizer with regex-based pre-tokenization."""

    def __init__(self):
        super().__init__()
        self.pat = re.compile(r'(\s+|[a-zA-Z]+|[0-9]+|\S)')
        # Ensure all parent class attributes are present
        self.merges = {}  # (token1, token2) -> new_token_id 
        self.vocab = {}   # token_id -> token (bytes)
        self.token_to_id = {}  # token (bytes) -> token_id
        self.vocab_size = 256

        # Pre-populate the vocabulary with the basic 256 byte tokens
        for i in range(256):
            token = bytes([i])
            self.vocab[i] = token
            self.token_to_id[token] = i

    def encode(self, text):
        """Override encode to use regex-based pre-tokenization."""
        # First split using regex pattern
        parts = [part.encode('utf-8') for part in re.findall(self.pat, text)]

        # Then encode each part with the base tokenizer
        ids = []
        for part in parts:
            # Convert to bytes and start with raw byte tokens
            bytes_list = list(part)
            tokens = [bytes([b]) for b in bytes_list]

            # Apply merges iteratively, as in the base class
            while len(tokens) >= 2:
                # Find valid merge pairs in the current sequence
                pairs = [(tokens[i], tokens[i+1]) for i in range(len(tokens)-1)]
                valid_pairs = [(pair, self.merges[pair]) for pair in pairs if pair in self.merges]

                # If no valid pairs, we're done
                if not valid_pairs:
                    break

                # Find the pair with the lowest merge ID (first learned)
                pair, new_id = min(valid_pairs, key=lambda x: x[1])

                # Apply the merge
                tokens = self.merge(tokens, pair, new_id)

            # Map tokens to IDs
            ids.extend([self.token_to_id[token] for token in tokens])

        return ids


# ## Special Tokens Support
# 
# Let's enhance our tokenizer to support special tokens, similar to GPT models.

# In[9]:


class SpecialTokensTokenizer(Tokenizer):
    """Enhanced tokenizer with support for special tokens."""

    def __init__(self, special_tokens=None):
        super().__init__()
        # Initialize special tokens dict
        self.special_tokens_dict = {}  # str -> id
        self.special_tokens_inv = {}   # id -> str

        # Add special tokens if provided
        if special_tokens:
            self.add_special_tokens(special_tokens)

    def add_special_tokens(self, tokens_dict):
        """
        Add special tokens to the tokenizer.
        Args:
            tokens_dict: Dictionary mapping token strings to their desired IDs
                         e.g., {'<|endoftext|>': 100257}
        """
        for token, idx in tokens_dict.items():
            # Make sure ID doesn't conflict with existing vocab
            if idx in self.vocab:
                raise ValueError(f"ID {idx} already exists in vocabulary")

            # Add to vocab and special tokens dictionaries
            token_bytes = token.encode('utf-8')
            self.vocab[idx] = token_bytes
            self.special_tokens_dict[token] = idx
            self.special_tokens_inv[idx] = token

            # Update vocab size if necessary
            self.vocab_size = max(self.vocab_size, idx + 1)

    def encode(self, text, allowed_special=None):
        """
        Encode text with special token handling.

        Args:
            text: The text to encode
            allowed_special: Set of special tokens to recognize, or "all" for all tokens
        """
        # Handle allowed_special parameter
        if allowed_special == "all":
            allowed_special = set(self.special_tokens_dict.keys())
        elif allowed_special is None:
            allowed_special = set()  # No special tokens allowed

        # First check for special tokens if any are allowed
        if allowed_special:
            # This is a simple greedy approach - in production you might use regex
            tokens = []
            i = 0
            while i < len(text):
                # Check if any special token starts at this position
                matched = False
                for special in allowed_special:
                    if text[i:].startswith(special):
                        # Found a special token, add its ID
                        tokens.append(self.special_tokens_dict[special])
                        i += len(special)
                        matched = True
                        break

                if not matched:
                    # No special token matched, process normally
                    # Find the longest non-special token sequence
                    j = i
                    while j < len(text) and not any(text[j:].startswith(s) for s in allowed_special):
                        j += 1

                    # Encode this chunk normally
                    if j > i:
                        chunk_ids = super().encode(text[i:j])
                        tokens.extend(chunk_ids)
                        i = j

            return tokens
        else:
            # No special tokens, encode normally
            return super().encode(text)

    def save(self, file_path):
        """Save with special tokens information."""
        # Start with base functionality
        super().save(file_path)

        # Add special tokens to the saved data
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Add special tokens dict
        data['special_tokens_dict'] = self.special_tokens_dict

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load(self, file_path):
        """Load with special tokens information."""
        super().load(file_path)

        # Load special tokens if available
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if 'special_tokens_dict' in data:
            self.special_tokens_dict = data['special_tokens_dict']
            self.special_tokens_inv = {v: k for k, v in self.special_tokens_dict.items()}


# In[10]:


# Test special tokens support
# Create common GPT-style special tokens
special_tokens = {
    '<|endoftext|>': 100257,
    '<|fim_prefix|>': 100258,
    '<|fim_middle|>': 100259,
    '<|fim_suffix|>': 100260,
    '<|endofprompt|>': 100261
}

# Create and train a tokenizer with special tokens
special_tokenizer = SpecialTokensTokenizer()
special_tokenizer.train(training_text, vocab_size=500, verbose=False)
special_tokenizer.add_special_tokens(special_tokens)

# Test encoding/decoding with special tokens
test_with_special = "Here is some text <|endoftext|> followed by a special token."
encoded_special = special_tokenizer.encode(test_with_special, allowed_special="all")
decoded_special = special_tokenizer.decode(encoded_special)

print(f"Original text: '{test_with_special}'")
print(f"Encoded with {len(encoded_special)} tokens: {encoded_special}")
print(f"Decoded: '{decoded_special}'")
print(f"Round trip success: {test_with_special == decoded_special}")

# Visualize the tokens including the special token
print("\nToken visualization:")
token_strs = []
for token_id in encoded_special:
    if token_id in special_tokenizer.special_tokens_inv:
        # This is a special token
        token_strs.append(special_tokenizer.special_tokens_inv[token_id])
    else:
        # Regular token
        token_bytes = special_tokenizer.vocab[token_id]
        try:
            token_str = token_bytes.decode('utf-8')
            token_strs.append(token_str)
        except UnicodeDecodeError:
            token_strs.append(f"[hex: {token_bytes.hex()}]")

# Print with token boundaries
result = ""
for token in token_strs:
    if token in special_tokens:
        # Highlight special tokens
        result += f"[*{token}*]"
    else:
        result += f"[{token}]"
print(result)


# ## Benchmarking Against Reference Tokenizers
# 
# Let's compare our tokenizer implementation with other popular tokenizers.

# In[11]:


# Initialize the regex tokenizer
regex_tokenizer = RegexTokenizer()
regex_tokenizer.train(training_text, vocab_size=500, verbose=False)
print("Regex tokenizer trained with vocabulary size:", len(regex_tokenizer.token_to_id))


# In[12]:


# This cell would normally import and compare with reference tokenizers
# We provide pseudocode here as an example of what you would do

"""
# You would usually import tiktoken or transformers:
# import tiktoken
# from transformers import GPT2Tokenizer

# Define benchmark texts and functions
benchmark_texts = {
    "English": "The quick brown fox jumps over the lazy dog.",
    "Code": "def factorial(n): return 1 if n <= 1 else n * factorial(n-1)",
    "Mixed": "Training at 3.5x speed 😊 быстрое обучение",
    "Repeated": "token token token token token token"
}

def benchmark_tokenizer(name, tokenizer_func, texts):
    results = []
    for text_name, text in texts.items():
        # Measure encoding time
        start_time = time.time()
        tokens = tokenizer_func(text)
        encode_time = time.time() - start_time

        results.append({
            "tokenizer": name,
            "text": text_name,
            "tokens": len(tokens),
            "encode_time_ms": encode_time * 1000
        })
    return results

# Define encoding functions for different tokenizers
def encode_with_our_tokenizer(text):
    return tokenizer.encode(text)

# def encode_with_tiktoken(text):
#     enc = tiktoken.get_encoding("gpt2")
#     return enc.encode(text)

# def encode_with_hf_tokenizer(text):
#     hf_tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
#     return hf_tokenizer.encode(text)

# Run benchmarks
our_results = benchmark_tokenizer("Our BPE", encode_with_our_tokenizer, benchmark_texts)
# tiktoken_results = benchmark_tokenizer("tiktoken", encode_with_tiktoken, benchmark_texts)
# hf_results = benchmark_tokenizer("HuggingFace", encode_with_hf_tokenizer, benchmark_texts)

# all_results = our_results + tiktoken_results + hf_results
all_results = our_results

# Display results in a table
print(f"{'Tokenizer':<15} | {'Text':<10} | {'Tokens':<8} | {'Time (ms)':<10}")
print("-" * 50)
for r in all_results:
    print(f"{r['tokenizer']:<15} | {r['text']:<10} | {r['tokens']:<8} | {r['encode_time_ms']:<10.2f}")

# Here you would normally create visualization comparing the tokenizers
"""

# For now, we'll just run a simple benchmark on our own tokenizer
benchmark_texts = {
    "English": "The quick brown fox jumps over the lazy dog.",
    "Code": "def factorial(n): return 1 if n <= 1 else n * factorial(n-1)",
    "Mixed": "Training at 3.5x speed 😊 快速训练！",
    "Repeated": "token token token token token token"
}

def benchmark_our_tokenizers(texts):
    results = []
    tokenizers = {
        "Basic BPE": tokenizer,
        "Regex BPE": regex_tokenizer,
        "Special BPE": special_tokenizer
    }

    for name, tkn in tokenizers.items():
        for text_name, text in texts.items():
            # Measure encoding time
            start_time = time.time()

            # For special tokenizer, specify allowed_special
            if name == "Special BPE":
                tokens = tkn.encode(text, allowed_special="all")
            else:
                tokens = tkn.encode(text)

            encode_time = time.time() - start_time

            results.append({
                "tokenizer": name,
                "text": text_name,
                "tokens": len(tokens),
                "encode_time_ms": encode_time * 1000
            })
    return results

results = benchmark_our_tokenizers(benchmark_texts)

# Display results in a table
print(f"{'Tokenizer':<15} | {'Text':<10} | {'Tokens':<8} | {'Time (ms)':<10}")
print("-" * 50)
for r in results:
    print(f"{r['tokenizer']:<15} | {r['text']:<10} | {r['tokens']:<8} | {r['encode_time_ms']:<10.2f}")


# In[13]:


# Train the regex tokenizer first
regex_tokenizer = RegexTokenizer()
regex_tokenizer.train(training_text, vocab_size=500, verbose=False)

# Now we can do benchmarking
benchmark_texts = {
    "English": "The quick brown fox jumps over the lazy dog.",
    "Code": "def factorial(n): return 1 if n <= 1 else n * factorial(n-1)",
    "Mixed": "Training at 3.5x speed 😊 快速训练！",
    "Repeated": "token token token token token token"
}

def benchmark_our_tokenizers(texts):
    results = []
    tokenizers = {
        "Basic BPE": tokenizer,
        "Regex BPE": regex_tokenizer,
        "Special BPE": special_tokenizer
    }

    for name, tkn in tokenizers.items():
        for text_name, text in texts.items():
            # Measure encoding time
            start_time = time.time()

            # For special tokenizer, specify allowed_special
            if name == "Special BPE":
                tokens = tkn.encode(text, allowed_special="all")
            else:
                tokens = tkn.encode(text)

            encode_time = time.time() - start_time

            results.append({
                "tokenizer": name,
                "text": text_name,
                "tokens": len(tokens),
                "encode_time_ms": encode_time * 1000
            })
    return results

results = benchmark_our_tokenizers(benchmark_texts)

# Display results in a table
print(f"{'Tokenizer':<15} | {'Text':<10} | {'Tokens':<8} | {'Time (ms)':<10}")
print("-" * 50)
for r in results:
    print(f"{r['tokenizer']:<15} | {r['text']:<10} | {r['tokens']:<8} | {r['encode_time_ms']:<10.2f}")


# ## Enhanced Token Visualization
# 
# Let's improve our token visualization to better illustrate token boundaries and include additional token information.

# ## Testing the Regex Tokenizer
# 
# Let's compare the basic tokenizer with our regex-based tokenizer to see the differences.

# In[14]:


# Compare with the basic tokenizer
compare_text = "It's not just tokenization, it's BPE tokenization with regex pre-processing!"

basic_tokens = tokenizer.encode(compare_text)
regex_tokens = regex_tokenizer.encode(compare_text)

print(f"Basic tokenizer: {len(basic_tokens)} tokens")
print(f"Regex tokenizer: {len(regex_tokens)} tokens")

# Visualize the differences
print("\nBasic tokenization:")
visualize_tokenization(tokenizer, compare_text)

print("\nRegex tokenization:")
visualize_tokenization(regex_tokenizer, compare_text)


# ## Testing the Regex Tokenizer

# In[15]:


# Train the regex tokenizer
regex_tokenizer = RegexTokenizer()
regex_tokenizer.train(training_text, vocab_size=500, verbose=True)

# Compare with the basic tokenizer
compare_text = "It's not just tokenization, it's BPE tokenization with regex pre-processing!"

basic_tokens = tokenizer.encode(compare_text)
regex_tokens = regex_tokenizer.encode(compare_text)

print(f"Basic tokenizer: {len(basic_tokens)} tokens")
print(f"Regex tokenizer: {len(regex_tokens)} tokens")

# Visualize the differences
print("\nBasic tokenization:")
visualize_tokenization(tokenizer, compare_text)

print("\nRegex tokenization:")
visualize_tokenization(regex_tokenizer, compare_text)

