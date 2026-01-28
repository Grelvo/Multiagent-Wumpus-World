from agent.task import Task, TaskType
from util.helperFunc import get_neighbours
from util.config import *

from collections import deque
import heapq


class Agent:
    """An agent that wants to complete its gives task.

    :ivar agent_id (int): The unique id of the agent.
    :ivar x (int): The x coordinate of the agent.
    :ivar y (int): The y coordinate of the agent.
    :ivar has_arrow (bool): Whether the agent has an arrow.
    :ivar dead (bool): Whether the agent is dead.
    """
    def __init__(self, agent_id: int):
        self.agent_id: int = agent_id

        self.x: int | None = None
        self.y: int | None = None

        self.has_arrow = True

        self.dead = False

    def reset(self) -> None:
        """Resets the agent back to its initial state."""
        self.x = None
        self.y = None

        self.has_arrow = True

        self.dead = False

    def bid_for_task(self,
                     task: Task,
                     came_from: dict[tuple[int, int], tuple[int, int]],
                     cost_so_far: dict[tuple[int, int], int] | None,
                     agent_pos: list[tuple[int, int]]) -> tuple[float, list[tuple[int, int]] | None]:
        """Creates a bid value for a task and the path towards completing it.

        :param task: The task on which needs to be bid.
        :param came_from: The network of paths from its current position to any other.
        :param cost_so_far: A dict with the positions and the cost of getting to it.
        :param agent_pos: The positions of all the other agents.
        :return: The bid value for the task and the path for it.
        """
        bid = -float('inf')
        path = None
        cost = float('inf')
        manhattan_bonus = 0

        if self.dead:
            return bid, path

        if task.task_type == TaskType.MOVE:
            # recreates the path from the Network of paths and the goal
            path = self._reconstruct_path(came_from, task.target)
            if path is None:
                return bid, path
            tx, ty = task.target
            # bonus for giving an edge to targets that are further away from other agents
            if MANHATTEN_BONUS:
                manhattan_bonus = min([abs(ax - tx) + abs(ay - ty) for (ax, ay) in agent_pos], default=0) / 100
            # cost for getting to the target
            cost = cost_so_far.get(task.target, float('inf'))

        elif task.task_type == TaskType.SHOOT and self.has_arrow:
            # recreates the path to the nearest aligned cell from the Network of paths and the goal
            path = self._nearest_aligned_cell_path(came_from, task.target)
            if path is None:
                return bid, path
            tx, ty = path[len(path) - 1]
            # bonus for giving an edge to targets that are further away from other agents
            if MANHATTEN_BONUS:
                manhattan_bonus = min([abs(ax - tx) + abs(ay - ty) for (ax, ay) in agent_pos], default=0) / 100
            # cost for getting to the nearest aligned cell
            cost = cost_so_far.get((tx, ty), float('inf'))

        # creates bid with the reward, the travel cost and the manhatten-bonus
        bid = task.reward - cost + manhattan_bonus

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

    def create_dijkstra_paths(self, beliefs: dict[tuple[int, int], dict[str, bool]], risky=False) \
            -> tuple[dict[tuple[int, int], tuple[int, int]], dict[tuple[int, int], int]]:
        """Creates a Network of Paths from its current position to any other on the board.

        :param beliefs: The current beliefs the agents have on the board.
        :param risky: Whether an agent can run onto potential danger.
        :return: The Network of Paths and the cost to travel to each cell.
        """

        start = (self.x, self.y)
        frontier = [(0, start)]

        came_from: dict[tuple[int, int], tuple[int, int]] = {start: None}
        cost_so_far: dict[tuple[int, int], int] = {start: 0}

        while frontier:
            current_cost, (x, y) = heapq.heappop(frontier)

            neighbours = get_neighbours(x, y)
            for nx, ny in neighbours:
                cell_info = beliefs.get((nx, ny), {})

                if cell_info.get("pit") or cell_info.get("wumpus"):
                    continue

                if cell_info.get("potential_pit") or cell_info.get("potential_wumpus"):
                    if risky:
                        step_cost = 1000
                    else:
                        continue
                else:
                    step_cost = 1

                new_cost = current_cost + step_cost

                if (nx, ny) not in cost_so_far or new_cost < cost_so_far.get((nx, ny)):
                    cost_so_far[(nx, ny)] = new_cost
                    came_from[(nx, ny)] = (x, y)
                    heapq.heappush(frontier, (new_cost, (nx, ny)))

        return came_from, cost_so_far

    @staticmethod
    def _reconstruct_path(came_from: dict[tuple[int, int], tuple[int, int]], goal: tuple[int, int]) \
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

        path.reverse()
        return path

    def _nearest_aligned_cell_path(self, came_from: dict[tuple[int, int], tuple[int, int]], goal: tuple[int, int]) \
            -> list[tuple[int, int]] | None:
        """Gives the path to the nearest cell that is in the same row or column as the goal.

        :param came_from: The Network of Paths from its current position to any other.
        :param goal: The position of which the agent wants to be in the same row or column.
        :return: The shortest path to reach a cell aligned to the goal.
        """
        tx, ty = goal
        aligned_positions = []

        for (x, y) in came_from.keys():
            if x == tx or y == ty:
                aligned_positions.append((x, y))

        shortest_path: list[tuple[int, int]] | None = None
        for pos in aligned_positions:
            path = self._reconstruct_path(came_from, pos)

            if path is None:
                continue

            if shortest_path is None or len(path) < len(shortest_path):
                shortest_path = path

        return shortest_path
