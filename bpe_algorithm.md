## Description of Byte Pair Encoding (BPE) Algorithm

* step 1 - identify the most frequent pairs of characters/bytes in the text.
* step 2 - replace the most frequent pair of characters/bytes with a new unique token. add this token and pair mapping to a lookup table.
* step 3 - repeat steps 1 and 2 until a predefined vocabulary size is reached.
* step 4 - use the generated lookup table to tokenize the input text.
* step 5 - decode the tokenized text back to the original text using the lookup table.