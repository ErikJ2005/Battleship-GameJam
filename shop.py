from mainmenu import Button
from settings import Slider
from state import State
import pygame

class Skins:
    def __init__(self, spill, image_dir):
        self.spill = spill
        self.screen = spill.screen
        
        pygame.mixer.init()
        # Laster inn knapp lyden og setter volumet
        self.button_sound = pygame.mixer.Sound("music/button.wav")
        
        self.button_sound.set_volume(self.spill.button_volume)
        self.coins = 0
        self.items = [[pygame.image.load("images/ship.png"), 0],
                        [pygame.image.load("images/hotdog.png"), 50],
                        [pygame.image.load("images/gummibåt.png"), 100],
                        [pygame.image.load("images/pirateship.png"), 250],
                        [pygame.image.load("images/spaceship.png"), 500]]
        
        if image_dir == 0:
            self.items[0][0] = pygame.transform.rotate(self.items[0][0], 0)
            self.items[1][0] = pygame.transform.rotate(self.items[1][0], 90)
            self.items[2][0] = pygame.transform.rotate(self.items[2][0], 0)
            self.items[3][0] = pygame.transform.rotate(self.items[3][0], 0)
            self.items[4][0] = pygame.transform.rotate(self.items[4][0], 90)
        elif image_dir == 1:
            self.items[0][0] = pygame.transform.rotate(self.items[0][0], 90)
            self.items[1][0] = pygame.transform.rotate(self.items[1][0], 0)
            self.items[2][0] = pygame.transform.rotate(self.items[2][0], 90)
            self.items[3][0] = pygame.transform.rotate(self.items[3][0], 90)
            self.items[4][0] = pygame.transform.rotate(self.items[4][0], 0)
        self.item_scale = [(50,300), (150,300), (150,300), (150,300), (150,300)]
        self.buttons = [pygame.Rect(100 + 300*i, spill.screen.get_height()//2, 40, 40) for i in range(len(self.items))]
        self.locked = pygame.image.load("images/locked.png")
        self.unlocked = pygame.image.load("images/unlocked.png")
        
        self.start_up()

    def start_up(self):
        try:
            with open("personal_ownership.txt","r") as file:
                    self.owned_items = file.readline()
                    self.owned_items = self.owned_items.split("[")
                    self.owned_items.pop(0)
                    self.owned_items.pop(0)
                    self.owned_items[0] = self.owned_items[0].replace("]","").replace(" ","").replace("'","").replace('"',"").split(",")
                    self.owned_items[0][0] = int(self.owned_items[0][0])
                    self.coins = self.owned_items[0][0]
                    
                    self.owned_items[0][1] = self.owned_items[0][1].replace(",","").replace(" ","").replace("]","")
                    self.owned_items[0][1] = int(self.owned_items[0][1])


                    self.owned_items[1] = self.owned_items[1].replace("]","").replace(" ","").replace("'","").split(",")
                    
                    for i in range(len(self.owned_items[1])):
                        if self.owned_items[1][i] == "True":
                            self.owned_items[1][i] = True
                        elif self.owned_items[1][i] == "False":
                            self.owned_items[1][i] = False
                    
                    self.owned_items[2] = self.owned_items[2].replace(" ","").replace("]","").replace("'","").split(",")

        except:
            self.owned_items = [[0, 0],[False for i in range(len(self.items))], ["images/ship.png", "images/hotdog.png", "images/pirateship.png", "images/spaceship.png"]]
            self.owned_items[1][0] = True
    
    
    def update(self):
        for x in range(len(self.owned_items)):
            for y in range(len(self.owned_items[x])):
                    if self.owned_items[x][y] == '':
                        self.owned_items[x].pop(y)

        if self.coins != self.owned_items[0][0]:
            self.owned_items[0][0] = self.coins
            with open("personal_ownership.txt", "w") as file:
                file.write("")
                file.write(f"{self.owned_items}")
        
        for i in range(len(self.buttons)):
            if self.buttons[i].collidepoint(self.spill.pressed_actions["mouse"][1]) and self.spill.pressed and self.spill.pressed_actions["mouse"][0] and self.spill.pressed:
                if self.coins >= self.items[i][1] and not self.owned_items[1][i]:
                    self.button_sound.play()
                    self.owned_items[1][i] = True
                    self.coins -= self.items[i][1]
                    self.owned_items[0][0] = self.coins
                    with open("personal_ownership.txt", "w") as file:
                        file.write("")
                        file.write(f"{self.owned_items}")
                        
                if i != self.owned_items[0][1] and self.owned_items[1][i]:
                    self.button_sound.play()
                    self.owned_items[0][1] = i
                    with open("personal_ownership.txt", "w") as file:
                        file.write("")
                        file.write(f"{self.owned_items}")
                
    def draw_text(self, text: str, size: int, color: tuple, x: int, y: int):
        """ Tegner teksten man skriver inn på skjermen

        Args:
            text (str): Teksten man vil at sal vises 
            size (int): Størelsen på teksten
            color (tuple): Fargen til teksten
            x (int): x posisjonen til teksten
            y (int): y posisjonen til teksten
        """
        font = pygame.font.Font(None, size)
        info = font.render(text, True, color)
        self.spill.screen.blit(info, (x - info.get_width() // 2, y - info.get_height() // 2))
    

    def render(self, slider):
        for i in range(len(self.items)):
            self.buttons[i] = pygame.Rect(30+300*i - slider.value, self.screen.get_height()//2 - 200, 270, self.screen.get_height()//2 + 75)
            
            if self.owned_items[0][1] == i:
                pygame.draw.rect(self.screen, (139, 0, 0), self.buttons[i])
            elif self.buttons[i].collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(self.screen, (200, 200, 200), self.buttons[i])
            else:
                pygame.draw.rect(self.screen, (255, 255, 255), self.buttons[i])
                
            pygame.draw.rect(self.screen, (0, 0, 0), (30+300*i - slider.value, self.screen.get_height()//2 - 200, 270, self.screen.get_height()//2 + 75), 10)
            
            self.items[i][0] = pygame.transform.scale(self.items[i][0], self.item_scale[i])
            self.screen.blit(self.items[i][0], (150 + 300*i - slider.value - self.item_scale[i][0]//2, self.screen.get_height()//2 - 170))
            if not self.owned_items[1][i]:
                self.draw_text(f"Cost: {self.items[i][1]}", 30, (0,0,0), 220 + 300*i - slider.value, self.screen.get_height()//2 - 170)
            
            if not self.owned_items[1][i]:
                self.locked = pygame.transform.scale(self.locked, (50,75))
                self.screen.blit(self.locked, (150 + 300*i - slider.value - 50//2, self.screen.get_height()//2 - 100))
            elif self.owned_items[1][i]:
                self.unlocked = pygame.transform.scale(self.unlocked, (50*1.2,75))
                self.screen.blit(self.unlocked, (140 + 300*i - slider.value - 50//2, self.screen.get_height()//2 - 100))
        self.draw_text(f"Coins: {self.coins}", 30, (0,0,0), self.screen.get_width() - 100, 30)



class Shop(State):
    def __init__(self, spill):
        super().__init__(spill)
        self.screen = spill.screen
        self.bg = pygame.image.load("images/battleship_bg.jpg")
        self.bg = pygame.transform.scale(self.bg, (1200, 600))
        
        # Laster inn knapp lyden og setter volumet
        self.button_sound = pygame.mixer.Sound("music/button.wav")
        
        self.button_sound.set_volume(self.spill.button_volume)
        
        self.skins = Skins(spill, 1)
        self.slider = Slider(spill, self.screen.get_width()//2, self.screen.get_height()//2 + 200, 1000, 40, 0, len(self.skins.items)*150, 0)
        self.back_to_main_menu = Button(spill, self.spill.screen.get_width() // 2, self.spill.screen.get_height() // 2 + 250, 300, 50, "Main-menu", "images/buttons.png")
    
    def update(self):
        self.back_to_main_menu.color = (200, 200, 200) if self.back_to_main_menu.rect.collidepoint(pygame.mouse.get_pos()) else (0,0,0)
        
        if self.back_to_main_menu.rect.collidepoint(self.spill.pressed_actions["mouse"][1]) and self.spill.pressed and self.spill.pressed_actions["mouse"][0]:
            self.spill.pressed = False
            self.button_sound.play()
            self.spill.change_state("mainmenu")

        self.skins.update()
        self.slider.update()
    
    def render(self):
        self.screen.blit(self.bg, (0,0))
        self.back_to_main_menu.render(self.spill.screen)
        self.skins.render(self.slider)
        self.slider.render(self.screen)