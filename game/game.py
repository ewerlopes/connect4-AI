from control.eventmanager import *
from model.model import *
from problem.game_problem import Connect4
from problem.utils import PLAYER2, PLAYER1, DRAW
import logging
import numpy as np


class GameEngine(object):
    """
    Tracks the game state.
    """

    def __init__(self, evManager):
        """
        evManager (EventManager): Allows posting messages to the event queue.

        Attributes:
        running (bool): True while the engine is online. Changed via QuitEvent().
        _whose_turn (int): Keeps whose turn it is. Using constant values PLAYER1, PLAYER2.
        _board (int matrix): game board.
        has_ended (bool): a flag to mark whether the current match has ended
        """
        self.evManager = evManager
        evManager.RegisterListener(self)

        self._whose_turn = None
        self._board = None
        self.has_ended = None

        self.running = False
        self.state = StateMachine()
        self.game_problem = Connect4()

        self.scores = { 
            PLAYER1: 0,
            PLAYER2: 0
        }

        self.new_game()
        
    def notify(self, event):
        """
        Called by an event in the message queue. 
        """

        if isinstance(event, QuitEvent):
            self.running = False
        elif isinstance(event, Restart):
            self.new_game()
        elif isinstance(event, StateChangeEvent):
            # pop request
            if not event.state:
                # false if no more states are left
                if not self.state.pop():
                    self.evManager.Post(QuitEvent())
            else:
                # push a new state on the stack
                self.state.push(event.state)

    def new_game(self):
        self._whose_turn = PLAYER1
        # board represented as a matrix
        self._board = np.zeros(self.game_problem.get_board_dim, dtype=int)
        self.has_ended = False

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
    
    def advance_turn(self):
        """
        Advances turn
        """
        self._whose_turn = PLAYER1 if self._whose_turn != PLAYER1 else PLAYER2

    def run(self, p1_engine, p2_engine):
        """
        Starts the game engine loop.

        This pumps a Tick event into the message queue for each loop.
        The loop ends when this object hears a QuitEvent in notify(). 
        """
        self.running = True
        self.evManager.Post(InitializeEvent())
        self.state.push(STATE_PLAY)
        players = {
            PLAYER1: p1_engine,
            PLAYER2:  p2_engine
            }
        
        while self.running:
            if not self.has_ended:
                player = players[self.whose_turn]
                move = player.choose(self.game_problem, self._board)

                if move is None:
                    new_tick = TickEvent()
                    self.evManager.Post(new_tick)
                    continue

                self._board = self.game_problem.make_action(self.whose_turn, move, self._board)
                is_terminal = self.game_problem.is_terminal(self._board)

                if is_terminal == DRAW:
                    # post draw event.
                    new_tick = DrawEvent()
                    self.evManager.Post(new_tick)
                    self.has_ended = True
                elif (is_terminal == PLAYER1) or (is_terminal == PLAYER2):
                    # send event saying who has won
                    new_tick = WinEvent(is_terminal)
                    self.evManager.Post(new_tick)
                    self.scores[self.whose_turn] += 1
                    self.has_ended = True
                else:
                    self.advance_turn()

            new_tick = TickEvent()
            self.evManager.Post(new_tick)