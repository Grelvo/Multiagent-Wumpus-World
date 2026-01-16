class Task:
    def __init__(self, type_: str, target: tuple[int, int] = None, direction: tuple[int, int] | None = None):
        self.type: str = type_
        self.target: tuple[int, int] | None = target
        self.direction: tuple[int, int] | None = direction


class ExplorationTask:
    def __init__(self, target: tuple[int, int] = None):
        self.target: tuple[int, int] | None = target
        self.reward: int = 1


class TaskResult:
    def __init__(self, dead=False, gold=False):
        self.dead: bool = dead
        self.gold: bool = gold
