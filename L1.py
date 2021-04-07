def insertSort(array):
	for i in range(1,len(array)):
		pos = i
		value = array[i]

		while pos > 0 and array[pos - 1] > value :
			array[pos] = array[pos-1]
			pos = pos - 1

		array[pos] = value

def selectSort(array):
	for i in range(0, len(array)):
		pos = i
		for j in range(i+1,len(array)):
			if(array[pos]>array[j]):
				pos = j
		array[i], array[pos] = array[pos], array[i]




	


