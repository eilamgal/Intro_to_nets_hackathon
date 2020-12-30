import struct
import socket
import time
import queue
import scapy


def broadcast(time_limit=10, interval=1, tcp_port=40440):
    start_time = time.time()

    socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    while True:
        try:
            socket_server.bind((socket.gethostname(), tcp_port))
            break
        except Exception as massage: 
            print('Bind failed. Message', massage) 

    udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    # Set broadcasting mode
    udp_server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    # Set a timeout 
    udp_server.settimeout(0.3)

    # i = 0
    while time.time() - start_time < time_limit:
        packed = struct.pack('IBH', 0xfeedbeef, 0x2, tcp_port)  # ? +i ? Message to broadcast : Magic coockie, message type, and port to connect through TCP
        # i += 1  # next client to 
        try:
            udp_server.sendto(packed, (socket.gethostname(), 13117))
        except socket.timeout:
            print("Broadcast timout!")
            
        time.sleep(interval)



if __name__ == "__main__":
    thread_1 = broadcast()
    thread_2 = listen_for_clients()
    play()


