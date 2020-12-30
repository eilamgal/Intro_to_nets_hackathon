import struct 
import socket
import time
import sys
import select
import tty
import termios


def _is_data():
    flag =select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])
    # print('is data:',flag)
    return flag


def look_for_server():
    
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
    # Set broadcasting mode
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client.bind(("", 13117))

    while True:
        try:
            data, addr = client.recvfrom(10)
            cookie, msg_type, port_number  = struct.unpack('IBH', data)
            if cookie == 0xfeedbeef and msg_type == 0x2 and port_number == 2018:  #  == 2018
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
        message = str(client_socket.recv(1024),"utf-8")

        end_message_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # end_message_socket.setblocking(0)
        end_message_socket.connect(server_address)

        print(message)

        # print("connected successfully")

        return end_message_socket
    except ConnectionRefusedError as e:
        print("Could not send team name! Trying to find a different server...", e)
        return None


def play_with_server(server_address, end_message_socket):
    print(end_message_socket.getsockname())

    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.bind(('',end_message_socket.getsockname()[1]))

    inputs = [end_message_socket]
    outputs = []
    while 1:
        readable, writable, exceptional = select.select(inputs, outputs, [],1)
        print(readable)
        for s in readable:
            if s is end_message_socket:  # New client is trying to connect
                print("receiving")
                message = s.recv(1024)
                print(str(message,"utf-8"))
                break

        if _is_data():
            keys_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            keys_socket.connect(server_address)
            keys_socket.setblocking(0)
            c = sys.stdin.read(1)
            # print(c)
            keys_socket.send(bytes(c,"utf-8"))                

    for open_socket in inputs:
        open_socket.setblocking(1)
        open_socket.close()


if __name__ == "__main__":
    old_settings = termios.tcgetattr(sys.stdin)
    try:
        tty.setcbreak(sys.stdin.fileno())
        server_connection = None
        while(server_connection == None):
            server_address = look_for_server()
            end_message_socket = connect_to_server(server_address)
            play_with_server(server_address, end_message_socket)
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)