class DeepLogic {
    int find(int[][] matrix, int target) {
        for (int[] first : matrix) {
            for (int value : first) {
                if (value == target)
                    return unknownValue + secondUnknownValue;
            }
        }
        return -1;
    }
}
