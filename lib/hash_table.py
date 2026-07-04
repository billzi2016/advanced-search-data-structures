"""开放寻址哈希表。

本模块实现一个集合语义的整数哈希表，冲突解决方式为线性探测。
删除时使用墓碑标记，而不是直接把槽位置空；否则后续冲突元素的探测链会被截断，
导致明明仍在表里的 key 查询失败。
"""

_TOMBSTONE = object()


class OpenAddressingHashTable:
    """使用线性探测和墓碑删除的开放寻址哈希表。"""

    def __init__(self, capacity: int = 8) -> None:
        """创建哈希表，并把容量提升到不小于输入值的 2 的幂。"""

        if capacity < 4:
            capacity = 4
        # 容量保持为 2 的幂，方便用位运算把 hash 映射到桶下标。
        self.capacity = self._next_power_of_two(capacity)
        self.size = 0
        # 槽位可能是 None、真实 int key，或删除后的墓碑标记。
        self._table: list[int | object | None] = [None] * self.capacity

    def add(self, key: int) -> None:
        """加入 key；如果已存在则保持不变。"""

        # 负载因子过高会增加线性探测长度，插入前先扩容。
        if (self.size + 1) / self.capacity > 0.65:
            self._resize(self.capacity * 2)

        index = self._find_slot(key)
        if self._table[index] == key:
            return
        self._table[index] = key
        self.size += 1

    def contains(self, key: int) -> bool:
        """沿探测链查找 key 是否存在。"""

        # 查询沿探测序列查找，直到命中 key 或遇到从未使用过的空槽。
        index = self._probe_for_key(key)
        return index is not None

    def remove(self, key: int) -> None:
        """删除 key；不存在时不做任何修改。"""

        index = self._probe_for_key(key)
        if index is None:
            return
        # 开放寻址不能直接置 None，否则会截断后续冲突 key 的探测链。
        self._table[index] = _TOMBSTONE
        self.size -= 1

        # 删除较多后收缩表，顺便清理墓碑。
        if self.capacity > 8 and self.size / self.capacity < 0.2:
            self._resize(self.capacity // 2)

    def to_list(self) -> list[int]:
        """返回表中真实 key 的升序列表，忽略空槽和墓碑。"""

        # 对外展示时忽略空槽和墓碑，并排序便于测试对比。
        return sorted(value for value in self._table if isinstance(value, int))

    def _find_slot(self, key: int) -> int:
        """为插入寻找槽位。

        如果探测过程中遇到墓碑，会记录第一个墓碑；只有确认后面没有同名 key 后，
        才复用墓碑位置，避免把同一个 key 插入两次。
        """

        first_tombstone: int | None = None
        index = self._hash(key)

        for _ in range(self.capacity):
            value = self._table[index]
            if value is None:
                # 优先复用探测过程中遇到的第一个墓碑。
                return first_tombstone if first_tombstone is not None else index
            if value is _TOMBSTONE and first_tombstone is None:
                first_tombstone = index
            elif value == key:
                return index
            # 线性探测：冲突后向后移动一个槽位。
            index = (index + 1) % self.capacity

        if first_tombstone is not None:
            return first_tombstone
        raise RuntimeError("hash table is full")

    def _probe_for_key(self, key: int) -> int | None:
        """沿线性探测序列寻找已有 key 的槽位。"""

        index = self._hash(key)
        for _ in range(self.capacity):
            value = self._table[index]
            if value is None:
                # 遇到真正空槽说明探测链结束，key 不存在。
                return None
            if value != _TOMBSTONE and value == key:
                return index
            index = (index + 1) % self.capacity
        return None

    def _resize(self, capacity: int) -> None:
        """重建哈希表到新容量，并在搬迁过程中清理墓碑。"""

        # 重新建表时只搬迁真实 key，墓碑会自然被清除。
        old_values = [value for value in self._table if isinstance(value, int)]
        self.capacity = self._next_power_of_two(capacity)
        self._table = [None] * self.capacity
        self.size = 0
        for value in old_values:
            self.add(value)

    def _hash(self, key: int) -> int:
        """把 Python hash 映射到当前表容量范围内。"""

        # capacity 是 2 的幂时，capacity - 1 可作为低位掩码。
        return hash(key) & (self.capacity - 1)

    def _next_power_of_two(self, value: int) -> int:
        """计算不小于 value 的最小 2 的幂。"""

        # 简单循环计算不小于 value 的最小 2 的幂。
        power = 1
        while power < value:
            power *= 2
        return power
