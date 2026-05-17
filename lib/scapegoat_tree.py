from dataclasses import dataclass
import math


@dataclass
class _ScapegoatNode:
    key: int
    left: "_ScapegoatNode | None" = None
    right: "_ScapegoatNode | None" = None
    parent: "_ScapegoatNode | None" = None


class ScapegoatTree:
    def __init__(self, alpha: float = 0.7) -> None:
        if not 0.5 < alpha < 1:
            raise ValueError("alpha must be between 0.5 and 1")
        # alpha 越接近 0.5，树越严格平衡，重建也越频繁。
        self.alpha = alpha
        self.root: _ScapegoatNode | None = None
        # size 是当前节点数，max_size 记录上一次全局重建后的最大规模。
        self.size = 0
        self.max_size = 0

    def insert(self, key: int) -> None:
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
        node = self.root
        while node is not None:
            if key == node.key:
                return True
            node = node.left if key < node.key else node.right
        return False

    def delete(self, key: int) -> None:
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
        result: list[int] = []
        self._inorder(self.root, result)
        return result

    def _height_limit(self) -> float:
        # 理论高度上界约为 log_{1/alpha}(n)。
        return math.log(self.size, 1 / self.alpha) if self.size > 1 else 0

    def _find_scapegoat(self, node: _ScapegoatNode) -> _ScapegoatNode | None:
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
        while node.left is not None:
            node = node.left
        return node

    def _subtree_size(self, node: _ScapegoatNode | None) -> int:
        if node is None:
            return 0
        return 1 + self._subtree_size(node.left) + self._subtree_size(node.right)

    def _inorder(self, node: _ScapegoatNode | None, result: list[int]) -> None:
        if node is None:
            return
        self._inorder(node.left, result)
        result.append(node.key)
        self._inorder(node.right, result)
