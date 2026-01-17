from enum import Enum


class TaskType(Enum):
    """An enum to hold the different types of task types."""
    MOVE = 1
    SHOOT = 2


class Task:
    """The base task class.

    :ivar task_type (TaskType): The type of task.
    :ivar target (tuple[int, int]): The target of the task.
    :ivar path (list[tuple[int, int]]): The path to complete the task.
    :ivar reward (int): The reward for completing the task.
    """
    def __init__(self, task_type: TaskType, target: tuple[int, int], reward: int):
        self.task_type = task_type
        self.target: tuple[int, int] = target
        self.path: list[tuple[int, int]] | None = None
        self.reward: int = reward


class MoveTask(Task):
    """A task to move to a certain target."""
    def __init__(self, target: tuple[int, int]):
        super().__init__(TaskType.MOVE, target, 1)


class ShootTask(Task):
    """A task to shoot a certain target."""
    def __init__(self, target: tuple[int, int]):
        super().__init__(TaskType.SHOOT, target, 10)


class TaskResult:
    """The result of a task.

    :ivar dead (bool): Whether the agent died as a result of the task.
    :ivar gold (bool): Whether the agent found gold as a result of the task.
    """
    def __init__(self, dead=False, gold=False):
        self.dead: bool = dead
        self.gold: bool = gold
