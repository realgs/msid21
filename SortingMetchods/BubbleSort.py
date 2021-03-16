def bubbleSort(numbers):
    minChangeIndex = 0
    maxChangeIndex = len(numbers) - 1
    sorted = False
    while not sorted:
        lastChangeIndex = -1
        for i in range(minChangeIndex, maxChangeIndex):
            if numbers[i] > numbers[i + 1]:
                numbers[i], numbers[i + 1] = numbers[i + 1], numbers[i]
                if lastChangeIndex < 0:
                    minChangeIndex = i
                lastChangeIndex = i
        if minChangeIndex:
            minChangeIndex = minChangeIndex - 1
        maxChangeIndex = lastChangeIndex
        if lastChangeIndex < 0:
            sorted = True



someNumbers = [3, 2, 12, 56, 12, 11, 61, 0, 23, 19, 21, 27, 21, 21, 24,]
bubbleSort(someNumbers)
print(someNumbers)
