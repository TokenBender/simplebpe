# Byte Pair Encoding (BPE) Algorithm

This repository contains an implementation of the Byte Pair Encoding (BPE) algorithm, a data compression technique that iteratively replaces the most frequent pair of bytes in a sequence with a single, unused byte.

## Algorithm Overview

The BPE algorithm follows these steps:

1. Identify the most frequent pairs of characters/bytes in the text.
2. Replace the most frequent pair with a new unique token and add this mapping to a lookup table.
3. Repeat steps 1 and 2 until a predefined vocabulary size is reached.
4. Use the generated lookup table to tokenize input text.
5. Decode the tokenized text back to the original text using the lookup table.

## Usage

[Instructions on how to use the implementation will be added here]

## License

[License information will be added here]