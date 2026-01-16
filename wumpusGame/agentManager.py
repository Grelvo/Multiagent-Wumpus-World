from wumpusGame.task import ExplorationTask
from wumpusGame.board import Board
from wumpusGame.agent import Agent


class AgentManager:
    @staticmethod
    def create_tasks(agents: list[Agent], board: Board) -> list[ExplorationTask]:
        unexplored_cells = [
            cell for cell in board.cells
            if not any((cell.x, cell.y) in agent.visited for agent in agents)
        ]

        tasks = [ExplorationTask((cell.x, cell.y)) for cell in unexplored_cells]
        return tasks

    @staticmethod
    def create_bids(agents: list[Agent], tasks: list[ExplorationTask]) -> list[tuple[float, int, ExplorationTask, list[tuple[int, int]]]]:
        bids: list[tuple[float, int, ExplorationTask, any]] = []
        for agent in agents:
            if agent.dead:
                continue

            came_from = agent.create_bfs_paths()
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
