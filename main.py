import random


def select_sort(list):
    for i in range(0, len(list)):
        id_min = i
        for j in range(i + 1, len(list)):
            if list[j] < list[id_min]:
                id_min = j
        list[i], list[id_min] = list[id_min], list[i]


def insert_sort(list):
    for i in range(1, len(list)):
        curr_element = list[i]
        j = i - 1
        while j > -1 and curr_element < list[j]:
            list[j + 1] = list[j]
            j -= 1
        list[j + 1] = curr_element


def generate_list_int(length, range_start, range_stop):
    return [random.randint(range_start, range_stop) for _ in range(0, length)]


def generate_list_float(length, range_start, range_stop):
    return [round(random.uniform(range_start, range_stop), 2) for _ in range(0, length)]


if __name__ == '__main__':
    list_int = generate_list_int(5, -10, 10)
    list_int_copy = list_int.copy()
    list_int_test = list_int.copy()
    list_float = generate_list_float(5, -10, 10)
    list_float_copy = list_float.copy()
    list_float_test = list_float.copy()
    print("Generated lists:")
    print(list_int)
    print(list_float)
    print()

    select_sort(list_int)
    select_sort(list_float)
    insert_sort(list_int_copy)
    insert_sort(list_float_copy)

    print("Lists sorted using selection sort:")
    print(list_int)
    print(list_float)
    print()
    print("Lists sorted using insertion sort:")
    print(list_int_copy)
    print(list_float_copy)
    print()

    assert list_int == sorted(list_int_test), "Failed selection sort for int"
    assert list_float == sorted(list_float_test), "Failed selection sort for float"
    assert list_int_copy == sorted(list_int_test), "Failed insertion sort for int"
    assert list_float_copy == sorted(list_float_test), "Failed insertion sort for float"
    print("All assertions passed.")
