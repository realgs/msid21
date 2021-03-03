from sorting import *

if __name__ == '__main__':
    lst = [1, 2, 3, 7, 11, 3, 7, 4, 9]

    res = merge_sorted(lst)
    print(lst)
    print(res)

    lst = [-x for x in lst]

    radix_sort(lst)
    print(lst)


