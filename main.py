def merge_sort(array):
    if len(array) < 2:
        return

    middle = len(array) // 2
    left_array = array[:middle]
    right_array = array[middle:]

    merge_sort(left_array)
    merge_sort(right_array)
    merge(array, left_array, right_array)
    return array


def merge(array, l, r):
    i = 0
    j = 0
    k = 0

    while i < len(l) and j < len(r):
        if l[i] < r[j]:
            array[k] = l[i]
            i += 1
        else:
            array[k] = r[j]
            j += 1
        k += 1

    while i < len(l):
        array[k] = l[i]
        i += 1
        k += 1

    while j < len(r):
        array[k] = r[j]
        j += 1
        k += 1


def selection_sort(array):
    j = 0
    while j < len(array):
        i = j
        min_ind = j
        while i < len(array):
            if array[i] < array[min_ind]:
                min_ind = i
            i += 1
        array[j], array[min_ind] = array[min_ind], array[j]
        j += 1
    return array


# tests
array1 = [5, 11, 21, 7, 12, 6]
array2 = [4, 7, 3, 22, 12, 24, 8, 2]
array3 = [21, 12, 17, 5]
array4 = [1, 7, 2, 12, 11, 5, 5, 8, 3]

print("Merge sort")
print(merge_sort(array1))
print(merge_sort(array2))
print("Selection sort")
print(selection_sort(array3))
print(selection_sort(array4))
