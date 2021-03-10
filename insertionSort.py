
def sort(array):
    for i in range(1, len(array)):
        element = array[i]
        pos = i - 1

        while pos >= 0 and element < array[pos]:
            array[pos + 1] = array[pos]
            pos -= 1
        array[pos + 1] = element
