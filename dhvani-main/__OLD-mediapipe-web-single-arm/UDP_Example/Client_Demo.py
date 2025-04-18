import socket
import time

# UDP Socket
def socket_connection():
    host = ""
    port = 8080
    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    addr = (host, port)

    while True:
        data = input(">> ")
        data = data.encode("utf-8")
        soc.sendto(data,addr)
        



socket_connection()