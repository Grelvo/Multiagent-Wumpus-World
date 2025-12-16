from agents.baseAgent import BaseAgent


class ExplorerAgent(BaseAgent):
    def extended_decide_next_move(self, possible_moves: dict[tuple[int, int], int], board):
        for move in possible_moves:
            if move not in self.visited:
                possible_moves[move] += 10
        # später einfügen das falls keiner einen Bonus bekommen hat den moves einen Bonus geben die so nah wie möglich an neuen Feldern sind
