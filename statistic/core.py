import datetime


class Statistics:
    def __init__(self):
        self._cycles: int = 0
        self._steps: int = 0
        self._deaths: int = 0
        self._cells_explored: int = 0

    def update(self, steps: int, deaths: int, cells_explored: int) -> None:
        self._cycles += 1
        self._steps = steps
        self._deaths = deaths
        self._cells_explored = cells_explored
    
    def write_file(self) -> None:
        with open('../Softwareagenten/Intelligente-Softwareagenten/statistics/%s-cycles%d' % (datetime.now().strftime('%Y-%m-%d-%H-%M-%S'), self._cycles) , 'x') as f:
            f.write('Total amounts: \n')
            f.write('   amount of cycles: %d \n' % self._cycles)
            f.write('   number of steps: %d \n' % self._steps)
            f.write('   number of deaths: %d \n' % self._deaths)
            f.write('   amount of explored cells: %d \n' % self._cells_explored)
            f.write('Amounts per cycle: \n')
            f.write('   average number of steps: %f \n' % (self._steps/self._cycles))
            f.write('   average number of deaths: %f \n' % (self._deaths/self._cycles))
            f.write('   average amount of explored cells: %f \n' % (self._cells_explored/self._cycles))
            f.close()
