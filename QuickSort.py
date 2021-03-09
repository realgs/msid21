
def choose_pivot(arr, m, n): return (m+n)//2

def swap(arr, left, right):
	if left != right:
		acc = arr[left]
		arr[left] = arr[right]
		arr[right] = acc

def partition(arr, startIndex, endIndex):
	swap(arr, startIndex, choose_pivot(arr, startIndex, endIndex))
	value = arr[startIndex]
	idxBigger = startIndex + 1
	idxLower = endIndex - 1
	condition = True
	
	while condition:
		while idxBigger <= idxLower and arr[idxBigger] <=  value:
			idxBigger += 1
		while arr[idxLower] > value:
			idxLower -= 1
		if idxBigger < idxLower:
			swap(arr, idxBigger, idxLower)
		else: 
			condition = False
			
	swap(arr, idxLower, startIndex)
	return idxLower
	

def quicksort(arr, startIndex, endIndex):
	if (endIndex - startIndex) > 1: 
		pivot = partition(arr, startIndex, endIndex)
		quicksort(arr, startIndex, pivot )
		quicksort(arr, pivot + 1, endIndex)

def sort(arr): 
	quicksort(arr, 0, len(arr))

array = [12, 4, 5, 6, 7, 3, 1, 15]
sort(array)
print(array)

arr1 = [0, 4, 0, 2, 3, 3, 0, 5]
sort(arr1)
print(arr1)

arr2 = [0, 5, 7, 9, 1, 8, 0, 2]
sort(arr2)
print(arr2)

arr3 = [8, 7, 6, 5, 4, 3, 2, 1]
sort(arr3)
print(arr3)
