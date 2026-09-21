def summarize(values):
    # The loop keeps the aggregation explicit for review.
    total = 0
    count = 0
    for value in values:
        total += value
        count += 1
    if count == 0:
        return 0
    return total / count
