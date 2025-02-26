#https://github.com/ErikJ2005/Battleship-GameJam.git

import pygame
from mainmenu import MainMenu
from battleship import BattleShips
from game_end_screen import EndScreen

class Main:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1200, 600))
        self.pressed_actions = {"mouse": [False, (0, 0)], "enter" : False, "key" : [False,""], "backspace" : False, "rotate" : "horizontal"}
        self.ip = ""
        self.winner = ""
        self.font = pygame.font.Font(None, 32)
        self.states = {
            "mainmenu": MainMenu(self),
            "battleship": BattleShips(self),
            "endscreen": EndScreen(self),
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
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                self.pressed_actions["mouse"][1] = pygame.mouse.get_pos()
                self.pressed_actions["mouse"][0] = True
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    if self.pressed_actions["rotate"] == "horizontal":
                        self.pressed_actions["rotate"] = "vertical"  
                    else:
                        self.pressed_actions["rotate"] = "horizontal"
                
                if event.key == pygame.K_RETURN:
                    self.pressed_actions["enter"] = True
                elif event.key == pygame.K_BACKSPACE:
                    self.pressed_actions["backspace"] = True
                else:
                    self.pressed_actions["key"] = [True, event.unicode]

    def update(self):
        self.state.update()
    
    def render(self):
        self.state.render()
        pygame.display.flip()
        
# Kjører spillet
main = Main()
while main.running:
    main.main_loop()
