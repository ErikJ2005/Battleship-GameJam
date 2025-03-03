import pygame
import subprocess
import socket
import threading
from state import State

class Button(State):
    def __init__(self, spill, x: int, y: int, width: int, height: int, text: str):
        super().__init__(spill)
        self.x = x
        self.y = y
        self.width = width
        self.height = height     
        
        self.button = pygame.image.load("images/buttons.png")
        self.button = pygame.transform.scale(self.button, (width, height))
        self.rect = pygame.Rect(x - (width + 4) // 2, y - (height + 4) // 2, width + 4, height + 4)
        self.font = pygame.font.Font(None, height - 3)
        self.text = text
        self.color = (0, 0, 0)

    def render(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        screen.blit(self.button, (self.x - self.width // 2, self.y - self.height // 2))
        button_text = self.font.render(self.text, True, (0, 0, 0))
        screen.blit(button_text, (self.rect.x + (self.rect.width - button_text.get_width()) // 2, 
                                  self.rect.y + (self.rect.height - button_text.get_height()) // 2))

class MainMenu(State):
    def __init__(self, spill):
        super().__init__(spill)
        self.UDP_PORT = 50000
        self.TIMEOUT = 4
        self.discovered_servers = []  # List of discovered server IPs
        self.selected_ip = None

        # Load images
        self.bg = pygame.image.load("images/battleship_bg.jpg")
        self.ship1 = pygame.image.load("images/battleship2.png")
        self.ship2 = pygame.image.load("images/battleship2.png")
        self.bg = pygame.transform.scale(self.bg, (self.spill.screen.get_width(), self.spill.screen.get_height()))
        self.ship2 = pygame.transform.flip(self.ship2, 1, 0)

        # Buttons
        self.host_game = Button(spill, self.spill.screen.get_width() // 2, self.spill.screen.get_height() // 2, 300, 50, "Host game")
        self.join_game = Button(spill, self.spill.screen.get_width() // 2, self.spill.screen.get_height() // 2 + 100, 300, 50, "Join game")
        self.singleplayer_game = Button(self, self.spill.screen.get_width()//2, self.spill.screen.get_height() // 2 + 200, 300, 50, "Singleplayer")

        # Start listening for servers in a separate thread
        self.running = True
        threading.Thread(target=self.listen_for_servers, daemon=True).start()

    def listen_for_servers(self):
        """ Continuously listens for server broadcasts in a separate thread. """
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        udp_sock.bind(("", self.UDP_PORT))
        udp_sock.settimeout(1)  # Prevents blocking indefinitely

        while self.running:
            try:
                data, addr = udp_sock.recvfrom(1024)
                message = data.decode()
                _, ip, _ = message.split(":")

                # Add only unique IPs
                if ip not in self.discovered_servers:
                    self.discovered_servers.append(ip)
            except socket.timeout:
                pass  # No new message, continue loop

    def draw_text(self, text: str, size: int, color: tuple, x: int, y: int):
        font = pygame.font.Font(None, size)
        info = font.render(text, True, color)
        self.spill.screen.blit(info, (x - info.get_width() // 2, y - info.get_height() // 2))


    def update(self):
        """ Handles button interaction and server selection. """
        # Change button color on hover
        self.host_game.color = (200, 200, 200) if self.host_game.rect.collidepoint(pygame.mouse.get_pos()) else (0,0,0)
        self.join_game.color = (200, 200, 200) if self.join_game.rect.collidepoint(pygame.mouse.get_pos()) else (0,0,0)
        self.singleplayer_game.color = (200, 200, 200) if self.singleplayer_game.rect.collidepoint(pygame.mouse.get_pos()) else (0,0,0)

        # Host game button click
        if self.host_game.rect.collidepoint(self.spill.pressed_actions["mouse"][1]):
            subprocess.Popen(["python", "host.py"])
            self.spill.ip = socket.gethostbyname(socket.gethostname())
            self.spill.change_state("battleship")

        # Check if any IP is clicked
        for i, ip in enumerate(self.discovered_servers):
            ip_rect = pygame.Rect(self.spill.screen.get_width() - 350, 100 + i * 40, 300, 30)
            if ip_rect.collidepoint(self.spill.pressed_actions["mouse"][1]):
                self.selected_ip = ip

        # Join game button click
        if self.join_game.rect.collidepoint(self.spill.pressed_actions["mouse"][1]) and self.selected_ip:
            self.spill.ip = self.selected_ip
            self.spill.change_state("battleship")
        
        if self.singleplayer_game.rect.collidepoint(self.spill.pressed_actions["mouse"][1]):
            self.spill.change_state("localbattleships")

    def render(self):
        """ Draws the menu, buttons, and available servers. """
        self.spill.screen.blit(self.bg, (0, 0))
        self.spill.screen.blit(self.ship1, (self.spill.screen.get_width() - self.ship1.get_width(), self.spill.screen.get_height() - self.ship1.get_height() + 50))
        self.spill.screen.blit(self.ship2, (0, self.spill.screen.get_height() - self.ship1.get_height() + 50))
        self.draw_text("Battle Ships", 100, (0, 0, 0), self.spill.screen.get_width() // 2, 100)

        # Render buttons
        self.host_game.render(self.spill.screen)
        self.join_game.render(self.spill.screen)
        self.singleplayer_game.render(self.spill.screen)

        self.draw_text("Online servers", 40, (0, 0, 0), self.spill.screen.get_width() - 200, 100)
        # Display discovered IPs
        for i, ip in enumerate(self.discovered_servers):
            color = (200, 200, 200, 100) if ip == self.selected_ip else (255, 255, 255, 100)
            # Create a transparent surface
            rect_surface = pygame.Surface((300, 30), pygame.SRCALPHA)
            rect_surface.fill(color)  # Fill with RGBA color
            # Blit the transparent surface onto the main screen
            self.spill.screen.blit(rect_surface, (self.spill.screen.get_width() - 350, 115 + i * 40))
            
            pygame.draw.rect(self.spill.screen, color, (self.spill.screen.get_width() - 350, 115 + i * 40, 300, 30), 2)
            self.draw_text(ip, 30, (0, 0, 0), self.spill.screen.get_width()-200, 130 + i * 40)
