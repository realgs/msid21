def merge_sort(array):
    if len(array) > 1:
        inner_merge_sort(array, 0, len(array) - 1)


def merge(array, left_index, right_index, middle_index):
    left_array = array[left_index:middle_index + 1]
    right_array = array[middle_index + 1:right_index + 1]

    left_copy_index = right_copy_index = 0
    sorted_index = left_index

    while left_copy_index < len(left_array) and right_copy_index < len(right_array):

        if left_array[left_copy_index] <= right_array[right_copy_index]:
            array[sorted_index] = left_array[left_copy_index]
            left_copy_index += + 1
        else:
            array[sorted_index] = right_array[right_copy_index]
            right_copy_index = right_copy_index + 1

        sorted_index += 1

    while left_copy_index < len(left_array):
        array[sorted_index] = left_array[left_copy_index]
        left_copy_index += 1
        sorted_index += 1

    while right_copy_index < len(right_array):
        array[sorted_index] = right_array[right_copy_index]
        right_copy_index += 1
        sorted_index += 1


def inner_merge_sort(inner_array, left_index, right_index):
    if left_index < right_index:
        middle_index = (left_index + right_index) // 2
        inner_merge_sort(inner_array, left_index, middle_index)
        inner_merge_sort(inner_array, middle_index + 1, right_index)
        merge(inner_array, left_index, right_index, middle_index)
