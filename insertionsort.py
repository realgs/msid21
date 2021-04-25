def insertionSort(array):
    for i in range(1, len(array)):
        j = 0
        temp = array[i]
        while array[j] < array[i]:
            j +=1
        for k in reversed(range(j, i)):
            array[k+1]=array[k]
        array[j] = temp