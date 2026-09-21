class Sum {
    int sum(int[] values) {
        // Accumulate values in one visible pass.
        int total = 0;
        for (int value : values)
            total += value;
        return total;
    }
}
