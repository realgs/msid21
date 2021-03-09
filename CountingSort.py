
def counting_sort(arr, k):
	k+=1
	n = len(arr)
	pos = []
	result = []
	for i in range(0, k):
		pos.append(0)
	
	for i in range(0, n):
		result.append(0)
		
	for j in range(0, n):
		pos[arr[j]] += 1

	pos[0] -= 1
	
	for i in range(1, k):
		pos[i] += pos[i-1]
	
	for j in range(n-1, -1, -1):
		result[pos[arr[j]]] = arr[j]
		pos[arr[j]] -= 1
		
	for j in range(0, n):
		arr[j] = result[j]

arr1 = [0, 4, 0, 2, 3, 3, 0, 5]
counting_sort(arr1, 5)
print(arr1)

arr2 = [0, 5, 7, 9, 1, 8, 0, 2]
counting_sort(arr2, 9)
print(arr2)

arr3 = [8, 7, 6, 5, 4, 3, 2, 1]
counting_sort(arr3, 8)
print(arr3)
