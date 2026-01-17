class Percept:
    """The information an agent can perceive in its cell.

    :ivar breeze (bool): Whether the cell contains a breeze.
    :ivar stench (bool): Whether the cell contains a stench.
    """
    def __init__(self, breeze: bool = False, stench: bool = False):
        self.breeze: bool = breeze
        self.stench: bool = stench
