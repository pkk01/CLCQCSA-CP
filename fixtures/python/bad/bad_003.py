def unsafe(items):
    for first in items:
        for second in items:
            for third in items:
                for fourth in items:
                    if fourth:
                        return unknown_result
    return None
