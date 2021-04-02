def insert_sort(number_array):
    size = len(number_array)
    for i in range(1, size):
        value = number_array[i]
        j = i - 1
        while j >= 0 and value < number_array[j]:
            number_array[j + 1] = number_array[j]
            j -= 1
        number_array[j + 1] = value
    return number_array
