def find_pair(matrix, target):
    for row in matrix:
        for value in row:
            if value == target:
                return row, value
    return None
