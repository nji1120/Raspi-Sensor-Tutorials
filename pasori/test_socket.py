from socket import socket, AF_INET,SOCK_DGRAM
import time

def sleep(start_time,sleep_time)->None:
    while time.time_ns()-start_time<sleep_time:
        pass

PORT=5000
SERVER="192.168.1.3"

sock=socket(AF_INET,SOCK_DGRAM)
sock.bind(("",PORT))
msg,address=sock.recvfrom(65335) #まずは一旦受信する
print(msg,address)


FREQUENCY=1 #Hz
count=0
while True:
    start_time=time.time_ns()
    try:        
        sock.sendto(f"{count}".encode("utf-8"),(SERVER,PORT))
        print(count)
        #--
    except KeyboardInterrupt:
        sock.close()
        break
    count+=1

    sleep(start_time,sleep_time=1/FREQUENCY*10**9)
