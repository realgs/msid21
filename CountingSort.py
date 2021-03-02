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
