__all__ = ["merge_sorted", "radix_sort"]


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


def merge_sorted(xs: list) -> list:
    if len(xs) <= 1:
        return xs

    mid = len(xs) // 2
    left, right = xs[:mid], xs[mid:]

    return merge(merge_sorted(left), merge_sorted(right))


def radix_sort(xs: list[int]) -> None:
    """Accepts list of integers of the same sign"""

    if xs:
        base = 10
        n = 0
        max_integer_length = len(str(max(xs)))

        while max_integer_length > n:
            buckets: list[list[int]] = [[] for _ in range(10)]

            for x in xs:
                buckets[x // (base ** n) % 10].append(x)

            i = 0
            for bucket in buckets:
                for x in bucket:
                    xs[i] = x
                    i += 1

            n += 1
