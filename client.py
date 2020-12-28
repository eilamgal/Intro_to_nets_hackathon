import scapy
import struct 


def look_for_server():
    pass


def connect_to_server(ip):
    pass


def play_with_server(server_socket):
    pass


if __name__ == "__main__":
    print()
    while True:
        server_ip = look_for_server()
        server_socket = connect_to_server(server_ip)
        play_with_server(server_socket)

