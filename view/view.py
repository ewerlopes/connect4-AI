from control.eventmanager import *
from configparser import ConfigParser
from problem.utils import PLAYER2, PLAYER1
import utils
import model
import logging
import sys
import pygame
import settings
import os


class GraphicalView(object):
    """
    Draws the model state onto the screen.
    """

    def __init__(self, evManager, model):
        """
        evManager (EventManager): Allows posting messages to the event queue.
        model (GameEngine): a strong reference to the game Model.
                
        Attributes:
        isinitialized (bool): pygame is ready to draw.
        screen (pygame.Surface): the screen surface.
        clock (pygame.time.Clock): keeps the fps constant.
        smallfont (pygame.Font): a small font.
        """
        
        self.evManager = evManager
        evManager.RegisterListener(self)
        self.model = model
        self.isinitialized = False
        self.screen = None
        self.clock = None
        self.smallfont = None
    
    def notify(self, event):
        """
        Receive events posted to the message queue. 
        """

        if isinstance(event, InitializeEvent):
            self.initialize()
        elif isinstance(event, QuitEvent):
            # shut down the pygame graphics
            self.isinitialized = False
            pygame.quit()
        elif isinstance(event, TickEvent):
            if not self.isinitialized:
                return
            currentstate = self.model.state.peek()
            if currentstate == model.STATE_MENU:
                self.rendermenu()
            if currentstate == model.STATE_PLAY:
                self.renderplay()
            if currentstate == model.STATE_HELP:
                self.renderhelp()
            # limit the redraw speed to 30 frames per second
            self.clock.tick(30)
    
    def rendermenu(self):
        """
        Render the game menu.
        """

        self.screen.fill((0, 0, 0))
        somewords = self.smallfont.render(
                    'You are in the Menu. Space to play. Esc exits.', 
                    True, (0, 255, 0))
        self.screen.blit(somewords, (0, 0))
        pygame.display.flip()
        
    def renderplay(self):
        """
        Render the game play.
        """

        self.screen.fill((0, 0, 0))
        somewords = self.smallfont.render(
                    'You are Playing the game. F1 for help.', 
                    True, (0, 255, 0))
        self.screen.blit(somewords, (0, 0))
        pygame.display.flip()
        
    def renderhelp(self):
        """
        Render the help screen.
        """

        self.screen.fill((0, 0, 0))
        somewords = self.smallfont.render(
                    'Help is here. space, escape or return.', 
                    True, (0, 255, 0))
        self.screen.blit(somewords, (0, 0))
        pygame.display.flip()
        
    def initialize(self):
        """
        Set up the pygame graphical display and loads graphical resources.
        """

        result = pygame.init()
        pygame.font.init()
        pygame.display.set_caption('demo game')
        self.screen = pygame.display.set_mode((600, 60))
        self.clock = pygame.time.Clock()
        self.smallfont = pygame.font.Font(None, 40)
        self.isinitialized = True


class ConsoleView(object):
    """
    Draws the model state onto the terminal screen.
    """

    def __init__(self, evManager, model):
        """
        evManager (EventManager): Allows posting messages to the event queue.
        model (GameEngine): a strong reference to the game Model.

        Attributes:
        isinitialized (bool): pygame is ready to draw.
        screen (pygame.Surface): the screen surface.
        clock (pygame.time.Clock): keeps the fps constant.
        smallfont (pygame.Font): a small font.
        """

        self.evManager = evManager
        evManager.RegisterListener(self)
        self.model = model
        self.isinitialized = False

    def notify(self, event):
        """
        Receive events posted to the message queue. 
        """

        if isinstance(event, InitializeEvent):
            self.initialize()
        elif isinstance(event, QuitEvent):
            # shut down the pygame graphics
            self.isinitialized = False
            pygame.quit()
        elif isinstance(event, DrawEvent):
            self.renderboard()
            self.renderdraw()
        elif isinstance(event, WinEvent):
            self.renderboard()
            self.renderwin(event.winner)
        elif isinstance(event, TickEvent):
            if not self.isinitialized:
                return
            currentstate = self.model.state.peek()
            if currentstate == model.STATE_PLAY:
                self.renderboard()
                
    def initialize(self):
        """
        Set up the graphical resources.
        """
        self.isinitialized = True
        self.renderboard()
        self.renderturn()
        
    def renderdraw(self):
        print '\n<<< Game over: DRAW!'
        print
        
    def renderwin(self, player):
        print '\n<<< Game over: {} win'.format(player)
        print 
    
    def renderturn(self):
        print '\n<<< New turn!'
        print 
        
    def renderboard(self):
        """
        Render the game board.
        """
        
        disc = {
            0: ' ',
            1: 'R',
            2: 'Y'
        }

        s = []
        for row in reversed(self.model.board.transpose()):
            s.append(' | '.join(disc[x] for x in row))
        s.append(' | '.join('-' * 7))
        s.append(' | '.join(map(str, range(1, 8))))
        s = ['| ' + x + ' |' for x in s]
        s = [i + ' ' + x for i, x in zip('ABCDEFG  ', s)]
        s = '\n'.join(s)
        
        print s
        print


class GameView:
    """
        Draws the model state onto the screen.
        """

    def __init__(self, evManager, model):
        """
        evManager (EventManager): Allows posting messages to the event queue.
        model (GameEngine): a strong reference to the game Model.

        Attributes:
        isinitialized (bool): pygame is ready to draw.
        screen (pygame.Surface): the screen surface.
        clock (pygame.time.Clock): keeps the fps constant.
        smallfont (pygame.Font): a small font.
        """

        self.evManager = evManager
        evManager.RegisterListener(self)
        self.model = model
        self.isinitialized = False
        # the array of chips already placed on the game
        self.chips = None
        self.board_cell_image = None
        self.board_cell_highlighted_image = None
        self.dev_mode = True
        self.no_sounds = False
        self.clock = None
        self.window = None
        self.config = None
        self.sounds_volume = None
        self.musics_volume = None
        self.placed_sound = None
        self.column_change_sound = None
        self.column_full_sound = None
        self.win_sound = None
        self.applause_sound = None
        self.boo_sound = None
        self.title_font = None
        self.normal_font = None
        self.previous_move_failed = None
        self.highlighted_chips = None

    def load_config(self):
        logging.info('Loading configuration')
        self.config = ConfigParser(defaults=settings.DEFAULT_CONFIG, interpolation=None)
        
        if os.path.isfile(settings.CONFIG_FILE):
            logging.info('Configuration file exist')

            self.config.read(settings.CONFIG_FILE)
        else:
            logging.info('Configuration file does not exist')

            self.config.add_section('connectfour')

            with open(settings.CONFIG_FILE, 'w') as configfile:
                self.config.write(configfile)

    def notify(self, event):
        """
        Receive events posted to the message queue. 
        """

        if isinstance(event, InitializeEvent):
            self.initialize()
        elif isinstance(event, QuitEvent):
            # shut down the pygame graphics
            self.isinitialized = False
            pygame.quit()
        elif isinstance(event, TickEvent):
            if not self.isinitialized:
                return
            currentstate = self.model.state.peek()
            if currentstate == model.STATE_MENU:
                self.rendermenu()
            if currentstate == model.STATE_PLAY:
                self.renderplay()
            if currentstate == model.STATE_HELP:
                self.renderhelp()
            # limit the redraw speed to 30 frames per second
            self.clock.tick(30)

    def initialize(self):
        """
        Set up the pygame graphical display and loads graphical resources.
        """

        logging.info('Initializing game')

        result = pygame.init()
        # the array of chips already placed on the game
        self.chips = pygame.sprite.Group()

        logging.info('Loading images')

        self.board_cell_image = utils.load_image('board_cell.png')
        self.board_cell_highlighted_image = utils.load_image('board_cell_highlighted.png')

        logging.info('Loading sounds')

        #############################
        # setting screen properties #
        #############################
        self.clock = pygame.time.Clock()
        self.window = pygame.display.set_mode(settings.WINDOW_SIZE, pygame.DOUBLEBUF)
        pygame.display.set_caption('Connect Four ' + settings.VERSION)
        pygame.display.set_icon(utils.load_image('icon.png'))

        self.load_config()
        #############################

        self.sounds_volume = self.config.getfloat('connectfour', 'sounds_volume')
        self.musics_volume = self.config.getfloat('connectfour', 'music_volume')

        self.placed_sound = utils.load_sound('placed.wav', volume=self.sounds_volume)
        self.column_change_sound = utils.load_sound('column_change.wav', volume=self.sounds_volume)
        self.column_full_sound = utils.load_sound('column_full.wav', volume=self.sounds_volume)
        self.win_sound = utils.load_sound('win.wav', volume=self.sounds_volume)
        self.applause_sound = utils.load_sound('applause.wav', volume=self.sounds_volume)
        self.boo_sound = utils.load_sound('boo.wav', volume=self.sounds_volume)

        logging.info('Loading fonts')

        self.title_font = utils.load_font('Gidole-Regular.ttf', 22)
        self.normal_font = utils.load_font('Gidole-Regular.ttf', 16)
        
        self.isinitialized = True
        
    def new_game(self):
        logging.info('Starting new game')
        self.chips.empty()
        self.highlighted_chips = {}

        logging.info('Loading random music')
        utils.load_random_music(
            ['techno_dreaming.wav', 'techno_celebration.wav', 'electric_rain.wav', 'snake_trance.wav'],
            volume=self.musics_volume)

    def draw_board(self):
        """Draw the board itself (the game support)."""
        board = self.model.get_board
        for x in range(0, settings.COLS):
            for y in range(0, settings.ROWS):
                if (y, x) in self.highlighted_chips.keys() and self.highlighted_chips[(y, x)]:
                    image = self.board_cell_highlighted_image
                else:
                    image = self.board_cell_image

                self.window.blit(image, (
                x * settings.IMAGES_SIDE_SIZE, y * settings.IMAGES_SIDE_SIZE + settings.BOARD_MARGIN_TOP))

    def draw_background(self):
        self.window.fill(settings.COLORS.BLACK.value)

        blue_rect_1 = pygame.Rect((0, 0), (settings.WINDOW_SIZE[0], settings.COLUMN_CHOOSING_MARGIN_TOP - 1))
        blue_rect_2 = pygame.Rect((0, settings.COLUMN_CHOOSING_MARGIN_TOP), (
            settings.WINDOW_SIZE[0], settings.IMAGES_SIDE_SIZE))

        self.window.fill(settings.COLORS.BLUE.value, blue_rect_1)
        self.window.fill(settings.COLORS.BLUE.value, blue_rect_2)

    def draw_header(self, status_text, status_color):
        # Status
        status = self.title_font.render(status_text, True, status_color)
        status_rect = status.get_rect()
        status_rect.x = 10
        status_rect.centery = 25

        self.window.blit(status, status_rect)

        # Game name
        game_name = self.normal_font.render('Connect Four v' + settings.VERSION, True, settings.COLORS.WHITE.value)
        game_name_rect = game_name.get_rect()
        game_name_rect.centery = 25
        game_name_rect.right = self.window.get_rect().width - 10

        self.window.blit(game_name, game_name_rect)

        # Scores
        pygame.draw.line(self.window, settings.COLORS.BLACK.value, (game_name_rect.left - 15, 0),
                         (game_name_rect.left - 15, settings.COLUMN_CHOOSING_MARGIN_TOP - 1))

        scores_yellow = self.title_font.render(str(self.model.scores[PLAYER2].score), True,
                                               settings.COLORS.YELLOW.value)
        scores_yellow_rect = scores_yellow.get_rect()
        scores_yellow_rect.centery = 25
        scores_yellow_rect.right = game_name_rect.left - 25

        self.window.blit(scores_yellow, scores_yellow_rect)

        dash = self.title_font.render('-', True, settings.COLORS.WHITE.value)
        dash_rect = dash.get_rect()
        dash_rect.centery = 25
        dash_rect.right = scores_yellow_rect.left - 5

        self.window.blit(dash, dash_rect)

        scores_red = self.title_font.render(str(self.model.scores[PLAYER1].score), True,
                                            settings.COLORS.RED.value)
        scores_red_rect = scores_red.get_rect()
        scores_red_rect.centery = 25
        scores_red_rect.right = dash_rect.left - 5

        self.window.blit(scores_red, scores_red_rect)

        pygame.draw.line(self.window, settings.COLORS.BLACK.value, (scores_red_rect.left - 15, 0),
                         (scores_red_rect.left - 15, settings.COLUMN_CHOOSING_MARGIN_TOP - 1))

    def _place_chip(self, col):
        """Move chip down on the screen (effectively perform player movement"""

        if self.program_state == settings.GAME_STATES.PLAYING and self.current_player_chip:
            # Check all rows in the currently selected column starting from the top
            chip_row_stop = self.get_row(col)

            if chip_row_stop is not False:  # Actually move the chip in the current column and reset the current one (to create a new one later)
                self.placed_sound.play()
                self.current_player_chip_column = col
                self.current_player_chip.rect.right = settings.IMAGES_SIDE_SIZE * \
                                                      (self.current_player_chip_column + 1)
                self.current_player_chip.rect.top += settings.IMAGES_SIDE_SIZE * (chip_row_stop + 1)
                self.current_player_chip = None
                self.current_player_chip_column = 0
                self.previous_move_failed = False
                logging.info('Movement SUCCEEDED!')
                logging.info("-- BOARD: ")
                board = self.game_problem.get_board()
                for i in range(len(board)):
                    logging.info(board[i])
            else:  # The column is full
                self.column_full_sound.play()
                self.previous_move_failed = True
                logging.info('Movement FAILED {} column full.'.format(col))

    def update(self):
        self.draw_background()

        if self.program_state == settings.GAME_STATES.PLAYING:

            if not self.current_player_chip:
                logging.info(self.current_player.name + ' player turn')
                self.current_player_chip = self.current_player.chip()

                self.chips.add(self.current_player_chip)
                self.current_player_chip.rect.left = 0
                self.current_player_chip.rect.top = settings.COLUMN_CHOOSING_MARGIN_TOP

            status_text = self.current_player.name + " PLAYER'S TURN!"
            status_color = self.current_player.color

            move = self.current_player.engine.choose(self.game_problem)
            self.game_problem = self.game_problem.move(move)
            self._place_chip(move)

            if self.game_problem.end == Connect4.DRAW_ID:
                pygame.mixer.music.stop()
                self.boo_sound.play()
                self.program_state = settings.GAME_STATES.NO_ONE_WIN
                logging.info('No one won')
            elif self.game_problem.end is None and not self.previous_move_failed:  # It's the other player's turn if the current player didn't win
                self.current_player = self.players[self.game_problem.whose_turn_is_it]
                logging.info('Starting new player turn')
            elif self.game_problem.end == Connect4.PLAYER1_ID or self.game_problem.end == Connect4.PLAYER2_ID:
                pygame.mixer.music.stop()
                self.win_sound.play()
                self.program_state = settings.GAME_STATES.WON
                pygame.time.set_timer(settings.EVENTS.WINNER_CHIPS_EVENT.value, 600)
                logging.info(self.current_player.name + ' WINS!')
                self.current_player.score += 1
                self.highlighted_chips = Connect4.get_win_segment(self.game_problem._board)


        elif self.program_state == settings.GAME_STATES.WON:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:  # The user want to go back to the game menu
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_RETURN:  # Pressing the Return key will start a new game
                        self.new_game()
                elif event.type == settings.EVENTS.WINNER_CHIPS_EVENT.value:
                    for k in self.highlighted_chips.keys():
                        self.highlighted_chips[k] = not self.highlighted_chips[k]

                    pygame.time.set_timer(settings.EVENTS.WINNER_CHIPS_EVENT.value, 600)

            status_text = self.current_player.name + ' PLAYER WINS!'
            status_color = self.current_player.color
        elif self.program_state == settings.GAME_STATES.NO_ONE_WIN:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:  # The user want to go back to the game menu
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_RETURN:  # Pressing the Return key will start a new game
                        self.new_game()

            status_text = 'TIE!'
            status_color = settings.COLORS.WHITE.value

        self.draw_header(status_text, status_color)
        self.chips.draw(self.window)
        self.draw_board()
