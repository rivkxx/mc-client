import socket
from mcproto.packets.clientbound import JoinGame, ChatMessage
from mcproto.packets.serverbound import Handshake, LoginStart
from mcproto import Protocol

def create_minecraft_client(server_address, port, username):
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
            elif isinstance(packet, ChatMessage):
                print(f"[CHAT] {packet.message}")
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    server = input("Enter server address (e.g., localhost): ")
    port = int(input("Enter server port (default: 25565): "))
    username = input("Enter your username: ")
    create_minecraft_client(server, port, username)
