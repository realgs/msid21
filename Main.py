from CountingSort import count_sort
from QuickSort import quick_sort


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


print("Count Sort: ")
array1 = [1, 2, 3, 4, 5]
array2 = [5, 4, 3, 2, 1]
array3 = [3, 1, 5, 2, 4]
array4 = [3, 8, 5, 1, 8, 2, 2, 1, 4, 3]
array5 = [-3, -6, 2, -1, -3, -1, 0]

sort_and_print(array1, count_sort)
sort_and_print(array2, count_sort)
sort_and_print(array3, count_sort)
sort_and_print(array4, count_sort)
sort_and_print(array5, count_sort)

print("Quick Sort: ")
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
