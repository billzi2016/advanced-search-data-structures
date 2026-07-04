"""线性查找。

本模块展示最朴素的查找方式：不建立索引，也不要求输入有序，
只从左到右逐个比较元素。它的时间复杂度是 O(n)，但实现简单，
也是理解其他查找算法收益的基线。
"""


def linear_search(values: list[int], target: int) -> int:
    """在列表中从左到右查找目标值。

    参数:
        values: 任意顺序的整数列表，可以为空，也可以包含重复值。
        target: 要查找的整数。

    返回:
        命中时返回第一个匹配位置；未命中时返回 -1。
    """

    # 线性查找不要求数组有序，适合小规模数据或没有索引的场景。
    # 从左到右逐个比较，命中后立即返回第一个匹配位置。
    for index, value in enumerate(values):
        if value == target:
            return index

    # 全部扫描完成仍未命中，用 -1 表示不存在。
    return -1
