def quicksort(arr):
	def quick(startIdx, endIdx): 
		if startIdx+1 < endIdx:
			part = partition(startIdx, endIdx)
			quick(startIdx,part)		
			quick(part,endIdx)
			
	def partition(f , to):
		mid = (f+to)//2
		swap(f,mid)	
		pivotVal = arr[f]
		idxBigger = f+1
		idxLower = to-1
		cont = True
		while cont:
			while idxBigger <= idxLower and arr[idxBigger] <= pivotVal:
				idxBigger+=1
			while arr[idxLower] > pivotVal: 
				idxLower-=1
			if idxBigger < idxLower:
				swap(idxBigger,idxLower)
			else:
				cont = False		
		swap(idxLower,f)
		return idxLower 
		
	def swap(left, right):
		if left != right:
			temp = arr[left]
			arr[left] = arr[right]
			arr[right] = temp
			
	quick(0,len(arr))
	return arr		
			
def printList(xs):
    for i in range(len(xs)):
        print(xs[i], end=" ")
    print()
		
printList(quicksort([1,2,3,4,5,88,-1]))
printList(quicksort([5,4,3,2,1]))
printList(quicksort([1,2,3,4]))
printList(quicksort([1,2,3,4,5,5]))
printList(quicksort([1,2,3,4,5,5,4,3,2,1]))


		
