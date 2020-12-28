import socket
import struct
import time

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
# Set broadcasting mode
server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

# Set a timeout so the socket does not block
# indefinitely when trying to receive data.
server.settimeout(0.2)

packed = struct.pack('IBH',0xfeedbeef,0x2,2018)
# packed = struct.pack('IB',0xfeedbeef,0x2)
# packed = b'0xfeedbeef22018'

while True:
    server.sendto(packed, (socket.gethostname(), 40404))
    time.sleep(1)