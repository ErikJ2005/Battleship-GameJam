# https://github.com/Ex1118/Battleship-GameJam.git


from battleship import Player, BattleShips
import random
import pygame
import json
import time

class Bot(Player):
    def __init__(self, spill):
        super().__init__(spill,1)
        self.destroyed_ships = 0
        self.good_attacks = []
        self.focus = 0
        self.battle_info = [[]]
        self.ship_sizes = []
        self.battle_focus = False

    def place_ships(self,board: list, ship_sizes: list):
        i = 0
        while len(self.ships) < 5:
            if self.place_ship(board, random.randint(0, 9), random.randint(0, 9), random.choice(["horizontal", "vertical"]), ship_sizes[i]):
                i += 1
    
    def best_attack_location(self, defender: Player):
        best_attack = []
        first_quarter = 0
        first_max = 25
        second_quarter = 0
        secound_max = 25
        third_quarter = 0
        third_max = 25
        fourth_quarter = 0
        foruth_max = 25
        for x_pos in range(len(defender.board)):
            for y_pos in range(len(defender.board[x_pos])):
                if defender.board[y_pos][x_pos] == 3:
                    if x_pos < 5 and y_pos < 5:
                        first_quarter += 1
                    elif x_pos >= 5 and y_pos < 5:
                        second_quarter += 1
                    elif x_pos < 5 and y_pos >= 5:
                        third_quarter += 1
                    elif x_pos >= 5 and y_pos >= 5:
                        fourth_quarter += 1
                elif defender.board[y_pos][x_pos] == 2:
                    if x_pos < 5 and y_pos < 5:
                        first_max -= 1
                    elif x_pos >= 5 and y_pos < 5:
                        secound_max -= 1
                    elif x_pos < 5 and y_pos >= 5:
                        third_max -= 1
                    elif x_pos >= 5 and y_pos >= 5:
                        foruth_max -= 1
            if first_quarter < first_max  and first_quarter < second_quarter and first_quarter < third_quarter and first_quarter < fourth_quarter:
                best_attack = [random.randint(0,4), random.randint(0,4)]
            elif second_quarter < secound_max and second_quarter < first_quarter and second_quarter < third_quarter and second_quarter < fourth_quarter:
                best_attack = [random.randint(5,9), random.randint(0,4)]
            elif third_quarter < third_max and third_quarter < first_quarter and third_quarter < second_quarter and third_quarter < fourth_quarter:
                best_attack = [random.randint(0,4), random.randint(5,9)]
            elif fourth_quarter < foruth_max and fourth_quarter < first_quarter and fourth_quarter < second_quarter and fourth_quarter < third_quarter:
                best_attack = [random.randint(5,9), random.randint(5,9)]
            else:
                best_attack = [random.randint(0,9), random.randint(0,9)]
        return best_attack
                    
    def attack(self, local_battleships, enemy_board: list, defender: Player):
        attack_value = -1
        self.battle_info = local_battleships.good_attack_checker(self,defender)
        battle_info = self.battle_info
        shot_lock = True
        random_choice = random.randint(0,1)

        for i in range(len(battle_info[-1])):
                if len(battle_info[-1][i]) > 0 and len(battle_info[-1][i]) < battle_info[2][i]:
                    self.focus = i
                    self.battle_focus = True
                    break
                    
                if self.battle_focus:
                    if len(battle_info[-1][self.focus]) == battle_info[2][self.focus]:
                        self.battle_focus = False
                        
        if self.battle_focus:
            for i in range(len(battle_info[-1][self.focus])):
                if len(battle_info[-1][self.focus]) < 2:
                    z = json.loads(json.dumps(battle_info[-1][self.focus][i]))
                    if random_choice == 0:
                        start_index = 0
                        end_index = 2
                        increase = 1
                    else:
                        start_index = 1
                        end_index = -1
                        increase = -1
                    
                    for xy in range(start_index,end_index,increase):
                            start_value = -1
                            end_value = 3
                            if z[xy] == 0:
                                start_value = 1
                            elif z[xy] == 9:
                                end_value = 1
                                
                            for amount_pos in range(start_value, end_value,3):
                                z[xy] += amount_pos
                                if z not in self.attacked_positions and shot_lock:
                                    grid_x, grid_y = z
                                    shot_lock = False
                            z = json.loads(json.dumps(battle_info[-1][self.focus][i]))
                else:
                    if len(battle_info[-1][self.focus]) > 0:
                        direction_start = json.loads(json.dumps(battle_info[-1][self.focus][0]))
                        direction_end = json.loads(json.dumps(battle_info[-1][self.focus][i]))
                        z = direction_end
                        if direction_start == direction_end:
                            direction_end = json.loads(json.dumps(battle_info[-1][self.focus][i+1]))
                            if direction_start[0] == direction_end[0]:
                                xy = 1

                            elif direction_start[1] == direction_end[1]:
                                xy = 0
                        elif direction_start[0] == direction_end[0]:
                            xy = 1

                        elif direction_start[1] == direction_end[1]:
                            xy = 0

                        start_value = -1
                        end_value = 3
                        if z[xy] == 0:
                            start_value = 1
                        elif z[xy] == 9:
                            end_value = 1
                                    
                        for amount_pos in range(start_value, end_value,3):
                            z[xy] += amount_pos
                            if z not in self.attacked_positions and shot_lock:
                                grid_x, grid_y = z
                                shot_lock = False
                        z = direction_end

            
        else:

            grid_x, grid_y = self.best_attack_location(defender)
                    

        if 0 <= grid_x < self.grid_size and 0 <= grid_y < self.grid_size:
                if [grid_x, grid_y] not in self.attacked_positions:
                    self.attacked_positions.append([grid_x, grid_y])
                    
                    if enemy_board[grid_y][grid_x] == 0:
                            enemy_board[grid_y][grid_x] = 3
                            attack_value = 3
        

                    if enemy_board[grid_y][grid_x] == 1:
                            enemy_board[grid_y][grid_x] = 2
                            attack_value = 2
        if attack_value == 2 or attack_value == 3:
            local_battleships.render()
            time.sleep(1)
                        
        return attack_value
                            
                        

class LocalBattleships(BattleShips):
    def __init__(self, spill):
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



    def good_attack_checker(self, attacker: Player, defender: Player):
        ship_sunk = 0
        ship_attack_pos = []
        ship_size_pos = []
        ship_sunk_index = []
        local_defender = json.loads(json.dumps(defender.ships))
        for battleship in range(len(local_defender)):
            for attack in attacker.attacked_positions:
                if attack in local_defender[battleship][0]:
                    if attack not in attacker.good_attacks:
                        attacker.good_attacks.append(attack)
                        
        for battleship in range(len(local_defender)):
            ship_size_pos.append(len(local_defender[battleship][0]))
            ship_attack_pos.append([])
            for attack in attacker.good_attacks:
                if attack in local_defender[battleship][0]:
                    ship_attack_pos[battleship].append(attack)
                    local_defender[battleship][0].remove(attack)
                
            if len(local_defender[battleship][0]) == 0:
                ship_sunk_index.append(battleship)
                ship_sunk += 1
        return [ship_sunk, json.loads(json.dumps(defender.player_id)), ship_size_pos, ship_sunk_index, ship_attack_pos]
                    
                    
                
            

    def update(self):
        if self.spill.pressed_actions["key"][0] and self.spill.pressed_actions["key"][1] == "r":
            if self.orientation == "horizontal":
                self.orientation = "vertical"
            else:
                self.orientation = "horizontal"
            self.spill.pressed_actions["key"] = [False, ""]  # Reset key press
        

        # plassering av skip
        if self.spill.pressed_actions["mouse"][0] and len(self.player.ships) < 5:
            x, y = self.spill.pressed_actions["mouse"][1]
            grid_x, grid_y = (x - self.grid_offset_x) // self.cell_size, (y - self.grid_offset_y) // self.cell_size
            self.spill.pressed_actions["mouse"][0] = False
                    
            if self.player.place_ship(self.player.board, grid_x, grid_y, self.orientation, self.ship_sizes[self.ship_index]):
                self.ship_index += 1  # Gå videre til neste skip
                        
            else:
                print("Kan ikke plassere skipet her!")
        
         # sjekker om alle ships er plasert og laster in alle motstander skip en gang
            if not self.loaded_ships and len(self.player.ships) == 5:
                self.player2.battle_info = self.good_attack_checker(self.player2, self.player)
                self.loaded_ships = True
                self.attack_phase = True
                print("ships placed")

        if self.player.my_turn:
            self.text_turn = "Attack the other player board"
            if self.spill.pressed_actions["mouse"][0] and self.loaded_ships:
                self.player.attack(self.player2.board)
                self.player.destroyed_ships = self.good_attack_checker(self.player, self.player2)[0]
                self.spill.pressed_actions["mouse"][0] = False  # Nullstill klikk
                if len(self.player.good_attacks) > 0:
                    if self.player.good_attacks[-1] == self.player.attacked_positions[-1]:
                        self.player.my_turn = True
                    elif self.player.good_attacks != self.player.attacked_positions[-1]:
                        self.player.my_turn = False
                        self.render()
            

        if not self.player.my_turn and self.loaded_ships:
            self.spill.pressed_actions["mouse"][0] = False  # Nullstill klikk
            self.text_turn = "Hope the oponent doesn't hit you"
            while self.player2.attack(self, self.player.board, self.player) != 3: pass
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
        # Tegner informasjonstekst
        if not self.attack_phase:
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
        
        self.draw_text(f"ships sunk: {self.player.destroyed_ships}", 50, (0, 0, 0), self.spill.screen.get_width() // 2, 30)
        pygame.display.flip()
        