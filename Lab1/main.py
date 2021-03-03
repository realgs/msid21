
def insertionSort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and key < arr[j]:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key



arr = [12, 11, 13, 5, 6]
insertionSort(arr)
print("Sorted array is:")
for i in range(len(arr)):
    print("%d" % arr[i])

def mergeSort(arr):
    if len(arr) > 1:

        mid = len(arr)//2

        left = arr[:mid]

        right = arr[mid:]

        mergeSort(left)

        mergeSort(right)

        i = j = k = 0

        while i < len(left) and j < len(right):
            if left[i] < right[j]:
                arr[k] = left[i]
                i += 1
            else:
                arr[k] = right[j]
                j += 1
            k += 1

        while i < len(left):
            arr[k] = left[i]
            i += 1
            k += 1

        while j < len(right):
            arr[k] = right[j]
            j += 1
            k += 1

arr1 = [12, 11, 13, 5, 6]
mergeSort(arr1)
print("Sorted array is:")
for q in range(len(arr1)):
    print("%d" % arr1[q])