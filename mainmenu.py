from state import State
import pygame
from network import Network
import socket

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
        screen.blit(text_surface, (self.rect.x + (200 - text_surface.get_width())//2, self.rect.y + (40-text_surface.get_height())//2))
    

class MainMenu(State):
    def __init__(self, spill):
        super().__init__(spill)
        self.button_height = 20
        self.button_width = 100
        self.color = (200, 200, 200)
        self.bg = pygame.image.load("images/battleship_bg.jpg")
        self.bg = pygame.transform.scale(self.bg, (1200, 600))
        self.text_input = TextInput(spill,self.spill.screen.get_width()//2-200//2, self.spill.screen.get_height()//2-40//2+100, 200, 40)
        self.x = 1200
        

    def update(self):
        self.text_input.update()

    def render(self):
        self.spill.screen.blit(self.bg, (0,0))
        self.text_input.render(self.spill.screen)
        
        