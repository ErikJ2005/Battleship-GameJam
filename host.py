import socket
from _thread import *
import threading
import json
import sys, time

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server = socket.gethostbyname(socket.gethostname())
port = 5555

print(f"Server IP address: {server}")

try:
    s.bind((server, port))
except socket.error as e:
    print(str(e))

s.listen(2)  # Maks 2 spillere
print("Waiting for a connection")

currentId = "0"
pos = ["0:False:[]:False:[]:0", "1:False:[]:False:[]:0"]
active_connections = 0
lock = threading.Lock()
last_attacks = ["", ""]
current_turn = "0"
running = True  # Kontrollerer hovedløkken

BROADCAST_IP = "255.255.255.255"
brodcasting = True


def udp_broadcast():
    global brodcasting
    """Broadcasts the server IP over UDP."""
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    message = f"SERVER:{socket.gethostbyname(socket.gethostname())}:5555".encode()
    while brodcasting:
        udp_sock.sendto(message, (BROADCAST_IP, 50000))
        print("Broadcasting server IP...")
        time.sleep(2)  # Send every 2 seconds


def reset_game():
    """Resetter spillet og avslutter serveren hvis ingen spillere er igjen."""
    global currentId, pos, active_connections, last_attacks, current_turn, running
    with lock:
        if active_connections == 0:  # Sjekk om begge har forlatt
            currentId = "0"
            pos = ["0:False:[]:False:[]:0", "1:False:[]:False:[]:0"]
            last_attacks = ["", ""]
            current_turn = "0"
            running = False  # Stopper hovedløkken


def threaded_client(conn):
    """Håndterer en klientforbindelse i en egen tråd."""
    global currentId, pos, active_connections, last_attacks, current_turn, brodcasting
    with lock:
        active_connections += 1
        player_id = currentId
        conn.send(str.encode(player_id))
        currentId = "1" if currentId == "0" else "0"
        if active_connections == 2:
            brodcasting = False

    try:
        while True:
            data = conn.recv(2048)
            if not data:
                break

            reply = data.decode("utf-8")
            arr = reply.split(":")
            id = int(arr[0])
            nid = 1 - id  # Motstanderens ID
            turn = 0

            # Sjekk om det er et nytt angrep
            if arr[4] != last_attacks[id]:
                for ship in json.loads(pos[nid].split(":")[2]):
                    for part in ship[0]:  # Liste med (x, y) koordinater
                        if json.loads(arr[4])[-1] == part:
                            current_turn = str(id)
                            turn = 1
                if turn != 1:
                    current_turn = str(nid)

                last_attacks[id] = arr[4]  # Oppdater siste angrep

            # Oppdater spillerens posisjon
            arr[5] = current_turn
            pos[id] = ":".join(arr)

            # Send oppdatert data til motstanderen
            conn.sendall(str.encode(pos[nid]))

    except Exception as e:
        print(f"Error: {e}")

    print("Connection Closed")
    with lock:
        active_connections -= 1  # Reduser antall aktive spillere

    reset_game()  # Sjekk om spillet skal resettes
    conn.close()


threading.Thread(target=udp_broadcast, daemon=True).start()
# Hovedløkken for å håndtere klientforbindelser
while running:
    try:
        s.settimeout(1)  # Unngå at accept() blokkerer evig
        conn, addr = s.accept()
        print(f"Connected to: {addr}")
        start_new_thread(threaded_client, (conn,))
    except socket.timeout:
        pass  # Fortsett løkken hvis det ikke er nye tilkoblinger

# Når hovedløkken stopper, lukk serveren riktig
print("Shutting down server...")
s.close()
sys.exit()
