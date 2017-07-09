import random

from agents.base import Engine


class RandomEngine(Engine):
    def __init__(self, play_as):
        Engine.__init__(self, play_as)

    def choose(self, game_problem, board):
        moves = game_problem.actions(board)
        return random.choice(moves)

    def __str__(self):
        return 'Random'
