from random import randint


def divide(arr, left, right):
    pivot = randint(left, right)
    arr[left], arr[pivot] = arr[pivot], arr[left]
    pivot = left
    left += 1

    while left <= right:

        while left <= right and arr[pivot] <= arr[right]:
            right -= 1

        while left <= right and arr[pivot] >= arr[left]:
            left += 1

        if left <= right:
            arr[left], arr[right] = arr[right], arr[left]

    arr[pivot], arr[right] = arr[right], arr[pivot]

    return right


def quick_sort_indexed(arr, left_idx, right_idx):
    if left_idx < right_idx:
        pivot_idx = divide(arr, left_idx, right_idx)
        quick_sort_indexed(arr, left_idx, pivot_idx - 1)
        quick_sort_indexed(arr, pivot_idx + 1, right_idx)


def quick_sort(arr):
    quick_sort_indexed(arr, 0, len(arr) - 1)
