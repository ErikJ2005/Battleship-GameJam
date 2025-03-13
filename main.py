import pygame
from mainmenu import MainMenu
from battleship import BattleShips
from game_end_screen import EndScreen
from local_battleship import LocalBattleships
from settings import Settings
from shop import Shop

class Main:
    def __init__(self):
        
        # Spiller musiken til spillet
        pygame.mixer.init()
        pygame.mixer.music.load("music/theme_song.wav")
        pygame.mixer.music.play(-1)  # loop
        pygame.mixer.music.set_volume(0.2)  # float tall

        # Volum nivåer
        self.miss_volume = 0.2
        self.hit_volume = 0.2
        self.music_volume = 0.2
        self.button_volume = 0.5
        
        # Pygame og skjerm oppsett
        pygame.init()
        self.screen = pygame.display.set_mode((1200, 600))
        pygame.display.set_caption("Battleships")
        icon = pygame.image.load("images/battleship2.png")
        pygame.display.set_icon(icon)
        
        self.running = True
        self.width = self.screen.get_width()
        self.height = self.screen.get_height()
        
        # Input setup
        self.pressed_actions = {"mouse": [False, (0, 0)], "enter" : False, "backspace" : False, "rotate" : "horizontal", "slider": False}
        self.pressed = True
        
        # Variabler som brukes over flere scripts
        self.ip = ""
        self.winner = ""
        self.disconnect = False
        
        self.font = pygame.font.Font(None, 32)
        
        # Setter opp states
        self.states = {
            "mainmenu" : MainMenu,
            "battleship" : BattleShips,
            "localbattleships" : LocalBattleships,
            "endscreen" : EndScreen,
            "settings" : Settings,
            "shop" : Shop,
        }
        self.change_state("mainmenu")
    
    def change_state(self, state : str):
        """ Endrer på staten til spillet og kjører init på nytt

        Args:
            state (str): Key til staten i ordboken hvor alle statene er lagret
        """
        if state == "battleship":
            self.state = self.states[state](self, True)
        else:
            self.state = self.states[state](self)
    
    # Hoved loopen til spillet
    def main_loop(self):
        self.handle_input()
        self.update()
        self.render()

    def handle_input(self):
        # Får inn alle inputs til spillet så man kan bruke det i alle scriptene for hele spillet
        for event in pygame.event.get():
            # Gjør at man kan lukke spillet
            if event.type == pygame.QUIT:
                self.running = False
                pygame.mixer.music.stop()
            
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                if self.state == self.states["battleship"]:
                    self.disconnect = True
                elif self.state != self.states["mainmenu"]:
                    self.change_state("mainmenu")
                else:
                    self.running = False
                    pygame.mixer.music.stop()
            
            # Får inn mus inputen og posisjonen til der man trykket
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.pressed_actions["mouse"][1] = pygame.mouse.get_pos()
                self.pressed_actions["mouse"][0] = True
                self.pressed_actions["slider"] = True
            else: 
                self.pressed_actions["mouse"][0] = False
                
            if event.type == pygame.MOUSEBUTTONUP:
                self.pressed_actions["mouse"][1] = (0,0)
                self.pressed_actions["slider"] = False
                self.pressed = True
            
            # Får i keyboard input for å kunne rotere skip
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    if self.pressed_actions["rotate"] == "horizontal":
                        self.pressed_actions["rotate"] = "vertical"  
                    else:
                        self.pressed_actions["rotate"] = "horizontal"
    # Update metoden 
    def update(self):
        pygame.mixer.music.set_volume(self.music_volume)  # float tall
        self.state.update()
    
    # Render metoden
    def render(self):
        self.state.render()
        pygame.display.flip()
        
# Kjører spillet
main = Main()
while main.running:
    main.main_loop()

