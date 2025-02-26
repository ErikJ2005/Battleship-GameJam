import pygame, subprocess, socket
from state import State

class TextInput(State):
    def __init__(self, spill, x, y, width, height, font_size=30, text_color=(0, 0, 0), bg_color=(200, 200, 200), border_color=(0, 0, 0)):
        super().__init__(spill)
        self.rect = pygame.Rect(x, y, width, height)
        self.font = pygame.font.Font(None, font_size)
        self.text = ""
        self.text_color = text_color
        self.bg_color = bg_color
        self.border_color = border_color
        self.active = False
        self.x = 0
        self.y = 0
        
    def update(self):
        if self.spill.pressed_actions["mouse"][1] is not None:
            self.x, self.y = self.spill.pressed_actions["mouse"][1]

        if self.rect.collidepoint(self.x, self.y):
            if self.spill.pressed_actions["enter"]:
                self.spill.ip = self.text
                self.spill.pressed_actions["mouse"][1] = (0, 0)
                self.spill.change_state("battleship")
                self.spill.pressed_actions["enter"] = False  # Reset after processing
            elif self.spill.pressed_actions["backspace"]:
                self.text = self.text[:-1]
                self.spill.pressed_actions["backspace"] = False  # Reset after processing
            elif self.spill.pressed_actions["key"][0]:
                self.text += self.spill.pressed_actions["key"][1]
                self.spill.pressed_actions["key"][0] = False  # Reset after processing

    def render(self, screen):
        pygame.draw.rect(screen, self.bg_color, self.rect)
        pygame.draw.rect(screen, self.border_color, self.rect, 1)
        text_surface = self.font.render(self.text, True, self.text_color)
        screen.blit(text_surface, (self.rect.x + (self.rect.width - text_surface.get_width())//2, self.rect.y + (self.rect.height-text_surface.get_height())//2))
    
class Button(State):
    def __init__(self, spill, x : int, y : int, width : int, height : int, text : str):
        super().__init__(spill)
        self.rect = pygame.Rect(x-width//2, y-height//2, width, height)
        self.font = pygame.font.Font(None, height-1)
        self.text = text
        
    def render(self, screen):
        pygame.draw.rect(screen, (200, 200, 200), self.rect)
        button_text = self.font.render(self.text, True, (0, 0, 0))
        screen.blit(button_text, (self.rect.x + (self.rect.width-button_text.get_width())//2, self.rect.y + (self.rect.height-button_text.get_height())//2))

class MainMenu(State):
    def __init__(self, spill):
        super().__init__(spill)
        self.button_height = 20
        self.button_width = 100
        self.color = (200, 200, 200)
        self.bg = pygame.image.load("images/battleship_bg.jpg")
        self.bg = pygame.transform.scale(self.bg, (1200, 600))
        self.text_input = TextInput(spill,self.spill.screen.get_width()//2-100, self.spill.screen.get_height()//2-40//2+100, 200, 40)
        self.host_game = Button(spill, self.spill.screen.get_width()//2, self.spill.screen.get_height()//2, 300, 50, "Host game")
        
    def start_host(self):
        with open("host.py") as f:
            exec(f.read())

    def update(self):
        if self.host_game.rect.collidepoint(self.spill.pressed_actions["mouse"][1]):
            subprocess.Popen(["python", "host.py"])
            self.spill.ip = socket.gethostbyname(socket.gethostname())
            self.spill.change_state("battleship")
        self.text_input.update()

    def render(self):
        self.spill.screen.blit(self.bg, (0,0))
        self.text_input.render(self.spill.screen)
        self.host_game.render(self.spill.screen)
        