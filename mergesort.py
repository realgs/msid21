
def merge_sort(xs):
	return sort(xs,0,len(xs)-1)
	
def sort(xs, startIdx, endIdx):
	if startIdx == endIdx:
		result = []
		result.append(xs[startIdx])
		return result	
	split = (startIdx + endIdx)//2
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
		
print(merge_sort([21,23,45,12,31,17,-1,0]) == [-1,0,12,17,21,23,31,45])
print(merge_sort([5,4,3,2,1]) == [1,2,3,4,5])
print(merge_sort([1,2,3,4]) == [1,2,3,4])
print(merge_sort([1,2,3,4,5,5,1,2,3,4]) == [1,1,2,2,3,3,4,4,5,5])
		
		 
			
  
