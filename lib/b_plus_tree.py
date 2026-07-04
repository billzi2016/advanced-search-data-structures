"""B+ 树。

B+ 树把真实 key 全部保存在叶子节点，内部节点只存分隔键用于导航。
叶子节点通过 next 指针串成有序链表，因此范围查询可以从起始叶子顺序扫描，
不必反复从根节点重新查找。
"""

from dataclasses import dataclass, field


@dataclass
class _BPlusNode:
    """B+ 树节点。

    leaf 为 True 时 children 为空，keys 保存真实数据；
    leaf 为 False 时 keys 只作为孩子区间分隔符。
    next 只在叶子层使用，用于串联相邻叶子。
    """

    leaf: bool
    keys: list[int] = field(default_factory=list)
    children: list["_BPlusNode"] = field(default_factory=list)
    next: "_BPlusNode | None" = None


class BPlusTree:
    """集合语义的 B+ 树。"""

    def __init__(self, max_keys: int = 4) -> None:
        """创建 B+ 树。

        参数:
            max_keys: 单个节点最多保存的 key 数；超过后触发分裂。
        """

        if max_keys < 3:
            raise ValueError("max_keys must be at least 3")
        # max_keys 控制单个节点最多保存多少个 key。
        # B+ 树所有真实数据都保存在叶子节点，内部节点只做导航。
        self.max_keys = max_keys
        self.root = _BPlusNode(leaf=True)

    def insert(self, key: int) -> None:
        """插入 key；重复 key 不会重复进入叶子链表。"""

        # 保持集合语义，重复 key 不重复插入叶子链表。
        if self.contains(key):
            return

        split = self._insert(self.root, key)
        if split is None:
            return

        # 根节点分裂时创建新的内部根节点，树高增加一层。
        separator, right = split
        self.root = _BPlusNode(
            leaf=False,
            keys=[separator],
            children=[self.root, right],
        )

    def contains(self, key: int) -> bool:
        """查找 key 是否存在，最终判断发生在叶子节点。"""

        # 查找总是先走到叶子节点，再在叶子 key 列表中判断是否存在。
        leaf = self._find_leaf(key)
        return key in leaf.keys

    def keys(self) -> list[int]:
        """沿叶子链表返回所有 key 的升序列表。"""

        # 先找到最左叶子，再沿 next 指针扫描所有叶子，得到全量升序 key。
        node = self.root
        while not node.leaf:
            node = node.children[0]

        result: list[int] = []
        while node is not None:
            result.extend(node.keys)
            node = node.next
        return result

    def range_query(self, start: int, end: int) -> list[int]:
        """返回闭区间 [start, end] 内的所有 key。

        如果 start > end，区间无效，直接返回空列表。
        """

        if start > end:
            return []

        # 范围查询从 start 所在叶子开始，沿叶子链表顺序扫描。
        node = self._find_leaf(start)
        result: list[int] = []

        while node is not None:
            for key in node.keys:
                if key > end:
                    return result
                if key >= start:
                    result.append(key)
            node = node.next

        return result

    def _insert(self, node: _BPlusNode, key: int) -> tuple[int, _BPlusNode] | None:
        """递归插入 key。

        返回 None 表示当前节点没有分裂；返回 (separator, right) 表示当前节点
        分裂出右侧新节点，调用方需要把分隔键和右节点插入父节点。
        """

        if node.leaf:
            # 叶子节点保存真实 key，插入后如果溢出则分裂叶子。
            self._insert_key_sorted(node.keys, key)
            if len(node.keys) <= self.max_keys:
                return None
            return self._split_leaf(node)

        # 内部节点只负责选择递归下降的孩子。
        index = self._child_index(node, key)
        split = self._insert(node.children[index], key)
        if split is None:
            return None

        # 子节点分裂后，把分隔键插入当前内部节点。
        separator, right = split
        node.keys.insert(index, separator)
        node.children.insert(index + 1, right)

        if len(node.keys) <= self.max_keys:
            return None
        return self._split_internal(node)

    def _split_leaf(self, node: _BPlusNode) -> tuple[int, _BPlusNode]:
        """分裂溢出的叶子节点，并维护叶子 next 链。"""

        # 叶子分裂时，右侧第一个 key 复制到父节点作为分隔键。
        mid = (len(node.keys) + 1) // 2
        right = _BPlusNode(leaf=True, keys=node.keys[mid:])
        node.keys = node.keys[:mid]

        # 维护叶子链表，使范围查询可以顺序扫描。
        right.next = node.next
        node.next = right
        return right.keys[0], right

    def _split_internal(self, node: _BPlusNode) -> tuple[int, _BPlusNode]:
        """分裂溢出的内部节点。

        与叶子分裂不同，内部节点的中间 key 会上移到父节点，
        左右两个内部节点都不再保存这个 separator。
        """

        # 内部节点分裂时，中间 key 上移，左右节点不再保留该 key。
        mid = len(node.keys) // 2
        separator = node.keys[mid]

        right = _BPlusNode(
            leaf=False,
            keys=node.keys[mid + 1 :],
            children=node.children[mid + 1 :],
        )
        node.keys = node.keys[:mid]
        node.children = node.children[: mid + 1]
        return separator, right

    def _find_leaf(self, key: int) -> _BPlusNode:
        """从根节点出发，沿内部节点分隔键找到 key 应落入的叶子。"""

        node = self.root
        while not node.leaf:
            # 内部节点的 key 是孩子区间分界，决定继续走哪条边。
            node = node.children[self._child_index(node, key)]
        return node

    def _child_index(self, node: _BPlusNode, key: int) -> int:
        """根据分隔键选择应该下降到哪个孩子。"""

        index = 0
        # key 大于等于分隔键时进入右侧孩子，符合 B+ 树内部节点导航规则。
        while index < len(node.keys) and key >= node.keys[index]:
            index += 1
        return index

    def _insert_key_sorted(self, keys: list[int], key: int) -> None:
        """把 key 插入短有序数组，并保持数组升序。"""

        # 在短数组中用右移插入，逻辑简单且符合节点内有序存储模型。
        index = len(keys) - 1
        keys.append(key)
        while index >= 0 and key < keys[index]:
            keys[index + 1] = keys[index]
            index -= 1
        keys[index + 1] = key
