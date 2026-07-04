"""跳跃查找。

跳跃查找适用于升序数组。它先按固定步长跨块跳跃，找到目标可能所在的块，
再在块内线性扫描。步长通常取 sqrt(n)，目的是让“跳多少次”和
“块内扫多少次”保持同一数量级。
"""

import math


def jump_search(values: list[int], target: int) -> int:
    """在升序列表中使用跳跃查找定位目标值。

    参数:
        values: 已经升序排列的整数列表。
        target: 要查找的整数。

    返回:
        命中时返回目标所在下标；未命中时返回 -1。
    """

    # 跳跃查找要求输入数组升序排列。
    if not values:
        return -1

    n = len(values)
    # 常用步长取 sqrt(n)，可以把跳跃次数和块内扫描次数平衡到同一量级。
    step = int(math.sqrt(n)) or 1
    previous = 0
    current = step

    # 先按固定步长跳跃，定位目标可能所在的块。
    while previous < n and values[min(current, n) - 1] < target:
        previous = current
        current += step
        if previous >= n:
            # 跳过数组末尾仍未遇到不小于目标的块，说明目标不存在。
            return -1

    # 在块内执行线性扫描。
    for index in range(previous, min(current, n)):
        if values[index] == target:
            return index
        if values[index] > target:
            # 块内已经出现更大的值，后续元素只会更大，可以提前结束。
            break

    return -1
