from wumpusGame.task import ExplorationTask
from wumpusGame.board import Board
from wumpusGame.agent import Agent
from wumpusGame.percept import Percept
from util.config import GRID_SIZE


class AgentManager:
    def __init__(self, agents: list[Agent]):
        self._agents: list[Agent] = agents
        self.shared_visited: set[tuple[int, int]] = set()
        self.shared_beliefs: dict[tuple[int, int], dict[str, bool]] = {}
        self._potential_danger_groups: list[list[tuple[int, int]]] = []

    def reset(self):
        self.shared_visited = set()
        self.shared_beliefs = {}
        self._potential_danger_groups = []

    def update_beliefs(self, agent: Agent, percept: Percept):
        self.shared_visited.add((agent.x, agent.y))
        self.shared_beliefs.setdefault((agent.x, agent.y), {}).update({
            "breeze": percept.breeze,
            "stench": percept.stench,
        })

        neighbors = [
            (agent.x + dx, agent.y + dy)
            for (dx, dy) in [(1, 0), (-1, 0), (0, 1), (0, -1)]
            if 0 <= agent.x + dx < GRID_SIZE and 0 <= agent.y + dy < GRID_SIZE
        ]

        if percept.stench or percept.breeze:
            potential_danger_group = []
            for nx, ny in neighbors:
                if (nx, ny) in self.shared_visited:
                    continue

                potential_danger_neighbors = [
                    (nx + dx, ny + dy)
                    for (dx, dy) in [(1, 0), (-1, 0), (0, 1), (0, -1)]
                    if 0 <= nx + dx < GRID_SIZE and 0 <= ny + dy < GRID_SIZE
                ]

                if any(pdn_pos in self.shared_visited and not (self.shared_beliefs.get(pdn_pos, {}).get("breeze") or self.shared_beliefs.get(pdn_pos, {}).get("stench")) for pdn_pos in potential_danger_neighbors):
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

    def potential_danger(self, pos: tuple[int, int]):
        pos_belief = self.shared_beliefs.get(pos, {})
        return pos_belief.get("potential_pit") or pos_belief.get("potential_wumpus")

    def create_tasks(self, board: Board) -> list[ExplorationTask]:
        unexplored_cells = [
            cell for cell in board.cells
            if not (cell.x, cell.y) in self.shared_visited
        ]

        tasks = [ExplorationTask((cell.x, cell.y)) for cell in unexplored_cells]
        return tasks

    def create_bids(self, tasks: list[ExplorationTask]) -> list[tuple[float, int, ExplorationTask, list[tuple[int, int]]]]:
        bids: list[tuple[float, int, ExplorationTask, list[tuple[int, int]]]] = []
        for agent in self._agents:
            if agent.dead:
                continue

            came_from = agent.create_bfs_paths(self.shared_beliefs)
            for task in tasks:
                path = agent.reconstruct_bfs_path(came_from, task.target)
                bid = agent.bid_for_task(task, path)
                bids.append((bid, agent.agent_id, task, path))

        bids.sort(reverse=True, key=lambda x: x[0])
        return bids

    @staticmethod
    def award_tasks(bids: list[tuple[float, int, ExplorationTask, list[tuple[int, int]]]]) -> dict[int, ExplorationTask]:
        awarded_tasks: dict[int, ExplorationTask] = {}
        for bid, agent_id, task, path in bids:
            if agent_id not in awarded_tasks and task not in awarded_tasks.values():
                if path is None:
                    continue
                task.target = path[1]
                awarded_tasks[agent_id] = task
        return awarded_tasks
