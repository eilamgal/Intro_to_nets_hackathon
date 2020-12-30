import struct
import select, socket, queue, time
import scapy
import concurrent.futures
import itertools

TCP_PORT= 2018
TIME_LIMIT = 10

def broadcast(time_limit=TIME_LIMIT, interval=0.6):
    print("Broadcasting")
    start_time = time.time()

    udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    # Set broadcasting mode
    udp_server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    # Set a timeout 
    udp_server.settimeout(0.3)

    while time.time() - start_time < time_limit:
        packed = struct.pack('IBH', 0xfeedbeef, 0x2, TCP_PORT)
        try:
            udp_server.sendto(packed, ('<broadcast>', 13117))  #TODO - check address
        except socket.timeout:
            print("Broadcast timout!")
        time.sleep(interval)
    
    udp_server.close()


def listen_for_clients(time_limit=TIME_LIMIT):
    print("Listening")

    start_time = time.time()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setblocking(0)

    while True and time.time() - start_time < time_limit:
        try:
            server.bind(('', TCP_PORT))
            break
        except Exception as massage: 
            print('Bind failed. Message', massage)
            time.sleep(1)

    server.listen(5)
    inputs = [server]
    team_names = {}  # {team_ip : team_name}
    print(server)
    while inputs and time.time() - start_time < time_limit:  # 
        # print(rainbow("loop"))
        readable, writable, exceptional = select.select(inputs, [], inputs, (time_limit - (time.time() - start_time))) 
        for s in readable:
            if s is server:  # New client is trying to connect
                connection, client_address = s.accept()
                print(client_address[0], "connected")
                connection.setblocking(0)
                inputs.append(connection)
                team_names[connection] = (None, client_address[0])

            else:  # The client should sent team's name
                data = s.recv(1024)
                # print("data:", data)
                if team_names[s][0] == None:
                    if data:
                        team_names[s] = (str(data,"utf-8")[0:-1], team_names[s][1])
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
    
    return team_names, inputs, server


def start_new_match(team_names, sockets, server, time_limit=TIME_LIMIT):
    print (team_names)
    group1=[]
    group2=[]

    for idx ,team in enumerate(team_names.values()):
        if  idx%2==0:
            group1.append(team)
        else:
            group2.append(team)

    # print("gr1:", group1)

    teams_dictionary = {}
    for team in group1 + group2:
        teams_dictionary[team[1]] = (team[0], 1 if team in group1 else 2, 0)
    
    # print(teams_dictionary)

    message = """Welcome to Keyboard Spamming Battle Royale.
Group 1:
=====
"""
    for team in group1:
        message += team[0]+'\n' 

    message +="Group 2:\n=====\n"
    for team in group2:
        message += team[0]+'\n'
    
    message += "Start pressing keys on your keyboard as fast as you can!!"

    print(message) 
    for open_socket in sockets:
        if open_socket != server:
            open_socket.sendall(bytes(message,"utf-8"))
            open_socket.setblocking(1)
            open_socket.close()


    # print("Playing")
    start_time = time.time()

    inputs = [server]
    socket_ips = {}

    # end_sockets = []
    # for i in range(len(teams_dictionary.keys())):
    #     end_sockets.append()

    while inputs and time.time() - start_time < time_limit:  # 
        # print("loop")
        readable, writable, exceptional = select.select(inputs, [], inputs, (time_limit - (time.time() - start_time))) 
        for s in readable:
            if s is server:  # New client is trying to connect
                connection, client_address = s.accept()
                print(client_address[0], "connected")
                connection.setblocking(0)
                inputs.append(connection)
                socket_ips[connection] = client_address[0]

            else:  # The client should sent team's name
                data = s.recv(8)
                if data:
                    teams_dictionary[socket_ips[connection]][2] += 1
                inputs.remove(s)
                s.close()
        for s in exceptional:
            inputs.remove(s)
            s.close()

    for open_socket in sockets:
        if open_socket != server:
            open_socket.sendall(bytes("goodbye","utf-8"))
            open_socket.setblocking(1)
            open_socket.close()

    print(inputs)
    server.setblocking(1)
    server.close()




# def listen_for_clients():
#     server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     server.setblocking(0)
#     server.bind(('localhost', 50000))
#     server.listen(5)
#     inputs = [server]
#     outputs = []
#     team_name = {}
#     team_counters = {}
#     while inputs:
#         readable, writable, exceptional = select.select(inputs, [], inputs)
#         for s in readable:
#             if s is server:
#                 connection, client_address = s.accept()
#                 connection.setblocking(0)
#                 inputs.append(connection)
#                 team_counters[client_address] = 0
#                 team_name[client_address] = None
#             else:
#                 data, client_address = s.recvfrom(1024)
#                 if team_name[client_address] == None:
#                     if data:
#                         team_name[client_address] = data         
#                     else:
#                         inputs.remove(s)
#                         s.close()
#                 else:
#                     if data:
#                         team_counters[client_address] += 1
#                     else:
#                         inputs.remove(s)
#                         s.close()

#         for s in writable:
#             try:
#                 next_msg = team_counters[s].get_nowait()
#             except Queue.Empty:
#                 outputs.remove(s)
#             else:
#                 s.send(next_msg)

#         for s in exceptional:
#             inputs.remove(s)
#             if s in outputs:
#                 outputs.remove(s)
#             s.close()
#             del team_counters[s]

def rainbow(text):
    colors = ['\033[3{}m{{}}\033[0m'.format(n) for n in range(1,7)]
    rainbow = itertools.cycle(colors)
    letters = [next(rainbow).format(L) for L in text]
    return ''.join(letters)

if __name__ == "__main__":
    
    # while 1:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            broadcast = executor.submit(broadcast)
            # print(broadcast.running)
            teams_future = executor.submit(listen_for_clients)
            # print(teams_future.running)
            team_names, sockets, server = teams_future.result()

        # for team in team_names:
        #     print(team[0])  
        if len(team_names) >= 1:
            print('new match')
            start_new_match(team_names, sockets, server)

        
        # play()


