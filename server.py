import struct
import select, socket, queue, time
import scapy
import concurrent.futures

TCP_PORT= 2018
TIME_LIMIT = 10

def broadcast(time_limit=TIME_LIMIT, interval=1):
    start_time = time.time()


    # socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # while True:
    #     try:
    #         socket_server.bind((socket.gethostname(), TCP_PORT))
    #         break
    #     except Exception as massage: 
    #         print('Bind failed. Message', massage)

    # socket_server.listen(5)
 

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


def listen_for_clients(time_limit=TIME_LIMIT):
    start_time = time.time()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setblocking(0)
    server.bind(('', TCP_PORT))
    server.listen(2)
    inputs = [server]
    team_names = {}  # {team_ip : team_name}

    while inputs and time.time() - start_time < time_limit:  # 

        readable, writable, exceptional = select.select(inputs, [], inputs, (time_limit - (time.time() - start_time))) 
        for s in readable:
            if s is server:  # New client is trying to connect
                connection, client_address = s.accept()
                # print(client_address)
                connection.setblocking(0)
                inputs.append(connection)
                team_names[connection] = (None, client_address[0])

            else:  # The client should sent team's name
                data= s.recv(1024)
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
                    inputs.remove(s)
                    s.close()

        for s in exceptional:
            inputs.remove(s)
            s.close()
    
    return team_names.values()


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


if __name__ == "__main__":
    timeout = TIME_LIMIT
    # broadcast(2)
    # team_names = listen_for_clients(10)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        broadcast = executor.submit(broadcast, timeout)
        # print(broadcast.running)
        teams_future = executor.submit(listen_for_clients, timeout)
        # print(teams_future.running)
        team_names = teams_future.result()


    for team in team_names:
        print(team[0])
    # play()


