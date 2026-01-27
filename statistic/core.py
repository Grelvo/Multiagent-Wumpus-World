from util.config import *

from datetime import datetime


class Statistics:
    """Handles the statistics of the games played.

    :ivar _cycles (int): The amount of game cycles
    :ivar _game_steps (int): The total number of game_steps over all played game cycles
    :ivar _deaths (int): The total number of deaths over all played game cycles
    :ivar _cells_explored (int): The total amount of explored cells over all played game cycles
    :ivar _stuck_amount (int): The total rotations where the agents got stuck and had no more moves according to their strategy
    """
    def __init__(self):
        self._cycles: int = 0
        self._game_steps: int = 0
        self._deaths: int = 0
        self._cells_explored: int = 0
        self._stuck_amount: int = 0

    def get_cycles(self) -> int:
        """Returns the amount of cycles saved in Statistics"""
        return self._cycles
    
    def increase_stuck_amount(self) -> None:
        self._stuck_amount += 1

    def update(self, game_steps: int, deaths: int, cells_explored: int) -> None:
        self._cycles += 1
        self._game_steps += game_steps
        self._deaths += deaths
        self._cells_explored += cells_explored

    def create_file(self) -> None:
        if self._cycles == 0:
            return

        with open(f'../Intelligente-Softwareagenten/statistic/statistics/'
                  f'{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}-cycles-{self._cycles}', 'x') as f:
            f.write(f'Strategy: \n'
                    f'   Shoot: {SHOOT} \n'
                    f'   Risky: {RISKY} \n'
                    f'   Manhatten_Bonus: {MANHATTEN_BONUS} \n'
                    f'Total amounts: \n'
                    f'   amount of cycles: {self._cycles} \n'
                    f'   amount of stuck cycles: {self._stuck_amount} \n'
                    f'   number of game steps: {self._game_steps} \n'
                    f'   number of deaths: {self._deaths} \n'
                    f'   amount of explored cells: {self._cells_explored} \n'
                    f'Average amounts per cycle: \n'
                    f'   average number of game steps: {round(self._game_steps/self._cycles, 2)} \n'
                    f'   average number of deaths: {round(self._deaths/self._cycles, 2)} \n'
                    f'   average amount of explored cells: {round(self._cells_explored/self._cycles, 2)} \n'
                    )
