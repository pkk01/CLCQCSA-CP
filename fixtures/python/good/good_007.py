def search(items, target):
    for first in items:
        for second in items:
            if first == second and first == target:
                return True
    return False
