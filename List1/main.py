import bubbleSort
import insertionSort
import random


def randomInts(low, high, size):
    return [random.randint(low, high) for _ in range(size)]


def randomFloats(low, high, size):
    return [random.uniform(low, high) for _ in range(size)]


def main():
    testInts = randomInts(-100, 100, 50)
    test1Bubble = testInts.copy()
    test1Insert = testInts.copy()

    testInts.sort()
    bubbleSort.sort(test1Bubble)
    insertionSort.sort(test1Insert)

    assert testInts == test1Bubble
    assert testInts == test1Insert

    testFloats = randomFloats(-100, 100, 50)
    test2Bubble = testFloats.copy()
    test2Insert = testFloats.copy()

    testFloats.sort()
    bubbleSort.sort(test2Bubble)
    insertionSort.sort(test2Insert)

    assert testFloats == test2Bubble
    assert testFloats == test2Insert

    testEmpty = randomFloats(-100, 100, 0)
    test3Bubble = testEmpty.copy()
    test3Insert = testEmpty.copy()

    testEmpty.sort()
    bubbleSort.sort(test3Bubble)
    insertionSort.sort(test3Insert)

    assert testEmpty == test3Bubble
    assert testEmpty == test3Insert


if __name__ == "__main__":
    main()
