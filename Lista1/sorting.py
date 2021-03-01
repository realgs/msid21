
def quicksort(num_list):
    if len(num_list) <= 1:
        return num_list

    pivot = num_list[0]
    lesser = [num for num in num_list if num < pivot]
    equal = [num for num in num_list if num == pivot]
    greater = [num for num in num_list if num > pivot]
    return quicksort(lesser) + equal + quicksort(greater)


def mergesort(num_list):
    list_len = len(num_list)

    if list_len == 0:
        return
    elif list_len == 1:
        return num_list

    mid = list_len // 2
    left_list = num_list[:mid]
    right_list = num_list[mid:]

    mergesort(left_list)
    mergesort(right_list)

    left_iter = 0
    right_iter = 0
    main_iter = 0

    left_length = len(left_list)
    right_length = len(right_list)

    while left_iter < left_length and right_iter < right_length:
        if left_list[left_iter] < right_list[right_iter]:
            num_list[main_iter] = left_list[left_iter]
            left_iter += 1
        else:
            num_list[main_iter] = right_list[right_iter]
            right_iter += 1

        main_iter += 1

    while left_iter < left_length:
        num_list[main_iter] = left_list[left_iter]
        left_iter += 1
        main_iter += 1

    while right_iter < right_length:
        num_list[main_iter] = right_list[right_iter]
        right_iter += 1
        main_iter += 1

    return num_list


test_list = [2, 5, 1, 8, 12, -5, 4, 20, 0, 500, -54, 25, 12, -544]
control_list = [-544, -54, -5, 0, 1, 2, 4, 5, 8, 12, 12, 20, 25, 500]

assert control_list == quicksort(test_list)
assert control_list == mergesort(test_list)
