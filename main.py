"""统一正确性验证入口。

这个文件不是算法实现本身，而是把仓库中的数组查找、树形搜索结构、
跳表、Trie 和哈希表全部拉到同一套验收场景里。它的设计意图是：

1. 用固定样例覆盖空输入、重复值、负数、删除、范围查询和前缀查询。
2. 让所有结构都表现成“集合式 key 容器”，重复插入不产生重复元素。
3. 输出简单的 PASS/FAIL 文本，方便在本地或 CI 中快速判断是否破坏语义。
"""

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
    """运行单个测试函数，并把断言异常转换成统一的终端输出。

    参数:
        name: 展示在终端里的测试名称，通常对应算法或数据结构名称。
        test_func: 不接收参数的测试函数，内部通过 assert 表达预期。

    返回:
        测试通过返回 True；任何 AssertionError 都会被捕获并返回 False。
    """

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
    """验证线性查找在无序数组和边界输入上的行为。

    线性查找的特点是“不依赖输入顺序”，因此这里故意不排序样例。
    重复元素场景下使用 list.index 作为基准，确保实现返回第一个命中下标。
    """

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
    """复用同一套样例验证所有要求升序输入的数组查找算法。

    这些算法可能在重复值中返回任意一个命中位置，所以测试不要求固定下标；
    只要求返回的下标合法，并且该位置上的值确实等于目标值。
    """

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
    """验证具有有序遍历能力的搜索树或树形索引结构。

    参数:
        factory: 创建空结构的工厂函数，避免不同测试共享状态。
        supports_delete: 有些结构当前版本尚未实现删除，测试时显式跳过删除段。
        validator: 可选的不变量检查函数，例如 AVL 高度平衡或红黑树黑高一致。

    这个测试把结构当成集合来检查：重复输入只保留一个 key，中序遍历必须升序。
    """

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
    """验证 B+ 树的叶子链表、查找和范围查询语义。

    B+ 树与普通 B 树最大的区别是：真实 key 全部出现在叶子节点，
    内部节点只作为导航索引。因此这里不只检查 contains，还检查叶子链表输出。
    """

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
    """验证跳表的查找、删除和第 0 层有序链表输出。

    跳表的高层只是加速索引，完整数据都必须能在第 0 层顺序走到。
    所以 to_list 是判断结构是否仍然有序、是否漏删漏插的关键接口。
    """

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
    """验证 Trie 的完整单词、前缀、前缀枚举和删除剪枝。

    这里特意使用 search/sea/seat/seal 这组共享前缀单词，
    用来确认删除一个单词时不会误删其他仍然依赖同一前缀路径的单词。
    """

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
    """验证开放寻址哈希表的集合语义和墓碑删除行为。

    开放寻址删除时不能直接把槽位置空，否则会截断后续冲突 key 的探测链。
    因此测试会在删除后继续检查剩余 key 是否仍然可查。
    """

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
    """依次运行所有算法和数据结构的正确性验收。

    任意一个测试失败都会立即以非零退出码结束，避免后续 PASS 输出掩盖问题。
    """

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
