"""红黑树。

本模块实现插入版红黑树，用颜色约束维持近似平衡。
红黑树没有 AVL 那么严格的高度平衡，但通过“根黑、红节点不相邻、
从任一节点到叶子的黑节点数一致”等规则，把树高限制在 O(log n)。
"""

from dataclasses import dataclass


RED = "RED"
BLACK = "BLACK"


@dataclass
class _RBNode:
    """红黑树内部节点。

    parent 指针让旋转和插入修复可以从当前节点向上调整。
    None 子节点在红黑树定义中视为黑色外部叶子。
    """

    key: int
    color: str = RED
    left: "_RBNode | None" = None
    right: "_RBNode | None" = None
    parent: "_RBNode | None" = None


class RedBlackTree:
    """集合语义的红黑树。

    当前实现支持插入、查找、中序遍历和结构校验；删除尚未实现，
    因此主测试会跳过红黑树删除场景。
    """

    def __init__(self) -> None:
        # 这里使用 None 代表外部黑色哨兵叶子，节点本身只保存真实 key。
        self.root: _RBNode | None = None

    def insert(self, key: int) -> None:
        """按 BST 规则插入红色新节点，然后修复红黑性质。"""

        # 先按普通 BST 规则找到插入位置，新节点默认染红。
        parent: _RBNode | None = None
        current = self.root

        while current is not None:
            parent = current
            if key == current.key:
                return
            current = current.left if key < current.key else current.right

        node = _RBNode(key=key, parent=parent)
        if parent is None:
            self.root = node
        elif key < parent.key:
            parent.left = node
        else:
            parent.right = node

        # 红节点可能破坏“红节点不能有红孩子”的规则，需要插入修复。
        self._fix_insert(node)

    def contains(self, key: int) -> bool:
        """按 BST 路径查找 key 是否存在。"""

        node = self.root
        while node is not None:
            if key == node.key:
                return True
            node = node.left if key < node.key else node.right
        return False

    def inorder(self) -> list[int]:
        """返回所有 key 的升序列表。"""

        result: list[int] = []
        self._inorder(self.root, result)
        return result

    def validate(self) -> bool:
        """检查根节点颜色、连续红节点约束和黑高一致性。"""

        # 红黑树根节点必须为黑色。
        if self.root is not None and self.root.color != BLACK:
            return False
        # 递归检查红色约束和所有路径黑高一致性。
        return self._validate_node(self.root)[0]

    def _validate_node(self, node: _RBNode | None) -> tuple[bool, int]:
        """递归校验子树并返回校验结果和黑高。

        黑高指从当前节点到任意外部叶子路径上的黑节点数量。
        红黑树要求同一节点的左右子树黑高相同。
        """

        if node is None:
            # None 叶子视为黑色，高度贡献 1。
            return True, 1

        if node.color == RED:
            # 红节点的左右孩子都必须是黑色。
            if self._color(node.left) == RED or self._color(node.right) == RED:
                return False, 0

        left_valid, left_black_height = self._validate_node(node.left)
        right_valid, right_black_height = self._validate_node(node.right)
        if not left_valid or not right_valid:
            return False, 0
        if left_black_height != right_black_height:
            return False, 0

        black_height = left_black_height + (1 if node.color == BLACK else 0)
        return True, black_height

    def _fix_insert(self, node: _RBNode) -> None:
        """修复插入红节点后可能出现的连续红节点问题。

        处理分三类：叔叔为红时重新染色并向上递归；叔叔为黑且当前形态是折线时
        先旋转成直线；直线形态下再通过一次旋转和变色恢复局部平衡。
        """

        # 只要父节点是红色，就说明出现了连续红节点，需要向上修复。
        while node.parent is not None and node.parent.color == RED:
            parent = node.parent
            grandparent = parent.parent
            if grandparent is None:
                break

            if parent == grandparent.left:
                uncle = grandparent.right
                if self._color(uncle) == RED:
                    # 情况 1：叔叔也是红色，父叔染黑，祖父染红，继续向上检查。
                    parent.color = BLACK
                    if uncle is not None:
                        uncle.color = BLACK
                    grandparent.color = RED
                    node = grandparent
                else:
                    if node == parent.right:
                        # 情况 2：左-右折线，先把它旋转成左-左直线。
                        node = parent
                        self._rotate_left(node)
                        parent = node.parent
                        grandparent = parent.parent if parent is not None else None
                    if parent is not None and grandparent is not None:
                        # 情况 3：左-左直线，变色后右旋祖父。
                        parent.color = BLACK
                        grandparent.color = RED
                        self._rotate_right(grandparent)
            else:
                uncle = grandparent.left
                if self._color(uncle) == RED:
                    # 镜像情况 1：叔叔为红色时只需要重新染色。
                    parent.color = BLACK
                    if uncle is not None:
                        uncle.color = BLACK
                    grandparent.color = RED
                    node = grandparent
                else:
                    if node == parent.left:
                        # 镜像情况 2：右-左折线，先右旋父节点。
                        node = parent
                        self._rotate_right(node)
                        parent = node.parent
                        grandparent = parent.parent if parent is not None else None
                    if parent is not None and grandparent is not None:
                        # 镜像情况 3：右-右直线，变色后左旋祖父。
                        parent.color = BLACK
                        grandparent.color = RED
                        self._rotate_left(grandparent)

        if self.root is not None:
            # 不管中间怎么调整，最终根节点必须保持黑色。
            self.root.color = BLACK

    def _rotate_left(self, node: _RBNode) -> None:
        """围绕 node 做左旋，并维护父指针和根指针。"""

        # 左旋保持中序顺序不变，只调整局部父子关系。
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

    def _rotate_right(self, node: _RBNode) -> None:
        """围绕 node 做右旋，并维护父指针和根指针。"""

        # 右旋是左旋的镜像操作。
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

    def _color(self, node: _RBNode | None) -> str:
        """读取节点颜色；None 外部叶子按黑色处理。"""

        return BLACK if node is None else node.color

    def _inorder(self, node: _RBNode | None, result: list[int]) -> None:
        """递归中序遍历。"""

        if node is None:
            return
        self._inorder(node.left, result)
        result.append(node.key)
        self._inorder(node.right, result)
