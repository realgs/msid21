
def mergesort(xs):
	return sort(xs,0,len(xs)-1)
	
def sort(xs, startIdx, endIdx):
	if startIdx == endIdx:
		result = []
		result.append(xs[startIdx])
		return result	
	split = (startIdx+endIdx)//2
	return merge(sort(xs,startIdx,split),sort(xs,split+1,endIdx)) 
		

def merge(left, right):
	result = []
	idxL = 0
	idxR = 0
	while idxR < len(right) and idxL < len(left):
		if left[idxL] < right[idxR]:
			result.append(left[idxL])
			idxL+=1
		else:
			result.append(right[idxR])
			idxR+=1
	if idxR >= len(right):
		result.extend(left[idxL:])
	else:
		result.extend(right[idxR:])
	return result

def printList(ys):
    for i in range(len(ys)):
        print(ys[i], end=" ")
    print()
		
printList(mergesort([21,23,45,12,31,17,-1,0]))
printList(mergesort([5,4,3,2,1]))
printList(mergesort([1,2,3,4]))
printList(mergesort([1,2,3,4,5,5,1,2,3,4]))
		
		 
			
  
