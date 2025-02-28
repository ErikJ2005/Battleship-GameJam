import pygame, subprocess, socket
from state import State
    
class Button(State):
    def __init__(self, spill, x : int, y : int, width : int, height : int, text : str):
        super().__init__(spill)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        self.button = pygame.image.load("images/buttons.png")
        self.button = pygame.transform.scale(self.button, (width, height))
        self.rect = pygame.Rect(x-(width+4)//2, y-(height+4)//2, width+4, height+4)
        self.font = pygame.font.Font(None, height-3)
        self.text = text
        self.color = (0,0,0)
        
    def render(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        screen.blit(self.button, (self.x-self.width//2, self.y-self.height//2))
        button_text = self.font.render(self.text, True, (0, 0, 0))
        screen.blit(button_text, (self.rect.x + (self.rect.width-button_text.get_width())//2, self.rect.y + (self.rect.height-button_text.get_height())//2))

class MainMenu(State):
    def __init__(self, spill):
        super().__init__(spill)
        self.UDP_PORT = 50000
        self.TIMEOUT = 4
        self.button_height = 20
        self.button_width = 100
        self.bg = pygame.image.load("images/battleship_bg.jpg")
        self.bg = pygame.transform.scale(self.bg, (1200, 600))
        self.host_game = Button(spill, self.spill.screen.get_width()//2, self.spill.screen.get_height()//2, 300, 50, "Host game")
        self.join_game = Button(spill, self.spill.screen.get_width()//2, self.spill.screen.get_height()//2+100, 300, 50, "Join game")
        
    def start_host(self):
        with open("host.py") as f:
            exec(f.read())
            
    def draw_text(self, text : str, size : int, color : tuple, x: int, y : int):
        font  = pygame.font.Font(None, size)
        info = font.render(text, True, color)
        self.spill.screen.blit(info, (x - info.get_width() // 2,y - info.get_height() // 2))

    def update(self):
        if self.host_game.rect.collidepoint(pygame.mouse.get_pos()):
            self.host_game.color = (200,200,200)
        else:
            self.host_game.color = (0,0,0)
        if self.host_game.rect.collidepoint(self.spill.pressed_actions["mouse"][1]):
            subprocess.Popen(["python", "host.py"])
            self.spill.ip = socket.gethostbyname(socket.gethostname())
            self.spill.change_state("battleship")
            
        if self.join_game.rect.collidepoint(pygame.mouse.get_pos()):
            self.join_game.color = (200,200,200)
        else:
            self.join_game.color = (0,0,0)
        if self.join_game.rect.collidepoint(self.spill.pressed_actions["mouse"][1]):
            # Listen for UDP broadcasts
            udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            udp_sock.bind(("", self.UDP_PORT))
            
            udp_sock.settimeout(self.TIMEOUT)

            print("Waiting for server broadcast...")
            
            try:
                data, addr = udp_sock.recvfrom(1024)
                message = data.decode()
                print(f"Received: {message}")

                # Extract server IP and TCP port
                _, self.text, server_port = message.split(":")
                
                self.spill.ip = self.text
                self.spill.change_state("battleship")
            except:
                print("Couldn't connect to a server")
                self.spill.pressed_actions["mouse"][1] = (0,0)

    def render(self):
        self.spill.screen.blit(self.bg, (0,0))
        self.draw_text("Battle Ships", 100, (0,0,0), self.spill.screen.get_width()//2, 100)
        self.join_game.render(self.spill.screen)
        self.host_game.render(self.spill.screen)
        