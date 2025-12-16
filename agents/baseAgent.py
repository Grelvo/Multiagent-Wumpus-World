from util.config import GRID_SIZE

import random


class BaseAgent:
    def __init__(self, agent_id: int):
        self.agent_id: int = agent_id

        self.x: int | None = None
        self.y: int | None = None

        self.visited: list[tuple[int, int]] = []
        self.dead = False
        self.score = 0

    def reset(self):
        self.x = None
        self.y = None

        self.visited = []
        self.dead = False

    def decide_next_move(self, board) -> tuple[int, int]:
        possible_moves: dict[tuple[int, int], int] = {
            (self.x + 1, self.y): 0,
            (self.x - 1, self.y): 0,
            (self.x, self.y + 1): 0,
            (self.x, self.y - 1): 0,
        }

        for move in possible_moves:
            x, y = move

            # avoid going out of bounds
            if not (0 <= x < GRID_SIZE) or not (0 <= y < GRID_SIZE):
                possible_moves[move] -= 1000
                continue

            cell = board.grid[x][y]

            # avoid wumpus and pit
            if ((cell.x, cell.y) not in self.visited
                    and (board.grid[self.x][self.y].hasBreeze
                         or board.grid[self.x][self.y].hasStench)):
                possible_moves[move] -= 100

        self._extended_decide_next_move(possible_moves, board)

        good_moves = [move for move in possible_moves.keys() if possible_moves[move] > 0]
        neutral_moves = [move for move in possible_moves.keys() if possible_moves[move] == 0]

        if len(good_moves) != 0:
            return random.choice(good_moves)
        elif len(neutral_moves) != 0:
            return random.choice(neutral_moves)
        else:
            return max(possible_moves, key=possible_moves.get)

    def _extended_decide_next_move(self, possible_moves: dict[tuple[int, int], int], board) -> None:
        pass
