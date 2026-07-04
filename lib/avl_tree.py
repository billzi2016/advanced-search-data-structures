"""AVL 树。

AVL 是严格高度平衡的二叉搜索树。每个节点保存子树高度，
插入或删除后沿递归回溯路径更新高度，并在平衡因子超过范围时旋转。
本模块重点展示 LL、LR、RR、RL 四类失衡如何统一收敛到局部旋转。
"""

from dataclasses import dataclass


@dataclass
class _AVLNode:
    """AVL 内部节点。

    height 是以当前节点为根的子树高度，空子树高度按 0 处理。
    插入、删除和旋转后必须及时更新，否则后续平衡判断会失真。
    """

    key: int
    left: "_AVLNode | None" = None
    right: "_AVLNode | None" = None
    height: int = 1


class AVLTree:
    """集合语义的 AVL 搜索树。"""

    def __init__(self) -> None:
        # AVL 树在每个节点维护高度，用高度差判断是否需要旋转。
        self.root: _AVLNode | None = None

    def insert(self, key: int) -> None:
        """插入 key，并在回溯阶段恢复 AVL 高度平衡。"""

        # 插入后沿递归回溯路径重新计算高度并恢复平衡。
        self.root = self._insert(self.root, key)

    def _insert(self, node: _AVLNode | None, key: int) -> _AVLNode:
        """递归插入 key，返回重平衡后的子树根。"""

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
        """按 BST 路径查找 key 是否存在。"""

        node = self.root
        while node is not None:
            if key == node.key:
                return True
            node = node.left if key < node.key else node.right
        return False

    def delete(self, key: int) -> None:
        """删除 key，并在受影响路径上恢复平衡。"""

        # 删除和插入一样可能改变根节点。
        self.root = self._delete(self.root, key)

    def _delete(self, node: _AVLNode | None, key: int) -> _AVLNode | None:
        """递归删除 key，返回删除并重平衡后的子树根。"""

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
        """返回所有 key 的升序列表，用于验证 BST 顺序性质。"""

        result: list[int] = []
        self._inorder(self.root, result)
        return result

    def is_balanced(self) -> bool:
        """检查整棵树是否满足 AVL 平衡条件和高度字段一致性。"""

        # 测试辅助方法：同时验证高度字段和 AVL 平衡条件。
        return self._check_balance(self.root) >= 0

    def _check_balance(self, node: _AVLNode | None) -> int:
        """返回子树高度；发现不平衡或高度字段错误时返回 -1。"""

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
        """递归中序遍历。"""

        if node is None:
            return
        self._inorder(node.left, result)
        result.append(node.key)
        self._inorder(node.right, result)

    def _minimum(self, node: _AVLNode) -> _AVLNode:
        """返回当前子树中的最小节点，用于两个孩子节点的删除替换。"""

        while node.left is not None:
            node = node.left
        return node

    def _height(self, node: _AVLNode | None) -> int:
        """读取节点高度；空节点高度定义为 0。"""

        return node.height if node is not None else 0

    def _update_height(self, node: _AVLNode) -> None:
        """根据左右子树高度刷新当前节点高度。"""

        # 当前节点高度等于更高子树高度加一。
        node.height = max(self._height(node.left), self._height(node.right)) + 1

    def _balance_factor(self, node: _AVLNode) -> int:
        """计算平衡因子：左子树高度减右子树高度。"""

        # 正数表示左高，负数表示右高。
        return self._height(node.left) - self._height(node.right)

    def _rebalance(self, node: _AVLNode) -> _AVLNode:
        """对一个可能失衡的子树执行必要旋转并返回新根。

        balance > 1 表示左侧过高，balance < -1 表示右侧过高。
        如果高的一侧内部朝相反方向倾斜，需要先对子节点做一次反向旋转。
        """

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
        """左旋当前子树，并返回旋转后的新根。"""

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
        """右旋当前子树，并返回旋转后的新根。"""

        # 右旋把左孩子提升为子树根，当前节点成为其右孩子。
        pivot = node.left
        if pivot is None:
            return node

        node.left = pivot.right
        pivot.right = node
        self._update_height(node)
        self._update_height(pivot)
        return pivot
