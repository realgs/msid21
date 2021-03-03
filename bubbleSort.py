def bubbleSort(array):
    for i in range(0, len(array)-1):
        for j in range(0, len(array)-1):
            if array[j] > array[j+1]:
                temp = array[j]
                array[j] = array[j+1]
                array[j+1] = temp
    return array

def show(array):
    for i in range(len(array)):
        print(array[i], end=" ")
    print()

show(bubbleSort([5,6,-7,12,7,-3,0,4,-7]))