import time
from collections import defaultdict

from problem.utils import DRAW
from game.evaluate import INF
from agents.greedy import GreedyEngine


class NegamaxEngine(GreedyEngine):
    FORMAT_STAT = (
        'score: {score} [time: {time:0.3f}s, pv: {pv}]\n' +
        'nps: {nps}, nodes: {nodes}, leaves: {leaves}, draws: {draws}, mates: {mates}'
        )

    def __init__(self, play_as, maxdepth=4):
        super(NegamaxEngine, self).__init__(play_as)
        self._maxdepth = int(maxdepth)

    def choose(self, game_problem, board):
        self.initcnt()
        pv, score = self.search(game_problem, board, self._maxdepth)

        self.showstats(pv, score)
        
        return pv[0]

    def initcnt(self):
        self._startt = time.time()
        self._counters = cnt = defaultdict(int)
        cnt['nodes'] = 0
        cnt['leaves'] = 0
        cnt['draws'] = 0
        cnt['mates'] = 0

    def inc(self, cnt):
        self._counters[cnt] += 1

    def showstats(self, pv, score):
        t = time.time() - self._startt
        if t:
            nps = self._counters['nodes'] / t
        else:
            nps = 0

        pv = ', '.join(str(x+1) for x in pv)

        ctx = self._counters.copy()
        ctx['pv'] = pv
        ctx['nps'] = nps
        ctx['score'] = score
        ctx['time'] = t
        
        print(self.FORMAT_STAT.format(**ctx))
    
    def search(self, game_problem, board, depth, ply=1):
        self.inc('nodes')

        if game_problem.is_terminal(board) is not None:
            return self.endscore(game_problem, board, ply)

        if depth <= 0:
            self.inc('leaves')
            return [], game_problem.evaluate(self.playing_as, board)

        bestmove = []
        bestscore = -INF
        for m in game_problem.actions(board):
            nextmoves, score = self.search(game_problem,
                                           game_problem.make_action(self.playing_as, m, board),
                                           depth - 1, ply + 1)
            score = -score
            if not bestmove or score >= bestscore:
                bestscore = score
                bestmove = [m] + nextmoves

        return bestmove, bestscore

    def endscore(self, game_problem, board, ply):
        self.inc('leaves')
        if game_problem.is_terminal(board) == DRAW:
            self.inc('draws')
            return [], 0
        else:
            self.inc('mates')
            return [], -(INF - ply)

    def __str__(self):
        return 'Negamax(%s)' % self._maxdepth
