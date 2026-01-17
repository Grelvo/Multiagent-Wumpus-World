from util.config import GRID_SIZE


def is_in_bounds(pos: tuple[int, int]) -> bool:
    """Helper function to determine if a postion is in bounds.

    :param pos: The position that needs to be checked.
    :return: Whether the position is in bounds.
    """
    return 0 <= pos[0] < GRID_SIZE and 0 <= pos[1] < GRID_SIZE


def get_neighbours(x: int, y: int) -> list[tuple[int, int]]:
    """Gets all the neighbours of a position.

    :param x: The x postion of which the neighbours should be got.
    :param y: The y postion of which the neighbours should be got.
    :return: A list of the positions neighbours.
    """
    return [
        (nx, ny)
        for nx, ny in [
            (x + 1, y),
            (x - 1, y),
            (x, y + 1),
            (x, y - 1),
        ]
        if is_in_bounds((nx, ny))
    ]