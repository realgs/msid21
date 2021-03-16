def insertSort(numbers):
    for i in range(1, len(numbers)):
        element = numbers[i]
        j = i - 1
        while j >= 0 and numbers[j] > element:
            numbers[j + 1] = numbers[j]
            j = j - 1
        numbers[j + 1] = element

someNumbers = [3, 2, 12, 56, 12, 11, 61, 0, 23, 19, 21, 27, 21, 21, 24]
insertSort(someNumbers)
print(someNumbers)
