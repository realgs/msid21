numbers = [10, 5, 2, 11, 200, -50, 10, 0, 1, -5]

def swap(array, firstIndex, secondIndex):
    tmp = array[firstIndex]
    array[firstIndex] = array[secondIndex]
    array[secondIndex] = tmp

def bubbleSort(array):
    for i in range(len(array)):
        for j in range(0, len(array) - i - 1):
            if array[j] > array [j + 1]:
                swap(array, j, j + 1)
    

bubbleSort(numbers)
print(numbers)