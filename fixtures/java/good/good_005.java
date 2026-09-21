class MatrixSearch {
    int find(int[][] matrix, int target) {
        for (int[] row : matrix) {
            for (int value : row) {
                if (value == target)
                    return value;
            }
        }
        return -1;
    }
}
