def mergeSort(array):

    def merge(innerArray, leftArray, rightArray):
        leftArrayIndex = rightArrayIndex = innerArrayIndex = 0
        while leftArrayIndex < len(leftArray) and rightArrayIndex < len(rightArray):
            if leftArray[leftArrayIndex] < rightArray[rightArrayIndex]:
                innerArray[innerArrayIndex] = leftArray[leftArrayIndex]
                leftArrayIndex += 1
            else:
                innerArray[innerArrayIndex] = rightArray[rightArrayIndex]
                rightArrayIndex += 1
            innerArrayIndex += 1

        while leftArrayIndex < len(leftArray):
            innerArray[innerArrayIndex] = leftArray[leftArrayIndex]
            leftArrayIndex += 1
            innerArrayIndex += 1

        while rightArrayIndex < len(rightArray):
            innerArray[innerArrayIndex] = rightArray[rightArrayIndex]
            rightArrayIndex += 1
            innerArrayIndex += 1

    def mergeSortHelper(innerArray):
        if len(innerArray) > 1:
            midIndex = len(innerArray) // 2
            leftArray = innerArray[:midIndex]
            rightArray = innerArray[midIndex:]
            mergeSortHelper(leftArray)
            mergeSortHelper(rightArray)
            merge(innerArray, leftArray, rightArray)

    mergeSortHelper(array)
    return array