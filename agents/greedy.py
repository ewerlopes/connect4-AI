import numpy as np

from game.evaldiff import evaldiff
from agents.base import Engine
from game.evaluate import Evaluator, INF


class GreedyEngine(Engine):
    def __init__(self, play_as):
        Engine.__init__(self, play_as)

    def choose(self, game_problem, board):
        moves = game_problem.actions(board)
        m = moves[0]
        moves = moves[1:]

        bestmove = m
        bestscore = -game_problem.evaluate(self.playing_as,
                                           game_problem.make_action(self.playing_as, m, board))

        for m in moves:
            score = -game_problem.evaluate(self.playing_as,
                                           game_problem.make_action(self.playing_as, m, board))
            if score > bestscore:
                bestmove = m
                bestscore = score

        print('Bestscore:', bestscore)
        return bestmove

    def __str__(self):
        return 'Greedy'


class WeightedGreedyEngine(Engine):
    """Same as GreedyEngine but move randomly using scores as weights

    """
    def __init__(self, play_as, verbose=True):
        Engine.__init__(self, play_as)
        self._evaluator = Evaluator()
        self._verbose = verbose
        self.evaluate = self._evaluator.evaluate

    def choose(self, game_problem, board):
        moves = game_problem.actions(board)

        # forced move?
        if len(moves) < 2:
            return moves[0]

        # winning move or threat blocking?
        scores = [evaldiff(board, m, self.playing_as) for m in moves]
        if max(scores) >= INF - 1:
            return max(zip(scores, moves))[1]

        weights = np.array(scores, dtype=float) + 1

        if weights.sum() == 0:
            weights = np.array([1 / len(moves)] * len(moves), dtype=float)
        else:
            weights /= weights.sum()

        selected_move = np.random.choice(moves, p=weights)

        if self._verbose:
            selected_score = scores[list(moves).index(selected_move)]
            print('Selected move %d with score %s' % (selected_move,
                                                      selected_score))

        return selected_move

    def __str__(self):
        return 'Weighted Greedy'
