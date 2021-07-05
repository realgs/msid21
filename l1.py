def swap(array, firstIndex, secondIndex):
    tmp = array[firstIndex]
    array[firstIndex] = array[secondIndex]
    array[secondIndex] = tmp

def bubblesort(array):
    for i in range(len(array)):
        for j in range(0, len(array) - i - 1):
            if array[j] > array [j + 1]:
                swap(array, j, j + 1)

def quicksort(array, start, end):
    if start >= end:
        return

    left = start
    right = end
    pivot = array[start + (end - start) / 2]

    while (left <= right):
        while (array[left] < pivot):
            left = left + 1
        
        while (array[right] > pivot):
            right = right - 1;
        
        if (left <= right):
            swap(array, left, right);
            left = left + 1;
            right = right - 1;

    if(start < right):
        quicksort(array, start, right)
    if(left < end):
        quicksort(array, left, end)    

def testSorting():
    numbersBubble = [10, 5, 2, 11, 200, -50, 10, 0, 1, -5]
    numbersQuick = [10, 5, 2, 11, 200, -50, 10, 0, 1, -5]

    bubblesort(numbersBubble)
    quicksort(numbersQuick, 0, len(numbersQuick) - 1)

    assert numbersBubble == [-50, -5, 0, 1, 2, 5, 10, 10, 11, 200], "Should be sorted ([-50, -5, 0, 1, 2, 5, 10, 10, 11, 200])"
    assert numbersQuick == [-50, -5, 0, 1, 2, 5, 10, 10, 11, 200], "Should be sorted ([-50, -5, 0, 1, 2, 5, 10, 10, 11, 200])"
    print("Tests passed!")

testSorting()
