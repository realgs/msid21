def insertionSort(arr):
    size = len(arr)
    
    for i in range(1, size):
        tmp = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > tmp :
            arr[j + 1] = arr[j]
            j = j - 1

        arr[j + 1] = tmp


