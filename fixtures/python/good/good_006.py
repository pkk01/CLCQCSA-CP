def describe(value):
    if value is None:
        return "missing"
    if value < 0:
        return "negative"
    if value == 0:
        return "zero"
    return "positive"
