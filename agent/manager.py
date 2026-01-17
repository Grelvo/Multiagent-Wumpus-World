from agent.task import Task, MoveTask
from agent.core import Agent
from agent.percept import Percept
from game.board import Board
from util.helperFunc import get_neighbours


class AgentManager:
    """Handles the shared vision of the Agents and Creates and awards Tasks to the Agents.

    :ivar _agents (list[Agent]): The agents that are being managed
    :ivar shared_visited (set[tuple[int, int]]): The Coordinates the agents have already visited
    :ivar shared_beliefs (dict[tuple[int, int], dict[str, bool]]): Contains the information the agents have gathered
        on the cells
    :ivar _potential_danger_groups (list[list[tuple[int, int]]]): A list of Groups of cells, of which exactly one
        is dangerous
    """
    def __init__(self, agents: list[Agent]):
        self._agents: list[Agent] = agents
        self.shared_visited: set[tuple[int, int]] = set()
        self.shared_beliefs: dict[tuple[int, int], dict[str, bool]] = {}
        self._potential_danger_groups: list[list[tuple[int, int]]] = []

    def reset(self) -> None:
        """Resets the Agent-Manager back to its initial state."""
        self.shared_visited = set()
        self.shared_beliefs = {}
        self._potential_danger_groups = []

    def update_beliefs(self, agent: Agent, percept: Percept) -> None:
        """Updates the shared_visited and shared_beliefs state.
        Also marks potential dangers and converts potential dangers to confirmed dangers.

        :param agent: The Agent that perceived something new.
        :param percept: The information the Agent perceived.
        """
        self.shared_visited.add((agent.x, agent.y))
        self.shared_beliefs.setdefault((agent.x, agent.y), {}).update({
            "breeze": percept.breeze,
            "stench": percept.stench,
        })

        neighbors = get_neighbours(agent.x, agent.y)

        if percept.stench or percept.breeze:
            potential_danger_group = []
            for nx, ny in neighbors:
                if (nx, ny) in self.shared_visited:
                    continue

                potential_danger_neighbors = get_neighbours(nx, ny)

                if any(
                        pdn_pos in self.shared_visited and not
                        (
                            self.shared_beliefs.get(pdn_pos, {}).get("breeze") or
                            self.shared_beliefs.get(pdn_pos, {}).get("stench")
                        )
                        for pdn_pos in potential_danger_neighbors
                ):
                    continue

                self.shared_beliefs.setdefault((nx, ny), {}).update({
                    "potential_pit": percept.breeze,
                    "potential_wumpus": percept.stench,
                })
                potential_danger_group.append((nx, ny))

            if len(potential_danger_group) == 1:
                potential_pit = self.shared_beliefs.get(potential_danger_group[0], {}).get("potential_pit")
                potential_wumpus = self.shared_beliefs.get(potential_danger_group[0], {}).get("potential_wumpus")
                self.shared_beliefs[potential_danger_group[0]].update({
                    "potential_pit": False,
                    "potential_wumpus": False,
                    "pit": potential_pit,
                    "wumpus": potential_wumpus,
                })
            elif len(potential_danger_group):
                self._potential_danger_groups.append(potential_danger_group)
        else:
            for nx, ny in neighbors:
                potential_pit = self.shared_beliefs.get((nx, ny), {}).get("potential_pit")
                potential_wumpus = self.shared_beliefs.get((nx, ny), {}).get("potential_wumpus")

                if not (potential_pit or potential_wumpus):
                    continue

                self.shared_beliefs[(nx, ny)].update({
                    "potential_pit": False,
                    "potential_wumpus": False,
                })

                for group in self._potential_danger_groups.copy():
                    if (nx, ny) not in group:
                        continue

                    group.remove((nx, ny))

                    if len(group) == 1:
                        self.shared_beliefs[group[0]].update({
                            "potential_pit": False,
                            "potential_wumpus": False,
                            "pit": potential_pit,
                            "wumpus": potential_wumpus,
                        })
                        self._potential_danger_groups.remove(group)

    def create_tasks(self, board: Board) -> list[Task]:
        """Creates Tasks for the agents to complete.

        :param board: The Board of the Game.
        :return: The list of created tasks.
        """
        unexplored_cells = [
            cell for cell in board.cells
            if not (cell.x, cell.y) in self.shared_visited
        ]

        tasks = [MoveTask((cell.x, cell.y)) for cell in unexplored_cells]
        return tasks

    def create_bids(self, tasks: list[Task]) -> list[tuple[float, int, Task, list[tuple[int, int]]]]:
        """Lets each agent bid for each task.

        :param tasks: The tasks that where created for this game state.
        :return: A list of bids that each contain: bid, agent_id, task, path.
        """
        bids: list[tuple[float, int, Task, list[tuple[int, int]]]] = []
        for agent in self._agents:
            if agent.dead:
                continue

            came_from = agent.create_bfs_paths(self.shared_beliefs)
            for task in tasks:
                bid, path = agent.bid_for_task(task, came_from)
                bids.append((bid, agent.agent_id, task, path))

        bids.sort(reverse=True, key=lambda x: x[0])
        return bids

    @staticmethod
    def award_tasks(bids: list[tuple[float, int, Task, list[tuple[int, int]]]]) -> dict[int, Task]:
        """Gives out one task to each agent.
        The Task that have the highest bid will be given out first,
        where the agent with the highest bid will get the task.

        :param bids: The bids the agents have made for each task.
        :return: A dict with the agent_id and the task that was given to that agent.
        """
        awarded_tasks: dict[int, Task] = {}
        for bid, agent_id, task, path in bids:
            if agent_id not in awarded_tasks and task not in awarded_tasks.values():
                if path is None:
                    continue
                task.path = path
                awarded_tasks[agent_id] = task
        return awarded_tasks
