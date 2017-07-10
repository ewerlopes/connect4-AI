from agents.base import Engine
from view import settings
from view.view import PLAYER_CHIPS
import pygame


class HumanEngine(Engine):
    def __init__(self, play_as, view, name):
        Engine.__init__(self, play_as)
        self.view = view
        self.name = name

    def choose(self, game_problem, board):
        """Ask the user to choose the move"""

        # self.column_change_sound.play()
        mousex, mousey = pygame.mouse.get_pos()
        col_clicked = (mousex / settings.IMAGES_SIDE_SIZE) % settings.COLS
        if (col_clicked >= 0) and (col_clicked < settings.COLS):
            player_chip = PLAYER_CHIPS[self.playing_as]()
            player_chip.rect.left = 0
            player_chip.rect.top = settings.COLUMN_CHOOSING_MARGIN_TOP
            player_chip.rect.right = settings.IMAGES_SIDE_SIZE * (col_clicked + 1)
            self.view.draw_human_chip(player_chip)

        for event in pygame.event.get(pygame.MOUSEBUTTONDOWN):
            # pygame.mouse.get_pressed() returns a tupple
            # (leftclick, middleclick, rightclick) Each one
            # is a boolean integer representing button up/down.
            if pygame.mouse.get_pressed()[0]:
                return col_clicked

        return None

    def __str__(self):
        return self.name