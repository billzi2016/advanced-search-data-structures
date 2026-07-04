"""Splay 树。

Splay 树是一种自调整二叉搜索树。它不保存高度、颜色或随机优先级，
而是在每次访问后把被访问节点或最后访问节点旋转到根部。
这种策略让近期频繁访问的 key 更接近根，获得摊还 O(log n) 的性能。
"""

from dataclasses import dataclass


@dataclass
class _SplayNode:
    """Splay 树内部节点，包含父指针以便向上旋转。"""

    key: int
    left: "_SplayNode | None" = None
    right: "_SplayNode | None" = None
    parent: "_SplayNode | None" = None


class SplayTree:
    """集合语义的 Splay 搜索树。"""

    def __init__(self) -> None:
        # Splay 树不存额外高度或颜色，靠访问后的旋转自调整。
        self.root: _SplayNode | None = None

    def insert(self, key: int) -> None:
        """插入 key，并把新节点或已有节点伸展到根。"""

        if self.root is None:
            self.root = _SplayNode(key)
            return

        node = self.root
        parent: _SplayNode | None = None
        while node is not None:
            parent = node
            if key == node.key:
                # 重复插入时不新增节点，但把已有节点旋转到根，提升后续访问局部性。
                self._splay(node)
                return
            node = node.left if key < node.key else node.right

        new_node = _SplayNode(key=key, parent=parent)
        if parent is not None and key < parent.key:
            parent.left = new_node
        elif parent is not None:
            parent.right = new_node
        # 新插入节点立即伸展到根。
        self._splay(new_node)

    def contains(self, key: int) -> bool:
        """查找 key；命中或未命中都会把最后访问节点伸展到根。"""

        node = self.root
        last: _SplayNode | None = None

        while node is not None:
            last = node
            if key == node.key:
                # 命中节点被提升到根，形成自适应缓存效果。
                self._splay(node)
                return True
            node = node.left if key < node.key else node.right

        if last is not None:
            # 未命中时把最后访问节点提升到根，也能优化相近 key 的后续访问。
            self._splay(last)
        return False

    def delete(self, key: int) -> None:
        """删除 key。

        contains 会先把目标节点伸展到根。删除根后，将左子树最大节点伸展到根，
        再把原右子树挂到它的右侧，从而保持 BST 顺序。
        """

        # contains 会把目标节点伸展到根，删除时只需要合并左右子树。
        if not self.contains(key) or self.root is None:
            return

        left = self.root.left
        right = self.root.right
        if left is not None:
            left.parent = None
        if right is not None:
            right.parent = None

        if left is None:
            self.root = right
            return

        self.root = left
        max_node = left
        while max_node.right is not None:
            max_node = max_node.right
        # 把左子树最大节点伸展到根，此时它没有右孩子，可直接挂上原右子树。
        self._splay(max_node)
        if self.root is not None:
            self.root.right = right
            if right is not None:
                right.parent = self.root

    def inorder(self) -> list[int]:
        """返回所有 key 的升序列表。"""

        result: list[int] = []
        self._inorder(self.root, result)
        return result

    def _splay(self, node: _SplayNode) -> None:
        """持续执行 Zig、Zig-Zig 或 Zig-Zag 旋转，直到 node 成为根。"""

        # 持续旋转直到目标节点成为根。
        while node.parent is not None:
            parent = node.parent
            grandparent = parent.parent

            if grandparent is None:
                # Zig：父节点就是根，只需一次单旋。
                if node == parent.left:
                    self._rotate_right(parent)
                else:
                    self._rotate_left(parent)
            elif node == parent.left and parent == grandparent.left:
                # Zig-Zig：节点和父节点同为左孩子，连续右旋。
                self._rotate_right(grandparent)
                self._rotate_right(parent)
            elif node == parent.right and parent == grandparent.right:
                # Zig-Zig 镜像：节点和父节点同为右孩子，连续左旋。
                self._rotate_left(grandparent)
                self._rotate_left(parent)
            elif node == parent.right and parent == grandparent.left:
                # Zig-Zag：先左旋父节点，再右旋祖父节点。
                self._rotate_left(parent)
                self._rotate_right(grandparent)
            else:
                # Zig-Zag 镜像：先右旋父节点，再左旋祖父节点。
                self._rotate_right(parent)
                self._rotate_left(grandparent)

    def _rotate_left(self, node: _SplayNode) -> None:
        """围绕 node 左旋，并维护父指针和根指针。"""

        # 左旋时 pivot 接管 node 的原位置，node 成为 pivot 的左孩子。
        pivot = node.right
        if pivot is None:
            return

        node.right = pivot.left
        if pivot.left is not None:
            pivot.left.parent = node

        pivot.parent = node.parent
        if node.parent is None:
            self.root = pivot
        elif node == node.parent.left:
            node.parent.left = pivot
        else:
            node.parent.right = pivot

        pivot.left = node
        node.parent = pivot

    def _rotate_right(self, node: _SplayNode) -> None:
        """围绕 node 右旋，并维护父指针和根指针。"""

        # 右旋时 pivot 接管 node 的原位置，node 成为 pivot 的右孩子。
        pivot = node.left
        if pivot is None:
            return

        node.left = pivot.right
        if pivot.right is not None:
            pivot.right.parent = node

        pivot.parent = node.parent
        if node.parent is None:
            self.root = pivot
        elif node == node.parent.right:
            node.parent.right = pivot
        else:
            node.parent.left = pivot

        pivot.right = node
        node.parent = pivot

    def _inorder(self, node: _SplayNode | None, result: list[int]) -> None:
        """递归中序遍历。"""

        if node is None:
            return
        self._inorder(node.left, result)
        result.append(node.key)
        self._inorder(node.right, result)
