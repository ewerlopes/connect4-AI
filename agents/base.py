from abc import ABCMeta, abstractmethod


class Engine(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def choose(self, board):
        raise NotImplemented
