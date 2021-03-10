import random
import unittest

from InsertSort import insertion_sort
from MergeSort import merge_sort


def get_random_float_array(size, low_bound, high_bound):
    return [random.uniform(low_bound, high_bound) for _ in range(size)]


def get_random_int_array(size, low_bound, high_bound):
    return [random.randint(low_bound, high_bound) for _ in range(size)]


class SortTest(unittest.TestCase):
    def test_int_insert_sort(self):
        int_array = get_random_int_array(1000, -5, 23)
        copy_int_array = int_array.copy()
        insertion_sort(int_array)

        self.assertEqual(int_array, sorted(copy_int_array))

    def test_float_insert_sort(self):
        float_array = get_random_float_array(1000, -5.6, 23.8)
        copy_float_array = float_array.copy()
        insertion_sort(float_array)

        self.assertEqual(float_array, sorted(copy_float_array))

    def test_int_merge_sort(self):
        int_array = get_random_int_array(1000, -5, 23)
        copy_int_array = int_array.copy()
        merge_sort(int_array)

        self.assertEqual(int_array, sorted(copy_int_array))

    def test_float_merge_sort(self):
        float_array = get_random_float_array(1000, -5.6, 23.8)
        copy_float_array = float_array.copy()
        merge_sort(float_array)

        self.assertEqual(float_array, sorted(copy_float_array))


if __name__ == '__main__':
    unittest.main()
