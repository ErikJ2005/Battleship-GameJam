import pygame
import subprocess
import socket
import threading
from state import State

class Button(State):
    def __init__(self, spill, x: int, y: int, width: int, height: int, text: str, image : str):
        super().__init__(spill)
        self.x = x
        self.y = y
        self.width = width
        self.height = height     
        
        self.button = pygame.image.load(image)
        self.button = pygame.transform.scale(self.button, (width, height))
        self.rect = pygame.Rect(x - (width + 4) // 2, y - (height + 4) // 2, width + 4, height + 4)
        self.font = pygame.font.Font(None, height - 3)
        self.text = text
        self.color = (0, 0, 0)

    def render(self, screen, show_text = True):
        pygame.draw.rect(screen, self.color, self.rect)
        screen.blit(self.button, (self.x - self.width // 2, self.y - self.height // 2))
        if show_text == True:
            button_text = self.font.render(self.text, True, (0, 0, 0))
            screen.blit(button_text, (self.rect.x + (self.rect.width - button_text.get_width()) // 2, self.rect.y + (self.rect.height - button_text.get_height()) // 2))

class MainMenu(State):
    def __init__(self, spill):
        super().__init__(spill)
        pygame.mixer.init()
        # Laster inn knapp lyden og setter volumet
        self.button_sound = pygame.mixer.Sound("music/button.wav")
        self.button_sound.set_volume(self.spill.button_volume)
        self.sound_id = None # Gjør at lyden kke blir spilt av flere ganger når man velger ip
        
        # setter opp netverk variabler
        self.UDP_PORT = 50000
        self.TIMEOUT = 4
        self.discovered_servers = []  # Listen av ip-er man mottar
        self.selected_ip = None # ip-en man har valgt

        # laster in bilder som blir brukt i main menu
        self.bg = pygame.image.load("images/battleship_bg.jpg")
        self.ship1 = pygame.image.load("images/battleship2.png")
        self.ship2 = pygame.image.load("images/battleship2.png")
        self.bg = pygame.transform.scale(self.bg, (self.spill.screen.get_width(), self.spill.screen.get_height()))
        self.ship2 = pygame.transform.flip(self.ship2, 1, 0)

        # knapper
        self.host_game = Button(spill, self.spill.screen.get_width() // 2, self.spill.screen.get_height() // 2, 300, 50, "Host game", "images/buttons.png")
        self.join_game = Button(spill, self.spill.screen.get_width() // 2, self.spill.screen.get_height() // 2 + 100, 300, 50, "Join game", "images/buttons.png")
        self.singleplayer_game = Button(self, self.spill.screen.get_width()//2, self.spill.screen.get_height() // 2 + 200, 300, 50, "Singleplayer", "images/buttons.png")
        self.settings = Button(self, 50, 50, 50, 50, "settings", "images/settings.png")
        
        
        self.running = True
        
        # Starten en ny thread som kjører samtidig som selve hovedmenyen for å høre etter om den får inn en ip
        threading.Thread(target=self.listen_for_servers, daemon=True).start() 

    def listen_for_servers(self):
        # Hører etter om den får inn et signal på den porten
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        udp_sock.bind(("", self.UDP_PORT))
        udp_sock.settimeout(1)  # gjør at den ikke henger seg opp for altid

        while self.running:
            try:
                data, addr = udp_sock.recvfrom(1024)
                message = data.decode()
                _, ip, _ = message.split(":")

                # Legger kun til unike ip-er
                if ip not in self.discovered_servers:
                    self.discovered_servers.append(ip)
            except socket.timeout:
                pass  # håpper over hvis den ikke finer noe

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


    def update(self):
        
        # Endrer farge på ramen til knappen når man holder over den
        self.host_game.color = (200, 200, 200) if self.host_game.rect.collidepoint(pygame.mouse.get_pos()) else (0,0,0)
        self.join_game.color = (200, 200, 200) if self.join_game.rect.collidepoint(pygame.mouse.get_pos()) else (0,0,0)
        self.singleplayer_game.color = (200, 200, 200) if self.singleplayer_game.rect.collidepoint(pygame.mouse.get_pos()) else (0,0,0)
        self.settings.color = (200, 200, 200) if self.settings.rect.collidepoint(pygame.mouse.get_pos()) else (0,0,0)
        
        # Settings knappen
        if self.settings.rect.collidepoint(self.spill.pressed_actions["mouse"][1]) and self.spill.pressed and self.spill.pressed_actions["mouse"][0]:
            self.button_sound.play()
            self.spill.pressed = False
            self.spill.change_state("settings")
        
        # Starter opp serveren og starter spillet så man kan vente på at en annen blir med på samme nett
        if self.host_game.rect.collidepoint(self.spill.pressed_actions["mouse"][1]):
            self.button_sound.play()
            subprocess.Popen(["python", "host.py"])
            self.spill.ip = socket.gethostbyname(socket.gethostname())
            self.spill.change_state("battleship")

        # Sjekker om noen av ip-ene i listen er klikket
        for i, ip in enumerate(self.discovered_servers):
            ip_rect = pygame.Rect(self.spill.screen.get_width() - 350, 115 + i * 40, 300, 30)
            if ip_rect.collidepoint(self.spill.pressed_actions["mouse"][1]) and self.sound_id != i:
                self.button_sound.play()
                self.selected_ip = ip
                self.sound_id = i

        # knap for å bli med i spillet til ip-en man har trykket
        if self.join_game.rect.collidepoint(self.spill.pressed_actions["mouse"][1]) and self.selected_ip:
            self.button_sound.play()
            self.spill.ip = self.selected_ip
            self.spill.change_state("battleship")
        
        # Knapp for å spille singleplayer
        if self.singleplayer_game.rect.collidepoint(self.spill.pressed_actions["mouse"][1]) and self.spill.pressed and self.spill.pressed_actions["mouse"][0]:
            self.button_sound.play()
            self.spill.change_state("localbattleships")

    def render(self):
        # Tegner bakgrun og overskriften
        self.spill.screen.blit(self.bg, (0, 0))
        self.spill.screen.blit(self.ship1, (self.spill.screen.get_width() - self.ship1.get_width(), self.spill.screen.get_height() - self.ship1.get_height() + 50))
        self.spill.screen.blit(self.ship2, (0, self.spill.screen.get_height() - self.ship1.get_height() + 50))
        self.draw_text("Battle Ships", 100, (0, 0, 0), self.spill.screen.get_width() // 2, 100)

        # tegner knappene
        self.host_game.render(self.spill.screen)
        self.join_game.render(self.spill.screen)
        self.singleplayer_game.render(self.spill.screen)
        self.settings.render(self.spill.screen, False)

        # Tegner listen med ip-er
        self.draw_text("Online servers", 40, (0, 0, 0), self.spill.screen.get_width() - 200, 100)
        for i, ip in enumerate(self.discovered_servers):
            rect = pygame.Rect(self.spill.screen.get_width() - 350, 115 + i * 40, 300, 30)
            
            # Henter fargen til knappene i listen
            color = (138, 0, 0, 100) if ip == self.selected_ip else (200, 200, 200, 100)  if rect.collidepoint(pygame.mouse.get_pos()) else (255, 255, 255, 100)
            # Lager en ny surface som er gjenomsiktig
            rect_surface = pygame.Surface((300, 30), pygame.SRCALPHA)
            rect_surface.fill(color)  # seltter fargen med hvor gjennomsiktig man vil at den skal være
            
            # Tegner alt sammen ut på skjermen
            self.spill.screen.blit(rect_surface, (self.spill.screen.get_width() - 350, 115 + i * 40))
            pygame.draw.rect(self.spill.screen, color, (self.spill.screen.get_width() - 350, 115 + i * 40, 300, 30), 2)
            self.draw_text(ip, 30, (0, 0, 0), self.spill.screen.get_width()-200, 130 + i * 40)
