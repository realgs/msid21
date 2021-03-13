import random


def bubble_sort(number_array):
    size = len(number_array)
    for i in range(1, size):
        for left in range(0, size - i):
            right = left + 1
            if number_array[left] >= number_array[right]:
                number_array[left], number_array[right] = number_array[right], number_array[left]
    return number_array


def create_array(size, start, end):
    number_array = []
    for i in range(size):
        number_array.append(random.randint(start, end))
    return number_array


array_1 = create_array(10, 1, 500)
print("Created array: ", array_1)
print("Sorted array: ", bubble_sort(array_1))
