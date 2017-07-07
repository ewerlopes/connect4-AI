from problem.utils import WrongMoveError
from agents.base import Engine


class HumanEngine(Engine):
    def __init__(self, name):
        self.name = name

    def choose(self, board):
        """Ask the user to choose the move"""

        print(board)
        while True:
            try:
                move = int(input('Your move: ')) - 1
                board.actions(move)
            except ValueError:
                print('Wrong move! Must be an integer between 1-8.')
            except WrongMoveError as e:
                print(e.message)
            else:
                break
        return move

    def __str__(self):
        return self.name
