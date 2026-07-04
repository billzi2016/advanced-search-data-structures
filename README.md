# Advanced Search Data Structures

This is a Python project that implements search algorithms and search-oriented data structures.

The project goal is direct: each file in `lib/` implements one search algorithm or search data structure, while `main.py` provides a unified entry point to validate lookup results, set-like semantics, and ordered traversal results.

## Project Goals

- Provide runnable implementations of common array search algorithms.
- Implement multiple classic tree-based search structures and verify their core semantics.
- Cover non-tree index structures such as hashing, skip lists, and tries.
- Keep each module focused on one responsibility so the code is easy to read, test, and extend.

## Core Features

- Basic search algorithms: linear search, binary search, jump search, interpolation search, exponential search, and Fibonacci search.
- Balanced search trees: AVL tree, red-black tree, scapegoat tree, splay tree, and treap.
- Multiway search trees: B-tree and B+ tree.
- Other index structures: BST, skip list, trie, and open-addressing hash table.
- Unified test entry point: validates hits, misses, insertion, deletion, ordered traversal, range queries, and prefix queries.

## Tech Stack

- Python 3
- Standard library `dataclasses`
- Standard library `math`
- No third-party dependencies

## Project Structure

```text
advanced-search-data-structures/
├── README.md
├── .gitignore
├── main.py
└── lib/
    ├── __init__.py
    ├── avl_tree.py
    ├── b_plus_tree.py
    ├── b_tree.py
    ├── binary_search.py
    ├── bst.py
    ├── exponential_search.py
    ├── fibonacci_search.py
    ├── hash_table.py
    ├── interpolation_search.py
    ├── jump_search.py
    ├── linear_search.py
    ├── red_black_tree.py
    ├── scapegoat_tree.py
    ├── skip_list.py
    ├── splay_tree.py
    ├── treap.py
    └── trie.py
```

## Implemented Algorithms and Structures

| Name | Type | Average Lookup Complexity | Notes |
| --- | --- | --- | --- |
| Linear search | Array search | O(n) | Does not require sorted input |
| Binary search | Array search | O(log n) | Requires sorted input |
| Jump search | Array search | O(sqrt n) | Requires sorted input |
| Interpolation search | Array search | O(log log n) | Works better for uniformly distributed data |
| Exponential search | Array search | O(log n) | Useful when the boundary is unknown or the target is near the front |
| Fibonacci search | Array search | O(log n) | Uses Fibonacci-based partitioning |
| BST | Binary search tree | O(h) | Unbalanced; worst case O(n) |
| AVL tree | Balanced binary search tree | O(log n) | Strictly height-balanced |
| Red-black tree | Balanced binary search tree | O(log n) | Maintains approximate balance through color constraints |
| Scapegoat tree | Balanced binary search tree | Amortized O(log n) | Restores balance through local rebuilding |
| Splay tree | Self-adjusting binary search tree | Amortized O(log n) | Rotates accessed nodes to the root |
| Treap | Randomized balanced tree | O(log n) | Satisfies both BST and heap properties |
| B-tree | Multiway search tree | O(log n) | Suitable for block storage and disk-index models |
| B+ tree | Multiway index tree | O(log n) | Leaf links support range queries |
| Skip list | Layered linked-list index | O(log n) | Uses multiple forward-pointer layers to speed up search |
| Trie | Prefix tree | O(k) | Suitable for exact string lookup and prefix queries |
| Open-addressing hash table | Hash index | O(1) | Uses linear probing and tombstone deletion |

## How to Run

```bash
python3 main.py
```

Expected output:

```text
[PASS] linear_search
[PASS] binary_search
[PASS] jump_search
[PASS] interpolation_search
[PASS] exponential_search
[PASS] fibonacci_search
[PASS] BST
[PASS] AVLTree
[PASS] RedBlackTree
[PASS] ScapegoatTree
[PASS] SplayTree
[PASS] Treap
[PASS] BTree
[PASS] BPlusTree
[PASS] SkipList
[PASS] Trie
[PASS] OpenAddressingHashTable
All search algorithms and data structures passed correctness tests.
```

## Test Coverage

`main.py` validates the following scenarios:

- Empty arrays, single-element arrays, duplicate elements, negative numbers, and mixed negative/positive arrays.
- Hit and miss results for sorted-array search algorithms.
- Insertion, lookup, and ordered output for search trees and index structures.
- Deletion behavior for structures that support deletion.
- Leaf-link ordering and range queries for the B+ tree.
- Word lookup, prefix checks, prefix enumeration, and deletion for the trie.

## Current Progress

- Core search algorithms and major search data structures are implemented.
- A unified correctness validation entry point is available.
- Performance benchmarks and visualization output have not been added yet.

## Roadmap

- Add randomized stress tests and structural invariant checks.
- Add performance benchmarks to compare lookup latency across data sizes.
- Add visualization export for tree structures to observe rotations, splits, and rebuilding.
