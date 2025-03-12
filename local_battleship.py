# https://github.com/Ex1118/Battleship-GameJam.git

# git config --global user.email "andreas.sanila@icloud.com"

# Dette skal gjøre det mulig å kjøre spillet som en .exe fil:

# Step 1: Installer pyinstaller
# pip install pyinstaller

# Step 2: Naviger til mappen hvor main.py ligger
# cd "C:\Path\To\Your\Project"

# Step 3: Kjør kommandoen under for å lage en .exe fil
# pyinstaller --onefile main.py


from battleship import Player, BattleShips
import random
import pygame
import json
import time


class Bot(Player):
    """
    En Bot med navn: Grik-Alpha-Sigma-13-21
    Opprinnelse: Fra romstasjonen Omnikron-3-Beta
    
    Hovedmål: Bip Bop
    
    Sidemål: Dorf
    
    Hobby: Ser på profesjonell Gleep-Glorp-Zoop og heier på Worf
    
    Jobb: Rommer kanonene på romstasjonen Omnikron-3-Beta
    """
    
    def __init__(self, spill):
        """
        Her er variabler.

        Args:
            spill (main): Den karakteren du spiller mest av alle i et spill.
        """
        super().__init__(spill,1)
        self.destroyed_ships = 0
        self.good_attacks = []
        self.focus = 0
        self.battle_info = [[]]
        self.battle_focus = False

        self.splash = pygame.mixer.Sound("music/splash.wav")
        self.explosion = pygame.mixer.Sound("music/explosion.wav")
        self.splash.set_volume(self.spill.miss_volume)
        self.explosion.set_volume(self.spill.hit_volume)


    def place_ships(self,board: list, ship_sizes: list):
        """
        Plaserer skip.

        Args:
            board (list): Brettet som den plasserer skipene på
            ship_sizes (list): Størrelsen på skipene som blir plassert
        """
        
        i = 0
        while len(self.ships) < len(ship_sizes):
            if self.place_ship(board, random.randint(0, 9), random.randint(0, 9), random.choice(["horizontal", "vertical"]), ship_sizes[i]):
                i += 1

    def best_attack_location(self, defender: Player):
        shot_lock = True
        empty_pos = []

        for len_focus in range(len(self.battle_info[-2])):
            if self.battle_info[-2][len_focus] == -1:
                length = self.battle_info[2][len_focus]

        for x_pos in range(len(defender.board)):
            for y_pos in range(len(defender.board[x_pos])):
                if [x_pos, y_pos] not in self.attacked_positions:
                    empty_pos.append([x_pos,y_pos])
        while shot_lock:
            shot = empty_pos[random.randint(0,len(empty_pos)-1)]
            shot_copy = json.loads(json.dumps(shot))
            for rotasjon in range(2):
                for xy in range(length):
                    if shot in self.attacked_positions:
                        shot = json.loads(json.dumps(shot_copy))
                        break 
                    else:
                        if shot_copy[rotasjon] < length:
                            shot[rotasjon] += 1
                        elif shot_copy[rotasjon] >= length:
                            shot[rotasjon] -= 1
                        if shot[rotasjon] == shot_copy[rotasjon] - length+1:
                            shot_lock = False
                            shot[rotasjon] += random.randint(0,length-1)
                            return shot
                        elif shot[rotasjon] == shot_copy[rotasjon] + length-1:
                            shot_lock = False
                            shot[rotasjon] -= random.randint(0,length-1)
                            return shot

                shot = json.loads(json.dumps(shot_copy))
        return shot_copy


    def attack_algorithm(self, z: list, xy_cords: bool, xy_value: int):
        """
        Dette er angrepsalgoritmen som går dersom det er fokus på et skip.
        
        Brukes denne i praksis kommer allierte skip til å synke før fiendens...

        Args:
            z (list): Kordinatene som skal bli skjekket.
            xy_cords (bool): Skrur av og på muligheten om å styre hvilken akse som skal skjekkes eller ikke.
            xy_value (int): Hvis xy_cords er True så bestemmer denne variablen hvilken akse som skal skjekkes.

        Returns:
            list: Angrepskordinatene dersom den finner det med en True/False value der true betyr at kordinatene ikke er angrepskordinater ellers er det angrepskordinater.
        """
        
        battle_info = json.loads(json.dumps(z))
        shot_lock = True
        if random.randint(0,1) == 0:
            start_index = 0
            end_index = 2
            increase = 1
        else:
            start_index = 1
            end_index = -1
            increase = -1
        
        for xy in range(start_index,end_index,increase):
            if not xy_cords:
                xy_change = xy
            else:
                xy_change = xy_value

            start_value = -1
            end_value = 3
            if z[xy_change] == 0:
                start_value = 1
            elif z[xy_change] == 9:
                end_value = 1
                    
            for amount_pos in range(start_value, end_value,3):
                z[xy_change] += amount_pos
                if z not in self.attacked_positions and shot_lock:
                    grid_x, grid_y = z
                    shot_lock = False
            z = battle_info
        if shot_lock == False:
            return [grid_x, grid_y], shot_lock
        else:
            return z, shot_lock
        

    def attack(self, local_battleships, defender: Player):
        """
        Angrepsmetoden til Bot
        Warning: IKKE MENT TIL Å BRUKES PÅ ORDENTLIG!!

        Args:
            local_battleships (LocalBattleships): importerer local_battleships for å kunne bruke dens good_attack_checker() metode.
            defender (Player): Klassen til spilleren med hensikt i å bruke boardet til spilleren og good_attack_checker().

        Returns:
            int: Denne verdien beskriver om den traff vann, et skip eller om den ikke traff noe.
        """
        if local_battleships.all_ships_sunk(defender.board):
            attack_value = 3
        else:
            attack_value = -1
            self.battle_info = local_battleships.good_attack_checker(self, defender)
            battle_info = json.loads(json.dumps(self.battle_info))
            shot_lock = True

            # Bot ser om den har noen skip som den har truffet men ikke ødelagt
            for i in range(len(battle_info[-1])):
                if len(battle_info[-1][i]) > 0 and len(battle_info[-1][i]) < battle_info[2][i]:
                    self.focus = i
                    self.battle_focus = True
                    break
                        
                if self.battle_focus:
                    if len(battle_info[-1][self.focus]) == battle_info[2][self.focus]:
                        self.battle_focus = False
            
            # Hvis et skip er truffet, men ikke ødelagt så fokuserer den på skipet
            if self.battle_focus:
                for i in range(len(battle_info[-1][self.focus])):
                    z = json.loads(json.dumps(battle_info[-1][self.focus][i]))
                    if len(battle_info[-1][self.focus]) < 2:
                        z, shot_lock = self.attack_algorithm(z, False, 0)
                        if not shot_lock:
                            grid_x, grid_y  = z
                    else:
                        direction_start = json.loads(json.dumps(battle_info[-1][self.focus][0]))
                        direction_end = json.loads(json.dumps(battle_info[-1][self.focus][i]))
                        if direction_start == direction_end:
                            direction_end = json.loads(json.dumps(battle_info[-1][self.focus][i+1]))
                        if direction_start[0] == direction_end[0]:
                            xy = 1

                        elif direction_start[1] == direction_end[1]:
                            xy = 0

                        z, shot_lock = self.attack_algorithm(z, True, xy)
                        if not shot_lock:
                            grid_x, grid_y = z
            else:
                grid_x, grid_y = self.best_attack_location(defender)
                        
            # Sjekker om et skuddet treffer på et nytt sted og om den treffer/bommer skuddet
            if 0 <= grid_x < self.grid_size and 0 <= grid_y < self.grid_size:
                if [grid_x, grid_y] not in self.attacked_positions:
                    self.attacked_positions.append([grid_x, grid_y])
                        
                    if defender.board[grid_y][grid_x] == 0:
                        defender.board[grid_y][grid_x] = 3
                        attack_value = 3
                        self.splash.play()
            
                    if defender.board[grid_y][grid_x] == 1:
                        defender.board[grid_y][grid_x] = 2
                        attack_value = 2
                        self.explosion.play()
            
            # Hvis det er et nytt skudd legger programmet til et 1 sek delay   
            if attack_value == 2 or attack_value == 3:
                local_battleships.render()
                time.sleep(0.8)
                        
        return attack_value
                            
                        

class LocalBattleships(BattleShips):
    def __init__(self, spill):
        """
        Flere variabler.

        Args:
            spill (main): Den karakteren i alle filmer og spill som de fleste liker best alltid.
        """
        super().__init__(spill,False)
        self.player = Player(spill,0)
        self.player.destroyed_ships = 0
        self.player.good_attacks = []
        self.player2 = Bot(spill)
        self.player2.place_ships(self.player2.board, self.ship_sizes)
        self.player2.ship_sizes = self.ship_sizes
        self.game_ready = True
        self.player.my_turn = True
        self.loaded_ships = False
        self.battleship_attack = False
        self.destroyed_ships = 0

        self.splash = pygame.mixer.Sound("music/splash.wav")
        self.explosion = pygame.mixer.Sound("music/explosion.wav")
        self.splash.set_volume(self.spill.miss_volume)
        self.explosion.set_volume(self.spill.hit_volume)


    def good_attack_checker(self, attacker: Player, defender: Player):
        """
        Sjekker om data om angreperen har et bra angrep og legger det i en liste.
        
        Denne metoden returnerer også en liste med data som hvor mange skip angriperen har sunket, 
        hvilket player som ble truffet, hvilket størrelse de forskjellige kipene har, indeksen til de 
        forskjellige kipstypene og punktene som du har truffet på de skipene sortert i hvilket skip du traff.
        

        Args:
            attacker (Player): Angriperen
            defender (Player): Beskyttern

        Returns:
            list: En liste med mye data. Da blir Sam Altman glad :).
        """
        ship_sunk = 0
        ship_attack_pos = []
        ship_size_pos = []
        ship_sunk_index = []
        local_defender = json.loads(json.dumps(defender.ships))
        for battleship in range(len(local_defender)):
            ship_size_pos.append(len(local_defender[battleship][0]))
            ship_attack_pos.append([])
            for attack in attacker.attacked_positions:
                if attack in local_defender[battleship][0]:
                    ship_attack_pos[battleship].append(attack)
                    local_defender[battleship][0].remove(attack)
                    if attack not in attacker.good_attacks:
                        attacker.good_attacks.append(attack)
                           
            if len(local_defender[battleship][0]) == 0:
                ship_sunk_index.append(battleship)
                ship_sunk += 1
            else:
                ship_sunk_index.append(-1)
        return [ship_sunk, json.loads(json.dumps(defender.player_id)), ship_size_pos, ship_sunk_index, ship_attack_pos]
    
    def all_ships_sunk(self, board) -> bool:
        """ Sjekker om alle skip har sunket
        Returns:
            bool: returnerer True hvis alle skip har sunket og ellers False
        """
        # sjekker om alle skip har sunket
        for row in board:
            if 1 in row:
                return False
        return True


    def update(self):
        """
        Update loopen med alt som skjer inni.
        
        Tips: Skru av hjemmekameraet ditt ellers vil Jeff Bazos se in i sjelen din...
        """
        self.orientation = self.spill.pressed_actions["rotate"]
        
        # plassering av skip
        if self.spill.pressed_actions["mouse"][0] and len(self.player.ships) < 5:
            x, y = self.spill.pressed_actions["mouse"][1]
            grid_x, grid_y = (x - self.grid_offset_x) // self.cell_size, (y - self.grid_offset_y) // self.cell_size
            self.spill.pressed_actions["mouse"][0] = False
                    
            if self.player.place_ship(self.player.board, grid_x, grid_y, self.orientation, self.ship_sizes[self.ship_index]):
                self.ship_index += 1  # Gå videre til neste skip
                self.splash.play()
                        
            else:
                print("Kan ikke plassere skipet her!")
        
         # sjekker om alle ships er plasert og laster in alle motstander skip en gang
            if not self.loaded_ships and len(self.player.ships) == 5:
                self.player2.battle_info = self.good_attack_checker(self.player2, self.player)
                self.loaded_ships = True
                self.attack_phase = True
                print("ships placed")

        # Spiller sin tur
        if self.player.my_turn:
            self.text_turn = "Attack the other player board"
            x, y = self.spill.pressed_actions["mouse"][1]
            grid_x, grid_y = (x - self.grid_offset_x) // self.cell_size, (y - self.grid_offset_y) // self.cell_size
            if self.spill.pressed_actions["mouse"][0] and self.loaded_ships and 11 <= grid_x < 21 and 0 <= grid_y < self.grid_size:
                self.player.attack(self.player2.board)
                self.player.destroyed_ships = self.good_attack_checker(self.player, self.player2)[0]
                if len(self.player.good_attacks) > 0:
                    if self.player.good_attacks[-1] == self.player.attacked_positions[-1]:
                        self.player.my_turn = True
                    elif self.player.good_attacks != self.player.attacked_positions[-1]:
                        self.render()
                        time.sleep(0.5)
                elif self.player.good_attacks == []:
                    self.render()
                    time.sleep(0.5)

        # Bot sin tur
        if not self.player.my_turn and self.loaded_ships:
            self.spill.pressed_actions["mouse"][1] = (0,0)  # Nullstill klikk
            self.spill.pressed_actions["mouse"][0] = False
            self.text_turn = "Don't get hit!"
            while self.player2.attack(self, self.player) != 3: pass
            self.destroyed_ships = self.player2.battle_info[0]
            self.player.my_turn = True
        
        
        # Sjekker om en spiller har vunnet
        if self.player.all_ships_sunk() and self.loaded_ships:
            self.spill.change_state("endscreen")
            self.spill.winner = "You lost!"
        if self.player2.all_ships_sunk() and self.loaded_ships:
            self.spill.change_state("endscreen")
            self.spill.winner = "You Won!"  
                

    def render(self):
        """
        Render metoden for all rendering i Singleplayer.
        Enda et tips: Det er ingen grunn for det. Han har alt om deg fra før :)
        
        """
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
                ship_image = pygame.transform.rotate(ship_image, -90)
                
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
        # Tegner informasjonstekst
        if not self.attack_phase:
            text = "Place your ships! Press 'R' to rotate the ship"
            self.draw_text(text, 30, (0, 0, 0), self.spill.screen.get_width() // 2, self.spill.screen.get_height() - 40)
        else:
            text = "Time to battle!!"
            self.draw_text(text, 70, (0, 0, 0), self.spill.screen.get_width() // 2, self.spill.screen.get_height() - 40)
        
        # Info text
        if not self.attack_phase:
            self.draw_text(self.spill.pressed_actions["rotate"] if len(self.player.ships) < 5 else "You have placed all your ships", 40, (0, 0, 0), self.spill.screen.get_width() // 2 - self.cell_size * 5 - self.cell_size // 2, self.spill.screen.get_height() - 120)
        else:
            self.draw_text(self.text_turn, 40, (0, 0, 0), self.spill.screen.get_width() // 2 - self.cell_size * 5 - self.cell_size // 2, self.spill.screen.get_height() - 120)    
        
        self.draw_text(f"ships sunk: {self.player.destroyed_ships}", 50, (0, 0, 0), self.spill.screen.get_width() // 2, 30)
        pygame.display.flip()