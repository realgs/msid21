def mergeSort(array):
    return sort(array, 0, len(array)-1)

def sort(array, start, end):
    if start == end: return [array[start]]
    half = (start+end) //2
    return merge(sort(array, start, half), sort(array, half+1, end))

def merge(array1, array2):
    result = []
    count1 = 0
    count2 = 0
    while count1 < len(array1) and count2 < len(array2):
        if array1[count1] < array2[count2]:
            result.append(array1[count1])
            count1 += 1
        else:
            result.append(array2[count2])
            count2 += 1

    if count1 >= len(array1): result.extend(array2[count2:])
    if count2 >= len(array2): result.extend(array1[count1:])
    return result

def show(array):
    for i in range(len(array)):
        print(array[i], end=" ")
    print()

show(mergeSort([9,14,72,-3,0,81,4,2]))