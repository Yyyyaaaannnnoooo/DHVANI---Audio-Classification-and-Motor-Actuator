import socket
import time

# UDP Socket
def socket_connection():
    ip = ""
    port = 8080
    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (ip, port)
    soc.bind(server_address)
    while True:
        data, addr = soc.recvfrom(1024)
        print(addr)
        data = data.decode("utf-8")
        print(data)
        # soc.sendto(data,addr)
        # time.sleep(5)



socket_connection()