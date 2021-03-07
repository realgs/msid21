from insertionSort import insertionSort
from selectionSort import selectionSort

print("INSERTION SORT TEST")
array = [0, 54.5, 5, 6, 2, 1, -2, 20, 150, 99]
print(array)
insertionSort(array)
print(array)
array = ['d', 'a', 'c', 'b']
insertionSort(array)
print(array)

print("SELECTION SORT TEST")
array1 = [0, 54, 5, 6, 2, 1, -2, 20, 150.91, 99, 150.90]
print(array1)
selectionSort(array1)
print(array1)
array = ['d', 'a', 'c', 'b']
insertionSort(array)
print(array)