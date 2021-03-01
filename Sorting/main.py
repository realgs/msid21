from Sorting import SortingAlgorithms
import random


def generate_random_int_list(size: int, start: int, end: int):
    return [random.randint(start, end) for _ in range(size)]


def generate_random_float_list(size: int, start: int, end: int):
    return [random.uniform(start, end) for _ in range(size)]


def main():
    test_array_1 = generate_random_int_list(15, -100, 100)
    insertsort_array = SortingAlgorithms.insertsort(test_array_1.copy())
    quicksort_array = SortingAlgorithms.quicksort(test_array_1.copy())

    assert insertsort_array == quicksort_array

    test_array_2 = generate_random_int_list(30, -200, 200)
    insertsort_array = SortingAlgorithms.insertsort(test_array_2.copy())
    quicksort_array = SortingAlgorithms.quicksort(test_array_2.copy())

    assert insertsort_array == quicksort_array

    test_array_3 = generate_random_float_list(15, -100, 100)
    insertsort_array = SortingAlgorithms.insertsort(test_array_3.copy())
    quicksort_array = SortingAlgorithms.quicksort(test_array_3.copy())

    assert insertsort_array == quicksort_array

    test_array_4 = generate_random_float_list(30, -200, 200)
    insertsort_array = SortingAlgorithms.insertsort(test_array_4.copy())
    quicksort_array = SortingAlgorithms.quicksort(test_array_4.copy())

    assert insertsort_array == quicksort_array

    print("All tests passed successfully")


if __name__ == '__main__':
    main()
