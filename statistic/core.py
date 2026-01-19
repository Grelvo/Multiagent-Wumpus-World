from datetime import datetime


class Statistics:
    def __init__(self):
        self._cycles: int = 0
        self._steps: int = 0
        self._deaths: int = 0
        self._cells_explored: int = 0

    def update(self, steps: int, deaths: int, cells_explored: int) -> None:
        self._cycles += 1
        self._steps += steps
        self._deaths += deaths
        self._cells_explored += cells_explored
    
    def create_file(self) -> None:
        if self._cycles == 0:
            return

        with open(f'../Intelligente-Softwareagenten/statistic/statistics/'
                  f'{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}-cycles-{self._cycles}', 'x') as f:
            f.write(f'Total amounts: \n'
                    f'   amount of cycles: {self._cycles} \n'
                    f'   number of steps: {self._steps} \n'
                    f'   number of deaths: {self._deaths} \n'
                    f'   amount of explored cells: {self._cells_explored} \n'
                    f'Average amounts per cycle: \n'
                    f'   average number of steps: {round(self._steps/self._cycles, 2)} \n'
                    f'   average number of deaths: {round(self._deaths/self._cycles, 2)} \n'
                    f'   average amount of explored cells: {round(self._cells_explored/self._cycles, 2)} \n'
                    )
