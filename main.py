def bubble_sort(array):
    for i in range(0, len(array)-1):
        for j in range(i+1, len(array)):
            if array[i] > array[j]:
                temp = array[i]
                array[i] = array[j]
                array[j] = temp


array = [1, 3, 0, 2, 5, 7, 9]
bubble_sort(array)
print(array)

