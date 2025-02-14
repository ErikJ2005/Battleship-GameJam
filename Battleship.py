"""
git config --global user.email 

Start of the project
"""
from state import State
from network import Network

class Ship:
    def __init__(self, size):
        pass
    
class Player:
    def __init__(self):
        pass

class Computer:
    def __init__(self):
        pass



class BattleShip(State):
    def __init__(self, spill):
        super().__init__(spill)
        self.net = Network()
        self.player1 = Player()
        self.player2 = Player()
        
    def send_data(self):
        """
        Send position to server
        :return: None
        """
        data = str(self.net.id) + ":" + str(self.player1.x) + "," + str(self.player1.y)
        reply = self.net.send(data)
        return reply
    
    def parse_data(data):
        try:
            d = data.split(":")[1].split(",")
            return int(d[0]), int(d[1])
        except:
            return 0,0

    def update(sefl):
        pass

    def render(sefl):
        pass
    