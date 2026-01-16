from wumpusGame.percept import Percept
from wumpusGame.task import Task, ExplorationTask
from util.config import GRID_SIZE

from collections import deque


class Agent:
    def __init__(self, agent_id: int):
        self.agent_id: int = agent_id

        self.x: int | None = None
        self.y: int | None = None

        self.visited: list[tuple[int, int]] = []
        self.belief: dict[tuple[int, int], dict[str, bool]] = {}

        self.dead = False

    def reset(self):
        self.x = None
        self.y = None

        self.visited = []
        self.dead = False

    def update_belief(self, percept: Percept):
        self.visited.append((self.x, self.y))
        self.belief[(self.x, self.y)] = self.belief.get((self.x, self.y), {})
        self.belief[(self.x, self.y)].update({
            "breeze": percept.breeze,
            "stench": percept.stench,
        })

        neighbors = [(self.x + 1, self.y), (self.x - 1, self.y), (self.x, self.y + 1), (self.x, self.y - 1)]

        if percept.stench or percept.breeze:
            for nx, ny in neighbors:
                if (nx, ny) not in self.visited and 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                    self.belief.setdefault((nx, ny), {})
                    self.belief[(nx, ny)]["potential_danger"] = True
        else:
            for nx, ny in neighbors:
                if (nx, ny) in self.belief and 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                    if self.belief[(nx, ny)].get("potential_danger"):
                        self.belief[(nx, ny)]["potential_danger"] = False

    def bid_for_task(self, task: ExplorationTask, path) -> float:
        if self.dead:
            return -float('inf')

        tx, ty = task.target

        cell_info = self.belief.get((tx, ty), {})
        if path is None or cell_info.get("potential_danger"):
            return -float('inf')

        path_length = len(path)

        bid = task.reward - path_length
        return bid

    def create_bfs_paths(self) -> any:
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

                cell_info = self.belief.get((nx, ny), {})
                if cell_info.get("potential_danger"):
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
