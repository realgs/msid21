import random
from timeit import default_timer as timer


def quicksort(num_list):
    if len(num_list) <= 1:
        return num_list

    pivot = num_list[0]
    lesser = [num for num in num_list if num < pivot]
    equal = [num for num in num_list if num == pivot]
    greater = [num for num in num_list if num > pivot]
    return quicksort(lesser) + equal + quicksort(greater)



l = [2, 5, 1, 8, 12, -5, 4, 20, 0]
start = timer()
quicksort(l)
end = timer()
print(end - start)
