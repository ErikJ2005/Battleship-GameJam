from state import State
import pygame
from mainmenu import Button

class Slider:
    def __init__(self, spill, x, y, width, height, min_value, max_value, start_value):
        """ Lager en slider som man kan bruke for å styre ting som volum som vi gjør i dette tilfellet

        Args:
            spill (_type_): refererer tilbake til hoved scriptet så vi kan lese av inputten
            x (_type_): x posisjonen til der man vil at slideren skal være
            y (_type_): y posisjonen til der man vil at slideren skal være
            width (_type_): bredden til slideren
            height (_type_): høyden til slideren
            min_value (_type_): minste verdien til slideren
            max_value (_type_): største verdien til slideren
            start_value (_type_): start verdien til slideren
        """
        self.spill = spill
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.min_value = min_value
        self.max_value = max_value
        self.value = start_value
        
        # Setter størelsen på slider banen og håndtaket
        self.bar_rect = pygame.Rect(self.x - self.width // 2, self.y - self.height // 2, self.width, self.height)
        self.slider_width = self.height
        self.slider_rect = pygame.Rect(self.get_slider_x(), self.y - self.slider_width // 2, self.slider_width, self.slider_width)
        
        self.dragging = False

    def get_slider_x(self):
        # returnerer x verdien hvor håndtaket på slideren skal være
        return self.bar_rect.left + (self.value - self.min_value) / (self.max_value - self.min_value) * self.width

    def update(self):
        mouse_pressed = self.spill.pressed_actions["slider"]
        mouse_pos = pygame.mouse.get_pos()
        if mouse_pressed and (self.slider_rect.collidepoint(mouse_pos) or self.bar_rect.collidepoint(mouse_pos)): # sjekker at man trykker på slideren
            relative_x = max(self.bar_rect.left, min(mouse_pos[0], self.bar_rect.right)) # Sørger for at x verdien til håndtaket holder seg innenfor verdien til slideren
            self.value = (relative_x - self.bar_rect.left) / self.width * (self.max_value - self.min_value) + self.min_value # Finner verdien som blir mellim minste verdien og største veriden man satt
            self.slider_rect.x = self.get_slider_x() - self.slider_width // 2 # Finner den nye x posisjonen til håndtaket

    def render(self, screen):
        pygame.draw.rect(screen, (200, 200, 200), self.bar_rect)  # tegner banen til slideren
        pygame.draw.rect(screen, (100, 100, 100), self.slider_rect)  # tegner håndtaket til slideren


class Settings(State):
    def __init__(self, spill):
        super().__init__(spill)
        
        self.bg = pygame.image.load("images/battleship_bg.jpg")
        self.bg = pygame.transform.scale(self.bg, (self.spill.screen.get_width(), self.spill.screen.get_height()))
        
        self.button_sound = pygame.mixer.Sound("music/button.wav")
        self.button_sound.set_volume(self.spill.button_volume)
        
        self.back_to_main_menu = Button(spill, self.spill.screen.get_width() // 2, self.spill.screen.get_height() // 2 + 200, 300, 50, "Main-menu", "images/buttons.png")
        
        # Lager de forskjellige sliderne
        self.music_slider = Slider(spill, self.spill.screen.get_width()//2, 100, 200, 30, 0, 1, self.spill.music_volume)
        self.button_slider = Slider(spill, self.spill.screen.get_width()//2, 200, 200, 30, 0, 1, self.spill.button_volume)
        self.miss_slider = Slider(spill, self.spill.screen.get_width()//2, 300, 200, 30, 0, 1, self.spill.miss_volume)
        self.hit_slider = Slider(spill, self.spill.screen.get_width()//2, 400, 200, 30, 0, 1, self.spill.hit_volume)
    
    def draw_text(self, text : str, size : int, color : tuple, x: int, y : int):
        """ Tegner teksten man skriver inn på skjermen

        Args:
            text (str): Teksten man vil at sal vises 
            size (int): Størelsen på teksten
            color (tuple): Fargen til teksten
            x (int): x posisjonen til teksten
            y (int): y posisjonen til teksten
        """
        font  = pygame.font.Font(None, size)
        info = font.render(text, True, color)
        self.spill.screen.blit(info, (x - info.get_width() // 2,y - info.get_height() // 2))

    def update(self):
        self.back_to_main_menu.color = (200, 200, 200) if self.back_to_main_menu.rect.collidepoint(pygame.mouse.get_pos()) else (0,0,0)
        
        if self.back_to_main_menu.rect.collidepoint(self.spill.pressed_actions["mouse"][1]) and self.spill.pressed and self.spill.pressed_actions["mouse"][0]:
            self.button_sound.play()
            self.spill.pressed = False
            self.spill.change_state("mainmenu")
        
        self.music_slider.update()
        self.button_slider.update()
        self.miss_slider.update()
        self.hit_slider.update()

        self.spill.music_volume = self.music_slider.value
        self.spill.button_volume = self.button_slider.value
        self.spill.miss_volume = self.miss_slider.value
        self.spill.hit_volume = self.hit_slider.value

        self.button_sound.set_volume(self.spill.button_volume)
        self.button_sound.set_volume(self.spill.button_volume)
        self.button_sound.set_volume(self.spill.button_volume)
    
    def render(self):
        self.spill.screen.blit(self.bg, (0, 0))
        self.back_to_main_menu.render(self.spill.screen)
        self.music_slider.render(self.spill.screen)
        self.button_slider.render(self.spill.screen)
        self.miss_slider.render(self.spill.screen)
        self.hit_slider.render(self.spill.screen)

        self.draw_text(f"music volume: {self.music_slider.value*100:.1f}%", 30, (0,0,0), self.spill.screen.get_width()//2 - 225, 100)
        self.draw_text(f"button volume: {self.button_slider.value*100:.1f}%", 30, (0,0,0), self.spill.screen.get_width()//2 - 225, 200)
        self.draw_text(f"splash volume: {self.miss_slider.value*100:.1f}%", 30, (0,0,0), self.spill.screen.get_width()//2 - 225, 300)
        self.draw_text(f"hit volume: {self.hit_slider.value*100:.1f}%", 30, (0,0,0), self.spill.screen.get_width()//2 - 225, 400)
