import heapq
import os

class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq
    

def ReadBitSequence(file, num_bits):
    bit_buffer = 0
    bit_count = 0

    while bit_count < num_bits:
        if bit_count == 0:
            byte = file.read(1)
            if not byte:
                break  
            bit_buffer = byte[0]

        current_bit = (bit_buffer >> (7 - bit_count)) & 1
        bit_count += 1
        yield current_bit

def WriteBitSequence(file, bit_sequence):
    bit_buffer = 0
    bit_count = 0

    for bit in bit_sequence:
        bit_buffer = (bit_buffer << 1) | bit
        bit_count += 1

        if bit_count == 8:
            file.write(bit_buffer.to_bytes(1, byteorder='big'))
            bit_buffer = 0
            bit_count = 0

    if bit_count > 0:
        file.write((bit_buffer << (8 - bit_count)).to_bytes(1, byteorder='big'))



def build_huffman_tree(frequencies):
    heap = [HuffmanNode(char, freq) for char, freq in enumerate(frequencies) if freq > 0]
    heapq.heapify(heap)

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = HuffmanNode(None, left.freq + right.freq)
        merged.left = left
        merged.right = right
        heapq.heappush(heap, merged)

    return heap[0]

def build_huffman_codes(node, code, codes):
    if node.char is not None:
        codes[node.char] = code
    if node.left is not None:
        build_huffman_codes(node.left, code + '0', codes)
    if node.right is not None:
        build_huffman_codes(node.right, code + '1', codes)

def encode(input_path, output_path):
    frequencies = [0] * 256

    with open(input_path, 'rb') as file:
        byte = file.read(1)
        while byte:
            frequencies[byte[0]] += 1
            byte = file.read(1)

    root = build_huffman_tree(frequencies)
    codes = {}
    build_huffman_codes(root, '', codes)

    with open(output_path, 'wb') as output_file, open(input_path, 'rb') as input_file:
        
        for freq in frequencies:
            output_file.write(freq.to_bytes(4, byteorder='big'))

        
        bit_buffer = 0
        bit_count = 0
        byte = input_file.read(1)
        while byte:
            code = codes[byte[0]]
            for bit in code:
                bit_buffer = (bit_buffer << 1) | int(bit)  
                bit_count += 1
                if bit_count == 8:
                    output_file.write(bit_buffer.to_bytes(1, byteorder='big'))
                    bit_buffer = 0
                    bit_count = 0
            byte = input_file.read(1)

        
        if bit_count > 0:
            output_file.write((bit_buffer << (8 - bit_count)).to_bytes(1, byteorder='big'))


def decode(input_path, output_path):
    frequencies = []

    with open(input_path, 'rb') as file:
  
        for _ in range(256):
            freq_bytes = file.read(4)
            freq = int.from_bytes(freq_bytes, byteorder='big')
            frequencies.append(freq)

        root = build_huffman_tree(frequencies)
        current_node = root

        with open(output_path, 'wb') as output_file:
            byte = file.read(1)
            while byte:
                for i in range(8):
                    current_bit = (byte[0] >> (7 - i)) & 1

                    if current_bit == 0:
                        current_node = current_node.left
                    elif current_bit == 1:
                        current_node = current_node.right

                    if current_node.char is not None:
                        output_file.write(bytes([current_node.char]))
                        current_node = root

                byte = file.read(1)


if __name__ == '__main__':
    input_file_path = 'input.txt'
    compressed_file_path = 'compressed.huf'
    decompressed_file_path = 'decompressed.txt'

    # Encoding
    encode(input_file_path, compressed_file_path)

    # Decoding
    decode(compressed_file_path, decompressed_file_path)