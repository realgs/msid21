import random


def generate_random_array(size: int, start: int, end: int, useInts: bool):
    return [random.randint(start, end) if useInts else random.uniform(start, end) for _ in range(size)]


def bubble_sort(array):
    array = array.copy()
    n = len(array)

    for i in range(n - 1):
        for j in range(0, n - i - 1):
            if array[j] > array[j + 1]:
                array[j], array[j + 1] = array[j + 1], array[j]

    return array


def insert_sort(array):
    array = array.copy()
    for i in range(1, len(array)):
        element = array[i]
        j = i - 1
        while j >= 0 and array[j] > element:
            array[j + 1] = array[j]
            j -= 1
        array[j + 1] = element

    return array


def test_sorting(size: int, start: int, end: int, useInts: bool):
    array = generate_random_array(size, start, end, useInts)
    bubble_sorted_array = bubble_sort(array)
    insert_sorted_array = insert_sort(array)

    print(bubble_sorted_array)
    print(insert_sorted_array)


def auto_test(array, sorting_function, expected_outcome):
    sorting_result = sorting_function(array)
    assert sorting_result == expected_outcome

    print('Array sorted successfully')


def main():
    # random values
    test_sorting(20, 0, 200, True)
    test_sorting(20, -200, 200, True)
    test_sorting(20, -200, -1, True)

    test_sorting(20, 0, 200, False)
    test_sorting(20, -200, 200, False)
    test_sorting(20, -200, -1, False)

    test_sorting(20, -1000000, 1000000, False)

    # specific values to test algorithms
    toSort1 = [38, -46, 93, 86, 5, -58, -28, 24, 91, 87, 78]
    expected_outcome1 = [-58, -46, -28, 5, 24, 38, 78, 86, 87, 91, 93]

    auto_test(toSort1, bubble_sort, expected_outcome1)
    auto_test(toSort1, insert_sort, expected_outcome1)

    toSort2 = [-22.123, -43.51, 0, 94.12, 3, 24, 55.12, 23.3, 12.23, 0, 2.23, 2.22, 4.21, -22.124]
    expected_outcome2 = [-43.51, -22.124, -22.123, 0, 0, 2.22, 2.23, 3, 4.21, 12.23, 23.3, 24, 55.12, 94.12]

    auto_test(toSort2, bubble_sort, expected_outcome2)
    auto_test(toSort2, insert_sort, expected_outcome2)


if __name__ == '__main__':
    main()


