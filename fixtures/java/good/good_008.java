class Nested {
    int find(int[][][] cube, int target) {
        for (int[][] plane : cube) {
            for (int[] row : plane) {
                for (int value : row) {
                    if (value == target)
                        return value;
                }
            }
        }
        return -1;
    }
}
