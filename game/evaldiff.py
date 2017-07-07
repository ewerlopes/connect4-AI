import numpy as np

from evaluate import INF
from tables import evaldiff_lookup, evaldiff_threat_lookup
from problem.game_problem import Connect4


def evaldiff(board, m, weights=np.array([1, 3, 9, 27], dtype=int)):
    r = board.get_free_row(m)
    stm = board.get_next_to_move
    indices = np.dot(Connect4.segments_around(board, r, m),
                     weights)
    partial_scores = evaldiff_lookup[stm][indices]

    if (partial_scores == 4**2).any():
        return INF

    if evaldiff_threat_lookup[stm][indices].any():
        return INF - 1

    return partial_scores.sum()
