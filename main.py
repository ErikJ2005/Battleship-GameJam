#https://github.com/ErikJ2005/Battleship-GameJam.git

import pygame
from mainmenu import MainMenu
from battleship import BattleShips
from game_end_screen import EndScreen
from local_battleship import LocalBattleships
from settings import Settings

class Main:
    def __init__(self):
        
        # Spiller musiken til spillet
        pygame.mixer.init()
        pygame.mixer.music.load("music/theme_song.wav")
        pygame.mixer.music.play(-1)  # loop
        pygame.mixer.music.set_volume(0.3)  # float tall

        # Volum nivåer
        self.miss_volume = 0.2
        self.hit_volume = 0.2
        self.music_volume = 0.2
        self.button_volume = 0.5
        
        pygame.init()

        self.screen = pygame.display.set_mode((1200, 600))
        self.running = True
        self.width = self.screen.get_width()
        self.height = self.screen.get_height()
        
        self.pressed_actions = {"mouse": [False, (0, 0)], "enter" : False, "key" : [False,""], "backspace" : False, "rotate" : "horizontal", "slider": False}
        self.pressed = True
        
        self.ip = ""
        self.winner = ""
        
        self.font = pygame.font.Font(None, 32)
        
        self.states = {
            "mainmenu" : MainMenu(self),
            "battleship" : BattleShips(self, True),
            "localbattleships" : LocalBattleships(self),
            "endscreen" : EndScreen(self),
            "settings" : Settings(self),
        }
        self.change_state("mainmenu")
        
    def change_state(self, state : str):
        self.state = self.states[state]
        if state == "battleship":
            self.state.__init__(self, True)
        else:
            self.state.__init__(self)
    
    def main_loop(self):
        self.handle_input()
        self.update()
        self.render()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.running = False
                pygame.mixer.music.stop()

            if event.type == pygame.MOUSEBUTTONDOWN:
                self.pressed_actions["mouse"][1] = pygame.mouse.get_pos()
                self.pressed_actions["mouse"][0] = True
                self.pressed_actions["slider"] = True
            else: 
                self.pressed_actions["mouse"][0] = False
                
            if event.type == pygame.MOUSEBUTTONUP:
                self.pressed_actions["slider"] = False
                self.pressed = True
            
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
        pygame.mixer.music.set_volume(self.music_volume)  # float tall
        self.state.update()
    
    def render(self):
        self.state.render()
        pygame.display.flip()
        
# Kjører spillet
main = Main()
while main.running:
    main.main_loop()
