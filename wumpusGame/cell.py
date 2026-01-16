class Cell:
    """
    Represents a Cell in the Gameboard Grid.
    Contains the Information of what is inside the Cell.
    """
    def __init__(self, x: int, y: int):
        self.x: int = x
        self.y: int = y

        self.hasPit: bool = False
        self.hasAliveWumpus: bool = False
        self.hasDeadWumpus: bool = False

        self.hasStench: bool = False
        self.hasBreeze: bool = False

        self.hasGold: bool = False
