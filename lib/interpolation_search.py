"""插值查找。

插值查找把目标值在“值域”中的比例映射到数组下标区间，
因此更适合数值分布接近均匀的升序数组。它不是简单地取中点，
而是估算 target 更可能出现在哪里。
"""


def interpolation_search(values: list[int], target: int) -> int:
    """在近似均匀分布的升序列表中查找目标值。

    参数:
        values: 升序整数列表。
        target: 要查找的整数。

    返回:
        命中时返回第一个匹配下标；未命中时返回 -1。

    关键点:
        当当前区间两端值相同，比例估算会除以零，因此必须单独处理。
    """

    # 插值查找要求数组升序排列，并利用数值大小估计目标位置。
    # 当数据分布接近均匀时，它通常比普通二分更少探测。
    if not values:
        return -1

    low = 0
    high = len(values) - 1

    # 根据数值分布估计探测位置，适合近似均匀分布的有序数组。
    while low <= high and values[low] <= target <= values[high]:
        if values[low] == values[high]:
            # 当前区间所有值相同，无法继续按比例估算位置。
            return low if values[low] == target else -1

        span = values[high] - values[low]
        # offset 按 target 在值域中的比例映射到下标区间。
        offset = (target - values[low]) * (high - low) // span
        position = low + offset

        if values[position] == target:
            # 为了和其他查找函数保持一致，重复元素时返回第一个命中位置。
            while position > 0 and values[position - 1] == target:
                position -= 1
            return position
        if values[position] < target:
            # 估计位置仍偏小，丢弃左侧区间。
            low = position + 1
        else:
            # 估计位置偏大，丢弃右侧区间。
            high = position - 1

    return -1
