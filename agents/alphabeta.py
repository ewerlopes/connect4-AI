from game.evaluate import INF
from agents.negamax import NegamaxEngine
from game.moveorder import MoveOrder
from agents.cached import CachedEngineMixin
from agents.deepening import IterativeDeepeningEngineMixin


class AlphaBetaEngine(NegamaxEngine):
    FORMAT_STAT = (
        'score: {score} [time: {time:0.3f}s, pv: {pv}]\n' +
        'nps: {nps}, nodes: {nodes}, betacuts: {betacuts}\n' +
        'leaves: {leaves}, draws: {draws}, mates: {mates}'
        )

    def __init__(self, maxdepth=4, ordering='seq'):
        super(AlphaBetaEngine, self).__init__(maxdepth)
        self.moveorder = MoveOrder(ordering).order

    def initcnt(self):
        super(AlphaBetaEngine, self).initcnt()
        self._counters['betacuts'] = 0

    def search(self, game_problem, board, depth, ply=1, alpha=-INF, beta=INF, hint=None):
        self.inc('nodes')

        if game_problem.is_terminal(board) is not None:
            return self.endscore(game_problem, board, ply)

        if depth <= 0:
            self.inc('leaves')
            return [], game_problem.evaluate(self.playing_as, board)

        bestmove = []
        bestscore = alpha
        for m in self.moveorder(board, game_problem.actions(board), hint):
            nextmoves, score = self.search(game_problem,
                                           game_problem.make_action(self.playing_as,
                                                                     m, board),
                                           depth - 1, ply + 1,
                                           -beta, -bestscore)
            score = -score
            if score > bestscore:
                bestscore = score
                bestmove = [m] + nextmoves
            elif not bestmove:
                bestmove = [m] + nextmoves

            if bestscore >= beta:
                self.inc('betacuts')
                break

        return bestmove, bestscore

    def __str__(self):
        return 'AlphaBeta(%s)' % self._maxdepth


class ABCachedEngine(CachedEngineMixin, AlphaBetaEngine):
    FORMAT_STAT = (
        'score: {score} [time: {time:0.3f}s, pv: {pv}]\n' +
        'nps: {nps}, nodes: {nodes}, betacuts: {betacuts}\n' +
        'hits: {hits}, leaves: {leaves}, draws: {draws}, mates: {mates}'
        )

    def initcnt(self):
        super(ABCachedEngine, self).initcnt()
        self._counters['hits'] = 0

    def __str__(self):
        return 'ABCache(%s)' % self._maxdepth


class ABDeepEngine(CachedEngineMixin, IterativeDeepeningEngineMixin,
                   AlphaBetaEngine):
    FORMAT_STAT = (
        '[depth: {depth}] score: {score} [time: {time:0.3f}s, pv: {pv}]\n' +
        'nps: {nps}, nodes: {nodes}, betacuts: {betacuts}\n' +
        'hits: {hits}, leaves: {leaves}, draws: {draws}, mates: {mates}'
        )

    def initcnt(self):
        super(ABDeepEngine, self).initcnt()
        self._counters['hits'] = 0

    def __str__(self):
        return 'ABDeep(%s)' % self._maxdepth
