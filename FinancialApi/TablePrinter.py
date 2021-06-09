MIN_COLUMN_SIZE = 20
TABLE_SEPARATOR = "|"


def printSingleSizeRow(cellSize, *texts):
    columnSize = MIN_COLUMN_SIZE * cellSize + \
        len(TABLE_SEPARATOR) * (cellSize - 1)
    output = TABLE_SEPARATOR

    for text in texts:
        output += f"{text:^{columnSize}}{TABLE_SEPARATOR}"

    print(output)


def printMultiSizeRow(*pairs):
    output = TABLE_SEPARATOR

    for pair in pairs:
        columnSize = MIN_COLUMN_SIZE * pair[0] + \
            len(TABLE_SEPARATOR) * (pair[0] - 1)
        output += f"{pair[1]:^{columnSize}}{TABLE_SEPARATOR}"

    print(output)


def printHorizontalSeparator(columns):
    dashesAmount = MIN_COLUMN_SIZE * columns + \
        len(TABLE_SEPARATOR) * (columns - 1)
    print(TABLE_SEPARATOR + ('-' * dashesAmount) + TABLE_SEPARATOR)
