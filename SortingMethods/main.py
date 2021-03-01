import mergeSort
import insertionSort
import random


def generateArrayOfInt(length, lowerNumber, higherNumber):
    return [random.randint(lowerNumber, higherNumber) for _ in range(0, length)]


def generateArrayOfFloat(length, lowerNumber, higherNumber, precision):
    return [round(random.uniform(lowerNumber, higherNumber), precision) for _ in range(0, length)]


if __name__ == '__main__':
    arrayOfInt1 = generateArrayOfInt(100, -1000, 1000)
    arrayOfIntClone1 = arrayOfInt1.copy()
    arrayOfFloats1 = generateArrayOfFloat(100, -1000, 1000, 3)
    arrayOfFloatsClone1 = arrayOfFloats1.copy()

    assert mergeSort.mergeSort(arrayOfInt1) == sorted(arrayOfIntClone1), "Failed"
    assert mergeSort.mergeSort(arrayOfFloats1) == sorted(arrayOfFloatsClone1), "Failed"

    arrayOfInt2 = generateArrayOfInt(100, -1000, 1000)
    arrayOfIntClone2 = arrayOfInt2.copy()
    arrayOfFloats2 = generateArrayOfFloat(100, -1000, 1000, 3)
    arrayOfFloatsClone2 = arrayOfFloats2.copy()

    assert insertionSort.insertionSort(arrayOfInt2) == sorted(arrayOfIntClone2), "Failed"
    assert insertionSort.insertionSort(arrayOfFloats2) == sorted(arrayOfFloatsClone2), "Failed"

    print("Tests passed successfully")
