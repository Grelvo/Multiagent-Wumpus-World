from wumpusGame.percept import Percept
from wumpusGame.task import Task, ExplorationTask
from util.config import GRID_SIZE

from collections import deque


class Agent:
    def __init__(self, agent_id: int):
        self.agent_id: int = agent_id

        self.x: int | None = None
        self.y: int | None = None

        self.dead = False

    def reset(self):
        self.x = None
        self.y = None

        self.dead = False

    def bid_for_task(self, task: ExplorationTask, path: list[tuple[int, int]]) -> float:
        if self.dead:
            return -float('inf')

        if path is None:
            return -float('inf')

        path_length = len(path)

        bid = task.reward - path_length
        return bid

    def create_bfs_paths(self, beliefs: dict[tuple[int, int], dict[str, bool]]) -> any:
        queue = deque([(self.x, self.y)])
        came_from = {(self.x, self.y): None}

        while queue:
            current = queue.popleft()
            x, y = current

            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nx, ny = x + dx, y + dy

                if not (0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE):
                    continue

                if (nx, ny) in came_from:
                    continue

                cell_info = beliefs.get((nx, ny), {})
                if cell_info.get("potential_pit") or cell_info.get("potential_wumpus") or cell_info.get("pit") or cell_info.get("wumpus"):
                    continue

                came_from[(nx, ny)] = current
                queue.append((nx, ny))

        return came_from

    @staticmethod
    def reconstruct_bfs_path(came_from: any, goal: tuple[int, int]) -> list[tuple[int, int]] | None:
        if goal not in came_from:
            return None

        path = []
        cur = goal
        while cur is not None:
            path.append(cur)
            cur = came_from[cur]

        return list(reversed(path))
