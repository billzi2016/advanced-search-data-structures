"""B 树。

B 树是多路搜索树，每个节点可以保存多个 key 和多个孩子。
它常用于磁盘或块存储模型，因为较高的分支因子可以降低树高。
本实现采用经典“下降前分裂满孩子”的插入策略，避免递归进入满节点。
"""

from dataclasses import dataclass, field


@dataclass
class _BTreeNode:
    """B 树节点。

    leaf 标记节点是否为叶子；keys 始终保持升序；
    非叶节点的 children 数量应当等于 len(keys) + 1。
    """

    leaf: bool
    keys: list[int] = field(default_factory=list)
    children: list["_BTreeNode"] = field(default_factory=list)


class BTree:
    """集合语义的 B 树。"""

    def __init__(self, min_degree: int = 3) -> None:
        """创建 B 树。

        参数:
            min_degree: 最小度数 t。除根以外，每个节点至少 t-1 个 key，
                最多 2t-1 个 key。
        """

        if min_degree < 2:
            raise ValueError("min_degree must be at least 2")
        # min_degree 是 B 树最小度数 t，每个节点最多 2t-1 个 key。
        self.min_degree = min_degree
        self.root = _BTreeNode(leaf=True)

    def insert(self, key: int) -> None:
        """插入 key；重复 key 会被忽略。"""

        # 本实现按集合语义处理，重复 key 不重复插入。
        if self.contains(key):
            return

        root = self.root
        if len(root.keys) == self._max_keys():
            # 根节点满时必须先分裂根，树高增加一层。
            new_root = _BTreeNode(leaf=False, children=[root])
            self._split_child(new_root, 0)
            self.root = new_root

        # 确保沿途不会向满节点递归，从而让插入只发生在非满节点中。
        self._insert_non_full(self.root, key)

    def contains(self, key: int) -> bool:
        """查找 key 是否存在。"""

        return self._contains(self.root, key)

    def inorder(self) -> list[int]:
        """返回所有 key 的升序列表。"""

        result: list[int] = []
        self._inorder(self.root, result)
        return result

    def _contains(self, node: _BTreeNode, key: int) -> bool:
        """在指定子树中查找 key。"""

        index = 0
        # 在当前节点的 key 数组中找到第一个不小于目标的位置。
        while index < len(node.keys) and key > node.keys[index]:
            index += 1

        if index < len(node.keys) and key == node.keys[index]:
            return True
        if node.leaf:
            return False
        # 未命中当前节点时，进入对应的孩子区间继续查找。
        return self._contains(node.children[index], key)

    def _insert_non_full(self, node: _BTreeNode, key: int) -> None:
        """向保证未满的节点或其后代中插入 key。

        关键不变量是：调用这个函数时 node 一定不是满节点。
        如果即将下降的孩子满了，就先分裂孩子，再决定进入左侧还是右侧。
        """

        index = len(node.keys) - 1

        if node.leaf:
            # 叶子节点中直接插入，并通过右移保持 key 有序。
            node.keys.append(key)
            while index >= 0 and key < node.keys[index]:
                node.keys[index + 1] = node.keys[index]
                index -= 1
            node.keys[index + 1] = key
            return

        # 内部节点先定位应该进入的孩子。
        while index >= 0 and key < node.keys[index]:
            index -= 1
        index += 1

        if len(node.children[index].keys) == self._max_keys():
            # 下降前先分裂满孩子，保证递归目标不是满节点。
            self._split_child(node, index)
            if key > node.keys[index]:
                # 分裂后中位数上移，如果 key 更大，应进入右侧新孩子。
                index += 1

        self._insert_non_full(node.children[index], key)

    def _split_child(self, parent: _BTreeNode, index: int) -> None:
        """分裂 parent.children[index] 这个满孩子。

        满孩子有 2t-1 个 key；中位 key 上移到父节点，
        左右两段 key 分别留在原孩子和新兄弟节点中。
        """

        degree = self.min_degree
        child = parent.children[index]
        sibling = _BTreeNode(leaf=child.leaf)

        # 满孩子包含 2t-1 个 key，中位 key 上移到父节点。
        median = child.keys[degree - 1]
        sibling.keys = child.keys[degree:]
        child.keys = child.keys[: degree - 1]

        if not child.leaf:
            # 内部节点分裂时，孩子指针也要按中位位置切开。
            sibling.children = child.children[degree:]
            child.children = child.children[:degree]

        parent.keys.insert(index, median)
        parent.children.insert(index + 1, sibling)

    def _max_keys(self) -> int:
        """返回单个节点允许保存的最大 key 数。"""

        return 2 * self.min_degree - 1

    def _inorder(self, node: _BTreeNode, result: list[int]) -> None:
        """递归中序遍历多路搜索树。"""

        if node.leaf:
            result.extend(node.keys)
            return

        # B 树中序遍历需要在每个 key 前遍历对应左侧孩子。
        for index, key in enumerate(node.keys):
            self._inorder(node.children[index], result)
            result.append(key)
        self._inorder(node.children[-1], result)
