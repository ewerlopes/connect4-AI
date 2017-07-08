import pygame


current_theme = None


class DefaultTheme:
    def __init__(self):
        self.text_color = pygame.Color('black')
        self.text_color_hovered = pygame.Color('black')
        self.text_color_disabled = pygame.Color('grey')

        self.background_color = pygame.Color('grey')
        self.background_color_hovered = pygame.Color('darkgrey')
        self.background_color_disabled = pygame.Color('darkgrey')

        self.border_color = pygame.Color('darkgrey')
        self.border_color_hovered = pygame.Color('black')
        self.border_color_disabled = pygame.Color('darkgrey')

        self.pointer = pygame.cursors.arrow
        self.pointer_hovered = pygame.cursors.tri_left

        self.hover_sound = None
        self.click_sound = None


def init(theme=DefaultTheme()):
    global current_theme

    current_theme = theme


def event_handler(gui_container, event):
    global current_theme

    for widget in gui_container:
        if isinstance(widget, Button):
            if not widget.is_disabled and widget.on_click is not None and event.type == pygame.MOUSEBUTTONDOWN and widget.rect.collidepoint(event.pos):
                if current_theme.click_sound:
                    current_theme.click_sound.stop()
                    current_theme.click_sound.play()

                widget.on_click(widget)
            elif not widget.is_disabled and event.type == pygame.MOUSEMOTION:
                if not widget.is_hovered and widget.rect.collidepoint(event.pos):
                    if current_theme.hover_sound:
                        current_theme.hover_sound.play()

                    widget.is_hovered = True

                    pygame.mouse.set_cursor(*widget.get_pointer())
                elif widget.is_hovered and not widget.rect.collidepoint(event.pos):
                    widget.is_hovered = False

                    pygame.mouse.set_cursor(*widget.get_pointer())
        elif isinstance(widget, Label):
            if not widget.is_disabled and widget.on_click is not None and event.type == pygame.MOUSEBUTTONDOWN and widget.rect.collidepoint(event.pos):
                if current_theme.click_sound:
                    current_theme.click_sound.stop()
                    current_theme.click_sound.play()

                widget.on_click(widget)
            elif widget.on_click and not widget.is_disabled and event.type == pygame.MOUSEMOTION:
                if not widget.is_hovered and widget.rect.collidepoint(event.pos):
                    widget.is_hovered = True

                    pygame.mouse.set_cursor(*widget.get_pointer())
                elif widget.is_hovered and not widget.rect.collidepoint(event.pos):
                    widget.is_hovered = False

                    pygame.mouse.set_cursor(*widget.get_pointer())


class Widget(pygame.sprite.Sprite):
    is_hovered = False
    is_disabled = False

    def __init__(self, disabled=False, data={}):
        pygame.sprite.Sprite.__init__(self)

        self.is_disabled = disabled
        self.data = data

    def draw(self):
        pass

    def update(self):
        self.draw()

    def get_background_color(self):
        if self.is_hovered:
            return current_theme.background_color_hovered
        elif self.is_disabled:
            return current_theme.background_color_disabled
        else:
            return current_theme.background_color

    def get_border_color(self):
        if self.is_hovered:
            return current_theme.border_color_hovered
        elif self.is_disabled:
            return current_theme.border_color_disabled
        else:
            return current_theme.border_color

    def get_text_color(self):
        if self.is_hovered:
            return current_theme.text_color_hovered
        elif self.is_disabled:
            return current_theme.text_color_disabled
        else:
            return current_theme.text_color

    def get_pointer(self):
        if self.is_hovered:
            return current_theme.pointer_hovered
        else:
            return current_theme.pointer


class Label(Widget):
    on_click = None

    def __init__(self, font, text, on_click=None, data={}):
        Widget.__init__(self, data=data)

        self.font = font
        self.text = text
        self.on_click = on_click

        self.draw()

        self.rect = self.image.get_rect()

    def draw(self):
        global current_theme

        self.image = self.font.render(self.text, True, self.get_text_color())


class Button(Widget):
    on_click = None

    def __init__(self, rect, font, text, on_click=None, disabled=False, data={}):
        Widget.__init__(self, disabled=disabled, data=data)

        self.image = pygame.Surface(rect.size)
        self.rect = rect
        self.font = font
        self.text = text
        self.internal_rect = pygame.Rect(0, 0, self.rect.w, self.rect.h)
        self.on_click = on_click

        self.draw()

    def draw(self):
        global current_theme

        self.image.fill(self.get_background_color())
        pygame.draw.rect(self.image, self.get_border_color(), self.internal_rect, 1)

        txt = self.font.render(self.text, True, self.get_text_color())
        txt_rect = txt.get_rect()
        txt_rect.center = self.internal_rect.center

        self.image.blit(txt, txt_rect)
