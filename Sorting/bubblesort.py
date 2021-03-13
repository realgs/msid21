def bubble_sort(number_array):
    size = len(number_array)
    for i in range(1, size):
        for left in range(0, size - i):
            right = left + 1
            if number_array[left] >= number_array[right]:
                number_array[left], number_array[right] = number_array[right], number_array[left]
    return number_array
