def bubbleSort(numbers):
    size = len(numbers)
    for i in range(1, size):
        for left in range(size - i):
            right = left + 1
            if numbers[left] > numbers[right]:
                temp = numbers[left]
                numbers[left] = numbers[right]
                numbers[right] = temp
    return numbers


def insertSort(numbers):
    size = len(numbers)
    for i in range(1, size):
        value = numbers[i]
        j = i - 1
        while value < numbers[j] and j >= 0:
            numbers[j + 1] = numbers[j]
            j = j - 1
        numbers[j + 1] = value
    return numbers


print("bubble sort:")
numbers1 = [5, 123, 1, 35, 23, 12, 6, 129]
print(numbers1)
bubble = bubbleSort(numbers1)
print(bubble)

print("insert sort:")
numbers2 = [7, 12, 3, 76, 31, 1, 9, 2]
print(numbers2)
insert = insertSort(numbers2)
print(insert)
