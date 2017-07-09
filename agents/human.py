from problem.utils import WrongMoveError
from agents.base import Engine
from view import settings
import pygame


class HumanEngine(Engine):
    def __init__(self, play_as, name):
        Engine.__init__(self, play_as)
        self.name = name

    def choose(self, game_problem, board):
        """Ask the user to choose the move"""

        # self.column_change_sound.play()
        mousex, mousey = pygame.mouse.get_pos()
        col_clicked = (mousex / settings.IMAGES_SIDE_SIZE) % settings.COLS
        if (col_clicked >= 0) and (col_clicked < settings.COLS):
            self.current_player_chip_column = col_clicked
            self.current_player_chip.rect.right = settings.IMAGES_SIDE_SIZE * \
                                                  (self.current_player_chip_column + 1)

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                # pygame.mouse.get_pressed() returns a tupple
                # (leftclick, middleclick, rightclick) Each one
                # is a boolean integer representing button up/down.
                if pygame.mouse.get_pressed()[0]:
                    self._move_chip_down()

        return move

    def __str__(self):
        return self.name
