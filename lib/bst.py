from dataclasses import dataclass


@dataclass
class _BSTNode:
    key: int
    left: "_BSTNode | None" = None
    right: "_BSTNode | None" = None


class BST:
    def __init__(self) -> None:
        # root 为整棵二叉搜索树的入口，空树时为 None。
        self.root: _BSTNode | None = None

    def insert(self, key: int) -> None:
        # 对外只暴露 key 插入，具体递归逻辑交给 _insert。
        self.root = self._insert(self.root, key)

    def _insert(self, node: _BSTNode | None, key: int) -> _BSTNode:
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
        node = self.root
        while node is not None:
            if key == node.key:
                return True
            # 利用 BST 有序性质，每次只需要进入一侧子树。
            node = node.left if key < node.key else node.right
        return False

    def delete(self, key: int) -> None:
        # 删除可能改变根节点，所以要接收递归返回的新根。
        self.root = self._delete(self.root, key)

    def _delete(self, node: _BSTNode | None, key: int) -> _BSTNode | None:
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
        # BST 中最小值一定在最左侧路径上。
        while node.left is not None:
            node = node.left
        return node

    def inorder(self) -> list[int]:
        # 中序遍历 BST 会得到升序结果，是验证结构正确性的关键接口。
        result: list[int] = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node: _BSTNode | None, result: list[int]) -> None:
        if node is None:
            return
        self._inorder(node.left, result)
        result.append(node.key)
        self._inorder(node.right, result)
