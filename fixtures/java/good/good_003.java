class Search {
    boolean contains(int[] values, int target) {
        for (int value : values) {
            if (value == target)
                return true;
        }
        return false;
    }
}
