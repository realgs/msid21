PRECISION = 4
MIN_COLUMN_SIZE = 16
TABLE_SEPARATOR = "|"

def printTableRow(cellSize, *headrs):
    columnSize = MIN_COLUMN_SIZE * cellSize + len(TABLE_SEPARATOR) * (cellSize - 1)
    output = TABLE_SEPARATOR

    for header in headrs:
        output += f"{header:^{columnSize}}{TABLE_SEPARATOR}"
    
    print(output)
