# Byte Pair Encoding (BPE) Tokenizer

This repository contains an educational, monolithic implementation of the Byte Pair Encoding (BPE) algorithm for tokenization, implemented as a Jupyter notebook. This project is inspired by Andrej Karpathy's minbpe and focuses on clarity and learning progression.

## Algorithm Overview

Byte Pair Encoding (BPE) is a data compression and tokenization technique that:

1. Starts with a vocabulary of single bytes (0-255)
2. Iteratively finds the most frequent adjacent token pairs
3. Merges these pairs to create new tokens
4. Continues until a desired vocabulary size is reached
5. Uses this vocabulary to encode and decode text

## Features

- Monolithic implementation with all functionality in one notebook
- Comprehensive step-by-step explanations
- Visualizations of the tokenization process
- Performance metrics and benchmarks
- Full test cases for all components
- Educational focus with clear documentation

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

## Example

```python
# Basic usage of the base tokenizer
tokenizer = Tokenizer()
tokenizer.train(training_text, vocab_size=500)

# Encode text to token IDs
token_ids = tokenizer.encode("Hello, world!")

# Decode token IDs back to text
decoded_text = tokenizer.decode(token_ids)

# Advanced usage with GPT4Tokenizer
gpt4_tokenizer = GPT4Tokenizer()
gpt4_tokenizer.train(training_text, vocab_size=1000)

# Encode with special tokens
tokens = gpt4_tokenizer.encode("Hello <|endoftext|> world!", allowed_special="all")

# Save and load in Karpathy-compatible format
gpt4_tokenizer.save_karpathy_format("my_tokenizer")
loaded_tokenizer = GPT4Tokenizer.load_karpathy_format("my_tokenizer.model")
```

## Dependencies

- jupyter, notebook
- numpy
- matplotlib
- regex (for advanced tokenization patterns)
- tiktoken (optional, for comparison)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.