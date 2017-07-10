import math
import random
from collections import defaultdict
from problem.game_problem import Connect4
from problem.utils import PLAYER1, PLAYER2, DRAW
from agents.base import Engine
from agents.greedy import WeightedGreedyEngine


class MonteCarloTreeSearch(Engine):
    def __init__(self, playing_as, simulations=1000, C=1/math.sqrt(2)):
        super(MonteCarloTreeSearch, self).__init__(playing_as)
        self.simulations = int(simulations)
        self.C = float(C)
        self.simulation_engine = WeightedGreedyEngine(False)
        self._stats = defaultdict(lambda: [0, 0])

    def choose(self, game_problem, board):
        stats, depth = self.search(game_problem, board, self.simulations, self.C)
        return self.select_best_move(stats, depth, game_problem, board)

    def search(self, game_problem, board, simulations, C):
        stats = self._stats
        root = board
        max_depth = 0

        for i in range(simulations):
            node = root
            states = []

            # select leaf node
            depth = 0
            while game_problem.is_terminal(node) is None:
                depth += 1
                move, select = self.select_next_move(stats, game_problem, node, C)
                node = game_problem.make_action(self.playing_as, move, node)
                states.append(Connect4.hashkey(node)[0])

                if not select:
                    break

            max_depth = max(depth, max_depth)

            # run.py simulation if not at the end of the game tree
            if game_problem.is_terminal(node) is None:
                result = self.simulate(game_problem, node)
            else:
                if game_problem.is_terminal(node) == 0:
                    result = 0.5
                else:
                    result = 0

            # propagate results
            for state in reversed(states):
                result = 1 - result
                stats[state][0] += 1
                stats[state][1] += result

        return stats, max_depth

    def get_next_to_move(self, whose_turn):
        return PLAYER1 if whose_turn != PLAYER1 else PLAYER2

    def simulate(self, game_problem, board):
        engine = self.simulation_engine
        node = board
        while game_problem.is_terminal(node) is None:
            m = engine.choose(game_problem, node)
            node = game_problem.make_action(self.playing_as, m, node)
        if game_problem.is_terminal(node) == DRAW:
            return 0.5
        elif game_problem.is_terminal(node) == self.get_next_to_move(self.playing_as):
            return 1
        else:
            return 0

    def select_next_move(self, stats, game_problem, board, C):
        """Select the next state and consider if it should be expanded"""

        bestscore = None
        bestmove = None

        children = [(m, stats[game_problem.hashkey(game_problem.make_action(self.playing_as, m, board))[0]])
                    for m in game_problem.actions(board)]
        total_n = sum(x[0] for (_, x) in children)

        for child_move, child_stat in children:
            n, w = child_stat
            if n == 0:
                return child_move, False
            else:
                score = (w / n) + C * math.sqrt(2 * math.log(total_n) / n)
                if bestscore is None or score > bestscore:
                    bestscore = score
                    bestmove = child_move

        assert bestmove is not None
        return bestmove, True

    def select_best_move(self, stats, depth, game_problem, board):
        """Select the best move at the end of the Monte Carlo tree search"""

        bestscore = 0
        bestmove = None
        total_n = 0
        moves = game_problem.actions(board)

        for m in moves:
            n, w = stats[Connect4.hashkey(game_problem.make_action(self.playing_as, m, board))[0]]
            total_n += n
            print('Move %d score: %d/%d (%0.1f%%)' % (m+1, w, n, w/n*100))
            if n > bestscore or (n == bestscore and random.random() <= 0.5):
                bestmove = m
                bestscore = n
        assert bestmove is not None

        print('Maximum depth: %d, Total simulations: %d' % (depth, total_n))

        return bestmove

    def __str__(self):
        return 'MCTS(%s, %0.2f)' % (self.simulations, self.C)
