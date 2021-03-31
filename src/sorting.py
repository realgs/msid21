def bubbleSort(array):
    change = True
    while change == True:
        change = False
        for i in range(len(array) - 1):
            if array[i] > array[i + 1]:
                temp = array[i]
                array[i] = array[i + 1]
                array[i + 1] = temp

                change = True

ar = [80, 1, 500, -1000, 5, 123, 53]
bubbleSort(ar)
print(ar)

def selectionSort(array):
    for i in range(len(array)):
        min = i
        for j in range(i, len(array)):
            if array[j] < array[min]:
                min = j
        temp = array[i]
        array[i] = array[min]
        array[min] = temp

ar = [80, 1, 500, -1000, 5, 123, 53]
selectionSort(ar)
print(ar)
