import struct 
import socket
import time
import sys
import select
import os
import scapy
if os.name != 'nt':
    import tty
    import termios
else:
    import msvcrt


def _is_data():
    if os.name != 'nt':
        return select.select([sys.stdin], [], [], 0)[0] != []
    else:
        return msvcrt.kbhit()

def look_for_server():
    # scapy.get_if_addr('eth1')
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
    # Set broadcasting mode
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client.bind(("", 13117))

    while True:
        try:
            # print('before address')
            data, addr = client.recvfrom(1024)
            print(data, addr)
            cookie, msg_type, port_number  = struct.unpack('IBH', data)
            if cookie == 0xfeedbeef and msg_type == 0x2: # and port_number == 2018:  #  == 2018
                print("received ", hex(cookie), hex(msg_type), port_number,"from", addr[0])
                return addr[0], port_number
            time.sleep(0.1)
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
        port = client_socket.getsockname()[1]
        print(port)
        message = str(client_socket.recv(1024),"utf-8")

        # end_message_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # end_message_socket.setblocking(0)
        # end_message_socket.connect(server_address)

        print(message)

        # print("connected successfully")

        return port
    except Exception as e:
        print("Could not send team name! Trying to find a different server...", e)
        return 0


def play_with_server(server_address, my_port):
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.bind(('', my_port))
    listen_socket.listen(5)

    inputs = [listen_socket]
    outputs = []
    stop = False
    while 1:
        readable, writable, exceptional = select.select(inputs, outputs, [],0)
        # print(readable)
        for s in readable:
            if s is listen_socket:  # New client is trying to connect
                connection, client_address = s.accept()
                # print(client_address[0], "connected")
                connection.setblocking(0)
                inputs.append(connection)
                stop= True
                inputs.remove(s)
                s.close()

            else:  # The client should sent team's name
                # print("receiving")
                data = s.recv(1024)
                print(str(data,"utf-8"))
                s.close()
                inputs.remove(s)
                return

        if _is_data() and not stop:
            keys_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            keys_socket.connect(server_address)
            keys_socket.setblocking(0)
            c = sys.stdin.read(1) if os.name != 'nt' else msvcrt.getch().decode('utf-8')
            # print(c)
            keys_socket.send(bytes(c,"utf-8"))
            keys_socket.close()                

    for open_socket in inputs:
        open_socket.setblocking(1)
        open_socket.close()


if __name__ == "__main__":
    if os.name != 'nt':
        old_settings = termios.tcgetattr(sys.stdin)
        try:
            tty.setcbreak(sys.stdin.fileno())
            port = 0
            while(port == 0):
                server_address = look_for_server()
                my_port = connect_to_server(server_address)
                play_with_server(server_address, my_port)
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    else:
        port = 0
        while(port == 0):
            server_address = look_for_server()
            my_port = connect_to_server(server_address)
            play_with_server(server_address, my_port)