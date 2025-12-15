from util.config import GRID_SIZE, NUM_WUMPUS, NUM_PITS, NUM_GOLD
from wumpusGame.cell import Cell

import random
from typing import Callable


class Board:
    """
    Represents the Gameboard for Hunt the Wumpus.

    Creates a Grid with Cells and randomly places:
    - Wumpus
    - Pits
    - Gold

    Also places Hints in the form of:
    - Breezes
    - Stench
    """
    def __init__(self):
        self.grid: list[list[Cell]] = []
        self.cells = []

    def setup_board(self) -> None:
        """Sets up the Cells in the Board"""
        self.grid = [
            [Cell(i, j) for j in range(GRID_SIZE)]
            for i in range(GRID_SIZE)
        ]

        self.cells = self._flatten_grid()
        self._populate_cells()

    def _populate_cells(self) -> None:
        """Populates the Cells in the Board"""
        self._place_element(NUM_WUMPUS, self._place_wumpus)
        self._place_element(NUM_PITS, self._place_pit)
        self._place_element(NUM_GOLD, self._place_gold)

        for cell in self.cells:
            neighbours = self._get_neighbours(cell)
            cell.hasStench = any(neighbour.hasWumpus for neighbour in neighbours)
            cell.hasBreeze = any(neighbour.hasPit for neighbour in neighbours)

    def _place_element(self, num: int, place_func: Callable[[Cell], None]) -> None:
        """Calls the gives place_func on randomly chosen cells"""
        cells = random.sample(self._get_available_cells(), num)
        for cell in cells:
            place_func(cell)

    @staticmethod
    def _place_wumpus(cell: Cell) -> None:
        """Helper Method for placing the Wumpus Element"""
        cell.hasWumpus = True

    @staticmethod
    def _place_pit(cell: Cell) -> None:
        """Helper Method for placing the Wumpus Element"""
        cell.hasPit = True

    @staticmethod
    def _place_gold(cell: Cell) -> None:
        """Helper Method for placing the Wumpus Element"""
        cell.hasGold = True

    def _get_available_cells(self) -> list[Cell]:
        """Returns the available Cells in the Board"""
        return [cell for cell in self.cells if not cell.hasWumpus and not cell.hasPit and not cell.hasGold]

    def _flatten_grid(self) -> list[Cell]:
        """Returns the flatten Grid"""
        return [cell for row in self.grid for cell in row]

    def _get_neighbours(self, cell: Cell) -> list[Cell]:
        """Returns the Neighbours of a Cell"""
        return [
            self.grid[x][y]
            for x, y in [
                (cell.x + 1, cell.y),
                (cell.x - 1, cell.y),
                (cell.x, cell.y + 1),
                (cell.x, cell.y - 1),
            ]
            if self._in_bounds((x, y))
        ]

    @staticmethod
    def _in_bounds(pos: tuple[int, int]) -> bool:
        """Checks if a given Position is in bounds"""
        return 0 <= pos[0] < GRID_SIZE and 0 <= pos[1] < GRID_SIZE

