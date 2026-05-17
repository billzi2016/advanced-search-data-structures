def exponential_search(values: list[int], target: int) -> int:
    # 指数查找要求数组升序排列。
    # 它先快速扩大右边界，再在确定区间内做二分查找。
    if not values:
        return -1

    if values[0] == target:
        return 0

    bound = 1
    # 右边界按 1, 2, 4, 8... 扩张，直到越界或遇到不小于目标的值。
    while bound < len(values) and values[bound] < target:
        bound *= 2

    # 目标只可能位于上一次边界之后到当前边界之间。
    return _binary_search_range(values, target, bound // 2 + 1, min(bound + 1, len(values)))


def _binary_search_range(values: list[int], target: int, left: int, right: int) -> int:
    # 在半开区间 [left, right) 内查找第一个大于等于 target 的位置。
    while left < right:
        mid = (left + right) // 2
        if values[mid] < target:
            left = mid + 1
        else:
            right = mid

    # 二分定位后仍要做一次值比较，避免把插入点误认为命中点。
    if left < len(values) and values[left] == target:
        return left
    return -1
