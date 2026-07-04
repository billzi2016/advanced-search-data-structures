"""斐波那契查找。

斐波那契查找和二分类似，都在升序数组中不断缩小候选区间。
区别在于它使用斐波那契数列决定分割点，历史上常用于减少某些存储模型下的
随机访问代价；在这里主要作为经典查找算法的可运行教学实现。
"""


def fibonacci_search(values: list[int], target: int) -> int:
    """在升序列表中使用斐波那契分割查找目标值。

    参数:
        values: 升序整数列表。
        target: 要查找的整数。

    返回:
        命中时返回第一个匹配下标；未命中时返回 -1。

    关键点:
        offset 表示已经被排除的左侧边界，fib/fib_minus_1/fib_minus_2
        则描述当前候选窗口的斐波那契大小。
    """

    # 斐波那契查找要求数组升序排列。
    # 它用斐波那契数控制分割点，思想上接近二分查找。
    n = len(values)
    if n == 0:
        return -1

    fib_minus_2 = 0
    fib_minus_1 = 1
    fib = fib_minus_1 + fib_minus_2

    # 找到不小于数组长度的最小斐波那契数。
    while fib < n:
        fib_minus_2 = fib_minus_1
        fib_minus_1 = fib
        fib = fib_minus_1 + fib_minus_2

    # offset 表示当前已经排除的左侧边界。
    offset = -1

    while fib > 1:
        # 防止分割点越过数组末尾。
        index = min(offset + fib_minus_2, n - 1)

        if values[index] < target:
            # 目标在右侧，整体窗口右移，并把斐波那契窗口缩小一级。
            fib = fib_minus_1
            fib_minus_1 = fib_minus_2
            fib_minus_2 = fib - fib_minus_1
            offset = index
        elif values[index] > target:
            # 目标在左侧，只缩小窗口，不移动 offset。
            fib = fib_minus_2
            fib_minus_1 = fib_minus_1 - fib_minus_2
            fib_minus_2 = fib - fib_minus_1
        else:
            # 重复元素时向左回退，返回第一个匹配位置。
            while index > 0 and values[index - 1] == target:
                index -= 1
            return index

    # 剩余一个候选位置时做最后确认。
    candidate = offset + 1
    if fib_minus_1 and candidate < n and values[candidate] == target:
        return candidate
    return -1
