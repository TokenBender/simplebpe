import tiktoken

text = 'This is a sample text'
tokenizer = tiktoken.get_encoding("gpt2")

tokenizer.encode(text)
print("Encoded tokens: {}".format(tokenizer.encode(text)))

byte_array = bytearray(text, 'utf-8')
print("Byte array: {}".format(list(byte_array)))

char_count = len(text)
token_count = len(tokenizer.encode(text))

print("Character count: {} and Token count: {}".format(char_count, token_count))