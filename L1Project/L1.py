def insert_sort(array):
    for i in range(1, len(array)):
        value = array[i]
        j = i
        while j > 0 and value < array[j - 1]:
            array[j] = array[j - 1]
            j -= 1
        array[j] = value


def bubble_sort(array):
    for i in range(1, len(array)):
        for left in range(0, len(array) - i):
            right = left + 1
            if array[left] > array[right]:
                temp = array[left]
                array[left] = array[right]
                array[right] = temp


numbers1 = [100, 50, 30, 20, 10]
numbers2 = [100, 50, -30, -20, -10, 5, 6, 3, 2, 11, -3]
numbers3 = [100, 50, 30, 20, 10]
numbers4 = [100, 50, -30, -20, -10, 5, 6, 3, 2, 11, -3]
insert_sort(numbers1)
insert_sort(numbers2)
bubble_sort(numbers3)
bubble_sort(numbers4)
assert numbers1 == [10, 20, 30, 50, 100], "numbers1 test failed"
assert numbers2 == [-30, -20, -10, -3, 2, 3, 5, 6, 11, 50, 100], "numbers2 test failed"
assert numbers3 == [10, 20, 30, 50, 100], "numbers3 test failed"
assert numbers4 == [-30, -20, -10, -3, 2, 3, 5, 6, 11, 50, 100], "numbers4 test failed"
