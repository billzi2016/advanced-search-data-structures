"""Treap。

Treap 同时满足两种性质：按 key 看是二叉搜索树，按 priority 看是堆。
这里使用确定性混合函数为 key 生成 priority，避免测试时出现随机结构差异；
工程上也可以把 priority 换成随机数来获得期望平衡。
"""

from dataclasses import dataclass


@dataclass
class _TreapNode:
    """Treap 内部节点。

    priority 越小表示堆优先级越高，节点越应该靠近根。
    """

    key: int
    priority: int
    left: "_TreapNode | None" = None
    right: "_TreapNode | None" = None


class Treap:
    """集合语义的 Treap 搜索树。"""

    def __init__(self) -> None:
        # Treap 同时满足 key 的 BST 性质和 priority 的小根堆性质。
        self.root: _TreapNode | None = None

    def insert(self, key: int) -> None:
        """插入 key，并通过旋转恢复 priority 小根堆性质。"""

        # 插入先按 BST 规则落位，再通过旋转恢复优先级堆性质。
        self.root = self._insert(self.root, key)

    def _insert(self, node: _TreapNode | None, key: int) -> _TreapNode:
        """递归插入，返回旋转调整后的子树根。"""

        if node is None:
            # priority 使用确定性函数生成，避免测试中出现随机波动。
            return _TreapNode(key=key, priority=self._priority(key))

        if key < node.key:
            node.left = self._insert(node.left, key)
            if node.left is not None and node.left.priority < node.priority:
                # 左孩子优先级更高时右旋，让它上浮。
                node = self._rotate_right(node)
        elif key > node.key:
            node.right = self._insert(node.right, key)
            if node.right is not None and node.right.priority < node.priority:
                # 右孩子优先级更高时左旋，让它上浮。
                node = self._rotate_left(node)
        # 相等 key 被忽略，保持集合语义。

        return node

    def contains(self, key: int) -> bool:
        """按 BST 路径查找 key 是否存在。"""

        node = self.root
        while node is not None:
            if key == node.key:
                return True
            node = node.left if key < node.key else node.right
        return False

    def delete(self, key: int) -> None:
        """删除 key，并在递归过程中保持 Treap 双重性质。"""

        # 删除时把目标节点向下旋转，直到可以被一个孩子直接替换。
        self.root = self._delete(self.root, key)

    def _delete(self, node: _TreapNode | None, key: int) -> _TreapNode | None:
        """递归删除 key。

        两个孩子都存在时，先让 priority 更高的孩子旋转上来，
        再继续在被旋转下去的子树中删除目标 key。
        """

        if node is None:
            return None

        if key < node.key:
            node.left = self._delete(node.left, key)
        elif key > node.key:
            node.right = self._delete(node.right, key)
        else:
            # 少于两个孩子时可以直接删除。
            if node.left is None:
                return node.right
            if node.right is None:
                return node.left

            # 两个孩子都存在时，让优先级更高的孩子上浮，再继续删除目标 key。
            if node.left.priority < node.right.priority:
                node = self._rotate_right(node)
                node.right = self._delete(node.right, key)
            else:
                node = self._rotate_left(node)
                node.left = self._delete(node.left, key)

        return node

    def inorder(self) -> list[int]:
        """返回所有 key 的升序列表。"""

        result: list[int] = []
        self._inorder(self.root, result)
        return result

    def _rotate_left(self, node: _TreapNode) -> _TreapNode:
        """左旋子树并返回新的子树根。"""

        # 左旋保持中序顺序，同时让右孩子成为新的子树根。
        pivot = node.right
        if pivot is None:
            return node

        node.right = pivot.left
        pivot.left = node
        return pivot

    def _rotate_right(self, node: _TreapNode) -> _TreapNode:
        """右旋子树并返回新的子树根。"""

        # 右旋保持中序顺序，同时让左孩子成为新的子树根。
        pivot = node.left
        if pivot is None:
            return node

        node.left = pivot.right
        pivot.right = node
        return pivot

    def _priority(self, key: int) -> int:
        """根据 key 生成确定性 priority。

        混合常数来自常见 64 位哈希扰动写法，目的不是加密，
        而是把相近 key 打散，避免优先级与 key 顺序强相关。
        """

        # 使用确定性混合函数生成优先级，便于测试复现。
        # 实际工程里也可以换成随机数，这里更强调可重复验证。
        value = (key + 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
        value = (value ^ (value >> 30)) * 0xBF58476D1CE4E5B9 & 0xFFFFFFFFFFFFFFFF
        value = (value ^ (value >> 27)) * 0x94D049BB133111EB & 0xFFFFFFFFFFFFFFFF
        return value ^ (value >> 31)

    def _inorder(self, node: _TreapNode | None, result: list[int]) -> None:
        """递归中序遍历。"""

        if node is None:
            return
        self._inorder(node.left, result)
        result.append(node.key)
        self._inorder(node.right, result)
