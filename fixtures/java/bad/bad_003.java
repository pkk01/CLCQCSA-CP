class UndefinedLoop {
    int find(int[] values, int target) {
        for (int value : missingValues) {
            if (value == target)
                return missingValue + anotherMissingValue;
        }
        return -1;
    }
}
