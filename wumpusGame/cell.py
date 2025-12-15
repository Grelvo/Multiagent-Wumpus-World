class Cell:
    """
    Represents a Cell in the Gameboard Grid.
    Contains the Information of what is inside the Cell.
    """
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

        # Hazards
        self.hasPit = False
        self.hasWumpus = False

        # Hints
        self.hasBreeze = False
        self.hasStench = False

        # Rewards
        self.hasGold = False
