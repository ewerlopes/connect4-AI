from abc import ABCMeta, abstractmethod


class Engine(object):
    __metaclass__ = ABCMeta
    
    def __init__(self, play_as):
        self._play_as = play_as

    @abstractmethod
    def choose(self, game_problem, board):
        raise NotImplemented
    
    @property
    def playing_as(self):
        return self._play_as
    
    @playing_as.setter
    def playing_as(self, to_play_as):
        self._play_as = to_play_as
