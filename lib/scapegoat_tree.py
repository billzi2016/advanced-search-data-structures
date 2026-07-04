"""替罪羊树。

替罪羊树是一种不在节点上保存高度、颜色或优先级的平衡搜索树。
它允许插入路径暂时变深；当深度超过理论上界时，向上寻找第一个重量比例失衡的
祖先节点，把这个局部子树整体重建成平衡树。删除过多时则触发全局重建。
"""

from dataclasses import dataclass
import math


@dataclass
class _ScapegoatNode:
    """替罪羊树内部节点。

    parent 指针用于从新插入节点向上寻找失衡祖先，也用于局部重建后重新接回父节点。
    """

    key: int
    left: "_ScapegoatNode | None" = None
    right: "_ScapegoatNode | None" = None
    parent: "_ScapegoatNode | None" = None


class ScapegoatTree:
    """集合语义的替罪羊树。"""

    def __init__(self, alpha: float = 0.7) -> None:
        """创建替罪羊树。

        参数:
            alpha: 重量平衡参数，必须位于 (0.5, 1)。值越小越严格平衡，
                但触发重建的频率也越高。
        """

        if not 0.5 < alpha < 1:
            raise ValueError("alpha must be between 0.5 and 1")
        # alpha 越接近 0.5，树越严格平衡，重建也越频繁。
        self.alpha = alpha
        self.root: _ScapegoatNode | None = None
        # size 是当前节点数，max_size 记录上一次全局重建后的最大规模。
        self.size = 0
        self.max_size = 0

    def insert(self, key: int) -> None:
        """插入 key；如果插入深度过大，则局部重建失衡祖先子树。"""

        if self.root is None:
            self.root = _ScapegoatNode(key)
            self.size = 1
            self.max_size = 1
            return

        depth = 0
        parent: _ScapegoatNode | None = None
        current = self.root
        while current is not None:
            parent = current
            if key == current.key:
                return
            # 插入路径深度会被记录，用来判断是否超出高度上界。
            current = current.left if key < current.key else current.right
            depth += 1

        node = _ScapegoatNode(key=key, parent=parent)
        if parent is not None and key < parent.key:
            parent.left = node
        elif parent is not None:
            parent.right = node

        self.size += 1
        self.max_size = max(self.max_size, self.size)

        if depth > self._height_limit():
            # 插入太深时，向上寻找第一个不满足 alpha 重量平衡的祖先。
            scapegoat = self._find_scapegoat(node)
            if scapegoat is not None:
                # 只重建失衡局部子树，而不是整棵树。
                self._rebuild_subtree(scapegoat)

    def contains(self, key: int) -> bool:
        """按 BST 路径查找 key 是否存在。"""

        node = self.root
        while node is not None:
            if key == node.key:
                return True
            node = node.left if key < node.key else node.right
        return False

    def delete(self, key: int) -> None:
        """删除 key；当当前规模比历史最大规模小太多时全局重建。"""

        # 替罪羊树删除本身按 BST 删除处理，规模下降过多时再全局重建。
        if not self.contains(key):
            return

        self.root = self._delete_node(self.root, key)
        if self.root is not None:
            self.root.parent = None
        self.size -= 1

        # 删除过多后整体重建，恢复替罪羊树的全局高度界。
        if self.size > 0 and self.size < self.alpha * self.max_size:
            nodes: list[_ScapegoatNode] = []
            self._collect_nodes(self.root, nodes)
            self.root = self._build_balanced(nodes, 0, len(nodes), None)
            self.max_size = self.size
        elif self.size == 0:
            self.max_size = 0

    def inorder(self) -> list[int]:
        """返回所有 key 的升序列表。"""

        result: list[int] = []
        self._inorder(self.root, result)
        return result

    def _height_limit(self) -> float:
        """计算当前规模允许的理论高度上界。"""

        # 理论高度上界约为 log_{1/alpha}(n)。
        return math.log(self.size, 1 / self.alpha) if self.size > 1 else 0

    def _find_scapegoat(self, node: _ScapegoatNode) -> _ScapegoatNode | None:
        """从插入节点向上寻找第一个违反 alpha 重量平衡的祖先。"""

        child = node
        parent = node.parent
        while parent is not None:
            # 如果某个孩子子树占父子树比例过大，父节点就是替罪羊。
            if self._subtree_size(child) > self.alpha * self._subtree_size(parent):
                return parent
            child = parent
            parent = parent.parent
        return None

    def _rebuild_subtree(self, node: _ScapegoatNode) -> None:
        """把指定子树收集为有序数组，再重建成高度平衡子树。"""

        # 中序收集得到有序节点数组，再按中点递归构造完全平衡子树。
        parent = node.parent
        nodes: list[_ScapegoatNode] = []
        self._collect_nodes(node, nodes)
        rebuilt = self._build_balanced(nodes, 0, len(nodes), parent)

        if parent is None:
            self.root = rebuilt
        elif parent.left == node:
            parent.left = rebuilt
        else:
            parent.right = rebuilt

    def _collect_nodes(self, node: _ScapegoatNode | None, nodes: list[_ScapegoatNode]) -> None:
        """中序收集节点对象，保留 key 的升序顺序。"""

        if node is None:
            return
        # 中序收集可以保留 BST 的升序 key 顺序。
        self._collect_nodes(node.left, nodes)
        nodes.append(node)
        self._collect_nodes(node.right, nodes)

    def _build_balanced(
        self,
        nodes: list[_ScapegoatNode],
        start: int,
        end: int,
        parent: _ScapegoatNode | None,
    ) -> _ScapegoatNode | None:
        """用有序节点数组的中点递归构造平衡 BST。

        注意这里复用原有节点对象，而不是创建新节点；因此必须重新写入
        parent、left 和 right 指针，避免残留旧结构中的链接。
        """

        if start >= end:
            return None

        mid = (start + end) // 2
        # 选择中点作为根，左右两边递归构造成高度接近平衡的子树。
        node = nodes[mid]
        node.parent = parent
        node.left = self._build_balanced(nodes, start, mid, node)
        node.right = self._build_balanced(nodes, mid + 1, end, node)
        return node

    def _delete_node(self, node: _ScapegoatNode | None, key: int) -> _ScapegoatNode | None:
        """执行普通 BST 删除，并维护 parent 指针。"""

        if node is None:
            return None

        if key < node.key:
            node.left = self._delete_node(node.left, key)
            if node.left is not None:
                node.left.parent = node
        elif key > node.key:
            node.right = self._delete_node(node.right, key)
            if node.right is not None:
                node.right.parent = node
        else:
            # 一个孩子以内直接提升孩子，注意维护 parent 指针。
            if node.left is None:
                if node.right is not None:
                    node.right.parent = node.parent
                return node.right
            if node.right is None:
                if node.left is not None:
                    node.left.parent = node.parent
                return node.left

            # 两个孩子时使用右子树最小节点替换。
            successor = self._minimum(node.right)
            node.key = successor.key
            node.right = self._delete_node(node.right, successor.key)
            if node.right is not None:
                node.right.parent = node

        return node

    def _minimum(self, node: _ScapegoatNode) -> _ScapegoatNode:
        """返回当前子树最小节点。"""

        while node.left is not None:
            node = node.left
        return node

    def _subtree_size(self, node: _ScapegoatNode | None) -> int:
        """递归计算子树节点数，用于重量平衡判断。"""

        if node is None:
            return 0
        return 1 + self._subtree_size(node.left) + self._subtree_size(node.right)

    def _inorder(self, node: _ScapegoatNode | None, result: list[int]) -> None:
        """递归中序遍历。"""

        if node is None:
            return
        self._inorder(node.left, result)
        result.append(node.key)
        self._inorder(node.right, result)
