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

ar1 = [80, 1, 500, -1000, 5, 123, 53]
bubbleSort(ar1)
print(ar1)