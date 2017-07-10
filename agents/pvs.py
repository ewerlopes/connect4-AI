from game.evaluate import INF
from agents.alphabeta import AlphaBetaEngine
from agents.cached import CachedEngineMixin
from agents.deepening import IterativeDeepeningEngineMixin


class PVSEngine(AlphaBetaEngine):
    def search(self, game_problem, board, depth, ply=1, alpha=-INF, beta=INF, hint=None):
        self.inc('nodes')

        if game_problem.is_terminal(board) is not None:
            return self.endscore(game_problem, board, ply)

        if depth <= 0:
            self.inc('leaves')
            return [], game_problem.evaluate(self.playing_as, board)

        bestmove = []
        bestscore = alpha
        for i, m in enumerate(self.moveorder(board, game_problem.actions(board), hint)):
            if i == 0 or depth == 1 or (beta-alpha) == 1:
                nextmoves, score = self.search(game_problem,
                                               game_problem.make_action(self.playing_as, m, board),
                                               depth - 1, ply + 1,
                                               -beta, -bestscore)
            else:
                # pvs uses a zero window for all the other searches
                _, score = self.search(game_problem,
                                       game_problem.make_action(self.playing_as, m, board),
                                       depth - 1, ply + 1,
                                       -bestscore - 1, -bestscore)
                score = -score
                if score > bestscore:
                    nextmoves, score = self.search(game_problem,
                                                   game_problem.make_action(self.playing_as, m, board),
                                                   depth - 1, ply + 1,
                                                   -beta, -bestscore)
                else:
                    continue

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
        return 'PVS(%s)' % self._maxdepth


class PVSCachedEngine(CachedEngineMixin, PVSEngine):
    FORMAT_STAT = (
        'score: {score} [time: {time:0.3f}s, pv: {pv}]\n' +
        'nps: {nps}, nodes: {nodes}, betacuts: {betacuts}\n' +
        'hits: {hits}, leaves: {leaves}, draws: {draws}, mates: {mates}'
        )

    def initcnt(self):
        super(PVSCachedEngine, self).initcnt()
        self._counters['hits'] = 0

    def __str__(self):
        return 'PVSCache(%s)' % self._maxdepth


class PVSDeepEngine(CachedEngineMixin, IterativeDeepeningEngineMixin, PVSEngine):
    FORMAT_STAT = (
        '[depth: {depth}] score: {score} [time: {time:0.3f}s, pv: {pv}]\n' +
        'nps: {nps}, nodes: {nodes}, betacuts: {betacuts}\n' +
        'hits: {hits}, leaves: {leaves}, draws: {draws}, mates: {mates}'
        )

    def initcnt(self):
        super(PVSDeepEngine, self).initcnt()
        self._counters['hits'] = 0

    def __str__(self):
        return 'PVSDeep(%s)' % self._maxdepth
