import struct 
import socket


def look_for_server():
    
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
    # Set broadcasting mode
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client.bind(("", 13117))

    while True:
        try:
            data, addr = client.recvfrom(10)
            cookie, msg_type, port_number  = struct.unpack('IBH', data)
            if cookie == 0xfeedbeef and msg_type == 0x2 and port_number > 0:
                print("received ", hex(cookie), hex(msg_type), port_number,"from", addr[0])
                return addr[0], port_number
            else:
                print("Bad argument received!")
        except (OSError, struct.error) : 
            print("Unexpected message  format")


def connect_to_server(ip):
    pass 


def play_with_server(server_socket):
    pass


if __name__ == "__main__":
    while True:
        server_ip = look_for_server()
        server_socket = connect_to_server(server_ip)
        play_with_server(server_socket)    
