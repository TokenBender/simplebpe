## needs clean up, incomplete


# Byte Pair Encoding (BPE) Tokenizer

This repository contains an educational, comprehensive implementation of the Byte Pair Encoding (BPE) algorithm for tokenization, implemented as Jupyter notebooks with full parity to Andrej Karpathy's minbpe. The project focuses on clarity, educational value, and practical application.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Jupyter Notebook](https://img.shields.io/badge/jupyter-%23FA0F00.svg?logo=jupyter&logoColor=white)](https://jupyter.org/)

## Algorithm Overview

Byte Pair Encoding (BPE) is a data compression and tokenization technique that:

1. Starts with a vocabulary of single bytes (0-255)
2. Iteratively finds the most frequent adjacent token pairs
3. Merges these pairs to create new tokens
4. Continues until a desired vocabulary size is reached
5. Uses this vocabulary to encode and decode text

## Features

The repository offers a comprehensive implementation of BPE tokenization with:

### Core Features
- Educational implementation with step-by-step explanations
- Multiple tokenizer variants with increasing sophistication
- Visualizations for tokenization process and vocabulary analysis
- Performance metrics and benchmarking across tokenizer types
- Full test suite with edge case handling

### Advanced Features
- **GPT2/GPT4 Pattern Splitting**: Advanced regex patterns for better tokenization boundaries
- **Special Token Handling**: Support for model-specific tokens with configurable behavior
- **Byte Shuffling**: Enhanced handling of multilingual content through byte permutation
- **Karpathy-Compatible Format**: Save/load in the same format as the original minbpe
- **Unicode Edge Case Testing**: Comprehensive testing for complex scripts and emoji

### Available Tokenizers
1. **Base Tokenizer**: Simple BPE algorithm implementation
2. **RegexTokenizer**: Enhanced with pattern-based pre-tokenization
3. **SpecialTokensTokenizer**: Adds support for special tokens like `<|endoftext|>`
4. **GPT4Tokenizer**: Complete implementation with byte shuffling for tiktoken compatibility

## Installation

Clone the repository and install the required dependencies:

```bash
git clone https://github.com/TokenBender/simplebpe.git
cd simplebpe
pip install -r requirements.txt
```

## Usage

Run the Jupyter notebooks to explore the BPE tokenizer implementations:

```bash
jupyter notebook
```

### BPE Tokenizer Notebook (Educational Implementation)

The `bpe_tokenizer.ipynb` notebook is structured into the following main sections:

1. Byte-Level Tokenization
2. Pair Frequency Counter
3. Merge Operations
4. Vocabulary Management
5. Encode and Decode Functions
6. Visualizations
7. Performance Metrics
8. Test Cases

Each section includes both explanation and implementation, followed by test cells to verify functionality.

### minbpe Notebook (Karpathy-style Implementation)

The `minbpe.ipynb` notebook provides a clean, minimal implementation inspired by Andrej Karpathy's minbpe approach:

1. Base Tokenizer Implementation
2. Training Algorithm
3. Encoding and Decoding Functions
4. Tokenization Efficiency Metrics
5. Visualization Tools
6. Advanced Features:
   - Regex Pre-tokenization with GPT2/GPT4 Patterns
   - Special Token Handling with configurable allowed_special parameter
   - GPT4Tokenizer with byte shuffling for improved multilingual support
   - Compatible Save/Load functionality in Karpathy's format
   - Comprehensive benchmarking and edge case testing

This implementation focuses on simplicity and readability while maintaining the essential functionality of a BPE tokenizer.

## Examples

### Basic Usage

```python
# Basic usage of the base tokenizer
from minbpe import Tokenizer

# Create a tokenizer and train it
tokenizer = Tokenizer()
tokenizer.train(training_text, vocab_size=500)

# Encode text to token IDs
token_ids = tokenizer.encode("Hello, world!")
print(f"Encoded: {token_ids}")
# Output: [72, 101, 108, 108, 111, 44, 32, 119, 111, 114, 108, 100, 33]

# Decode token IDs back to text
decoded_text = tokenizer.decode(token_ids)
print(f"Decoded: {decoded_text}")
# Output: "Hello, world!"
```

### Advanced Usage with GPT4Tokenizer

```python
from minbpe import GPT4Tokenizer

# Create and train a GPT4Tokenizer
gpt4_tokenizer = GPT4Tokenizer()
gpt4_tokenizer.train(training_text, vocab_size=1000)

# Handle special tokens with various options
text_with_special = "Prompt: <|endoftext|> Generate a story."

# Option 1: Allow all special tokens
tokens_all = gpt4_tokenizer.encode(text_with_special, allowed_special="all")

# Option 2: Allow only specific special tokens
tokens_some = gpt4_tokenizer.encode(text_with_special, 
                                   allowed_special={"<|endoftext|>"})

# Option 3: Encode without special tokens (treat as normal text)
tokens_none = gpt4_tokenizer.encode(text_with_special, allowed_special="none")
```

### Serialization and Deserialization

```python
# Save and load using Karpathy-compatible format
gpt4_tokenizer.save_karpathy_format("my_tokenizer")
# Creates: my_tokenizer.model (for loading) and my_tokenizer.vocab (for inspection)

# Load from saved model
loaded_tokenizer = GPT4Tokenizer.load_karpathy_format("my_tokenizer.model")

# Verify identical behavior
original_tokens = gpt4_tokenizer.encode("Test text", allowed_special="all")
loaded_tokens = loaded_tokenizer.encode("Test text", allowed_special="all")
assert original_tokens == loaded_tokens
```

## Project Structure

The repository is organized as follows:

```
tokenizer_from_scratch/
├── bpe_tokenizer.ipynb     # Educational monolithic implementation
├── minbpe.ipynb           # Clean implementation with full Karpathy parity
├── minbpe.py              # Module version for easy import
├── requirements.txt       # Project dependencies
├── test_bpe_fix.py        # Test suite for BPE implementation
├── test_notebook.py       # Test notebook execution integrity
├── PR.md                  # Requirement tracking document
├── KNOWN_ISSUES.md        # Bug tracking and resolutions
└── CLAUDE.md              # Development guidelines
```

## Dependencies

- **Required**:
  - `jupyter`: Interactive notebook environment (>= 1.0.0)
  - `numpy`: Numerical computing library (>= 1.20.0)
  - `matplotlib`: Visualization library (>= 3.4.0)
  - `regex`: Enhanced regular expression support (>= 2022.1.18)

- **Optional**:
  - `tiktoken`: OpenAI's tokenizer library for comparison (>= 0.3.0)

## Benchmarks

The tokenizer implementations have been benchmarked against various text types:

| Tokenizer Type | English | Code | Multilingual | Emoji | Special Tokens |
|----------------|---------|------|--------------|-------|----------------|
| Basic          | Fast    | Good | Limited      | Fair  | Not supported  |
| Regex          | Fast    | Good | Good         | Good  | Not supported  |
| SpecialTokens  | Fast    | Good | Good         | Good  | Supported      |
| GPT4           | Fast    | Good | Excellent    | Excellent | Full support |

## Known Limitations

There are some known limitations with Unicode edge cases, particularly:
- Complex bidirectional text (mixed RTL/LTR scripts)
- Some emoji sequences with zero-width joiners
- Certain combining characters

See KNOWN_ISSUES.md for details on these limitations and potential solutions.

## Contributing

Contributions are welcome! Please follow these steps:

1. Check the issue tracker for open issues
2. Fork the repository
3. Create a feature branch (`git checkout -b feature/amazing-feature`)
4. Commit your changes following the protocol in CLAUDE.md
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- Andrej Karpathy for the [minbpe](https://github.com/karpathy/minbpe) implementation
- OpenAI for the [tiktoken](https://github.com/openai/tiktoken) library and tokenizer designs
- The research community for BPE algorithm improvements
