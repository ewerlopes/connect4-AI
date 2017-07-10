from enum import Enum
#from view import utils
import pygame
import sys
import gui
import os

VERSION = '1.2'
FPS = 30
IMAGES_SIDE_SIZE = 80
COLS = 7
ROWS = 6
COLUMN_CHOOSING_MARGIN_TOP = 50
BOARD_MARGIN_TOP = IMAGES_SIDE_SIZE + COLUMN_CHOOSING_MARGIN_TOP
WINDOW_SIZE = (IMAGES_SIDE_SIZE * COLS, (IMAGES_SIDE_SIZE * ROWS) + BOARD_MARGIN_TOP)

# When frozen by PyInstaller, the path to the resources is different
RESOURCES_ROOT = os.path.join(sys._MEIPASS, 'resources') if getattr(sys, 'frozen', False) else 'view/resources'

CONFIG_FILE = 'connectfour.ini'

DEFAULT_CONFIG = {
    'sounds_volume': 0.1,
    'music_volume': 0.2
}


class GuiTheme(gui.DefaultTheme):
    def __init__(self, sounds_volume=0.5):
        gui.DefaultTheme.__init__(self)

        # self.hover_sound = utils.load_sound('hover.wav', volume=sounds_volume)
        self.click_sound = utils.load_sound('click.wav', volume=sounds_volume)


class COLORS(Enum):
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    YELLOW = (255, 174, 0),
    BLUE = (0, 42, 224)


class GAME_STATES(Enum):
    PLAYING = 2
    WON = 4
    NO_ONE_WIN = 6


class EVENTS(Enum):
    WINNER_CHIPS_EVENT = pygame.USEREVENT + 1
    GET_ONLINE_GAMES = pygame.USEREVENT + 2
    CLEAN_LAN_GAMES = pygame.USEREVENT + 3


class LOBBY_STATES(Enum):
    HOST_ONLINE_GAME = 2
    HOST_LAN_GAME = 4
    JOIN_ONLINE_GAME = 6
    JOIN_LAN_GAME = 8


class NETWORK_ENGINE_MODE(Enum):
    HOST = 2
    JOIN = 4


def set_logging_config(dev=False):

    import logging

    try:
        import colorlog
        have_colorlog = True
    except ImportError:
        have_colorlog = False

    # create logger
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    ch = logging.StreamHandler(sys.__stdout__)  # Add this
    ch.setLevel(logging.DEBUG)

    # create formatter
    # formatter = logging.Formatter('%(asctime)s [%(levelname)s] -- %(message)s')

    format = '%(asctime)s - %(levelname)-8s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    if have_colorlog and os.isatty(2):
        cformat = '%(log_color)s' + format
        formatter = colorlog.ColoredFormatter(cformat, date_format,
                                              log_colors={'DEBUG': 'reset', 'INFO': 'reset',
                                                          'WARNING': 'bold_yellow', 'ERROR': 'bold_red',
                                                          'CRITICAL': 'bold_red'})
    else:
        formatter = logging.Formatter(format, date_format)

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

    logging.basicConfig(
        format=format,
        datefmt=date_format,
        stream=sys.stdout,
    )

    logging.getLogger().setLevel(logging.DEBUG if dev else logging.WARNING)