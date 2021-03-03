def bubble_sort(array):
    for i in range(len(array)):
        for j in range(0, len(array) - i - 1):
            if array[j] > array[j + 1]:
                tmp = array[j]
                array[j] = array[j + 1]
                array[j + 1] = tmp


def insert_sort(array):
    for i in range(len(array)):
        tmp = array[i]
        j = i - 1
        while j >= 0 and tmp < array[j]:
            array[j + 1] = array[j]
            j -= 1
        array[j + 1] = tmp


numbers1 = [3, 2, 1, 100, -10]
numbers2 = [23, -1, 0, 11, 2]
bubble_sort(numbers1)
insert_sort(numbers2)
print(numbers1)
print(numbers2)
