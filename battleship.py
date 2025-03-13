import pygame
from state import State
from network import Network
from shop import Skins
import json  # Import JSON module

class Player(State):
    def __init__(self, spill, player_id):
        """ Spiller klasse som har all funksjonaliteten en spiller trenger for å kunne spille

        Args:
            spill (_type_): peker tilbake til hoved skriptet
            player_id (_type_): id til spilleren for å holde styr på hvem som er hvem
        """
        super().__init__(spill)
        self.player_id = player_id
        self.ships = []  # Liste med skipene 
        self.attacked_positions = [] # Liste med angrepene
        self.ships_placed = False  # Hålder styr på om skipene er plasert
        self.grid_size = 10
        self.cell_size = 40
        
        # Brettet til spilleren
        self.board = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        
        # Hålder styr på hvem sin tur det er
        self.my_turn = False
        
        # Finner hvor fiende brette er for at man skal kunne angripe
        self.grid_offset_x = (self.spill.screen.get_width() - (self.grid_size * self.cell_size * 2) - 40) // 2
        self.grid_offset_y = 50
        
        # Setter opp lydefekter 
        self.splash = pygame.mixer.Sound("music/splash.wav")
        self.explosion = pygame.mixer.Sound("music/explosion.wav")
        self.splash.set_volume(self.spill.miss_volume)
        self.explosion.set_volume(self.spill.hit_volume)

    def place_ship(self, board : list, x : int, y : int, orientation : str, ship_size : int) -> bool:
        """ Plasserer et skip på brettet man vil i retningen man vil og av størrelsen man vil

        Args:
            board (list): spill brettet skipet skal plaseres på
            x (int): x posisjonen til første ruten til skipet
            y (int): y posisjonen til første ruten til skipet
            orientation (str): hvilke retning skipet skal peke
            ship_size (int): størelsen på skipet

        Returns:
            bool: returnerer True hvis hvis skpet kunne bli lagt til på den posisjonen og False hvis skipet ikke kunne bli lagt til
        """
        
        if not self.ships_placed:
            if 0 <= x < 10 and 0 <= y < 10:
                new_positions = []

                if orientation == "horizontal":
                    if x + ship_size > 10:  # Korrigert sjekk
                        return False  # Skipet går utenfor brettet
                    new_positions = [(x + i, y) for i in range(ship_size)]

                elif orientation == "vertical":
                    if y + ship_size > 10:  # Korrigert sjekk
                        return False  # Skipet går utenfor brettet
                    new_positions = [(x, y + i) for i in range(ship_size)]

                # Sjekk om noen av posisjonene er opptatt
                for pos in new_positions:
                    if board[pos[1]][pos[0]] == 1:
                        return False  # Overlapping oppdaget

                # Plasser skipet
                for pos in new_positions:
                    board[pos[1]][pos[0]] = 1  # Marker cellene som skip 
                self.ships.append([new_positions, orientation])
                self.ships_placed = len(self.ships) >= 5  # Sjekk om alle skip er plassert
                return True
            
        return False
    
    def attack(self, enemy_board : list):
        """ henter x og y kordinatet til musen og angriper ruten man valgte på brettet man har lagt inn

        Args:
            enemy_board (list): brettet man vil angripe
        """

        x, y = self.spill.pressed_actions["mouse"][1]
        grid_x, grid_y = (x - self.grid_offset_x - (self.grid_size * self.cell_size + 40)) // self.cell_size, (y - self.grid_offset_y) // self.cell_size

        # Sjekk at spilleren kun angriper motstanderens brett
        if 0 <= grid_x < self.grid_size and 0 <= grid_y < self.grid_size:
            if [grid_x, grid_y] not in self.attacked_positions:
                self.attacked_positions.append([grid_x, grid_y])
                
                if enemy_board[grid_y][grid_x] == 1:  # Treffer et skip
                    self.explosion.play()
                    enemy_board[grid_y][grid_x] = 2  # Marker som truffet
                else:
                    self.splash.play()
                    enemy_board[grid_y][grid_x] = 3  # Marker som bom 
                self.my_turn = False
    
    def all_ships_sunk(self) -> bool:
        """ Sjekker om alle skip har sunket
        Returns:
            bool: returnerer True hvis alle skip har sunket og ellers False
        """
        # sjekker om alle skip har sunket
        for row in self.board:
            if 1 in row:
                return False
        return True
    
class BattleShips(State):
    def __init__(self, spill, nettworking : bool):
        """ Hoved spillet som er det som blir kjørt når man spiller

        Args:
            spill (_type_): peker mot hoved scriptet
            nettworking (_type_): Sier om man skal bruke netverk eller ikke så man kan gjenbruke koden hvis man vil lage en singleplayer versjon
        """
        super().__init__(spill)
        # Alle bildene som blir brukt
        self.bg = pygame.image.load("images/battleship_bg.jpg")
        self.hit_image = pygame.image.load("images/hit.png")
        self.miss_image = pygame.image.load("images/miss.png")

        self.skins = Skins(spill, 0)
        
        self.ship_image = self.skins.items[self.skins.owned_items[0][1]][0]
            
        # Setter opp lydeffekter
        self.splash = pygame.mixer.Sound("music/splash.wav")
        self.explosion = pygame.mixer.Sound("music/explosion.wav")
        self.splash.set_volume(self.spill.miss_volume)
        self.explosion.set_volume(self.spill.hit_volume)
        
        self.bg = pygame.transform.scale(self.bg, (self.spill.screen.get_width(), self.spill.screen.get_height()))
        self.font = pygame.font.Font(None, 24)
        
        # Setter opp netverk og kobler til riktig ip
        if nettworking:
            self.net = None
            try:
                self.net = Network(self.spill.ip)   
            except:
                if hasattr(self.spill, "states"):
                    self.spill.change_state("mainmenu")  
                    return  
            
            if self.net:  
                self.player = Player(spill, int(self.net.id))
                self.player2 = Player(spill, 1 - int(self.net.id))
            else:
                self.player = None  
            
            self.received_ships = []
            
            self.game_ready = False
            self.loaded_ships = False
            
            self.text_turn = ""

        self.grid_size = 10
        self.cell_size = 40
        
        # Finner hvor fiende brette skal tegnes
        self.grid_offset_x = (self.spill.screen.get_width() - (self.grid_size * self.cell_size * 2) - 40) // 2
        self.grid_offset_y = 50
        
        self.attack_phase = False 
        
        # Skip informasjon
        self.ship_sizes = [2, 3, 3, 4, 5] 
        self.orientation = "horizontal" 
        self.ship_index = 0  
        self.ship_sunk = 0
        
    def send_data(self, ships : list, attacks : list) -> str:
        """ Sender og motar data fre serveren

        Args:
            ships (list): Liste med kordinaten tol skipene og vilken vei de peker
            attacks (list): Liste med hvor du har angrepet

        Returns:
            str: motar en string som ineholder all data fra motstander
        """
        try:
            ships_str = json.dumps(ships)
            attacks_str = json.dumps(attacks)  
            
            ships_placed = len(self.player.ships) == 5
            data_str = f"{self.player.player_id}:True:{ships_str}:{ships_placed}:{attacks_str}:0"
            reply = self.net.send(data_str)
            return reply
        except Exception as e:
            print(f"Error sending data: {e}")
            return None 
        
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
        
    def ships_sunk(self, received_ships : list):
        """ Sjekker hvor mange skip som har sunket ved å sjekke om alle kordinatene til et skip har blitt fjernet fra en del av listen

        Args:
            received_ships (list): skipene på motstander brettet 
        """
        for index , ships in enumerate(received_ships):
            for attacks in self.player.attacked_positions:
                if attacks in ships[0]:
                    ships[0].remove(attacks)
            if len(ships[0]) == 0:
                self.ship_sunk += 1
                self.received_ships.pop(index)
                
    def update(self):
        try:
            # Endrer seg når r blir trykket
            self.orientation = self.spill.pressed_actions["rotate"]

            # Mottar og sender data
            received_data = self.send_data(self.player.ships, self.player.attacked_positions)
            
            # splitter opp data-en for at den skal kunne brukes
            data_parts = received_data.split(":")
            
            # Sjekker hvem sin tur det er som blir styrt av serveren
            if data_parts[5] == f"{self.player.player_id}":
                self.player.my_turn = True
            else:
                self.player.my_turn = False

            # Plassering av skip
            if data_parts[1] == "True":
                self.game_ready = True
                if self.spill.pressed_actions["mouse"][0] and len(self.player.ships) < 5:
                    x, y = self.spill.pressed_actions["mouse"][1]
                    grid_x, grid_y = (x - self.grid_offset_x) // self.cell_size, (y - self.grid_offset_y) // self.cell_size
                    
                    if self.player.place_ship(self.player.board, grid_x, grid_y, self.orientation, self.ship_sizes[self.ship_index]):
                        self.splash.play()
                        self.ship_index += 1
                        
                    self.spill.pressed_actions["mouse"][0] = False
            
            # Angriper motstanderens brett
            if self.player.my_turn:
                self.text_turn = "Attack the other player board"
                if self.spill.pressed_actions["mouse"][0] and self.loaded_ships:
                    self.player.attack(self.player2.board)
                    self.spill.pressed_actions["mouse"][0] = False
            else:
                self.text_turn = "Don't get hit!"
                
            # Laster inn alle skip som motstanderen har plassert
            if data_parts[3] == "True" and not self.loaded_ships and len(self.player.ships) == 5:
                self.loaded_ships = True
                self.attack_phase = True
                self.received_ships = json.loads(data_parts[2])
                for i in range(5):
                    self.player2.place_ship(self.player2.board, self.received_ships[i][0][0][0], self.received_ships[i][0][0][1], self.received_ships[i][1], self.ship_sizes[i])
            
            # Motar posisjonene hvor motstanderen har angrepet
            received_attacks = json.loads(data_parts[4])  
            
            for attacks in received_attacks:
                y, x = attacks
                if self.player.board[x][y] == 0:
                    self.splash.play()
                    self.player.board[x][y] = 3
                elif self.player.board[x][y] == 1:
                    self.explosion.play()
                    self.player.board[x][y] = 2
            
            # Sjekker hvor mange skip som har sunket
            self.ships_sunk(self.received_ships)

            # Sjekker om alle skip er senket på ett av brettene
            if self.player.all_ships_sunk() and self.loaded_ships:
                self.send_data(self.player.ships, self.player.attacked_positions)
                self.net.disconnect()
                self.spill.change_state("endscreen")
                self.spill.winner = "You lost!"
            if self.player2.all_ships_sunk() and self.loaded_ships:
                self.send_data(self.player.ships, self.player.attacked_positions)
                self.net.disconnect()
                self.skins.coins += 5
                self.skins.update()
                self.spill.change_state("endscreen")
                self.spill.winner = "You Won!"
                
            if self.spill.disconnect == True:
                self.net.disconnect()
                self.spill.disconnect = False
                self.spill.change_state("mainmenu")

        except Exception as e:
            print(f"Error handling data: {data_parts}") # Printer ut error meldingen hvis man motar data koden ikke kan håndtere

    def get_hovered_cells(self, mouse_x : int, mouse_y  : int) -> list:
        """ finner ut hvilke ruter som skal markers

        Args:
            mouse_x (int): x posisjon til musen
            mouse_y (int): y posisjonen til musen

        Returns:
            list: kordinatene hvor rutene skal markeres
        """
        # Så lenge spillet ikke er klart returnerer den bare en tm liste
        if not self.game_ready or self.attack_phase or self.ship_index >= len(self.ship_sizes):
            return []

        # Finenr cellen musen er i
        grid_x = (mouse_x - self.grid_offset_x) // self.cell_size
        grid_y = (mouse_y - self.grid_offset_y) // self.cell_size

        # Sjekker at den er innenfor
        if 0 <= grid_x < self.grid_size and 0 <= grid_y < self.grid_size:
            ship_size = self.ship_sizes[self.ship_index] # Finner størelsen til skipet man skal plasere
            
            # Sjekker retningen til skipet og returnerer listen med alle kordinatene skipet vil dekke
            if self.orientation == "horizontal":
                if grid_x + ship_size <= self.grid_size:
                    return [(grid_x + i, grid_y) for i in range(ship_size)]
            elif self.orientation == "vertical":
                if grid_y + ship_size <= self.grid_size:
                    return [(grid_x, grid_y + i) for i in range(ship_size)]
        return []

    def render(self):
        # Tegner bakgrunnen
        self.bg = pygame.transform.scale(self.bg, (self.spill.screen.get_width(), self.spill.screen.get_height()))
        self.spill.screen.blit(self.bg, (0, 0))
        
        # Finner cellene som skal markeres
        mouse_x, mouse_y = pygame.mouse.get_pos()
        hovered_cells = self.get_hovered_cells(mouse_x, mouse_y)
        
        # Tegner brettet til spilleren
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                cell_x = self.grid_offset_x + (x * self.cell_size)
                cell_y = self.grid_offset_y + (y * self.cell_size)
                
                pygame.draw.rect(self.spill.screen, (0, 0, 0), (cell_x, cell_y, self.cell_size, self.cell_size), 1)
        
        # Tegner skipene til spilleren
        for ship in self.player.ships:
            positions, orientation = ship
            first_x, first_y = positions[0]

            ship_width = self.cell_size * len(positions)
            ship_height = ship_width // 5

            ship_image = pygame.transform.scale(self.ship_image, (ship_width, ship_height))

            if orientation == "vertical":
                ship_image = pygame.transform.rotate(ship_image, -90)
                
            cell_x = self.grid_offset_x + (first_x * self.cell_size) + ((self.cell_size - ship_height) // 2 if orientation == "vertical" else 0)
            cell_y = self.grid_offset_y + (first_y * self.cell_size) + ((self.cell_size - ship_height) // 2 if orientation == "horizontal" else 0)

            self.spill.screen.blit(ship_image, (cell_x, cell_y))
        
        # Tegner hvor noen har skutt og brettet til motstander
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                cell_x = self.grid_offset_x + (x * self.cell_size)
                cell_y = self.grid_offset_y + (y * self.cell_size)
                
                hit_image = pygame.transform.scale(self.hit_image, (self.cell_size - 8, self.cell_size - 8))
                miss_image = pygame.transform.scale(self.miss_image, (self.cell_size - 8, self.cell_size - 8))
                
                if self.player.board[y][x] == 2:
                    self.spill.screen.blit(hit_image, (cell_x + 4, cell_y + 4))
                if self.player.board[y][x] == 3:
                    self.spill.screen.blit(miss_image, (cell_x + 4, cell_y + 4))

                enemy_x = self.grid_offset_x + self.grid_size * self.cell_size + 40 + (x * self.cell_size)
                
                if self.player2.board[y][x] == 2:
                    self.spill.screen.blit(hit_image, (enemy_x + 4, cell_y + 4))
                if self.player2.board[y][x] == 3:
                    self.spill.screen.blit(miss_image, (enemy_x + 4, cell_y + 4))
                pygame.draw.rect(self.spill.screen, (0, 0, 0), (enemy_x, cell_y, self.cell_size, self.cell_size), 1)

        # Tegner rutene som skipe vil dekke når det blir plassert
        if hovered_cells:
            for (x, y) in hovered_cells:
                cell_x = self.grid_offset_x + (x * self.cell_size)
                cell_y = self.grid_offset_y + (y * self.cell_size)
                overlay = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
                overlay.fill((150, 150, 150, 128))
                self.spill.screen.blit(overlay, (cell_x, cell_y))
                
        # Skriver ut all tekst på skjermen
        if not self.game_ready:
            text = "Waiting for opponent..."
            self.draw_text(text, self.spill.screen.get_height()//8, (0, 0, 0), self.spill.screen.get_width() // 2, self.spill.screen.get_height() - self.spill.screen.get_height()//15)
        elif not self.attack_phase:
            text = "Place your ships! Press 'R' to rotate the ship"
            self.draw_text(text, self.spill.screen.get_height()//20, (0, 0, 0), self.spill.screen.get_width() // 2, self.spill.screen.get_height() - self.spill.screen.get_height()//15)
        else:
            text = "Time to battle!!"
            self.draw_text(text, self.spill.screen.get_height()//8, (0, 0, 0), self.spill.screen.get_width() // 2, self.spill.screen.get_height() - self.spill.screen.get_height()//15)
        
        if not self.attack_phase:
            self.draw_text(self.spill.pressed_actions["rotate"] if len(self.player.ships) < 5 else "You have placed all your ships", self.spill.screen.get_height()//15, (0, 0, 0), self.spill.screen.get_width() // 2 - self.cell_size * 5 - self.cell_size // 2, self.spill.screen.get_height() - self.spill.screen.get_height()//5)
        else:
            self.draw_text(self.text_turn, self.spill.screen.get_height()//15, (0, 0, 0), self.spill.screen.get_width() // 2 - self.cell_size * 5 - self.cell_size // 2, self.spill.screen.get_height() - 120)    
        
        self.draw_text(f"ships sunk: {self.ship_sunk}", self.spill.screen.get_height()//12, (0, 0, 0), self.spill.screen.get_width() // 2, self.spill.screen.get_height()//20)
        
        if self.player.player_id == 0:
            self.draw_text(f"Join ip: {self.spill.ip}", self.spill.screen.get_height()//15, (0, 0, 0), self.spill.screen.get_width()//6, self.spill.screen.get_height()//30)
