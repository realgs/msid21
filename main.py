import random
import string


def main():
    print("INSERT SORT TESTS")
    test_sort_algorithm(insert_sort)


def insert_sort(array):

    for i in range(1, len(array)):
        current_index = i
        while current_index > 0 and array[current_index] < array[current_index - 1]:
            swap(array, current_index, current_index - 1)
            current_index -= 1


def swap(array, index1, index2):
    aux = array[index1]
    array[index1] = array[index2]
    array[index2] = aux


def test_sort_algorithm(sort_algorithm):
    print("Test 1 empty array: {}".format(compare_arrays(0, 0, 1, sort_algorithm)))
    print("Test 2 small random integers: {}".format(compare_arrays(100, 1000, 2, sort_algorithm)))
    print("Test 3 big random integers: {}".format(compare_arrays(100, 1000, 1, sort_algorithm)))
    print("Test 4 big random float: {}".format(compare_arrays(100, 1000, 3, sort_algorithm)))
    print("Test 5 random characters: {}".format(compare_arrays(100, 1000, 4, sort_algorithm)))
    print("Test 6 random words: {}".format(compare_arrays(100, 1000, 5, sort_algorithm)))
    print("Test 7 ascending integers: {}".format(compare_arrays(100, 1000, -1, sort_algorithm)))
    print("Test 8 descending integers: {}\n\n".format(compare_arrays(100, 1000, -2, sort_algorithm)))


def compare_arrays(min_len, max_len, mode, sort_algorithm):
    if mode > 0:
        original_list = random_list(min_len, max_len, mode)
    else:
        original_list = ordered_list(min_len, max_len, abs(mode))

    copy_list = original_list[:]

    sort_algorithm(original_list)
    copy_list = sorted(copy_list)

    return original_list == copy_list


# mode 1 -> big random integers
# mode 2 -> small random integers
# mode 3 -> big random floats
# mode 4 -> random characters
# mode 5 -> random words
def random_list(min_len, max_len, mode):
    length_of_list = random.randint(min_len, max_len)
    letters = string.ascii_lowercase

    if mode == 1:
        return [random.randint(-1000000, 1000000) for _ in range(length_of_list)]
    elif mode == 2:
        return [random.randint(0, 10) for _ in range(length_of_list)]
    elif mode == 3:
        return [random.uniform(-100000, 1000000) for _ in range(length_of_list)]
    elif mode == 4:
        return [random.choice(letters) for _ in range(length_of_list)]
    else:
        return ["".join(random.choice(letters) for _ in range(random.randint(1, 10))) for _ in range(length_of_list)]


# mode 1 -> ascending order
# mode 2 -> descending order
def ordered_list(min_len, max_len, mode):
    length_of_list = random.randint(min_len, max_len)

    if mode == 1:
        return [i for i in range(length_of_list)]
    else:
        return [i for i in reversed(range(length_of_list))]


if __name__ == '__main__':
    main()
