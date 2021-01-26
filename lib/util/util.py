from typing import Optional


def get_min_key(array: list) -> Optional[int]:
    for i in range(len(array)):
        if array[i] == 0:
            return i
    return None
