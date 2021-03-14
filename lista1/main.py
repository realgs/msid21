def bubbleSort(numbers):
    size = len(numbers)
    for i in range (1, size):
        for left in range(size-i):
            right = left+1
            if numbers[left] > numbers[right]:
                temp = numbers[left]
                numbers[left] = numbers[right]
                numbers[right] = temp
    return numbers

numbers = [5, 123, 1, 35, 23, 12, 6, 129]
print(numbers)
bubble = bubbleSort(numbers)
print("bubble sort:")
print(bubble)