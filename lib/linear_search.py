def linear_search(values: list[int], target: int) -> int:
    # 线性查找不要求数组有序，适合小规模数据或没有索引的场景。
    # 从左到右逐个比较，命中后立即返回第一个匹配位置。
    for index, value in enumerate(values):
        if value == target:
            return index

    # 全部扫描完成仍未命中，用 -1 表示不存在。
    return -1
