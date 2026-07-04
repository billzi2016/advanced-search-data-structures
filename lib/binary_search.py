"""二分查找。

本模块实现 lower_bound 风格的二分查找：先找到第一个大于等于目标值的位置，
再检查该位置是否真的等于目标值。这样写可以自然处理重复元素，
并返回重复元素中的第一个下标。
"""


def binary_search(values: list[int], target: int) -> int:
    """在升序列表中查找目标值。

    参数:
        values: 已经按升序排列的整数列表。
        target: 要查找的整数。

    返回:
        目标存在时返回第一个匹配下标；不存在时返回 -1。

    注意:
        如果调用方传入未排序列表，二分查找的区间收缩假设会失效。
    """

    # 二分查找要求输入数组已经按升序排列。
    # 查找第一个大于等于 target 的位置，再判断是否命中。
    # 这种写法天然返回重复元素中的第一个位置。
    left = 0
    right = len(values)

    while left < right:
        mid = (left + right) // 2
        if values[mid] < target:
            # 中点值仍然偏小，目标只可能出现在右半区间。
            left = mid + 1
        else:
            # 中点值大于等于目标，保留 mid 位置继续向左收缩。
            right = mid

    # left 是 lower_bound 位置，必须再次比较才能确认是否真正命中。
    if left < len(values) and values[left] == target:
        return left
    return -1
