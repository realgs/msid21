def insertionSort(array):

    for i in range(1, len(array)):
        currentElement = array[i]
        previousElementIndex = i - 1

        while previousElementIndex >= 0 and currentElement < array[previousElementIndex]:
            array[previousElementIndex + 1] = array[previousElementIndex]
            previousElementIndex -= 1

        array[previousElementIndex + 1] = currentElement

    return array
