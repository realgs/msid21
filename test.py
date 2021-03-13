from bubblesort import bubbleSort
from insertionsort import insertionSort

array1 = [-2, 1, 10, 0, 5, 6, 7, -10, 20, 6]
array2 = [-2, 1, 10, 0, 5, 6, 7, -10, 20, 6]

print("bubble sort")
print("before: " + str(array1))
bubbleSort(array1)
print("after: " + str(array1))

print("")

print("insertion sort")
print("before: "+ str(array2))
insertionSort(array2)
print("after: " + str(array2))