# https://github.com/ErikJ2005/Battleship-GameJam.git

import socket
from _thread import *
import threading
import json

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Automatically get the local machine's IP address
server = socket.gethostbyname(socket.gethostname())
port = 5555

print(f"Server IP address: {server}")

try:
    s.bind((server, port))
except socket.error as e:
    print(str(e))

s.listen(2)
print("Waiting for a connection")

currentId = "0"
pos = ["0:False:[]:False:[]:0", "1:False:[]:False:[]:0"]
active_connections = 0
lock = threading.Lock()  # Prevent race conditions when modifying shared variables
last_attacks = ["", ""]  # Store the last attack of each player
current_turn = "0"  # Track whose turn it is (0 or 1)


def reset_game():
    """Resets the game state when both players disconnect."""
    global currentId, pos, active_connections, last_attacks, current_turn
    with lock:
        if active_connections == 0:  # Ensure both players have left before resetting
            print("Resetting game state...")
            currentId = "0"
            pos = ["0:False:[]:False:[]:0", "1:False:[]:False:[]:0"]
            last_attacks = ["", ""]  # Reset attack history
            current_turn = "0"  # Reset turn to player 0

def threaded_client(conn):
    global currentId, pos, active_connections, last_attacks, current_turn
    with lock:
        active_connections += 1  # Track active players
        player_id = currentId
        conn.send(str.encode(player_id))
        currentId = "1" if currentId == "0" else "0"  # Swap between 0 and 1

    try:
        while True:
            data = conn.recv(2048)
            if not data:
                break  # Exit loop on client disconnection

            reply = data.decode('utf-8')
            arr = reply.split(":")
            id = int(arr[0])
            nid = 1 - id  # Get opponent ID
            turn = 0
            
            # Check if there's a new attack
            if arr[4] != last_attacks[id]:
                for ship in json.loads(pos[nid].split(":")[2]):
                    for part in ship[0]: # liste med int (x og y kordinat)
                        if json.loads(arr[4])[-1] == part:
                            current_turn = str(id)
                            turn = 1 
                if turn != 1:       
                    current_turn = str(nid)
                    
                last_attacks[id] = arr[4]  # Update last attack
                
            # Update player's position
            arr[5] = current_turn  # Set the current turn state
            pos[id] = ":".join(arr)

            # Send updated opponent data
            conn.sendall(str.encode(pos[nid]))


    except Exception as e:
        print(f"Error: {e}")

    print("Connection Closed")
    with lock:
        active_connections -= 1  # Decrease active players count

    reset_game()  # Check if the game should reset
    print(f"Server IP address: {server}")
    conn.close()

while True:
    conn, addr = s.accept()
    print("Connected to:", addr)
    start_new_thread(threaded_client, (conn,))