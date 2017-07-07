from control.eventmanager import *
from model.model import *
from problem.game_problem import Connect4
import numpy as np

# GAME CONSTANTS
PLAYER1 = 1
PLAYER2 = 2
DRAW = 0
COMPUTE = -1


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
        self.board = np.zeros(self.game_problem.get_board_dim(), dtype=int) 
        
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
    def whose_turn(self):
        return self._whose_turn

    @property
    def advance_turn(self):
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
            is_terminal = self.game_problem.terminal_test(self.board)
            if not is_terminal:
                player = players[self.whose_turn]
                move = player.choose(self.board, self.game_problem)
                self.board = self.game_problem.move(move)
                newTick = TickEvent()
                self.evManager.Post(newTick)
            else:
                if self.isDrew(is_terminal):    # post draw event.
                    newTick = DrawEvent()
                    self.evManager.Post(newTick)
                else:   # send event saying who has won
                    newTick = WinEvent(self.whose_turn)
                    self.evManager.Post(newTick)
