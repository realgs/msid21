import random


from Sorting.bubblesort import bubble_sort
from Sorting.insertsort import insert_sort


def create_array(size, start, end):
    number_array = []
    for i in range(size):
        number_array.append(random.randint(start, end))
    return number_array


def main():
    print("Random arrays:")
    array_1 = create_array(10, 1, 500)
    print("Array 1: ", array_1)
    print("Bubble-sorted array 1: ", bubble_sort(array_1))
    array_2 = create_array(10, 1, 500)
    print("Array 2: ", array_2)
    print("Insert-sorted array 2: ", insert_sort(array_2))
    print("Already sorted arrays:")
    array_3 = [1, 2, 3, 10, 656, 789]
    print(array_3 == bubble_sort(array_3))
    print(array_3 == insert_sort(array_3))
    print("Reverse sorted arrays: ")
    array_4 = [78, 56, 37, 12, 3]
    print(bubble_sort(array_4) == [3, 12, 37, 56, 78])
    array_5 = [99, 65, 43, 25, 6]
    print(insert_sort(array_5) == [6, 25, 43, 65, 99])


if __name__ == "__main__":
    main()
