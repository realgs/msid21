from sorting import merge_sorted, radix_sort
from copy import copy

LENGTH = 2 << 10

if __name__ == '__main__':
    a = [1, 2, -13, 3, -7, 11, 3, 5, 7, 4, 9, 16, 34, -22, 17, 14]
    b = [121, 432, 564, 23, 1, 45, 4576, 1234, 5000, 23, 122, 788]
    b_ordered = sorted(b)

    assert merge_sorted(a) == sorted(a)
    assert merge_sorted(b) == sorted(b)
    radix_sort(b)
    assert b == b_ordered

    same_elements = [5] * LENGTH

    assert merge_sorted(same_elements) == sorted(same_elements)
    same_elements_cpy = copy(same_elements)
    radix_sort(same_elements_cpy)
    assert same_elements_cpy == sorted(same_elements)

    empty = []

    assert merge_sorted(empty) == []
    radix_sort(empty)
    assert empty == []

    range1 = list(range(LENGTH))
    range2 = list(range(LENGTH, 0, -1))

    assert merge_sorted(range1) == sorted(range1)
    assert merge_sorted(range2) == sorted(range2)

    range1_cpy, range2_cpy = copy(range1), copy(range2)
    radix_sort(range1_cpy)
    radix_sort(range2_cpy)
    assert range1_cpy == sorted(range1)
    assert range2_cpy == sorted(range2)
