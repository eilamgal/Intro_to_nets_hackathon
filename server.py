import struct
import select
import socket
import time
import os
from scapy.arch import get_if_addr
import concurrent.futures
import itertools

TCP_PORT = 2018
TIME_LIMIT = 10
BROADCAST_PORT = 13117
BROADCAST_INTERVAL = 1
MAGIC_COOKIE = 0xfeedbeef
MESSAGE_TYPE = 0X2
VIRTUAL_NETWORK = 'eth1'
MIN_TEAMS_TO_PLAY = 1


def broadcast(increment, time_limit=TIME_LIMIT, interval=BROADCAST_INTERVAL):
    """
    Broadcast an offer message to waiting clients on the specified port
    """

    ip = '<broadcast>' if os.name == 'nt' else get_if_addr(VIRTUAL_NETWORK)
    print("Server started, listening on ip address", ip)
    start_time = time.time()
    udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    # Set broadcasting mode
    udp_server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    # Set a timeout
    udp_server.settimeout(0.3)

    packed_message = struct.pack('IBH', MAGIC_COOKIE, MESSAGE_TYPE, TCP_PORT+increment)
    while time.time() - start_time < time_limit:
        try:
            udp_server.sendto(packed_message, (ip, BROADCAST_PORT))
        except Exception as e:
            print("Broadcasting error!", e)
            return False
        time.sleep(interval)
    udp_server.close()
    print('broadcast end')
    return True


def listen_for_clients(increment, time_limit=TIME_LIMIT):
    """
    Listen for clients that received the offer message and accept their connections
    """
    start_time = time.time()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setblocking(0)

    while True and time.time() - start_time < time_limit:
        try:
            server.bind(('', TCP_PORT + increment))
            break
        except Exception as massage: 
            print('Bind failed. Message', massage)
            time.sleep(1)

    server.listen(5)
    inputs = [server]
    team_names = {}  # {team_ip : team_name}

    while inputs and time.time() - start_time < time_limit:
        readable, writable, exceptional = select.select(inputs, [], inputs, (time_limit - (time.time() - start_time))) 
        for s in readable:
            if s is server:  # New client is trying to connect
                connection, client_address = s.accept()
                # print(client_address[0], "connected")
                connection.setblocking(0)
                inputs.append(connection)
                team_names[connection] = (None, client_address[0])

            else:  # The client should sent team's name
                data = s.recv(1024)
                # print("data:", data)
                if team_names[s][0] == None:
                    if data:
                        team_names[s] = (str(data, "utf-8")[0:-1], team_names[s][1])
                        # print(team_names)       
                    else:
                        inputs.remove(s)
                        s.close()
                else:
                    if data:
                        print("Unexpected data from client")

        for s in exceptional:
            inputs.remove(s)
            s.close()
        time.sleep(0.1)
    
    server.setblocking(1)

    return team_names, inputs, server


def start_new_match(team_names, sockets, server, time_limit=TIME_LIMIT):
    group1 = []
    group2 = []

    for idx, team in enumerate(team_names.values()):  #Split teams into groups
        if team != None:
            if idx % 2 == 0:
                group1.append(team)
            else:
                group2.append(team)

    teams_dictionary = {}
    for team in group1 + group2:
        teams_dictionary[team[1]] = (team[0], 1 if team in group1 else 2, 0)  # (team_name, group#, counter)
    # print(teams_dictionary)

    message = """Welcome to Keyboard Spamming Battle Royale.
Group 1:
=====
"""
    for team in group1:
        message += team[0]+'\n'
    message += "Group 2:\n=====\n"
    for team in group2:
        message += team[0]+'\n'
    message += "Start pressing keys on your keyboard as fast as you can!!"

    end_addresses = []  # Save clients' addresses to send end messages through
    print(message)
    for open_socket in sockets:
        try:
            if open_socket != server:
                open_socket.sendall(bytes(message, "utf-8"))
                open_socket.setblocking(1)
                end_addresses.append(open_socket.getpeername())
                open_socket.close()
        except Exception as e:
            print("Error while sending starting messages!", e)

    start_time = time.time()

    inputs = [server]
    socket_ips = {}

    while inputs and time.time() - start_time < time_limit:
        # try:
        readable, writable, exceptional = select.select(inputs, [], inputs, 0)
        for s in readable:
            if s is server:  # New client is trying to connect
                connection, client_address = s.accept()
                # print(client_address[0], "connected")
                connection.setblocking(0)
                inputs.append(connection)
                socket_ips[connection] = client_address[0]

            else:  # Client pressed a key
                data = s.recv(1)
                # print(data)
                if data:
                    teams_dictionary[socket_ips[connection]] = (teams_dictionary[socket_ips[connection]][0],teams_dictionary[socket_ips[connection]][1],teams_dictionary[socket_ips[connection]][2]+1)
                inputs.remove(s)
                s.close()
        for s in exceptional:
            inputs.remove(s)
            s.close()
        # except Exception as e:
        #     print("Error while receiving keys!", e)

    end_message = get_winner_annoucement(teams_dictionary.values())
    print(end_message)
    for address in end_addresses:
        try:
            open_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            open_socket.connect(address)
            open_socket.sendall(bytes(end_message, "utf-8"))  # TODO
            # open_socket.setblocking(1)
            open_socket.close()
        except Exception as e:
            print("Error while sending end messages!", e)
    # print(teams_dictionary)
    # server.setblocking(1)
    server.close()


def get_winner_annoucement(teams_dictionary):
    group1_counter = 0
    group2_counter = 0
    for team in teams_dictionary:
        if team[1] == 1:
            group1_counter += team[2]
        else:
            group2_counter += team[2]
    winner_annoucement = "Game Over!\n Group 1 typed in {} characters. Group 2 typed in {} characters.\n".format(group1_counter, group2_counter)
    if group1_counter == group2_counter:
        winner_annoucement += "Its a tie!!"
    else:
        winner_annoucement += "Group {} wins!".format(1 if group1_counter > group2_counter else 2)
    return winner_annoucement


def rainbow(text):
    colors = ['\033[3{}m{{}}\033[0m'.format(n) for n in range(1,4)]
    rainbow = itertools.cycle(colors)
    letters = [next(rainbow).format(L) for L in text]
    return ''.join(letters)


if __name__ == "__main__":
    increment = 1
    # while 1:
    with concurrent.futures.ThreadPoolExecutor() as executor:
        broadcast = executor.submit(broadcast, increment)
        teams_future = executor.submit(listen_for_clients, increment)
        team_names, sockets, server = teams_future.result()

        if len(team_names) >= MIN_TEAMS_TO_PLAY:
            match = executor.submit(start_new_match(team_names, sockets, server))
    # concurrent.futures.wait([broadcast, teams_future])
    executor.shutdown()
    # time.sleep(2)
