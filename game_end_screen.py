from state import State
import pygame
from mainmenu import Button

class EndScreen(State):
    def __init__(self, spill):
        super().__init__(spill)
        self.button_height = 20
        self.button_width = 100
        self.color = (200, 200, 200)
        self.bg = pygame.image.load("images/battleship_bg.jpg")

        self.button_sound = pygame.mixer.Sound("music/button.wav")
        self.button_sound.set_volume(self.spill.button_volume)

        self.bg = pygame.transform.scale(self.bg, (self.spill.screen.get_width(), self.spill.screen.get_height()))
        self.font = pygame.font.Font(None, 100)
        
        self.back_to_main_menu = Button(spill, self.spill.screen.get_width() // 2, self.spill.screen.get_height() // 2 + 200, 300, 50, "Main-menu", "images/buttons.png")

    def update(self):
        self.back_to_main_menu.color = (200, 200, 200) if self.back_to_main_menu.rect.collidepoint(pygame.mouse.get_pos()) else (0,0,0)
        
        # Knapp for å gå tilbake til main menu
        if self.back_to_main_menu.rect.collidepoint(self.spill.pressed_actions["mouse"][1]):
            self.button_sound.play()
            self.spill.pressed_actions["mouse"][1] = (0,0)
            self.spill.change_state("mainmenu")

    def render(self):
        self.bg = pygame.transform.scale(self.bg, (self.spill.screen.get_width(), self.spill.screen.get_height()))
        self.spill.screen.blit(self.bg, (0, 0))
        self.back_to_main_menu.render(self.spill.screen)
        winner = self.font.render(self.spill.winner, True, (0, 0, 0))
        self.spill.screen.blit(winner, (self.spill.screen.get_width() // 2 - winner.get_width() // 2, self.spill.screen.get_height() // 2 - winner.get_height() // 2))