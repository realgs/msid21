def insertion_sort(array):
    for i in range(1, len(array)):
        current_value = array[i]
        current_position = i

        while current_position > 0 and array[current_position - 1] > current_value:
            array[current_position] = array[current_position - 1]
            current_position = current_position - 1

        array[current_position] = current_value
