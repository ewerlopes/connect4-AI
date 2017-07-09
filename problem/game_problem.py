from abc import ABCMeta, abstractmethod
import numpy as np
from problem import utils
from utils import PLAYER1, PLAYER2, DRAW, INF

class Game:
    """
    A game is similar to a such problem, but it has a utility for each
    state and a terminal test instead of a path cost and a goal
    test. To create a game, subclass this class and implement
    legal_moves, make_move, utility, and terminal_test. You may
    override display and successors or you can inherit their default
    methods. You will also need to set the .initial attribute to the
    initial state; this can be done in the constructor.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def actions(self, state):
        """Return a list of the allowable moves at this point."""
        raise NotImplementedError

    @abstractmethod
    def make_action(self, player, action, board):
        """Return the state that results from making a move from a state."""
        raise NotImplementedError

    def is_terminal(self, state):
        """Return True if this is a final state for the game."""
        raise NotImplementedError

    def successors(self, state):
        """Return a list of legal (move, state) pairs."""
        raise NotImplementedError

    def __repr__(self):
        return '<%s>' % self.__class__.__name__


class Connect4(Game):
    """A TicTacToe-like game in which you can only make a move on the bottom
    row, or in a square directly above an occupied square.  Traditionally
    played on a 6x7 board and requiring 4 in a row.
    Play ConnectFour with an h x w board.
    A state has the player to move (who owns the turn), a cached utility,
    a list of moves in the form of a list of (x, y) positions, and a board,
    in the form of a dict of {(x, y): Player} entries, where Player is 'R'
    or 'Y', standing for 'Red' and 'Yellow' chips, respectively.
        The coordinates look as follows:
            0         x
            |------------->
            |
            |
            |
         y  v
    """

    def __init__(self, cols=7, rows=6):
        self._rows = rows
        self._cols = cols

    @property
    def get_board_dim(self):
        return self._cols, self._rows

    @classmethod
    def is_terminal(cls, board):
        """
        Return whether the current configuration of board is a terminal state
        :param board: game board state
        :return: None, in case it is not a terminal state. DRAW in case it was
                a draw, PLAYER1, PLAYER2 in case there was a win.
        """
        # Checks whether a player has won
        for seg in Connect4.segments(board):
            c = np.bincount(seg)
            if c[0]:
                continue
            if c[PLAYER1] == 4:
                return PLAYER1
            elif c[PLAYER2] == 4:
                return PLAYER2
        # Checks whether there was a tie.
        if board.all():
            return DRAW
        else:
            return None
        
    @classmethod
    def get_win_segment(cls, pos):
        
        def process(seg):
            w_seg = {}
            _indexes = np.arange(7 * 6).reshape((7, 6))
            _indexes = np.rot90(_indexes)
            for i in seg:
                for row in range(0,6):
                    for col in range(0,7):
                        if _indexes[row][col] == i:
                            w_seg[(row, col)] = True
            return w_seg

        for i,seg in enumerate(cls.segments(pos)):
            c = np.bincount(seg)
            if c[0]:
                continue
            if c[PLAYER1] == 4 or c[PLAYER2] == 4:
                return process(utils.all_segments[i])
                            

    @classmethod
    def _check_end_around(cls, pos, r, c, side):
        """Check whether the game has end by side or whether there was a tie"""
        if (cls.segments_around(pos, r, c) == side).all(1).any():
            return side

        if pos.all():
            return DRAW
        else:
            return None

    @classmethod
    def segments(cls, board):
        board = board.flatten()
        return board[utils.all_segments]

    @classmethod
    def rev_segments(cls, board):
        board = board.flatten()
        return board[utils.rev_segments]

    @classmethod
    def segments_around(cls, board, r, c):
        idx = c * board.shape[1] + r
        board = board.flatten()
        return board[utils.rev_segments[idx]]

    def make_action(self, player, action, board):
        """
        Make move to the board.
        :param player: The player to make the move. See Constant in game.py
        :param action: the column to place a chip
        :param board: the board game
        :return: a new board game with the action signed.
        """
        if not (0 <= action < self._cols):
            raise ValueError(action)

        if action is None:
            return
        
        pos = board.copy()

        free_row = pos[action].argmin()
        if pos[action][free_row] != 0:
            raise utils.WrongMoveError('Full/Occupied Column')
        pos[action][free_row] = player
        return pos
    
    def actions(self, board):   
        return np.flatnonzero(board[:, -1] == 0)
    
    @classmethod
    def evaluate(cls, player_id, board, weights=np.asarray([0, 0, 1, 4, 0])):
        scores = {PLAYER1: np.zeros(5, dtype=int),
                  PLAYER2: np.zeros(5, dtype=int)}

        if Connect4.is_terminal(board) is not None:
            if Connect4.is_terminal(board) == DRAW:
                return 0
            elif Connect4.is_terminal(board) == player_id:
                return INF
            else:
                return -INF

        segments = Connect4.segments(board)
        filtered_segments = segments[segments.any(1)]

        for s in filtered_segments:
            c = np.bincount(s, minlength=3)

            c1 = c[PLAYER1]
            c2 = c[PLAYER2]

            if c2 == 0:
                scores[PLAYER1][c1] += 1
            elif c1 == 0:
                scores[PLAYER2][c2] += 1

        s1 = (weights * scores[PLAYER1]).sum()
        s2 = (weights * scores[PLAYER2]).sum()

        score = s1 - s2
        if player_id == PLAYER1:
            return score
        else:
            return -score

    @classmethod
    def hashkey(cls, board):
        """Generates an hashkey

        Returns a tuple (key, flip)
        flip is True if it returned the key of the symmetric Board.

        """
        k1 = 0
        k2 = 0

        for x in board.flat:
            k1 *= 3
            k1 += int(x)
            assert k1 >= 0

        for x in board[::-1].flat:
            k2 *= 3
            k2 += int(x)
            assert k2 >= 0

        if k2 < k1:
            return k2, True
        else:
            return k1, False
