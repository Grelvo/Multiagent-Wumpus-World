from game.core import Game

import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--statistics", action=argparse.BooleanOptionalAction)
    args = parser.parse_args()

    game = Game()
    game.start_game()
