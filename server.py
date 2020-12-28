import struct
import socket

# packed = struct.pack('IBH',0xfeedbeef,0x2,2018)
# print(packed)
# cookie, msg_type, port_number  = struct.unpack('IBH', packed)
# print(hex(cookie), msg_type, port_number)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("www.python.org", 80))
print(socket.gethostname())


