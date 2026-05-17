def binary_search(values: list[int], target: int) -> int:
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
