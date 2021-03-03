def bubble_sort(array):
    for i in range(0, len(array)-1):
        for j in range(i+1, len(array)):
            if array[i] > array[j]:
                temp = array[i]
                array[i] = array[j]
                array[j] = temp


def insert_sort(array):
    for i in range(1, len(array)):
        current = array[i]
        j = i-1
        while j >= 0 and current < array[j]:
            array[j+1] = array[j]
            j -= 1
        array[j+1] = current


array = [1, 3, 0, 2, 5, 7, 9]
array2 = [1, 3, 0, 2, 5, 7, 9]
bubble_sort(array)
insert_sort(array2)
print(array)
print(array2)

