def quick_sort(unsorted):
    if len(unsorted) <= 1:
        return unsorted

    pivot = unsorted.pop()

    lower = []
    greater = []

    for item in unsorted:
        if item < pivot:
            lower.append(item)
        else:
            greater.append(item)

    return quick_sort(lower) + [pivot] + quick_sort(greater)


def merge(first, second):
    sorted = []
    i = j = 0
    len_first = len(first)
    len_second = len(second)

    while i < len_first and j < len_second:
        if first[i] < second[j]:
            sorted.append(first[i])
            i += 1
        else:
            sorted.append(second[j])
            j += 1

    if i < len_first:
        sorted.extend(first[i:len_first])
    if j < len_second:
        sorted.extend(second[j:len_second])

    return sorted


def merge_sort(unsorted):
    if len(unsorted) <= 1:
        return unsorted

    middle = len(unsorted) // 2
    left = unsorted[:middle]
    right = unsorted[middle:]

    return merge(merge_sort(left), merge_sort(right))


print(quick_sort([5, 8, 12, 56, 89, 100, 7, 9, 45, 51, 3, 5, 1, 2, 4, 5, 0]))
print(merge_sort([5, 8, 12, 56, 89, 100, 7, 9, 45, 51, 3, 5, 1, 2, 4, 5, 0]))
