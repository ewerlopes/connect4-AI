from control.eventmanager import *
from model.model import *
from problem.game_problem import Connect4
import numpy as np
from problem.utils import PLAYER2, PLAYER1, DRAW


class GameEngine(object):
    """
    Tracks the game state.
    """

    def __init__(self, evManager):
        """
        evManager (EventManager): Allows posting messages to the event queue.

        Attributes:
        running (bool): True while the engine is online. Changed via QuitEvent().
        """
        self.evManager = evManager
        evManager.RegisterListener(self)
        self.running = False
        self.state = StateMachine()
        self.game_problem = Connect4()
        self._whose_turn = PLAYER1
        # board represented as a matrix
        self._board = np.zeros(self.game_problem.get_board_dim, dtype=int)
        self.scores = { 
            PLAYER1: 0,
            PLAYER2: 0
        }
        
    def notify(self, event):
        """
        Called by an event in the message queue. 
        """

        if isinstance(event, QuitEvent):
            self.running = False
        if isinstance(event, StateChangeEvent):
            # pop request
            if not event.state:
                # false if no more states are left
                if not self.state.pop():
                    self.evManager.Post(QuitEvent())
            else:
                # push a new state on the stack
                self.state.push(event.state)

    @property
    def get_board(self):
        return self._board
    
    @property
    def whose_turn(self):
        """
        Says who is playing the current turn
        :return: A constant defining who plays.
        """
        return self._whose_turn

    @staticmethod
    def get_free_row(board, col):
        """
        Return a free row index
        :param board: a matrix representing the board
        :param col: the column for which to get the row
        :return: row index
        """
        row = board[col].argmin()
        if board[col][row] != 0:
            return None
        return row
    
    @property
    def advance_turn(self):
        """
        Returns who plays next.
        :return: A constant defining who plays next.
        """
        return PLAYER1 if self._whose_turn != PLAYER1 else PLAYER2

    def run(self, p1_engine, p2_engine):
        """
        Starts the game engine loop.

        This pumps a Tick event into the message queue for each loop.
        The loop ends when this object hears a QuitEvent in notify(). 
        """
        self.running = True
        self.evManager.Post(InitializeEvent())
        self.state.push(STATE_MENU)
        players = {
            PLAYER1: p1_engine,
            PLAYER2:  p2_engine
            }
        
        while self.running:
            is_terminal = self.game_problem.is_terminal(self._board)
            if not is_terminal:
                player = players[self.whose_turn]
                move = player.choose(self.game_problem, self._board)
                self._board = self.game_problem.make_action(player.playing_as, move, self._board)
                new_tick = TickEvent()
                self.evManager.Post(new_tick)
            elif is_terminal == DRAW:
                # post draw event.
                new_tick = DrawEvent()
                self.evManager.Post(new_tick)
            else:
                # send event saying who has won
                new_tick = WinEvent(is_terminal)
                self.evManager.Post(new_tick)
