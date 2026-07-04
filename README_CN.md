# Advanced Search Data Structures

这是一个 Python 查找算法与搜索数据结构实现项目。

项目目标很直接：`lib/` 中每个文件实现一种查找算法或搜索数据结构，`main.py` 统一验证查找结果、集合语义和有序遍历结果。

## 项目目标

- 整理常见数组查找算法的可运行实现。
- 实现多种经典树形搜索结构，并验证其基本语义。
- 覆盖散列、跳表、Trie 等非树形索引结构。
- 保持每个模块职责单一，便于阅读、测试和扩展。

## 核心功能

- 基础查找算法：线性查找、二分查找、跳跃查找、插值查找、指数查找、斐波那契查找。
- 平衡搜索树：AVL 树、红黑树、替罪羊树、Splay 树、Treap。
- 多路搜索树：B 树、B+ 树。
- 其他索引结构：BST、跳表、Trie、开放寻址哈希表。
- 统一测试入口：验证命中、未命中、插入、删除、有序遍历、范围查询和前缀查询。

## 技术栈

- Python 3
- 标准库 `dataclasses`
- 标准库 `math`
- 无第三方依赖

## 项目结构

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

## 已实现算法和结构

| 名称 | 类型 | 平均查找复杂度 | 说明 |
| --- | --- | --- | --- |
| 线性查找 | 数组查找 | O(n) | 不要求输入有序 |
| 二分查找 | 数组查找 | O(log n) | 要求输入有序 |
| 跳跃查找 | 数组查找 | O(sqrt n) | 要求输入有序 |
| 插值查找 | 数组查找 | O(log log n) | 对均匀分布数据更友好 |
| 指数查找 | 数组查找 | O(log n) | 适合边界未知或目标靠前场景 |
| 斐波那契查找 | 数组查找 | O(log n) | 使用斐波那契分割 |
| BST | 二叉搜索树 | O(h) | 未平衡，最坏 O(n) |
| AVL 树 | 平衡二叉搜索树 | O(log n) | 严格高度平衡 |
| 红黑树 | 平衡二叉搜索树 | O(log n) | 通过颜色约束保持近似平衡 |
| 替罪羊树 | 平衡二叉搜索树 | 摊还 O(log n) | 通过局部重建恢复平衡 |
| Splay 树 | 自调整二叉搜索树 | 摊还 O(log n) | 访问后旋转到根节点 |
| Treap | 随机化平衡树 | O(log n) | 同时满足 BST 和堆性质 |
| B 树 | 多路搜索树 | O(log n) | 适合块存储和磁盘索引模型 |
| B+ 树 | 多路索引树 | O(log n) | 叶子链表支持范围查询 |
| 跳表 | 分层链表索引 | O(log n) | 使用多层前向指针加速搜索 |
| Trie | 前缀树 | O(k) | 适合字符串精确查找和前缀查询 |
| 开放寻址哈希表 | 哈希索引 | O(1) | 使用线性探测和墓碑删除 |

## 运行方式

```bash
python3 main.py
```

预期输出：

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

## 测试说明

`main.py` 会验证以下场景：

- 空数组、单元素数组、重复元素、负数和正负混合数组。
- 有序数组查找算法的命中与未命中结果。
- 搜索树和索引结构的插入、查找和有序输出。
- 支持删除的结构会额外验证删除后的查找结果。
- B+ 树会验证叶子链表顺序和范围查询。
- Trie 会验证单词查找、前缀判断、前缀枚举和删除。

## 当前进度

- 已完成核心查找算法和主要搜索数据结构实现。
- 已提供统一正确性验证入口。
- 暂未引入性能基准测试和可视化输出。

## 后续计划

- 增加随机压力测试和结构不变量校验。
- 增加性能基准测试，比较不同数据规模下的查找延迟。
- 增加树结构可视化导出，便于观察旋转、分裂和重建过程。
