def count_sort(arr):
    result = [0 for i in range(len(arr))]

    min_val = min(arr)
    max_val = max(arr)
    counts_length = max_val - min_val + 1

    counts = [0 for _ in range(counts_length)]

    for i in arr:
        counts[i - min_val] += 1

    for i in range(1, counts_length):
        counts[i] += counts[i - 1]

    for i in range(len(arr)):
        result[counts[arr[i] - min_val] - 1] = arr[i]
        counts[arr[i] - min_val] -= 1

    for i in range(len(arr)):
        arr[i] = result[i]


def print_array(arr):
    print("[ ", end='')
    if len(arr) > 0:
        print(arr[0], end='')
    for i in range(1, len(arr)):
        print(", " + str(arr[i]), end='')
    print(" ]")


array1 = [1, 2, 3, 4, 5]
array2 = [5, 4, 3, 2, 1]
array3 = [3, 1, 5, 2, 4]
array4 = [3, 8, 5, 1, 8, 2, 2, 1, 4, 3]
array5 = [-3, -6, 2, -1, -3, -1, 0]

count_sort(array1)
print_array(array1)

count_sort(array2)
print_array(array2)

count_sort(array3)
print_array(array3)

count_sort(array4)
print_array(array4)

count_sort(array5)
print_array(array5)