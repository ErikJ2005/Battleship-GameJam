import pygame
from state import State
from network import Network
import json  # Import JSON module

class Player(State):
    def __init__(self, spill, player_id):
        super().__init__(spill)
        self.player_id = player_id
        self.ships = []  # List of ships with position, size, and health
        self.attacked_positions = []
        self.good_attacks = []
        self.ships_placed = False  # Track if the player has placed all ships
        self.grid_size = 10
        self.cell_size = 40
        
        self.board = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        
        self.my_turn = False
        
        self.grid_offset_x = (self.spill.screen.get_width() - (self.grid_size * self.cell_size * 2) - 40) // 2
        self.grid_offset_y = 50

    def place_ship(self, board, x, y, orientation, ship_size):
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
    
    def attack(self, enemy_board):
        x, y = self.spill.pressed_actions["mouse"][1]
        grid_x, grid_y = (x - self.grid_offset_x - (self.grid_size * self.cell_size + 40)) // self.cell_size, (y - self.grid_offset_y) // self.cell_size

        # Sjekk at spilleren kun angriper motstanderens brett
        if 0 <= grid_x < self.grid_size and 0 <= grid_y < self.grid_size:
            if [grid_x, grid_y] not in self.attacked_positions:
                self.attacked_positions.append([grid_x, grid_y])
                
                if enemy_board[grid_y][grid_x] == 1:  # Treffer et skip
                    enemy_board[grid_y][grid_x] = 2  # Marker som truffet
                else:
                    enemy_board[grid_y][grid_x] = 3  # Marker som bom 
                self.my_turn = False
    
    def all_ships_sunk(self):
        # sjekker om alle skip har sunket
        for row in self.board:
            if 1 in row:
                return False
        return True
    
class BattleShips(State):
    def __init__(self, spill, networking):
        super().__init__(spill)
        self.bg = pygame.image.load("images/battleship_bg.jpg")
        self.ship_image = pygame.image.load("images/ship.png")
        self.hit_image = pygame.image.load("images/hit.png")
        self.miss_image = pygame.image.load("images/miss.png")
        
        self.bg = pygame.transform.scale(self.bg, (1200, 600))
        self.font = pygame.font.Font(None, 24)
        
        if networking:
            self.net = None
            try:
                self.net = Network(self.spill.ip)   
            except:
                if hasattr(self.spill, "states"):
                    self.spill.change_state("mainmenu")  
                    return  
            
            if self.net:  
                self.player = Player(spill,int(self.net.id))
                self.player2 = Player(spill,1-int(self.net.id))
            else:
                self.player = None  
            
            self.received_ships = []
            
            self.game_ready = False # Er True hvis to spillere har blitt med
            self.loaded_ships = False # Er True når alle skipene er plassert
            
            self.text_turn = "" # Sier hvem sin tur det er

        self.grid_size = 10
        self.cell_size = 40
        
        self.grid_offset_x = (self.spill.screen.get_width() - (self.grid_size * self.cell_size * 2) - 40) // 2
        self.grid_offset_y = 50
        
        self.attack_phase = False 
        
        self.ship_sizes = [2, 3, 3, 4, 5] 
        self.orientation = "horizontal" 
        self.ship_index = 0  
        self.ship_sunk = 0
        
    def send_data(self, ships, attacks):
        try:
            ships_str = json.dumps(ships)
            attacks_str = json.dumps(attacks)  
            
            ships_placed = len(self.player.ships) == 5
            data_str = f"{self.player.player_id}:True:{ships_str}:{ships_placed}:{attacks_str}:0"
            reply = self.net.send(data_str)
            return reply
        except Exception as e:
            print(f"Error sending data: {e}")
            
        
    def draw_text(self, text : str, size : int, color : tuple, x, y):
        font  = pygame.font.Font(None, size)
        info = font.render(text, True, color)
        self.spill.screen.blit(info, (x - info.get_width() // 2,y - info.get_height() // 2))
        
    def ships_sunk(self, received_ships):
        # sjekk hvor mange skip har sunket
        for index , ships in enumerate(received_ships):
            for attacks in self.player.attacked_positions:
                if attacks in ships[0]:
                    ships[0].remove(attacks)
            if len(ships[0]) == 0:
                self.ship_sunk += 1
                self.received_ships.pop(index)
                
    def update(self):
        try:
            # Update orientation when "R" is pressed
            if self.spill.pressed_actions["key"][0] and self.spill.pressed_actions["key"][1] == "r":
                if self.orientation == "horizontal":
                    self.orientation = "vertical"
                else:
                    self.orientation = "horizontal"
                self.spill.pressed_actions["key"] = [False, ""]  # Reset key press

            received_data = self.send_data(self.player.ships, self.player.attacked_positions)
            
            data_parts = received_data.split(":")
            
            if data_parts[5] == f"{self.player.player_id}":
                self.player.my_turn = True
            else:
                self.player.my_turn = False

            # plassering av skip
            if data_parts[1] == "True":
                self.game_ready = True
                if self.spill.pressed_actions["mouse"][0] and len(self.player.ships) < 5:
                    x, y = self.spill.pressed_actions["mouse"][1]
                    grid_x, grid_y = (x - self.grid_offset_x) // self.cell_size, (y - self.grid_offset_y) // self.cell_size
                    self.spill.pressed_actions["mouse"][0] = False
                    
                    if self.player.place_ship(self.player.board, grid_x, grid_y, self.orientation, self.ship_sizes[self.ship_index]):
                        self.ship_index += 1  # Gå videre til neste skip
                        
                    else:
                        print("Kan ikke plassere skipet her!") 
            
            # Håndter angrep
            if self.player.my_turn:
                self.text_turn = "Attack the other player board"
                if self.spill.pressed_actions["mouse"][0] and self.loaded_ships:
                    self.player.attack(self.player2.board)
                    self.spill.pressed_actions["mouse"][0] = False  # Nullstill klikk
            else:
                self.spill.pressed_actions["mouse"][1] = (0, 0)
                self.text_turn = "Hope the oponent doesn't hit you"
                
            # sjekker om alle ships er plasert og laster in alle motstander skip en gang
            if data_parts[3] == "True" and not self.loaded_ships and len(self.player.ships) == 5:
                self.loaded_ships = True
                self.attack_phase = True
                print("ships placed")
                self.received_ships = json.loads(data_parts[2])  # Convert JSON string back to list
                for i in range(5):
                    self.player2.place_ship(self.player2.board, self.received_ships[i][0][0][0], self.received_ships[i][0][0][1], self.received_ships[i][1],self.ship_sizes[i])
                
            received_attacks = json.loads(data_parts[4])  
            
            # Sjekker hva motstanderen traff
            for attacks in received_attacks:
                y, x = attacks
                if self.player.board[x][y] == 0:
                    self.player.board[x][y] = 3
                elif self.player.board[x][y] == 1:
                    self.player.board[x][y] = 2
                    
            self.ships_sunk(self.received_ships)

            # Sjekker om en spiller har vunnet
            if self.player.all_ships_sunk() and self.loaded_ships:
                self.send_data(self.player.ships, self.player.attacked_positions)
                self.net.disconnect()
                self.spill.change_state("endscreen")
                self.spill.winner = "You lost!"
            if self.player2.all_ships_sunk() and self.loaded_ships:
                self.send_data(self.player.ships, self.player.attacked_positions)
                self.net.disconnect()
                self.spill.change_state("endscreen")
                self.spill.winner = "You Won!"

        except Exception as e:
            print(f"Error handling data: {data_parts}")

    def get_hovered_cells(self, mouse_x, mouse_y):
        """Calculate the cells that the ship will occupy based on the mouse position."""
        if not self.game_ready or self.attack_phase or self.ship_index >= len(self.ship_sizes):
            return []

        grid_x = (mouse_x - self.grid_offset_x) // self.cell_size
        grid_y = (mouse_y - self.grid_offset_y) // self.cell_size

        if 0 <= grid_x < self.grid_size and 0 <= grid_y < self.grid_size:
            ship_size = self.ship_sizes[self.ship_index]
            if self.orientation == "horizontal":
                if grid_x + ship_size <= self.grid_size:
                    return [(grid_x + i, grid_y) for i in range(ship_size)]
            elif self.orientation == "vertical":
                if grid_y + ship_size <= self.grid_size:
                    return [(grid_x, grid_y + i) for i in range(ship_size)]
        return []

    def render(self):
        self.spill.screen.blit(self.bg, (0, 0))
        
        # Get mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Calculate hovered cells using the current orientation
        hovered_cells = self.get_hovered_cells(mouse_x, mouse_y)
        
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                cell_x = self.grid_offset_x + (x * self.cell_size)
                cell_y = self.grid_offset_y + (y * self.cell_size)
                
                pygame.draw.rect(self.spill.screen, (0, 0, 0), (cell_x, cell_y, self.cell_size, self.cell_size), 1)
                
        for ship in self.player.ships:
            positions, orientation = ship
            first_x, first_y = positions[0]

            # Skalér bildet for å dekke hele skipet
            ship_width = self.cell_size * len(positions)
            ship_height = ship_width//5

            ship_image = pygame.transform.scale(self.ship_image, (ship_width, ship_height))

            # Roter bildet hvis nødvendig
            if orientation == "vertical":
                ship_image = pygame.transform.rotate(ship_image, 90)
                
            # Beregn posisjon på skjermen
            cell_x = self.grid_offset_x + (first_x * self.cell_size) + ((self.cell_size-ship_height)//2 if orientation == "vertical" else 0)
            cell_y = self.grid_offset_y + (first_y * self.cell_size) + ((self.cell_size-ship_height)//2 if orientation == "horizontal" else 0)

            if orientation == "vertical":
                self.spill.screen.blit(ship_image, (cell_x, cell_y))
            if orientation == "horizontal":
                self.spill.screen.blit(ship_image, (cell_x, cell_y))
        
        # Print brettene
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                cell_x = self.grid_offset_x + (x * self.cell_size)
                cell_y = self.grid_offset_y + (y * self.cell_size)
                
                hit_image = pygame.transform.scale(self.hit_image, (self.cell_size-8, self.cell_size-8))
                miss_image = pygame.transform.scale(self.miss_image, (self.cell_size-8, self.cell_size-8))
                
                # Tegn spillerens rutenett
                if self.player.board[y][x] == 2:
                    self.spill.screen.blit(hit_image, (cell_x+4, cell_y+4))
                if self.player.board[y][x] == 3:
                    self.spill.screen.blit(miss_image, (cell_x+4, cell_y+4))

                # Tegn fiendens rutenett
                enemy_x = self.grid_offset_x + self.grid_size * self.cell_size + 40 + (x * self.cell_size)
                
                if self.player2.board[y][x] == 2:
                    self.spill.screen.blit(hit_image, (enemy_x+4, cell_y+4))
                if self.player2.board[y][x] == 3:
                    self.spill.screen.blit(miss_image, (enemy_x+4, cell_y+4))
                pygame.draw.rect(self.spill.screen, (0, 0, 0), (enemy_x, cell_y, self.cell_size, self.cell_size), 1)

        # Tegner rutene skipet vil bli plassert
        if hovered_cells:
            for (x, y) in hovered_cells:
                cell_x = self.grid_offset_x + (x * self.cell_size)
                cell_y = self.grid_offset_y + (y * self.cell_size)
                overlay = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
                overlay.fill((150, 150, 150, 128))  # gjennomsiktig grå farge
                self.spill.screen.blit(overlay, (cell_x, cell_y))

        # Status meldinger
        if not self.game_ready:
            text = "Waiting for opponent..."
            self.draw_text(text, 70, (0, 0, 0), self.spill.screen.get_width() // 2, self.spill.screen.get_height() - 40)
        elif not self.attack_phase:
            text = "Place your ships! Press 'R' to rotate. sizes of the ships you place are: [2, 3, 3, 4, 5] in that order "
            self.draw_text(text, 30, (0, 0, 0), self.spill.screen.get_width() // 2, self.spill.screen.get_height() - 40)
        else:
            text = "Time to battle!!"
            self.draw_text(text, 70, (0, 0, 0), self.spill.screen.get_width() // 2, self.spill.screen.get_height() - 40)
        
        # Info text
        if not self.attack_phase:
            self.draw_text(self.spill.pressed_actions["rotate"] if len(self.player.ships) < 5 else "You have placed all your ships", 40, (0, 0, 0), self.spill.screen.get_width() // 2 - self.cell_size * 5 - self.cell_size // 2, self.spill.screen.get_height() - 120)
        else:
            self.draw_text(self.text_turn, 40, (0, 0, 0), self.spill.screen.get_width() // 2 - self.cell_size * 5 - self.cell_size // 2, self.spill.screen.get_height() - 120)    
        
        self.draw_text(f"ships sunk: {self.ship_sunk}", 50, (0, 0, 0), self.spill.screen.get_width() // 2, 30)
        
        if self.player.player_id == 0:
            self.draw_text(f"Join ip: {self.spill.ip}", 40, (0,0,0), 150, 20)