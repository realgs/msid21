import random


def main():
    # test_bubble_sort()
    test_quick_sort()


def test_bubble_sort():
    arr = [4324.432, -234.2, 43.2, 5, 10000, 5, 0, 1, 2, -5324.00043]
    bubble_sort(arr)
    assert arr == [-5324.00043, -234.2, 0, 1, 2, 5, 5, 43.2, 4324.432, 10000]

    arr = [0, 0, 0, 0, 0, 0]
    bubble_sort(arr)
    assert arr == [0, 0, 0, 0, 0, 0]

    arr = [0, 0, 0, 0, 0, -100.43]
    bubble_sort(arr)
    assert arr == [-100.43, 0, 0, 0, 0, 0]

    arr = [0, 0, 0, 100.54, 0, 0]
    bubble_sort(arr)
    assert arr == [0, 0, 0, 0, 0, 100.54]

    arr = [-5.002, -4.1, -3, -2.999, -1, 0, 1.5, 2, 3.7, 4, 5]
    bubble_sort(arr)
    assert arr == [-5.002, -4.1, -3, -2.999, -1, 0, 1.5, 2, 3.7, 4, 5]

    arr = [100.5, 50.4004, 35.84, 24, 15.9, 8, 0.0001, -0.0001, -6, -17.75, -29.43, -33, -77.0032001, -13123.1]
    bubble_sort(arr)
    assert arr == [-13123.1, -77.0032001, -33, -29.43, -17.75, -6, -0.0001, 0.0001, 8, 15.9, 24, 35.84, 50.4004, 100.5]

    arr = random.sample(range(-10000, 10000), 1000)
    arr_copy = arr.copy()
    bubble_sort(arr)
    arr_copy.sort()
    assert arr == arr_copy

    arr = []
    bubble_sort(arr)
    assert arr == []


def test_quick_sort():
    arr = [4324.432, -234.2, 43.2, 5, 10000, 5, 0, 1, 2, -5324.00043]
    quick_sort(arr)
    assert arr == [-5324.00043, -234.2, 0, 1, 2, 5, 5, 43.2, 4324.432, 10000]

    arr = [0, 0, 0, 0, 0, 0]
    quick_sort(arr)
    assert arr == [0, 0, 0, 0, 0, 0]

    arr = [0, 0, 0, 0, 0, -100.43]
    quick_sort(arr)
    assert arr == [-100.43, 0, 0, 0, 0, 0]

    arr = [0, 0, 0, 100.54, 0, 0]
    quick_sort(arr)
    assert arr == [0, 0, 0, 0, 0, 100.54]

    arr = [-5.002, -4.1, -3, -2.999, -1, 0, 1.5, 2, 3.7, 4, 5]
    quick_sort(arr)
    assert arr == [-5.002, -4.1, -3, -2.999, -1, 0, 1.5, 2, 3.7, 4, 5]

    arr = [100.5, 50.4004, 35.84, 24, 15.9, 8, 0.0001, -0.0001, -6, -17.75, -29.43, -33, -77.0032001, -13123.1]
    quick_sort(arr)
    assert arr == [-13123.1, -77.0032001, -33, -29.43, -17.75, -6, -0.0001, 0.0001, 8, 15.9, 24, 35.84, 50.4004, 100.5]

    arr = random.sample(range(-10000, 10000), 1000)
    arr_copy = arr.copy()
    quick_sort(arr)
    arr_copy.sort()
    assert arr == arr_copy

    arr = []
    quick_sort(arr)
    assert arr == []


def bubble_sort(arr):
    n = len(arr)

    for i in range(n - 1):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                swap(arr, j, j + 1)


def swap(arr, left, right):
    if left != right:
        arr[left], arr[right] = arr[right], arr[left]


def quick_sort(arr):
    quicksort(arr, 0, len(arr))


def quicksort(arr, start_index, end_index):
    if end_index - start_index > 1:
        part = partition(arr, start_index, end_index)

        quicksort(arr, start_index, part)
        quicksort(arr, part + 1, end_index)


def partition(arr, n_from, n_to):
    rnd = n_from + random.randrange(n_to - n_from)

    swap(arr, n_from, rnd)

    value = arr[n_from]

    idx_bigger = n_from + 1
    idx_lower = n_to - 1

    condition = True

    while condition:

        while idx_bigger <= idx_lower and arr[idx_bigger] <= value:
            idx_bigger += 1

        while arr[idx_lower] > value:
            idx_lower -= 1

        if idx_bigger < idx_lower:
            swap(arr, idx_bigger, idx_lower)

        condition = idx_bigger < idx_lower

    swap(arr, idx_lower, n_from)

    return idx_lower


if __name__ == '__main__':
    main()
