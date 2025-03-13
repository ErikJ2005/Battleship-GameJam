import socket

class Nettwork():
    def __init__(self, ip):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = ip # Nettverks ip

        self.port = 5555
        self.addr = (self.host, self.port)
        self.id = self.connect()

    def connect(self):
        self.client.connect(self.addr)
        return self.client.recv(2048).decode()
    
    def disconnect(self):
        self.client.close()
        
    def send(self, data : str) -> str:
        """ Sender data over nett ved hjelp at socket

        Args:
            data (str): data som skal bli sendt

        Returns:
            str: data som blir mottat
        """
        try:
            self.client.send(str.encode(data))
            reply = self.client.recv(2048).decode()
            return reply
        except socket.error as e:
            return str(e)
