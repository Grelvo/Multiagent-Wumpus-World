from util.config import GRID_SIZE, NUM_WUMPUS, NUM_PITS, NUM_GOLD
from util.helperFunc import is_in_bounds, get_neighbours
from game.cell import Cell
from agent.core import Agent
from agent.percept import Percept
from agent.task import Task, TaskResult, TaskType

import random
from typing import Callable


class Board:
    """The gameboard that contains all the cells.

    :ivar _grid (list[list[Cell]]): A grid layout of the gameboard.
    :ivar cells (list[Cell]): A list of all the cells in the grid.
    """
    def __init__(self):
        self._grid: list[list[Cell]] = []
        self.cells: list[Cell] = []

    def reset(self) -> None:
        """Resets the board back to its initial state."""
        self._grid = []
        self.cells = []

    def setup_board(self, agents: list[Agent]) -> None:
        """Sets up the cells in the board.

        :param agents: The agents that need to be placed on the board.
        """
        self._grid = [
            [Cell(i, j) for j in range(GRID_SIZE)]
            for i in range(GRID_SIZE)
        ]
        self.cells = self._get_flattened_grid()

        self._populate_cells(agents)

    def _populate_cells(self, agents: list[Agent]) -> None:
        """Populates the cells on the board with wumpus, pits, gold and the agents.

        :param agents: The agents that need to be placed on the board.
        """
        self._place_element(NUM_WUMPUS, self._place_wumpus)
        self._place_element(NUM_PITS, self._place_pit)
        self._place_element(NUM_GOLD, self._place_gold)

        for cell in self.cells:
            neighbours = get_neighbours(cell.x, cell.y)
            cell.hasStench = any(self._grid[nx][ny].hasAliveWumpus for nx, ny in neighbours)
            cell.hasBreeze = any(self._grid[nx][ny].hasPit for nx, ny in neighbours)

        agent_cells: list[Cell] = random.sample(self._get_available_cells(), len(agents))
        for index, cell in enumerate(agent_cells):
            agents[index].x = cell.x
            agents[index].y = cell.y

    def _place_element(self, num: int, place_func: Callable[[Cell], None]) -> None:
        """Places a certain number of elements on free spaces on the board.

        :param num: The number of elements that should be placed.
        :param place_func: A helper function to place the desired element.
        """
        cells = random.sample(self._get_available_cells(), num)
        for cell in cells:
            place_func(cell)

    @staticmethod
    def _place_wumpus(cell: Cell) -> None:
        """Helper method for placing the wumpus element.

        :param cell: The cell where the wumpus should be placed.
        """
        cell.hasAliveWumpus = True

    @staticmethod
    def _place_pit(cell: Cell) -> None:
        """Helper method for placing the pit element.

        :param cell: The cell where the pit should be placed.
        """
        cell.hasPit = True

    @staticmethod
    def _place_gold(cell: Cell) -> None:
        """Helper method for placing the gold element.

        :param cell: The cell where the gold should be placed.
        """
        cell.hasGold = True

    def _get_available_cells(self) -> list[Cell]:
        """Gathers the free available cell of the board.

        :return: The available cells.
        """
        return [
            cell for cell in self.cells
            if not cell.hasAliveWumpus
            and not cell.hasPit
            and not cell.hasGold
            and not cell.hasBreeze
            and not cell.hasStench
        ]

    def _get_flattened_grid(self) -> list[Cell]:
        """Gets a flattened version of the grid.

        :return: A list of all the cells in the grid.
        """
        return [cell for row in self._grid for cell in row]

    def get_percept(self, x: int, y: int) -> Percept:
        """Gets the information of the cell the agent perceives.

        :param x: The x coordinate of the cell.
        :param y: The y coordinate of the cell.
        :return: A percept object with the cell's information.
        """
        cell = self._grid[x][y]
        return Percept(
            breeze=cell.hasBreeze,
            stench=cell.hasStench,
        )

    def execute_task(self, agent: Agent, task: Task) -> TaskResult:
        """Executes a task an agent was awarded with.

        :param agent: The agent that was gives the task.
        :param task: The task that needs to execute.
        :return: The result of the agent trying to complete that task.
        """
        if task.task_type == TaskType.MOVE:
            next_target = task.path[1]

            if not is_in_bounds(next_target):
                return TaskResult(dead=True)

            agent.x, agent.y = next_target
            cell = self._grid[agent.x][agent.y]

            return TaskResult(
                dead=cell.hasPit or cell.hasAliveWumpus,
                gold=cell.hasGold,
            )
        elif task.task_type == TaskType.SHOOT:
            pass
