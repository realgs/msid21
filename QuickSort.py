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


def quick_sort_helper(arr, left_idx, right_idx):
    if left_idx < right_idx:
        pivot_idx = divide(arr, left_idx, right_idx)
        quick_sort_helper(arr, left_idx, pivot_idx - 1)
        quick_sort_helper(arr, pivot_idx + 1, right_idx)


def quick_sort(arr):
    quick_sort_helper(arr, 0, len(arr) - 1)


def print_array(arr):
    print("[ ", end='')
    if len(arr) > 0:
        print(arr[0], end='')
    for i in range(1, len(arr)):
        print(", " + str(arr[i]), end='')
    print(" ]")


def sort_and_print(arr, sort_func):
    print()
    print("Before: ", end='')
    print(arr)
    sort_func(arr)
    print("After:  ", end='')
    print(arr)
    print()


array1 = [1, 2, 3, 4, 5]
array2 = [5, 4, 3, 2, 1]
array3 = [3, 1, 5, 2, 4]
array4 = [3, 8, 5, 1, 8, 2, 2, 1, 4, 3]
array5 = [-3, -6, 2, -1, -3, -1, 0]

sort_and_print(array1, quick_sort)
sort_and_print(array2, quick_sort)
sort_and_print(array3, quick_sort)
sort_and_print(array4, quick_sort)
sort_and_print(array5, quick_sort)
