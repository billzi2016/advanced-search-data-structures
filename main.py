from lib.avl_tree import AVLTree
from lib.b_plus_tree import BPlusTree
from lib.b_tree import BTree
from lib.binary_search import binary_search
from lib.bst import BST
from lib.exponential_search import exponential_search
from lib.fibonacci_search import fibonacci_search
from lib.hash_table import OpenAddressingHashTable
from lib.interpolation_search import interpolation_search
from lib.jump_search import jump_search
from lib.linear_search import linear_search
from lib.red_black_tree import RedBlackTree
from lib.scapegoat_tree import ScapegoatTree
from lib.skip_list import SkipList
from lib.splay_tree import SplayTree
from lib.treap import Treap
from lib.trie import Trie


VALUES = [42, 17, 8, 99, 23, 4, 16, 15, 15, 0, -3, -100, 2048, 7, 64, 128, 256]
# 树和集合结构统一按去重后的 key 集合进行验证。
UNIQUE_VALUES = sorted(set(VALUES))
# 明确挑选几个不存在的值，覆盖低于最小值、中间空洞和高于最大值。
MISSING_VALUES = [-999, 5, 4096]
# 删除测试覆盖根附近值、最小值和重复输入中的值。
DELETE_VALUES = [42, -100, 15]


def run_test(name, test_func) -> bool:
    # 所有测试统一由这里捕获断言错误，并输出和参考项目一致的 PASS/FAIL 格式。
    try:
        test_func()
    except AssertionError as error:
        print(f"[FAIL] {name}")
        print(error)
        return False

    print(f"[PASS] {name}")
    return True


def test_linear_search() -> None:
    # 线性查找不要求有序，因此直接在原数组和多种边界输入上测试。
    cases = [
        [],
        [1],
        [3, 3, 3, 3],
        [4, -1, 0, -7, 8, 3, 3, -1],
        VALUES,
    ]

    for values in cases:
        targets = set(values) | set(MISSING_VALUES)
        for target in targets:
            actual = linear_search(values, target)
            # Python list.index 作为基准，只在目标存在时调用。
            expected = values.index(target) if target in values else -1
            assert actual == expected, f"linear_search({values}, {target}) expected {expected}, got {actual}"


def test_sorted_array_search(search_func) -> None:
    # 二分、跳跃、插值、指数、斐波那契查找都要求输入升序。
    cases = [
        [],
        [1],
        [3, 3, 3, 3],
        sorted([4, -1, 0, -7, 8, 3, 3, -1]),
        sorted(VALUES),
    ]

    for values in cases:
        targets = set(values) | set(MISSING_VALUES)
        for target in targets:
            actual = search_func(values, target)
            if target in values:
                # 对重复元素不强制要求具体下标，只要求返回位置确实命中目标。
                assert actual >= 0, f"{search_func.__name__} missed {target} in {values}"
                assert values[actual] == target, f"{search_func.__name__} returned wrong index {actual}"
            else:
                assert actual == -1, f"{search_func.__name__} should miss {target}, got {actual}"


def test_ordered_structure(factory, supports_delete: bool = True, validator=None) -> None:
    # 这个通用测试覆盖 BST、AVL、替罪羊树、Splay、Treap、B 树等有序结构。
    structure = factory()
    for value in VALUES:
        structure.insert(value)

    # 中序遍历或等价接口必须返回去重后的升序 key。
    assert structure.inorder() == UNIQUE_VALUES, f"inorder expected {UNIQUE_VALUES}, got {structure.inorder()}"
    for value in UNIQUE_VALUES:
        assert structure.contains(value), f"missing inserted value {value}"
    for value in MISSING_VALUES:
        assert not structure.contains(value), f"unexpectedly found missing value {value}"
    if validator is not None:
        # AVL 和红黑树会额外检查结构不变量。
        assert validator(structure), "structure invariant validation failed"

    if not supports_delete:
        return

    expected = set(UNIQUE_VALUES)
    for value in DELETE_VALUES:
        structure.delete(value)
        expected.discard(value)
        # 删除后既要查不到目标，也要保持剩余元素有序。
        assert not structure.contains(value), f"delete failed for {value}"
        assert structure.inorder() == sorted(expected), f"inorder mismatch after deleting {value}"
        if validator is not None:
            assert validator(structure), "structure invariant validation failed after delete"


def test_b_plus_tree() -> None:
    # B+ 树真实 key 全部在叶子层，因此重点验证叶子链表和范围查询。
    tree = BPlusTree(max_keys=4)
    for value in VALUES:
        tree.insert(value)

    assert tree.keys() == UNIQUE_VALUES, f"B+ leaf chain expected {UNIQUE_VALUES}, got {tree.keys()}"
    for value in UNIQUE_VALUES:
        assert tree.contains(value), f"B+ tree missing {value}"
    for value in MISSING_VALUES:
        assert not tree.contains(value), f"B+ tree unexpectedly found {value}"

    expected_range = [value for value in UNIQUE_VALUES if 7 <= value <= 99]
    # 范围查询应该只扫描叶子链表中落入区间的 key。
    assert tree.range_query(7, 99) == expected_range, "B+ range query mismatch"
    assert tree.range_query(100, 10) == [], "B+ inverted range should be empty"


def test_skip_list() -> None:
    # 跳表验证内容和有序结构类似，但遍历入口是第 0 层链表。
    skip_list = SkipList(max_level=8)
    for value in VALUES:
        skip_list.insert(value)

    assert skip_list.to_list() == UNIQUE_VALUES, "skip list order mismatch"
    for value in UNIQUE_VALUES:
        assert skip_list.contains(value), f"skip list missing {value}"
    for value in MISSING_VALUES:
        assert not skip_list.contains(value), f"skip list unexpectedly found {value}"

    expected = set(UNIQUE_VALUES)
    for value in DELETE_VALUES:
        skip_list.delete(value)
        expected.discard(value)
        assert not skip_list.contains(value), f"skip list delete failed for {value}"
        assert skip_list.to_list() == sorted(expected), "skip list order mismatch after delete"


def test_trie() -> None:
    # Trie 使用字符串样例，覆盖完整单词、共享前缀和删除剪枝。
    words = ["search", "sea", "seat", "seal", "tree", "trie", "trigger", "algorithm"]
    trie = Trie()
    for word in words:
        trie.insert(word)

    for word in words:
        assert trie.contains(word), f"trie missing {word}"
    assert not trie.contains("se"), "trie should not treat prefix as word"
    assert trie.starts_with("sea"), "trie missing prefix sea"
    assert trie.words_with_prefix("sea") == ["sea", "seal", "search", "seat"], "trie prefix listing mismatch"

    trie.delete("seal")
    assert not trie.contains("seal"), "trie delete failed"
    assert trie.contains("sea"), "trie delete removed shared prefix word"


def test_hash_table() -> None:
    # 哈希表验证开放寻址下的插入、查找、删除和扩缩容后内容一致性。
    table = OpenAddressingHashTable()
    for value in VALUES:
        table.add(value)

    assert table.to_list() == UNIQUE_VALUES, "hash table content mismatch"
    for value in UNIQUE_VALUES:
        assert table.contains(value), f"hash table missing {value}"
    for value in MISSING_VALUES:
        assert not table.contains(value), f"hash table unexpectedly found {value}"

    expected = set(UNIQUE_VALUES)
    for value in DELETE_VALUES:
        table.remove(value)
        expected.discard(value)
        assert not table.contains(value), f"hash table delete failed for {value}"
        assert table.to_list() == sorted(expected), "hash table content mismatch after delete"


def main() -> None:
    # 每个条目包含展示名称和对应测试函数，方便输出清晰的验收结果。
    tests = [
        ("linear_search", test_linear_search),
        ("binary_search", lambda: test_sorted_array_search(binary_search)),
        ("jump_search", lambda: test_sorted_array_search(jump_search)),
        ("interpolation_search", lambda: test_sorted_array_search(interpolation_search)),
        ("exponential_search", lambda: test_sorted_array_search(exponential_search)),
        ("fibonacci_search", lambda: test_sorted_array_search(fibonacci_search)),
        ("BST", lambda: test_ordered_structure(BST)),
        ("AVLTree", lambda: test_ordered_structure(AVLTree, validator=lambda tree: tree.is_balanced())),
        ("RedBlackTree", lambda: test_ordered_structure(RedBlackTree, supports_delete=False, validator=lambda tree: tree.validate())),
        ("ScapegoatTree", lambda: test_ordered_structure(ScapegoatTree)),
        ("SplayTree", lambda: test_ordered_structure(SplayTree)),
        ("Treap", lambda: test_ordered_structure(Treap)),
        ("BTree", lambda: test_ordered_structure(lambda: BTree(min_degree=3), supports_delete=False)),
        ("BPlusTree", test_b_plus_tree),
        ("SkipList", test_skip_list),
        ("Trie", test_trie),
        ("OpenAddressingHashTable", test_hash_table),
    ]

    for name, test_func in tests:
        if not run_test(name, test_func):
            raise SystemExit(1)

    print("All search algorithms and data structures passed correctness tests.")


if __name__ == "__main__":
    main()
