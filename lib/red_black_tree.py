from dataclasses import dataclass


RED = "RED"
BLACK = "BLACK"


@dataclass
class _RBNode:
    key: int
    color: str = RED
    left: "_RBNode | None" = None
    right: "_RBNode | None" = None
    parent: "_RBNode | None" = None


class RedBlackTree:
    def __init__(self) -> None:
        # 这里使用 None 代表外部黑色哨兵叶子，节点本身只保存真实 key。
        self.root: _RBNode | None = None

    def insert(self, key: int) -> None:
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
        node = self.root
        while node is not None:
            if key == node.key:
                return True
            node = node.left if key < node.key else node.right
        return False

    def inorder(self) -> list[int]:
        result: list[int] = []
        self._inorder(self.root, result)
        return result

    def validate(self) -> bool:
        # 红黑树根节点必须为黑色。
        if self.root is not None and self.root.color != BLACK:
            return False
        # 递归检查红色约束和所有路径黑高一致性。
        return self._validate_node(self.root)[0]

    def _validate_node(self, node: _RBNode | None) -> tuple[bool, int]:
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
        return BLACK if node is None else node.color

    def _inorder(self, node: _RBNode | None, result: list[int]) -> None:
        if node is None:
            return
        self._inorder(node.left, result)
        result.append(node.key)
        self._inorder(node.right, result)
