"""二叉搜索树 BST。

本模块实现最基础的二叉搜索树，用来作为其他平衡树的对照组。
BST 只依赖“左子树 key 更小、右子树 key 更大”的有序性质，
不维护高度、颜色或随机优先级，因此最坏情况下可能退化成链表。
"""

from dataclasses import dataclass


@dataclass
class _BSTNode:
    """BST 内部节点。

    key 是参与比较和查找的唯一值；left/right 分别指向更小和更大的子树。
    这个项目按集合语义处理重复 key，所以节点中不维护计数。
    """

    key: int
    left: "_BSTNode | None" = None
    right: "_BSTNode | None" = None


class BST:
    """未平衡二叉搜索树。

    提供插入、查找、删除和中序遍历。它适合理解搜索树的基本递归结构，
    但不适合作为稳定的高性能索引，因为输入有序时高度会变成 O(n)。
    """

    def __init__(self) -> None:
        # root 为整棵二叉搜索树的入口，空树时为 None。
        self.root: _BSTNode | None = None

    def insert(self, key: int) -> None:
        """插入一个 key；如果 key 已存在，则保持原树不变。"""

        # 对外只暴露 key 插入，具体递归逻辑交给 _insert。
        self.root = self._insert(self.root, key)

    def _insert(self, node: _BSTNode | None, key: int) -> _BSTNode:
        """递归插入并返回当前子树的新根。

        返回新根的写法可以统一处理“空子树创建节点”和“子树根未变化”两种情况。
        """

        if node is None:
            # 找到空位置后创建新节点。
            return _BSTNode(key)
        if key < node.key:
            # 小于当前节点的值放入左子树。
            node.left = self._insert(node.left, key)
        elif key > node.key:
            # 大于当前节点的值放入右子树。
            node.right = self._insert(node.right, key)
        # 相等时直接忽略，保持集合语义，不存重复 key。
        return node

    def contains(self, key: int) -> bool:
        """利用 BST 有序性质查找 key 是否存在。"""

        node = self.root
        while node is not None:
            if key == node.key:
                return True
            # 利用 BST 有序性质，每次只需要进入一侧子树。
            node = node.left if key < node.key else node.right
        return False

    def delete(self, key: int) -> None:
        """删除 key；不存在时不改变树。"""

        # 删除可能改变根节点，所以要接收递归返回的新根。
        self.root = self._delete(self.root, key)

    def _delete(self, node: _BSTNode | None, key: int) -> _BSTNode | None:
        """递归删除 key 并返回当前子树的新根。

        删除有三类情况：无孩子、一个孩子、两个孩子。两个孩子时用右子树最小节点
        作为后继替换当前 key，这样可以保持中序顺序不变。
        """

        if node is None:
            return None

        if key < node.key:
            node.left = self._delete(node.left, key)
        elif key > node.key:
            node.right = self._delete(node.right, key)
        else:
            # 只有一个孩子或没有孩子时，可以直接用孩子替换当前节点。
            if node.left is None:
                return node.right
            if node.right is None:
                return node.left

            # 两个孩子都存在时，用右子树最小节点作为后继替换当前节点。
            successor = self._minimum(node.right)
            node.key = successor.key
            node.right = self._delete(node.right, successor.key)

        return node

    def _minimum(self, node: _BSTNode) -> _BSTNode:
        """返回当前子树中 key 最小的节点。"""

        # BST 中最小值一定在最左侧路径上。
        while node.left is not None:
            node = node.left
        return node

    def inorder(self) -> list[int]:
        """返回所有 key 的升序列表。"""

        # 中序遍历 BST 会得到升序结果，是验证结构正确性的关键接口。
        result: list[int] = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node: _BSTNode | None, result: list[int]) -> None:
        """递归中序遍历，把结果追加到调用方传入的列表中。"""

        if node is None:
            return
        self._inorder(node.left, result)
        result.append(node.key)
        self._inorder(node.right, result)
