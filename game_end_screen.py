from state import State
import pygame

class EndScreen(State):
    def __init__(self, spill):
        super().__init__(spill)
        self.button_height = 20
        self.button_width = 100
        self.color = (200, 200, 200)
        self.bg = pygame.image.load("images/battleship_bg.jpg")
        self.bg = pygame.transform.scale(self.bg, (self.spill.screen.get_width(), self.spill.screen.get_height()))
        self.font = pygame.font.Font(None, 100)

    def update(self):
        if self.spill.pressed_actions["enter"]:
            self.spill.change_state("mainmenu")
            self.spill.pressed_actions["enter"] = False

    def render(self):
        self.bg = pygame.transform.scale(self.bg, (self.spill.screen.get_width(), self.spill.screen.get_height()))
        self.spill.screen.blit(self.bg, (0, 0))
        winner = self.font.render(self.spill.winner, True, (0, 0, 0))
        self.spill.screen.blit(winner, (self.spill.screen.get_width() // 2 - winner.get_width() // 2, self.spill.screen.get_height() // 2 - winner.get_height() // 2))