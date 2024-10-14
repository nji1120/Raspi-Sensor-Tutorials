from socket import socket, AF_INET,SOCK_DGRAM
import time

PORT=5000
SERVER="192.168.1.3"

sock=socket(AF_INET,SOCK_DGRAM)
sock.bind(("",PORT))


FREQUENCY=1 #Hz

while True:
    start_time=time.time_ns()
    try:        
        msg,address=sock.recvfrom(65335)
        msg=msg.decode(encoding="utf-8")
        print(msg,address)
        sock.sendto("aaaaaaa".encode("utf-8"),(SERVER,PORT))
        #--
    except KeyboardInterrupt:
        sock.close()
        break

    # sleep(start_time,sleep_time=1/FREQUENCY*10**9)
