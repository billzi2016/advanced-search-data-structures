def interpolation_search(values: list[int], target: int) -> int:
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
