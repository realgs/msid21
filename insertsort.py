import random


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


def create_array(size, start, end):
    number_array = []
    for i in range(size):
        number_array.append(random.randint(start, end))
    return number_array


array_1 = create_array(10, 1, 500)
print("Created array: ", array_1)
print("Sorted array: ", insert_sort(array_1))
