from dataclasses import dataclass, field


@dataclass
class _BPlusNode:
    leaf: bool
    keys: list[int] = field(default_factory=list)
    children: list["_BPlusNode"] = field(default_factory=list)
    next: "_BPlusNode | None" = None


class BPlusTree:
    def __init__(self, max_keys: int = 4) -> None:
        if max_keys < 3:
            raise ValueError("max_keys must be at least 3")
        # max_keys 控制单个节点最多保存多少个 key。
        # B+ 树所有真实数据都保存在叶子节点，内部节点只做导航。
        self.max_keys = max_keys
        self.root = _BPlusNode(leaf=True)

    def insert(self, key: int) -> None:
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
        # 查找总是先走到叶子节点，再在叶子 key 列表中判断是否存在。
        leaf = self._find_leaf(key)
        return key in leaf.keys

    def keys(self) -> list[int]:
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
        # 叶子分裂时，右侧第一个 key 复制到父节点作为分隔键。
        mid = (len(node.keys) + 1) // 2
        right = _BPlusNode(leaf=True, keys=node.keys[mid:])
        node.keys = node.keys[:mid]

        # 维护叶子链表，使范围查询可以顺序扫描。
        right.next = node.next
        node.next = right
        return right.keys[0], right

    def _split_internal(self, node: _BPlusNode) -> tuple[int, _BPlusNode]:
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
        node = self.root
        while not node.leaf:
            # 内部节点的 key 是孩子区间分界，决定继续走哪条边。
            node = node.children[self._child_index(node, key)]
        return node

    def _child_index(self, node: _BPlusNode, key: int) -> int:
        index = 0
        # key 大于等于分隔键时进入右侧孩子，符合 B+ 树内部节点导航规则。
        while index < len(node.keys) and key >= node.keys[index]:
            index += 1
        return index

    def _insert_key_sorted(self, keys: list[int], key: int) -> None:
        # 在短数组中用右移插入，逻辑简单且符合节点内有序存储模型。
        index = len(keys) - 1
        keys.append(key)
        while index >= 0 and key < keys[index]:
            keys[index + 1] = keys[index]
            index -= 1
        keys[index + 1] = key
