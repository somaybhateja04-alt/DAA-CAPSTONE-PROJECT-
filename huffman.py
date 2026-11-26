# Project 3: File Compression Using Huffman Coding
# Simple implementation (B.Tech 2nd year level)

import heapq
import os
import time


# ---------------------------------------------------------
# Node of the Huffman Tree
# ---------------------------------------------------------
class Node:
    def __init__(self, char, freq):
        self.char = char      # character (None for internal nodes)
        self.freq = freq      # frequency of the character
        self.left = None
        self.right = None


# ---------------------------------------------------------
# Step 1: Calculate character frequencies
# ---------------------------------------------------------
def calculate_frequencies(text):
    freq = {}
    for ch in text:
        if ch in freq:
            freq[ch] += 1
        else:
            freq[ch] = 1
    return freq


# ---------------------------------------------------------
# Step 2: Build the Huffman Tree using a min heap
# ---------------------------------------------------------
def build_tree(freq):
    heap = []
    count = 0  # tie breaker so that heap never compares Node objects
    # sorted() keeps the tree the same every time (needed for decoding)
    for ch in sorted(freq):
        heapq.heappush(heap, (freq[ch], count, Node(ch, freq[ch])))
        count += 1

    while len(heap) > 1:
        f1, _, left = heapq.heappop(heap)    # smallest
        f2, _, right = heapq.heappop(heap)   # second smallest

        parent = Node(None, f1 + f2)
        parent.left = left
        parent.right = right

        heapq.heappush(heap, (parent.freq, count, parent))
        count += 1

    return heap[0][2]   # root of the tree


# ---------------------------------------------------------
# Step 3: Generate binary codes (left = 0, right = 1)
# ---------------------------------------------------------
def generate_codes(node, current_code, codes):
    if node is None:
        return
    if node.char is not None:           # leaf node
        if current_code == "":
            current_code = "0"          # only one unique character
        codes[node.char] = current_code
        return
    generate_codes(node.left, current_code + "0", codes)
    generate_codes(node.right, current_code + "1", codes)


# ---------------------------------------------------------
# Step 4: Encoding
# ---------------------------------------------------------
def encode_text(text, codes):
    bits = ""
    for ch in text:
        bits += codes[ch]
    return bits


def bits_to_bytes(bits):
    # add extra 0s so length becomes multiple of 8
    padding = (8 - len(bits) % 8) % 8
    bits = bits + "0" * padding

    data = bytearray()
    for i in range(0, len(bits), 8):
        byte = bits[i:i + 8]
        data.append(int(byte, 2))
    return bytes(data), padding


def bytes_to_bits(data, padding):
    bits = ""
    for b in data:
        bits += format(b, "08b")        # byte -> 8 character binary string
    if padding > 0:
        bits = bits[:-padding]          # remove the extra padding bits
    return bits


# ---------------------------------------------------------
# Step 5: Decoding
# ---------------------------------------------------------
def decode_text(bits, root):
    result = []
    node = root

    # special case: only one unique character in the file
    if root.char is not None:
        return root.char * len(bits)

    for bit in bits:
        if bit == "0":
            node = node.left
        else:
            node = node.right

        if node.char is not None:       # reached a leaf
            result.append(node.char)
            node = root
    return "".join(result)


# ---------------------------------------------------------
# File handling
# ---------------------------------------------------------
# Compressed file format:
#   line 1 : frequency table  ->  "ascii:freq,ascii:freq,..."
#   line 2 : number of padding bits
#   rest   : the compressed data (bytes)
def compress_file(input_path, output_path):
    # newline="" keeps line endings exactly as they are in the file
    with open(input_path, "r", encoding="utf-8", newline="") as f:
        text = f.read()

    if len(text) == 0:
        print("File is empty, nothing to compress.")
        return

    start = time.time()

    freq = calculate_frequencies(text)
    root = build_tree(freq)
    codes = {}
    generate_codes(root, "", codes)
    bits = encode_text(text, codes)
    data, padding = bits_to_bytes(bits)

    # header = frequency table (so decoder can rebuild same tree)
    parts = []
    for ch in sorted(freq):
        parts.append(str(ord(ch)) + ":" + str(freq[ch]))
    header = ",".join(parts) + "\n" + str(padding) + "\n"

    with open(output_path, "wb") as f:
        f.write(header.encode("utf-8"))
        f.write(data)

    end = time.time()

    print("\n--- Huffman Codes ---")
    show_codes(codes, freq)
    print("\nCompression time: %.4f seconds" % (end - start))


def decompress_file(input_path, output_path):
    with open(input_path, "rb") as f:
        freq_line = f.readline().decode("utf-8").strip()
        padding = int(f.readline().decode("utf-8").strip())
        data = f.read()

    start = time.time()

    # rebuild the frequency table
    freq = {}
    for item in freq_line.split(","):
        code, count = item.split(":")
        freq[chr(int(code))] = int(count)

    root = build_tree(freq)
    bits = bytes_to_bits(data, padding)
    text = decode_text(bits, root)

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        f.write(text)

    end = time.time()
    print("Decompression time: %.4f seconds" % (end - start))


def show_codes(codes, freq):
    print("%-8s %-10s %s" % ("Char", "Frequency", "Code"))
    # show most frequent characters first (top 15 only)
    shown = 0
    for ch in sorted(freq, key=lambda c: freq[c], reverse=True):
        name = repr(ch)
        print("%-8s %-10d %s" % (name, freq[ch], codes[ch]))
        shown += 1
        if shown == 15:
            print("... (%d characters in total)" % len(freq))
            break


def compare_sizes(original_path, compressed_path):
    original = os.path.getsize(original_path)
    compressed = os.path.getsize(compressed_path)
    saved = original - compressed
    percent = (saved / original) * 100

    print("\n--- File Size Comparison ---")
    print("Original file size   :", original, "bytes")
    print("Compressed file size :", compressed, "bytes")
    print("Space saved          :", saved, "bytes")
    print("Compression ratio    : %.2f%%" % percent)


# ---------------------------------------------------------
# Main menu
# ---------------------------------------------------------
def main():
    while True:
        print("\n===== Huffman File Compression =====")
        print("1. Compress a file")
        print("2. Decompress a file")
        print("3. Compress + Decompress + Verify (full test)")
        print("4. Exit")
        choice = input("Enter choice: ").strip()

        if choice == "1":
            inp = input("Input text file: ").strip()
            out = input("Output compressed file (e.g. out.huff): ").strip()
            if not os.path.exists(inp):
                print("File not found!")
                continue
            compress_file(inp, out)
            compare_sizes(inp, out)

        elif choice == "2":
            inp = input("Compressed file: ").strip()
            out = input("Output text file: ").strip()
            if not os.path.exists(inp):
                print("File not found!")
                continue
            decompress_file(inp, out)
            print("Decompressed file saved as", out)

        elif choice == "3":
            inp = input("Input text file: ").strip()
            if not os.path.exists(inp):
                print("File not found!")
                continue
            compress_file(inp, "compressed.huff")
            decompress_file("compressed.huff", "decompressed.txt")
            compare_sizes(inp, "compressed.huff")

            with open(inp, "r", encoding="utf-8", newline="") as f1:
                a = f1.read()
            with open("decompressed.txt", "r", encoding="utf-8", newline="") as f2:
                b = f2.read()
            if a == b:
                print("Verification: SUCCESS (decompressed file is identical)")
            else:
                print("Verification: FAILED")

        elif choice == "4":
            print("Bye!")
            break
        else:
            print("Invalid choice, try again.")


if __name__ == "__main__":
    main()
