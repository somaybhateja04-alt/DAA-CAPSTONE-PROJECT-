# Project 3: File Compression Using Huffman Coding

**Course level:** B.Tech 2nd Year (AI & ML) — Data Structures & Algorithms
**Language:** Python 3 (only `heapq`, `os`, `time` from the standard library)

## 1. Problem Statement
Develop a file compression system using Huffman Coding that reduces the storage space
required for text files. The system calculates character frequencies, constructs a Huffman
tree, generates binary codes, and performs encoding and decoding. The time and space
complexity is analysed and the original and compressed file sizes are compared.

## 2. Idea
Normal text uses 8 bits for every character. Huffman coding gives **short codes to
frequent characters** and **long codes to rare characters**, so the total number of bits
becomes smaller. The codes are *prefix-free* (no code is the start of another code), so
decoding is never ambiguous.

## 3. Algorithm (steps)
1. **Read** the text file.
2. **Count frequency** of each character (dictionary).
3. **Build a min-heap** with one leaf node per character.
4. **Repeat**: remove the two nodes with the smallest frequency, join them under a new
   parent node (frequency = sum), push the parent back. Stop when one node (the root) is left.
5. **Generate codes** by walking the tree: left edge = `0`, right edge = `1`.
6. **Encode**: replace each character with its code, pack the bits into bytes.
7. **Save** the frequency table (header) + padding count + packed bytes.
8. **Decode**: rebuild the same tree from the header, read bits, walk the tree from the
   root (0 = left, 1 = right); at a leaf output the character and go back to the root.

## 4. Data Structures Used
| Structure | Where |
|---|---|
| Dictionary (hash map) | frequency table, code table |
| Binary tree (`Node` class) | Huffman tree |
| Min-heap (`heapq`) | choosing two smallest nodes |
| Recursion | generating codes from the tree |
| String / bytes | bit string and packed output |

## 5. Compressed File Format
```
line 1 : ascii:freq,ascii:freq,...      (frequency table)
line 2 : number of padding bits
rest   : compressed data bytes
```

## 6. How to Run
```
python3 huffman.py
```
Menu: 1 = Compress, 2 = Decompress, 3 = Compress + Decompress + Verify, 4 = Exit.
Quick test: choose `3` and enter `sample.txt`.

## 7. Time and Space Complexity
Let **n** = number of characters in the file and **k** = number of unique characters.

| Step | Time | Space |
|---|---|---|
| Frequency count | O(n) | O(k) |
| Build heap | O(k) | O(k) |
| Build tree (k-1 merges, each O(log k)) | O(k log k) | O(k) |
| Generate codes (visit every node) | O(k) | O(k) |
| Encode | O(n) | O(n) bits |
| Decode | O(n) | O(n) |
| **Total compression** | **O(n + k log k)** | **O(n + k)** |

Since k is small (at most the alphabet size, ~100 for English text), k log k is tiny
compared to n, so in practice the running time is **O(n)** — linear in file size.

## 8. Results (sample.txt)
| Measurement | Value |
|---|---|
| Original size | 33,435 bytes |
| Compressed size | 17,880 bytes |
| Space saved | 15,555 bytes |
| Compression | **46.52 %** |
| Unique characters (k) | 39 |
| Compression time | ~0.006 s |
| Decompression time | ~0.010 s |

The decompressed file was compared with the original and is **identical**
(lossless compression).

Example codes: space = `100` (3 bits), `e` = `001` (3 bits), `d` = `11110` (5 bits)
instead of 8 bits each.

## 9. Observations
- Text with an uneven character distribution (English) compresses well.
- **Very small files may get bigger**, because the header (frequency table) costs more
  than the bits saved.
- A file with random characters (all frequencies equal) compresses very little.
- A file with only one unique character is handled as a special case (code `0`).

## 10. Limitations and Future Work
- Header stores full frequency table; a more compact header (storing only code lengths)
  would save space.
- Bit string is built with Python strings, which is simple but slower than bit operations.
- Only text files (UTF-8) are supported; binary files could be supported by working on bytes.
- Compare with other methods (Run-Length Encoding, LZW, `zip`).

## 11. Conclusion
Huffman coding gives lossless compression in O(n + k log k) time. On the sample text it
reduced the file size by about 46 %, and the decoded file matched the original exactly.
