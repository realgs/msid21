# 2 sorting methods: bubble sort and quicksort

example = [20, 17, 4, 2, 11, 14, 21, 18, 7, 1, 10, 13]

def bubble_sort(list):
    l = len(list)
    for i in range(l-1):
        for j in range(0, l -i-1 ):
            if list[j]>list[j+1]:
                temp = list[j]
                list[j]= list[j+1]
                list[j+1] = temp
    return list

print(bubble_sort(example))