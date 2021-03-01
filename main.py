def bubble_sort(array):
    array = array.copy()
    n = len(array)

    for i in range(n - 1):
        for j in range(0, n - i - 1):
            if array[j] > array[j + 1]:
                array[j], array[j + 1] = array[j + 1], array[j]

    return array


def insert_sort(array):
    array = array.copy()
    for i in range(1, len(array)):
        element = array[i]
        j = i - 1
        while j >= 0 and array[j] > element:
            array[j + 1] = array[j]
            j -= 1
        array[j + 1] = element

    return array