from dataclasses import dataclass, field


@dataclass
class _SkipNode:
    key: int | None
    forward: list["_SkipNode | None"] = field(default_factory=list)


class SkipList:
    def __init__(self, max_level: int = 8) -> None:
        if max_level < 1:
            raise ValueError("max_level must be at least 1")
        # max_level 是跳表最高层数，head 在每一层都有前向指针。
        self.max_level = max_level
        # level 表示当前实际使用到的最高层数。
        self.level = 1
        self.head = _SkipNode(key=None, forward=[None] * max_level)

    def insert(self, key: int) -> None:
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
        current = self.head
        # 从最高层开始尽量向右走，无法前进时下降一层。
        for index in range(self.level - 1, -1, -1):
            while current.forward[index] is not None and current.forward[index].key < key:
                current = current.forward[index]

        # 第 0 层是完整有序链表，最终候选节点在 current 的右侧。
        candidate = current.forward[0]
        return candidate is not None and candidate.key == key

    def delete(self, key: int) -> None:
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
        # 第 0 层包含所有 key，顺序遍历即可得到升序列表。
        result: list[int] = []
        node = self.head.forward[0]
        while node is not None:
            if node.key is not None:
                result.append(node.key)
            node = node.forward[0]
        return result

    def _find_update_path(self, key: int) -> list[_SkipNode]:
        update = [self.head] * self.max_level
        current = self.head

        # 记录搜索路径，供插入和删除复用。
        for index in range(self.level - 1, -1, -1):
            while current.forward[index] is not None and current.forward[index].key < key:
                current = current.forward[index]
            update[index] = current

        return update

    def _level_for_key(self, key: int) -> int:
        # 使用确定性哈希决定层数，使跳表结构可复现。
        # 哈希低位连续为 1 的数量越多，节点层数越高。
        value = (key + 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
        level = 1
        while level < self.max_level and value & 1:
            level += 1
            value >>= 1
        return level
