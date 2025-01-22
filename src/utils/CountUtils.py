from typing import Tuple, List


def getPagesAndLimit(number: int) -> Tuple[List[int], int]:
    # limit max number is 50
    number = number
    if number <= 50:
        pages = [0]
        limit = number
    else:
        pages = list(range(0, number // 50 + 1))
        limit = 50
    return pages, limit
