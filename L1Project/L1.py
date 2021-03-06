def insert_sort(array):
    for i in range(1,len(array)):
        value = array[i]
        j = i
        while j > 0 and value < array[j - 1]:
            array[j] = array[j - 1]
            j -= 1
        array[j] = value
    return array

numbers1 = [100,50,30,20,10]
numbers2 = [100,50,-30,-20,-10,5,6,3,2,11,-3]
print(insert_sort(numbers1))
print(insert_sort(numbers2))