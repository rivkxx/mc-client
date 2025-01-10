import socket
import json
import time
import requests
from mcproto.packets.clientbound import JoinGame, ChatMessage
from mcproto.packets.serverbound import Handshake, LoginStart, PlayerPosition
from mcproto import Protocol

MOJANG_AUTH_URL = "https://authserver.mojang.com/authenticate"

def authenticate(username, password):
    try:
        print("[INFO] Authenticating with Mojang...")
        payload = {
            "agent": {"name": "Minecraft", "version": 1},
            "username": username,
            "password": password,
            "requestUser": True
        }
        response = requests.post(MOJANG_AUTH_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        print(f"[INFO] Authentication successful for {username}.")
        return data['selectedProfile']['id'], data['accessToken']
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Authentication failed: {e}")
        return None, None

def create_minecraft_client(server_address, port, username, uuid, access_token):
    try:
        # Connect to the Minecraft server
        sock = socket.create_connection((server_address, port))
        protocol = Protocol(sock)

        # Handshake
        protocol.send_packet(
            Handshake(
                protocol_version=758,  # 1.18.2 version protocol
                server_address=server_address,
                server_port=port,
                next_state=2  # 2 = Login state
            )
        )
        print("[INFO] Sent handshake packet.")

        # Login
        protocol.send_packet(LoginStart(username=username))
        print(f"[INFO] Sent login start packet as {username}.")

        while True:
            # Receive packets from the server
            packet = protocol.read_packet()
            if isinstance(packet, JoinGame):
                print("[INFO] Successfully joined the game!")
                break
            elif isinstance(packet, ChatMessage):
                print(f"[CHAT] {packet.message}")

        # Start sending player movement
        print("[INFO] Starting player movement...")
        x, y, z = 0, 64, 0  # Initial position
        while True:
            protocol.send_packet(
                PlayerPosition(
                    x=x, y=y, z=z, on_ground=True
                )
            )
            print(f"[INFO] Player moved to {x}, {y}, {z}.")
            x += 0.1  # Move slightly along the X-axis
            time.sleep(0.1)  # Simulate a player moving every 100ms
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    auth = input("Do you want to authenticate with Mojang? (yes/no): ").strip().lower()
    if auth == "yes":
        email = input("Enter your Mojang account email: ")
        password = input("Enter your Mojang account password: ")
        uuid, token = authenticate(email, password)
        if not uuid or not token:
            print("[ERROR] Could not authenticate. Exiting.")
            exit()
    else:
        uuid, token = None, None

    server = input("Enter server address (e.g., localhost): ")
    port = int(input("Enter server port (default: 25565): "))
    username = input("Enter your username: ")
    create_minecraft_client(server, port, username, uuid, token)

               __
              / _)
     _.----._/ /
    /         /
 __/ (  |  (  |
/__.-'|_|--|__|
