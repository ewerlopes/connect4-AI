import numpy as np
from problem.utils import PLAYER2, PLAYER1
from evaluate import INF
from tables import evaldiff_lookup, evaldiff_threat_lookup
from problem.game_problem import Connect4


def evaldiff(board, m, play_as, weights=np.array([1, 3, 9, 27], dtype=int)):

    def get_free_row(move):
        r = board[move].argmin()
        if board[move][r] != 0:
            return None
        return r

    r = get_free_row(m)
    next_to_play = PLAYER1 if play_as != PLAYER1 else PLAYER2
    stm = next_to_play
    indices = np.dot(Connect4.segments_around(board, r, m),
                     weights)
    partial_scores = evaldiff_lookup[stm][indices]

    if (partial_scores == 4**2).any():
        return INF

    if evaldiff_threat_lookup[stm][indices].any():
        return INF - 1

    return partial_scores.sum()
