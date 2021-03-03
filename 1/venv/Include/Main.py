import random
import string


def selection_sort(array):
    for i in range(0, len(array)):
        smallest_value_index = array[i:].index(min(array[i:]))
        swap(array, smallest_value_index + i, i)


def quick_sort(array):
    sort(array, 0, len(array) - 1)


def sort(array, start, end):
    if start < end:
        split = quick(array, start, end)
        sort(array, start, split - 1)
        sort(array, split + 1, end)


def quick(array, start, end):
    current_index = start
    pivot = array[(start + end) // 2]
    swap(array, (start + end) // 2, end)
    for i in range(start, end):
        if array[i] < pivot:
            swap(array, i, current_index)
            current_index = current_index + 1
    swap(array, end, current_index)
    return current_index


def swap(array, current_index, new_index):
    tmp = array[current_index]
    array[current_index] = array[new_index]
    array[new_index] = tmp


def sorting_test(sorting_method):
    print(sorting_method.__name__)
    print("Test 1 - small random int: {}".format(sorting_methods_test(sorting_method, random_int_array(100))))
    print("Test 2 - big random int: {}".format(sorting_methods_test(sorting_method, random_int_array(10000))))
    print("Test 3 - ordered int: {}".format(sorting_methods_test(sorting_method, ordered_int_array(1000, True))))
    print(
        "Test 4 - reverse ordered int: {}".format(sorting_methods_test(sorting_method, ordered_int_array(1000, False))))
    print("Test 5 - small random string: {}".format(sorting_methods_test(sorting_method, random_string_array(10))))
    print("Test 6 - big random string: {}".format(sorting_methods_test(sorting_method, random_string_array(1000))))


def sorting_methods_test(sorting_method, array):
    comparison_array = array[:]
    sorting_method(array)
    return array == sorted(comparison_array)


def random_int_array(size):
    return [random.randint(-2 * size, 2 * size) for _ in range(size)]


def ordered_int_array(size, is_ascending):
    return [i for i in range(size)] if is_ascending else [i for i in reversed(range(size))]


def random_string_array(size):
    return [random.choice(string.ascii_letters) for _ in range(random.randint(1, 10)) for _ in range(size)]


if __name__ == '__main__':
    sorting_test(selection_sort)
    sorting_test(quick_sort)
