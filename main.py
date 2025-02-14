import pygame
from mainmenu import MainMenu
from battleship import BattleShip
from game_end_screen import EndScreen

class Main:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((500, 500))
        self.clock = pygame.time.Clock()
        self.actions = {"left" : False, "right" : False, "up" : False, "down" : False}
        self.pressed_actions = {"return" : False}
        self.font = pygame.font.Font(None, 32)
        
        self.states = {
            "mainmenu" : MainMenu(self),
            "battleship" : BattleShip(self),
            "endscreen" : EndScreen(self),
        }
        self.change_state("mainmenu")
        
        self.running = True
    
    def change_state(self, state):
        self.state = self.states[state]
        self.state.__init__(self)
    
    def main_loop(self):
        self.handle_input()
        self.update()
        self.render()

    def handle_input(self):
        # Event-handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.actions["left"] = True
                if event.key == pygame.K_RIGHT:
                    self.actions["right"] = True
                if event.key == pygame.K_UP:
                    self.actions["up"] = True
                if event.key == pygame.K_DOWN:
                    self.actions["down"] = True
                if event.key == pygame.K_RETURN:
                    self.pressed_actions["return"] = True

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    self.actions["left"] = False
                if event.key == pygame.K_RIGHT:
                    self.actions["right"] = False
                if event.key == pygame.K_UP:
                    self.actions["up"] = False
                if event.key == pygame.K_DOWN:
                    self.actions["down"] = False
                    
    def skriv_tekst(self, surface : pygame.Surface, string : str, font : pygame.font.Font, color : tuple, center : tuple):
        # Lager tekst. Andre parameter er anti-alias. Sett til True for glatt og fin tekst.
        text = font.render(string, False, color)
        # Henter rektangelet rundt teksten, med sentrum der man ønsker.
        text_rect = text.get_rect(center = center)
        # Setter teksten på overflaten man spesifiserte.
        surface.blit(text, text_rect)

    def update(self):
        self.state.update()
        self.clock.tick(60)
    
    def render(self):
        self.state.render()
        pygame.display.flip()
        
# Kjører spillet
main = Main()
while main.running:
    main.main_loop()