from dataclasses import dataclass


@dataclass
class _AVLNode:
    key: int
    left: "_AVLNode | None" = None
    right: "_AVLNode | None" = None
    height: int = 1


class AVLTree:
    def __init__(self) -> None:
        # AVL 树在每个节点维护高度，用高度差判断是否需要旋转。
        self.root: _AVLNode | None = None

    def insert(self, key: int) -> None:
        # 插入后沿递归回溯路径重新计算高度并恢复平衡。
        self.root = self._insert(self.root, key)

    def _insert(self, node: _AVLNode | None, key: int) -> _AVLNode:
        if node is None:
            return _AVLNode(key)

        if key < node.key:
            node.left = self._insert(node.left, key)
        elif key > node.key:
            node.right = self._insert(node.right, key)
        else:
            # AVLTree 在这里按集合处理，重复 key 不再插入。
            return node

        # 插入可能让当前节点的左右高度差超过 1，需要重平衡。
        return self._rebalance(node)

    def contains(self, key: int) -> bool:
        node = self.root
        while node is not None:
            if key == node.key:
                return True
            node = node.left if key < node.key else node.right
        return False

    def delete(self, key: int) -> None:
        # 删除和插入一样可能改变根节点。
        self.root = self._delete(self.root, key)

    def _delete(self, node: _AVLNode | None, key: int) -> _AVLNode | None:
        if node is None:
            return None

        if key < node.key:
            node.left = self._delete(node.left, key)
        elif key > node.key:
            node.right = self._delete(node.right, key)
        else:
            # 一个孩子以内时直接提升孩子节点。
            if node.left is None:
                return node.right
            if node.right is None:
                return node.left

            # 两个孩子时使用右子树最小节点替换，再删除后继节点。
            successor = self._minimum(node.right)
            node.key = successor.key
            node.right = self._delete(node.right, successor.key)

        # 删除后同样要更新高度并检查四种旋转情况。
        return self._rebalance(node)

    def inorder(self) -> list[int]:
        result: list[int] = []
        self._inorder(self.root, result)
        return result

    def is_balanced(self) -> bool:
        # 测试辅助方法：同时验证高度字段和 AVL 平衡条件。
        return self._check_balance(self.root) >= 0

    def _check_balance(self, node: _AVLNode | None) -> int:
        if node is None:
            return 0
        left_height = self._check_balance(node.left)
        right_height = self._check_balance(node.right)
        if left_height < 0 or right_height < 0:
            return -1
        if abs(left_height - right_height) > 1:
            return -1
        if node.height != max(left_height, right_height) + 1:
            return -1
        return node.height

    def _inorder(self, node: _AVLNode | None, result: list[int]) -> None:
        if node is None:
            return
        self._inorder(node.left, result)
        result.append(node.key)
        self._inorder(node.right, result)

    def _minimum(self, node: _AVLNode) -> _AVLNode:
        while node.left is not None:
            node = node.left
        return node

    def _height(self, node: _AVLNode | None) -> int:
        return node.height if node is not None else 0

    def _update_height(self, node: _AVLNode) -> None:
        # 当前节点高度等于更高子树高度加一。
        node.height = max(self._height(node.left), self._height(node.right)) + 1

    def _balance_factor(self, node: _AVLNode) -> int:
        # 正数表示左高，负数表示右高。
        return self._height(node.left) - self._height(node.right)

    def _rebalance(self, node: _AVLNode) -> _AVLNode:
        self._update_height(node)
        balance = self._balance_factor(node)

        if balance > 1:
            # 左子树过高。若左孩子右倾，先左旋左孩子，再右旋当前节点。
            if node.left is not None and self._balance_factor(node.left) < 0:
                node.left = self._rotate_left(node.left)
            return self._rotate_right(node)

        if balance < -1:
            # 右子树过高。若右孩子左倾，先右旋右孩子，再左旋当前节点。
            if node.right is not None and self._balance_factor(node.right) > 0:
                node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

        return node

    def _rotate_left(self, node: _AVLNode) -> _AVLNode:
        # 左旋把右孩子提升为子树根，当前节点成为其左孩子。
        pivot = node.right
        if pivot is None:
            return node

        node.right = pivot.left
        pivot.left = node
        self._update_height(node)
        self._update_height(pivot)
        return pivot

    def _rotate_right(self, node: _AVLNode) -> _AVLNode:
        # 右旋把左孩子提升为子树根，当前节点成为其右孩子。
        pivot = node.left
        if pivot is None:
            return node

        node.left = pivot.right
        pivot.right = node
        self._update_height(node)
        self._update_height(pivot)
        return pivot
