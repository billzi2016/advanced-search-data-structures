"""跳表。

跳表用多层有序链表模拟平衡搜索结构。第 0 层保存所有 key，
更高层保存部分 key 作为快速通道。查找时从最高层向右走，无法继续时下降一层。
本实现用确定性层数函数代替随机抛硬币，方便测试和结果复现。
"""

from dataclasses import dataclass, field


@dataclass
class _SkipNode:
    """跳表节点。

    key 为 None 的节点只用作 head 哨兵；forward[i] 指向第 i 层的下一个节点。
    """

    key: int | None
    forward: list["_SkipNode | None"] = field(default_factory=list)


class SkipList:
    """集合语义的跳表。"""

    def __init__(self, max_level: int = 8) -> None:
        """创建跳表。

        参数:
            max_level: 允许的最高层数。层数越高，索引越稀疏但查找路径更短。
        """

        if max_level < 1:
            raise ValueError("max_level must be at least 1")
        # max_level 是跳表最高层数，head 在每一层都有前向指针。
        self.max_level = max_level
        # level 表示当前实际使用到的最高层数。
        self.level = 1
        self.head = _SkipNode(key=None, forward=[None] * max_level)

    def insert(self, key: int) -> None:
        """插入 key；如果 key 已存在则不重复插入。"""

        # update[i] 记录第 i 层中，插入位置左侧的最后一个节点。
        update = self._find_update_path(key)
        candidate = update[0].forward[0]
        if candidate is not None and candidate.key == key:
            return

        # 每个 key 的层数由确定性函数决定，避免随机测试不稳定。
        node_level = self._level_for_key(key)
        if node_level > self.level:
            # 新节点层数超过当前高度时，高出的层都从 head 后面插入。
            for index in range(self.level, node_level):
                update[index] = self.head
            self.level = node_level

        node = _SkipNode(key=key, forward=[None] * node_level)
        for index in range(node_level):
            # 标准链表插入：新节点指向后继，前驱再指向新节点。
            node.forward[index] = update[index].forward[index]
            update[index].forward[index] = node

    def contains(self, key: int) -> bool:
        """从最高层开始查找 key 是否存在。"""

        current = self.head
        # 从最高层开始尽量向右走，无法前进时下降一层。
        for index in range(self.level - 1, -1, -1):
            while current.forward[index] is not None and current.forward[index].key < key:
                current = current.forward[index]

        # 第 0 层是完整有序链表，最终候选节点在 current 的右侧。
        candidate = current.forward[0]
        return candidate is not None and candidate.key == key

    def delete(self, key: int) -> None:
        """删除 key，并清理已经为空的最高层。"""

        # 删除同样需要先找到每一层的前驱节点。
        update = self._find_update_path(key)
        candidate = update[0].forward[0]
        if candidate is None or candidate.key != key:
            return

        for index in range(self.level):
            if update[index].forward[index] != candidate:
                continue
            # 只在包含该节点的层上断开链接。
            update[index].forward[index] = candidate.forward[index] if index < len(candidate.forward) else None

        # 如果最高层已经没有元素，降低跳表当前高度。
        while self.level > 1 and self.head.forward[self.level - 1] is None:
            self.level -= 1

    def to_list(self) -> list[int]:
        """遍历第 0 层，返回所有 key 的升序列表。"""

        # 第 0 层包含所有 key，顺序遍历即可得到升序列表。
        result: list[int] = []
        node = self.head.forward[0]
        while node is not None:
            if node.key is not None:
                result.append(node.key)
            node = node.forward[0]
        return result

    def _find_update_path(self, key: int) -> list[_SkipNode]:
        """返回每一层中位于 key 插入/删除位置左侧的前驱节点。"""

        update = [self.head] * self.max_level
        current = self.head

        # 记录搜索路径，供插入和删除复用。
        for index in range(self.level - 1, -1, -1):
            while current.forward[index] is not None and current.forward[index].key < key:
                current = current.forward[index]
            update[index] = current

        return update

    def _level_for_key(self, key: int) -> int:
        """用确定性哈希为 key 计算节点层数。"""

        # 使用确定性哈希决定层数，使跳表结构可复现。
        # 哈希低位连续为 1 的数量越多，节点层数越高。
        value = (key + 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
        level = 1
        while level < self.max_level and value & 1:
            level += 1
            value >>= 1
        return level
