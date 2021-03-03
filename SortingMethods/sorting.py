__all__ = ["merge_sort"]


def merge(left: list, right: list) -> list:
    result = []
    i, j = 0, 0
    size_left, size_right = len(left), len(right)

    while i < size_left and j < size_right:
        if left[i] < right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    result = result + left[i:] if i < size_left else result + right[j:]

    return result


def merge_sort(xs: list) -> list:
    if len(xs) <= 1:
        return xs

    mid = len(xs) // 2
    left, right = xs[:mid], xs[mid:]

    return merge(merge_sort(left), merge_sort(right))
