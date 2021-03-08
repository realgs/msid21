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


array1 = [1, 2, 10, 16, 6, 3]
print(merge_sort(array1))


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
