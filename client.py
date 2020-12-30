import struct 
import socket
import time
import sys
import select
# import tty
# import termios


def _is_data():
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])


def look_for_server():
    
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
    # Set broadcasting mode
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client.bind(("", 13117))

    while True:
        try:
            data, addr = client.recvfrom(10)
            cookie, msg_type, port_number  = struct.unpack('IBH', data)
            if cookie == 0xfeedbeef and msg_type == 0x2 and port_number > 0:  #  == 2018
                print("received ", hex(cookie), hex(msg_type), port_number,"from", addr[0])
                return addr[0], port_number
            # else:
                # print("Bad argument received!")
        except (OSError, struct.error) : 
            # print("Unexpected broadcast message!")
            continue


def connect_to_server(server_address):
    print(server_address)
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(server_address)
        client_socket.send(b'Moshiki\n')

        print("connected successfully")

        return client_socket
    except ConnectionRefusedError as e:
        print("Could not send team name! Trying to find a different server...", e)
        return None


# def play_with_server(client_socket, server_address):

#     time.sleep(10)
#     # TODO try and catch
#     massage = client_socket.recv()
#     if not massage:
#         return
#     print(massage)
#     old_settings = termios.tcgetattr(sys.stdin)
#     try:
#         tty.setcbreak(sys.stdin.fileno())
#         end_time = time.time() + 10
#         while time.time() <= end_time:
#             if _is_data():
#                 c = sys.stdin.read(1)
#                 client_socket.send(bytes(c))

#     finally:
#         termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)


if __name__ == "__main__":
    server_connection = None
    while(server_connection == None):
        server_address = look_for_server()
        server_connection = connect_to_server(server_address)
    # play_with_server(server_socket)
