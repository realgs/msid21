def count_sort(arr):
    arr_len = len(arr)
    result = [0 for i in range(arr_len)]

    min_val = min(arr)
    positions = create_array_of_position(arr)

    for i in range(arr_len):
        result[positions[arr[i] - min_val] - 1] = arr[i]
        positions[arr[i] - min_val] -= 1

    for i in range(arr_len):
        arr[i] = result[i]


def create_array_of_position(arr):
    min_val = min(arr)
    max_val = max(arr)
    counts_length = max_val - min_val + 1

    counts = [0 for _ in range(counts_length)]

    for i in arr:
        counts[i - min_val] += 1

    for i in range(1, counts_length):
        counts[i] += counts[i - 1]

    return counts


def print_array(arr):
    print("[ ", end='')
    if len(arr) > 0:
        print(arr[0], end='')
    for i in range(1, len(arr)):
        print(", " + str(arr[i]), end='')
    print(" ]")


def sort_and_print(arr):
    print()
    print("Before: ", end='')
    print(arr)
    count_sort(arr)
    print("After:  ", end='')
    print(arr)
    print()


array1 = [1, 2, 3, 4, 5]
array2 = [5, 4, 3, 2, 1]
array3 = [3, 1, 5, 2, 4]
array4 = [3, 8, 5, 1, 8, 2, 2, 1, 4, 3]
array5 = [-3, -6, 2, -1, -3, -1, 0]

sort_and_print(array1)
sort_and_print(array2)
sort_and_print(array3)
sort_and_print(array4)
sort_and_print(array5)
