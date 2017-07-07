from abc import ABCMeta, abstractmethod
import utils
import numpy as np

##########################
#  SEARCH PROBLEM: GAME  #
##########################


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
    def legal_moves(self, state):
        """Return a list of the allowable moves at this point."""
        pass

    @abstractmethod
    def make_move(self, move, state):
        """Return the state that results from making a move from a state."""
        pass

    @abstractmethod
    def utility(self, state, player):
        """Return the value of this final state to player."""
        pass

    def terminal_test(self, state):
        """Return True if this is a final state for the game."""
        return not self.legal_moves(state)

    @staticmethod
    def to_move(state):
        """Return the player whose move it is in this state."""
        return state.to_move

    def display(self, state):
        """Print or otherwise display the state."""
        print state

    def successors(self, state):
        """Return a list of legal (move, state) pairs."""
        return [(move, self.make_move(move, state))
                for move in self.legal_moves(state)]

    def __repr__(self):
        return '<%s>' % self.__class__.__name__


class Connect4(object):
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
    ### CONSTANTS ###
    PLAYER1_ID = 1
    PLAYER2_ID = 2
    DRAW_ID = 0
    COMPUTE_END_RESULT = -1

    def __init__(self, board=None, stm=PLAYER1_ID, end_result=COMPUTE_END_RESULT, cols=7, rows=6):
        if board is None:
            # board represented as a matrix
            board = np.zeros((cols, rows), dtype=int)
        self._board = board
        self._next_to_move = stm
        self._rows = rows
        self._cols = cols
        
        # Check if the game is ended.
        if end_result == Connect4.COMPUTE_END_RESULT:
            self._end_result = self._check_end(board)
        else:
            self._end_result = end_result

    @property
    def get_board_dim(self):
        return self._cols, self._rows

    @property
    def end(self):
        return self._end_result

    @property
    def whose_turn_is_it(self):
        return self._next_to_move

    @property
    def other(self):
        return Connect4.PLAYER1_ID if self._next_to_move != Connect4.PLAYER1_ID else Connect4.PLAYER2_ID

    @classmethod
    def _check_end(cls, pos):
        for seg in cls.segments(pos):
            c = np.bincount(seg)
            if c[0]:
                continue
            if c[Connect4.PLAYER1_ID] == 4:
                return Connect4.PLAYER1_ID
            elif c[Connect4.PLAYER2_ID] == 4:
                return Connect4.PLAYER2_ID

        if pos.all():
            return Connect4.DRAW_ID
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
            if c[Connect4.PLAYER1_ID] == 4 or c[Connect4.PLAYER2_ID] == 4:
                return process(utils.all_segments[i])
                            

    @classmethod
    def _check_end_around(cls, pos, r, c, side):
        if (cls.segments_around(pos, r, c) == side).all(1).any():
            return side

        if pos.all():
            return Connect4.DRAW_ID
        else:
            return None

    @classmethod
    def segments(cls, pos):
        if isinstance(pos, Connect4):
            return cls.segments(pos._board)
        else:
            pos = pos.flatten()
            return pos[utils.all_segments]

    @classmethod
    def rev_segments(cls, pos):
        if isinstance(pos, Connect4):
            return cls.rev_segments(pos._board)
        else:
            pos = pos.flatten()
            return pos[utils.rev_segments]

    @classmethod
    def segments_around(cls, pos, r, c):
        if isinstance(pos, Connect4):
            return cls.segments_around(pos._board, r, c)
        else:
            idx = c * pos.shape[1] + r
            pos = pos.flatten()
            return pos[utils.rev_segments[idx]]
        
    def get_board(self):
        return [list(l) for l in reversed(self._board.transpose())]

    def __str__(self):
        disc = {
            0: ' ',
            1: 'R',
            2: 'Y'
        }

        s = []
        for row in reversed(self._board.transpose()):
            s.append(' | '.join(disc[x] for x in row))
        s.append(' | '.join('-' * 7))
        s.append(' | '.join(map(str, range(1, 8))))
        s = ['| ' + x + ' |' for x in s]
        s = [i + ' ' + x for i, x in zip('ABCDEFG  ', s)]
        s = '\n'.join(s)

        if self._end_result is Connect4.DRAW_ID:
            s += '\n<<< Game over: draw' % [self._end_result]
        elif self._end_result is not None:
            s += '\n<<< Game over: %s win' % disc[self._end_result]
        else:
            s += '\n<<< Move to %s' % disc[self._next_to_move]
        return s

    def move(self, m):
        if not (0 <= m < 7):
            raise ValueError(m)

        pos = self._board.copy()

        r = pos[m].argmin()
        if pos[m][r] != 0:
            raise utils.WrongMoveError('Full Column')
        pos[m][r] = self._next_to_move
        end = self._check_end_around(pos, r, m, self._next_to_move)
        stm = self.other
        return Connect4(pos, stm, end)

    def freerow(self, m):
        r = self._board[m].argmin()
        if self._board[m][r] != 0:
            return None
        return r

    def moves(self):
        return np.flatnonzero(self._board[:, -1] == 0)

    def hashkey(self):
        """Generates an hashkey

        Returns a tuple (key, flip)
        flip is True if it returned the key of the symmetric Board.

        """
        k1 = 0
        k2 = 0

        for x in self._board.flat:
            k1 *= 3
            k1 += int(x)
            assert k1 >= 0

        for x in self._board[::-1].flat:
            k2 *= 3
            k2 += int(x)
            assert k2 >= 0

        if k2 < k1:
            return k2, True
        else:
            return k1, False
