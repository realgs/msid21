def selectionSort(arr):
    for i in range(len(arr) - 1):
        minIndex = i
        for j in range(i , len(arr)):
            if arr[j] < arr[minIndex]:
               minIndex = j
           
        tmp = arr[i]
        arr[i] = arr[minIndex]
        arr[minIndex] = tmp

    
                           

