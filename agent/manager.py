from agent.task import Task, MoveTask, ShootTask, TaskResult
from agent.core import Agent
from game.board import Board
from util.helperFunc import get_neighbours
from util.config import SHOOT, RISKY


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
        self.shared_visited.clear()
        self.shared_beliefs = {}
        self._potential_danger_groups = []

    def update_beliefs(self, agent: Agent, result: TaskResult) -> None:
        """Updates the shared_visited and shared_beliefs state.
        Also marks potential dangers and converts potential dangers to confirmed dangers.

        :param agent: The agent that did the task.
        :param result: The result of the task.
        """
        self.shared_visited.add((agent.x, agent.y))
        self.shared_beliefs.setdefault((agent.x, agent.y), {}).update({
            "breeze": result.breeze,
            "stench": result.stench,
            "potential_pit": False,
            "potential_wumpus": False,
            "pit": result.pit,
            "wumpus": result.wumpus,
        })

        if result.wumpus_died:
            self.shared_beliefs.setdefault(result.wumpus_died, {}).update({
                "wumpus": False,
                "dead_wumpus": True,
            })

        neighbors = get_neighbours(agent.x, agent.y)

        if result.stench or result.breeze:
            potential_danger_group = []
            for nx, ny in neighbors:
                if (self.shared_beliefs.get((nx, ny), {}).get("wumpus") or
                        self.shared_beliefs.get((nx, ny), {}).get("dead_wumpus") or
                        self.shared_beliefs.get((nx, ny), {}).get("pit")):
                    potential_danger_group.append((nx, ny))
                    continue
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
                    "potential_pit": result.breeze,
                    "potential_wumpus": result.stench,
                })
                potential_danger_group.append((nx, ny))

            if all(self.shared_beliefs.get((pdx, pdy), {}).get("wumpus") or
                   self.shared_beliefs.get((pdx, pdy), {}).get("dead_wumpus") or
                   self.shared_beliefs.get((pdx, pdy), {}).get("pit") for (pdx, pdy) in potential_danger_group):
                return

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
                        if not (self.shared_beliefs.get(group[0], {}).get("wumpus") or
                                self.shared_beliefs.get(group[0], {}).get("dead_wumpus") or
                                self.shared_beliefs.get(group[0], {}).get("pit")):
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
        tasks = []

        move_tasks = [
            MoveTask((cell.x, cell.y)) for cell in board.cells
            if not (cell.x, cell.y) in self.shared_visited
            and not self.shared_beliefs.get((cell.x, cell.y), {}).get("wumpus")
            and not self.shared_beliefs.get((cell.x, cell.y), {}).get("pit")
        ]
        tasks.extend(move_tasks)

        if SHOOT:
            shoot_tasks = [
                ShootTask((bx, by)) for (bx, by) in self.shared_beliefs.keys()
                if self.shared_beliefs.get((bx, by), {}).get("wumpus")
            ]
            tasks.extend(shoot_tasks)

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

            came_from, cost_so_far = agent.create_dijkstra_paths(self.shared_beliefs, risky=RISKY)

            for task in tasks:
                bid, path = agent.bid_for_task(task, came_from, cost_so_far, [(a.x, a.y) for a in self._agents if a is not agent and not a.dead])
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
            if path is None or agent_id in awarded_tasks or task in awarded_tasks.values():
                continue
            task.path = path
            awarded_tasks[agent_id] = task
        return awarded_tasks
