def insertsort(array):
    for i in range(1, len(array)):
        selected_element = array[i]
        j = i - 1
        while j >= 0 and array[j] > selected_element:
            array[j + 1] = array[j]
            j = j - 1

        array[j + 1] = selected_element

    return array


def quicksort(array):
    if len(array) <= 1:
        return array
    pivot = array[int(len(array) / 2)]
    left = [x for x in array if x < pivot]
    middle = [x for x in array if x == pivot]
    right = [x for x in array if x > pivot]
    return quicksort(left) + middle + quicksort(right)
