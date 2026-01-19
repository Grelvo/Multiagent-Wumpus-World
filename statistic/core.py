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

        with open(f'../Intelligente-Softwareagenten/statistic/statistics/{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}-cycles-{self._cycles}', 'x') as f:
            f.write('Total amounts: \n')
            f.write('   amount of cycles: %d \n' % self._cycles)
            f.write('   number of steps: %d \n' % self._steps)
            f.write('   number of deaths: %d \n' % self._deaths)
            f.write('   amount of explored cells: %d \n' % self._cells_explored)
            f.write('Average amounts per cycle: \n')
            f.write('   average number of steps: %f \n' % round(self._steps/self._cycles, 2))
            f.write('   average number of deaths: %f \n' % round(self._deaths/self._cycles, 2))
            f.write('   average amount of explored cells: %f \n' % round(self._cells_explored/self._cycles, 2))
            f.close()
