class Cell:
    """Represents a cell in the gameboard grid and contains the information of what is inside.

    :ivar x (int): The x coordinate of the cell.
    :ivar y (int): The y coordinate of the cell.
    :ivar hasPit (bool): Whether the cell contains a pit.
    :ivar hasWumpus (bool): Whether the cell contains a wumpus, that is alive.
    :ivar hasDeadWumpus (bool): Whether the cell contains a wumpus, that is dead.
    :ivar hasStench (bool): Whether the cell contains a stench.
    :ivar hasBreeze (bool): Whether the cell contains a breeze.
    :ivar hasGold(bool): Whether the cell contains gold.
    """
    def __init__(self, x: int, y: int):
        self.x: int = x
        self.y: int = y

        self.hasPit: bool = False
        self.hasWumpus: bool = False
        self.hasDeadWumpus: bool = False

        self.hasStench: bool = False
        self.hasBreeze: bool = False

        self.hasGold: bool = False
