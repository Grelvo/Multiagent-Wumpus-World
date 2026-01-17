from agent.task import Task, TaskType
from util.helperFunc import get_neighbours

from collections import deque


class Agent:
    """An agent that wants to complete its gives task.

    :ivar agent_id (int): The unique id of the agent.
    :ivar x (int): The x coordinate of the agent.
    :ivar y (int): The y coordinate of the agent.
    :ivar dead (bool): Whether the agent is dead.
    """
    def __init__(self, agent_id: int):
        self.agent_id: int = agent_id

        self.x: int | None = None
        self.y: int | None = None

        self.dead = False

    def reset(self) -> None:
        """Resets the agent back to its initial state."""
        self.x = None
        self.y = None

        self.dead = False

    def bid_for_task(self, task: Task, came_from: dict[tuple[int, int], tuple[int, int]]) \
            -> tuple[float, list[tuple[int, int]] | None]:
        """Creates a bid value for a task and the path towards completing it.

        :param task: The task on which needs to be bid.
        :param came_from: The Network of Paths from its current Position to any other.
        :return: The bid value for the task and the path for it.
        """
        bid = -float('inf')
        path = None

        if self.dead:
            return bid, path

        if task.task_type == TaskType.MOVE:
            path = self._reconstruct_bfs_path(came_from, task.target)

            if path is None:
                return bid, path

            path_length = len(path)
            bid = task.reward - path_length

        elif task.task_type == TaskType.SHOOT:
            path = self._reconstruct_bfs_path(came_from, task.target)
            path_length = len(path)
            bid = task.reward - path_length

        return bid, path

    def create_bfs_paths(self, beliefs: dict[tuple[int, int], dict[str, bool]]) \
            -> dict[tuple[int, int], tuple[int, int]]:
        """Creates a Network of Paths from its current position to any other on the board.

        :param beliefs: The current beliefs the agents have on the board.
        :return: The Network of Paths.
        """
        queue = deque([(self.x, self.y)])
        came_from: dict[tuple[int, int], tuple[int, int]] = {(self.x, self.y): None}

        while queue:
            current = queue.popleft()
            x, y = current

            neighbours = get_neighbours(x, y)
            for nx, ny in neighbours:
                if (nx, ny) in came_from:
                    continue

                cell_info = beliefs.get((nx, ny), {})
                if (cell_info.get("potential_pit") or cell_info.get("potential_wumpus") or
                        cell_info.get("pit") or cell_info.get("wumpus")):
                    continue

                came_from[(nx, ny)] = current
                queue.append((nx, ny))

        return came_from

    @staticmethod
    def _reconstruct_bfs_path(came_from: dict[tuple[int, int], tuple[int, int]], goal: tuple[int, int]) \
            -> list[tuple[int, int]] | None:
        """Reconstructs the shortest path from its current position to the goal.

        :param came_from: The Network of Paths from its current position to any other.
        :param goal: The position the agents want to go to.
        :return: The shortest path to reach the goal.
        """
        if goal not in came_from:
            return None

        path = []
        cur = goal
        while cur is not None:
            path.append(cur)
            cur = came_from[cur]

        return list(reversed(path))
