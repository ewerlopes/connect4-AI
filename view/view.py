import pygame

import model
from control.eventmanager import *
from game.game import DRAW

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
