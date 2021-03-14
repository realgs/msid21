import random

if __name__ == '__main__':
    print("Hello World")


def quicksort(arr):
    quick(arr, 0, len(arr))


def quick(arr, start_index, end_index):
    if end_index - start_index > 1:
        part = partition(arr, start_index, end_index)

        quick(arr, start_index, part)
        quick(arr, part + 1, end_index)


def partition(arr, n_from, n_to):
    rnd = n_from + random.randrange(n_to - n_from)

    swap(arr, n_from, rnd)

    value = arr[n_from]

    idx_bigger = n_from + 1
    idx_lower = n_to - 1

    condition = idx_bigger < idx_lower

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


def swap(arr, left, right):
    if left != right:
        arr[left], arr[right] = arr[right], arr[left]
