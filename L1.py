def swap(arr, index_1, index_2):
    tmp = arr[index_1]
    arr[index_1] = arr[index_2]
    arr[index_2] = tmp


def choose_pivot(arr, begin, end):
    return arr[round((begin + end) / 2)]


def partition(arr, left, right):
    left_index = left
    right_index = right
    pivot = choose_pivot(arr, left, right)
    while left_index <= right_index:
        while arr[left_index] < pivot:
            left_index += 1
        while pivot < arr[right_index]:
            right_index -= 1
        if left_index <= right_index:
            swap(arr, left_index, right_index)
            left_index += 1
            right_index -= 1
    return left_index, right_index


def quick(arr, left, right):
    if left < right:
        left_index, right_index = partition(arr, left, right)
        if right_index - left < right - left_index:
            quick(arr, left, right_index)
            quick(arr, left_index, right)
        else:
            quick(arr, left_index, right)
            quick(arr, left, right_index)


def quick_sort(arr):
    quick(arr, 0, len(arr) - 1)


def bubble_sort(arr):
    for i in range(len(arr)):
        for j in range(len(arr) - 1 - i):
            if arr[j + 1] < arr[j]:
                swap(arr, j, j + 1)


def sorting_tests():
    array_1 = [4, 10, 3, 5, 1, 9, 2, 7, 6, 8]
    array_2 = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    array_3 = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
    result = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    quick_sort(array_1)
    assert array_1 == result, "quick sort error array_1"
    quick_sort(array_2)
    assert array_2 == result, "quick sort error array_2"
    quick_sort(array_3)
    assert array_3 == array_3, "quick sort error array_3"
    array_1 = [4, 10, 3, 5, 1, 9, 2, 7, 6, 8]
    array_2 = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    bubble_sort(array_1)
    assert array_1 == result, "bubble sort error array_1"
    bubble_sort(array_2)
    assert array_2 == result, "bubble sort error array_2"
    bubble_sort(array_3)
    assert array_3 == array_3, "bubble sort error array_3"
    print("All tests passed")


sorting_tests()
